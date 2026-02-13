import express from 'express';
import { config } from './config';
import { logger } from './utils/logger';
import { webhookHandler } from './handlers/webhook';
import { initWorker } from './worker';

const app = express();

// Middleware to parse JSON bodies
app.use(express.json());

app.post('/webhook', webhookHandler);

app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

app.listen(config.port, () => {
    logger.info(`Server running on port ${config.port}`);

    // Start the worker in the same process for MVP
    initWorker();
});
