import dotenv from 'dotenv'; // Load .env file
dotenv.config();

export const config = {
    port: process.env.PORT || 3000,
    github: {
        appId: process.env.GITHUB_APP_ID,
        privateKey: process.env.GITHUB_APP_PRIVATE_KEY,
        webhookSecret: process.env.WEBHOOK_SECRET,
    },
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        tls: {},
    },
    gemini: {
        apiKey: process.env.GEMINI_API_KEY,
    },
};
