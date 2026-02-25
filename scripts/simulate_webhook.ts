import axios from 'axios';
import crypto from 'crypto';
import dotenv from 'dotenv';

dotenv.config();

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'ai-reviewer-secret-123';
const PORT = process.env.PORT || 3000;

const payload = {
    action: 'opened',
    repository: {
        name: 'test-repo',
        full_name: 'test-user/test-repo',
        owner: {
            login: 'test-user'
        }
    },
    pull_request: {
        number: 1,
        head: {
            sha: 'test-sha-123'
        }
    },
    installation: {
        id: 12345
    }
};

const signPayload = (payload: any) => {
    const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
    return 'sha256=' + hmac.update(JSON.stringify(payload)).digest('hex');
};

const main = async () => {
    try {
        console.log(`Sending mock webhook to http://localhost:${PORT}/webhook...`);
        const signature = signPayload(payload);

        const response = await axios.post(`http://localhost:${PORT}/webhook`, payload, {
            headers: {
                'x-github-event': 'pull_request',
                'x-hub-signature-256': signature,
                'Content-Type': 'application/json'
            }
        });

        console.log('Server response:', response.status, response.data);
    } catch (error: any) {
        console.error('Failed to send webhook:', error.response?.data || error.message);
    }
};

main();
