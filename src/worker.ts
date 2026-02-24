import { Worker, Job } from 'bullmq';
import { config } from './config';
import { logger } from './utils/logger';
import { getGitHubClient, getPRDiff, postComment } from './services/github';
import { analyzeCode } from './services/ai';
import { prisma } from './db';

const processReviewJob = async (job: Job) => {
    const { installationId, owner, repo, prNumber } = job.data;
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

        // 4. Post Comments
        let commentBody = `### AI Code Review\n\n**Summary:** ${aiResponse.summary}\n\n`;

        if (aiResponse.reviews && aiResponse.reviews.length > 0) {
            commentBody += `**Findings:**\n`;
            aiResponse.reviews.forEach((review: any) => {
                commentBody += `- **[${review.severity}]** ${review.file}:${review.line} - ${review.message}\n`;
                if (review.suggestion) {
                    commentBody += `  \`\`\`suggested\n${review.suggestion}\n\`\`\`\n`;
                }
            });
        } else {
            commentBody += `✅ No major issues found.`;
        }

        await postComment(octokit, owner, repo, prNumber, commentBody);
        logger.info('Review posted', { jobId: job.id });

        // 5. Save Review to DB
        await prisma.review.create({
            data: {
                repositoryId: dbRepo.id,
                prNumber,
                commitHash: job.data.commitSha || 'unknown',
                status: 'COMPLETED',
                aiResponse: aiResponse as any,
            }
        });
        logger.info('Review saved to database', { jobId: job.id });

    } catch (error: any) {
        logger.error('Job processing failed', { jobId: job.id, error: error.message });
        // Optionally save failure to DB
        throw error; // Retry job
    }
};

export const initWorker = () => {
    const worker = new Worker('review', processReviewJob, {
        connection: {
            host: config.redis.host,
            port: config.redis.port,
            password: config.redis.password,
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
