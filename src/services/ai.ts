import { GoogleGenerativeAI } from '@google/generative-ai';
import { config } from '../config';
import { logger } from '../utils/logger';

const genAI = new GoogleGenerativeAI(
  config.gemini.apiKey || ''
);

export const analyzeCode = async (diff: string, customInstructions?: string) => {
  try {
    const modelName = config.gemini.model || 'gemini-2.5-flash';
    logger.info('Starting AI analysis', { model: modelName, apiKeyPresent: !!config.gemini.apiKey });

    // Some regions/keys require v1 explicit or different model names
    const model = genAI.getGenerativeModel({
      model: modelName
    });

    const prompt = `
    You are an expert Senior Software Engineer acting as a Code Reviewer.
    Your task is to review the following Pull Request diff and provide structured feedback.

    Instructions:
    1. Focus on Bugs, Security Issues, and Performance Bottlenecks.
    2. Ignore formatting/style issues (prettier handles that).
    3. Be specific and provide code examples for fixes.
    4. Return your response in valid JSON format with the following structure:
    {
      "reviews": [
        {
          "file": "filename",
          "line": 10,
          "severity": "HIGH" | "MEDIUM" | "LOW",
          "message": "description of the issue",
          "suggestion": "code snippet to fix it"
        }
      ],
      "summary": "General summary of the changes"
    }

    ${customInstructions ? `Custom Instructions for this repo: ${customInstructions}` : ''}

    Diff:
    ${diff}
    `;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Clean up markdown code blocks if present
    const cleanJson = text.replace(/```json/g, '').replace(/```/g, '');

    return JSON.parse(cleanJson);
  } catch (error: any) {
    logger.error('AI Analysis Failed', { error: error.message });
    throw error; // Let the worker retry
  }
};
