import { Worker, Job } from 'bullmq';
import { config } from './config';
import { logger } from './utils/logger';
import { getGitHubClient, getPRDiff, createReview, ReviewComment } from './services/github';
import { analyzeCode } from './services/ai';
import { prisma } from './db';

const processReviewJob = async (job: Job) => {
    const { installationId, owner, repo, prNumber, commitSha } = job.data;
    logger.info(`Processing review job ${job.id} for PR #${prNumber} in ${owner}/${repo}`);

    try {
        // 1. Get GitHub Client
        const octokit = await getGitHubClient(installationId);

        // 1a. Fetch or Create Repo Settings
        let dbRepo = await prisma.repository.findUnique({
            where: { githubId: BigInt(installationId) }
        });

        if (!dbRepo) {
            logger.info('Repository not found in DB, creating...', { installationId });
            dbRepo = await prisma.repository.create({
                data: {
                    githubId: BigInt(installationId),
                    owner,
                    name: repo,
                }
            });
        }

        const customPrompt = dbRepo?.customPrompt || '';

        // 2. Fetch Diff
        const diff = await getPRDiff(octokit, owner, repo, prNumber);
        if (!diff) {
            logger.warn('No diff found', { jobId: job.id });
            return;
        }

        // 3. Analyze Code
        const aiResponse = await analyzeCode(diff, customPrompt);
        logger.info('AI Analysis complete', { jobId: job.id, summary: aiResponse.summary });

        // 4. Post GitHub Review
        const summary = aiResponse.summary;
        const reviewComments: ReviewComment[] = (aiResponse.reviews || []).map((review: any) => {
            let body = `**[${review.severity}]** ${review.message}`;
            if (review.suggestion) {
                // Ensure suggestions are wrapped in appropriate markdown if not already
                const suggestion = review.suggestion.includes('```')
                    ? review.suggestion
                    : `\`\`\`suggestion\n${review.suggestion}\n\`\`\``;
                body += `\n\n${suggestion}`;
            }
            return {
                path: review.file,
                line: review.line,
                body: body
            };
        });

        await createReview(
            octokit,
            owner,
            repo,
            prNumber,
            commitSha || 'unknown',
            summary,
            reviewComments
        );
        logger.info('Review posted to GitHub', { jobId: job.id });

        // 5. Save Review to DB
        await prisma.review.create({
            data: {
                repositoryId: dbRepo.id,
                prNumber,
                commitHash: commitSha || 'unknown',
                status: 'COMPLETED',
                aiResponse: aiResponse as any,
            }
        });
        logger.info('Review saved to database', { jobId: job.id });

    } catch (error: any) {
        logger.error('Job processing failed', { jobId: job.id, error: error.message, stack: error.stack });
        throw error; // Let BullMQ handle retries
    }
};

export const initWorker = () => {
    const worker = new Worker('review', processReviewJob, {
        connection: {
            ...config.redis,
            username: "default"
        },
        concurrency: 2 // Handle 2 reviews at a time
    });

    worker.on('completed', (job) => {
        logger.info(`Job ${job.id} completed`);
    });

    worker.on('failed', (job, err) => {
        logger.error(`Job ${job?.id} failed with ${err.message}`);
    });

    logger.info('Worker started');
};
