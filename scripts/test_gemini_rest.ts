import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.join(__dirname, '../.env') });

const API_KEY = process.env.GEMINI_API_KEY || '';

async function testRest() {
    console.log(`Listing Gemini models via REST (v1)...`);
    const url = `https://generativelanguage.googleapis.com/v1/models?key=${API_KEY}`;

    try {
        const response = await axios.get(url);
        console.log('REST List Success:', JSON.stringify(response.data, null, 2));
    } catch (err: any) {
        console.error('REST Failed:', err.response?.status, JSON.stringify(err.response?.data, null, 2));
    }
}

testRest();
