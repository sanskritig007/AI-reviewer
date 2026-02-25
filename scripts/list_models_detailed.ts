import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.join(__dirname, '../.env') });

const API_KEY = process.env.GEMINI_API_KEY || '';

async function listModelsDetailed() {
    console.log(`Listing Gemini models with details (v1)...`);
    const url = `https://generativelanguage.googleapis.com/v1/models?key=${API_KEY}`;

    try {
        const response = await axios.get(url);
        const models = response.data.models;
        console.log('Available Models:');
        models.forEach((m: any) => {
            console.log(`- ${m.name} (${m.displayName}) - Methods: ${m.supportedMethods.join(', ')}`);
        });
    } catch (err: any) {
        console.error('REST Failed:', err.response?.status, err.response?.data);
    }
}

listModelsDetailed();
