import { Request, Response } from 'express';
import crypto from 'crypto';
import { config } from '../config';
import { logger } from '../utils/logger';
import { addReviewJob } from '../queue';

const verifySignature = (req: Request): boolean => {
    const signature = req.headers['x-hub-signature-256'] as string;
    const secret = config.github.webhookSecret;

    if (!signature || !secret) {
        logger.error('Missing signature or secret');
        return false;
    }

    const hmac = crypto.createHmac('sha256', secret);
    const digest = 'sha256=' + hmac.update(JSON.stringify(req.body)).digest('hex');

    const trusted = Buffer.from(signature);
    const untrusted = Buffer.from(digest);

    if (trusted.length !== untrusted.length) {
        return false;
    }

    return crypto.timingSafeEqual(trusted, untrusted);
};

export const webhookHandler = async (req: Request, res: Response): Promise<void> => {
    // 1. Verify Signature
    if (!verifySignature(req)) {
        logger.warn('Invalid Webhook Signature', { ip: req.ip });
        res.status(401).send('Unauthorized');
        return;
    }

    const { action, repository, pull_request, installation } = req.body;
    const event = req.headers['x-github-event'];

    logger.info('Webhook received', { event, action, repo: repository?.full_name });

    // 2. Filter Events
    if (event === 'pull_request' && ['opened', 'synchronize', 'reopened'].includes(action)) {
        try {
            // 3. Enqueue Job
            await addReviewJob({
                type: 'review',
                installationId: installation.id,
                owner: repository.owner.login,
                repo: repository.name,
                prNumber: pull_request.number,
                commitSha: pull_request.head.sha,
            });
            res.status(200).send('Queued');
        } catch (error) {
            logger.error('Failed to enqueue job', { error });
            res.status(500).send('Internal Server Error');
        }
    } else {
        res.status(200).send('Ignored');
    }
};
