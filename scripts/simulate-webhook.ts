import axios from 'axios';
import crypto from 'crypto';
import dotenv from 'dotenv';

dotenv.config();

const port = process.env.PORT || 3000;
const secret = process.env.WEBHOOK_SECRET || 'your-webhook-secret';

const payload = {
  action: 'opened',
  repository: {
    name: 'test-repo',
    owner: { login: 'test-user' },
    full_name: 'test-user/test-repo'
  },
  pull_request: {
    number: 1,
    head: { sha: 'random-sha' }
  },
  installation: { id: 123456 }
};

const hmac = crypto.createHmac('sha256', secret);
const digest = 'sha256=' + hmac.update(JSON.stringify(payload)).digest('hex');

console.log(`Sending webhook to http://localhost:${port}/webhook...`);

axios.post(`http://localhost:${port}/webhook`, payload, {
  headers: {
    'x-github-event': 'pull_request',
    'x-hub-signature-256': digest,
    'Content-Type': 'application/json'
  }
})
.then(res => console.log('✅ Success:', res.status, res.data))
.catch(err => console.log('❌ Error:', err.message));
