import { Queue } from 'bullmq';
import { config } from '../config';
import { logger } from '../utils/logger';
export const reviewQueue = new Queue("review", {
    connection: {
        ...config.redis,
        username: "default",
    },
});


reviewQueue.on('error', (err) => {
    logger.error('Redis Queue Error', { error: err.message });
});

export const addReviewJob = async (data: any) => {
    try {
        const job = await reviewQueue.add('review-job', data, {
            attempts: 3,
            backoff: {
                type: 'exponential',
                delay: 1000,
            },
        });
        logger.info(`Job added to queue`, { jobId: job.id, repo: data.repo });
        return job;
    } catch (error: any) {
        logger.error('Failed to add job to queue', { error: error.message });
        throw error;
    }
};
