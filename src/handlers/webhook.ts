
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

    // IMPORTANT: Use raw body (Buffer)
    const rawBody = req.body;

    const digest =
        'sha256=' +
        crypto
            .createHmac('sha256', secret)
            .update(rawBody) // 👈 RAW BUFFER
            .digest('hex');

    const trusted = Buffer.from(signature);
    const untrusted = Buffer.from(digest);

    if (trusted.length !== untrusted.length) {
        return false;
    }

    return crypto.timingSafeEqual(trusted, untrusted);
};

export const webhookHandler = async (req: Request, res: Response) => {
    try {
        // 1️⃣ Verify signature
        if (!verifySignature(req)) {
            logger.warn('Invalid Webhook Signature', { ip: req.ip });
            return res.status(401).send('Unauthorized');
        }

        // 2️⃣ Parse raw body manually
        const payload = JSON.parse(req.body.toString());

        const { action, repository, pull_request, installation } = payload;
        const event = req.headers['x-github-event'];

        logger.info('Webhook received', {
            event,
            action,
            repo: repository?.full_name,
        });

        // 3️⃣ Validate installation (GitHub App requirement)
        if (!installation?.id) {
            logger.error('Missing installation ID');
            return res.status(400).send('Missing installation');
        }

        // 4️⃣ Filter only valid PR events
        if (
            event === 'pull_request' &&
            ['opened', 'synchronize', 'reopened'].includes(action)
        ) {
            await addReviewJob({
                type: 'review',
                installationId: installation.id,
                owner: repository.owner.login,
                repo: repository.name,
                prNumber: pull_request.number,
                commitSha: pull_request.head.sha,
            });

            return res.status(200).send('Queued');
        }

        return res.status(200).send('Ignored');
    } catch (error: any) {
        console.error('REAL ERROR:', error);

        logger.error('Failed to process webhook', {
            message: error?.message,
            stack: error?.stack,
        });

        return res.status(500).send('Internal Server Error');
    }
};