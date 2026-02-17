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
    full_name: 'test-user/test-repo',
    id: 123456789 // Added fake repo ID
  },
  pull_request: {
    number: 1,
    head: { sha: 'random-sha' },
    title: 'Test PR'
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
  .catch(err => {
    console.error('❌ Error Details:');
    if (err.code === 'ECONNREFUSED') {
      console.error('🚨 Connection Refused: The server is NOT running.');
      console.error(`Ensure you have 'npm run dev' running in a SEPARATE terminal.`);
    } else if (err.response) {
      console.error('Status:', err.response.status);
      console.error('Data:', err.response.data);
    } else if (err.request) {
      console.error('No response received.');
      console.error('Error Message:', err.message);
    } else {
      console.error('Setup Error:', err.message);
    }
  });
