import OpenAI from 'openai';
import { config } from '../config';
import { logger } from '../utils/logger';

const openai = new OpenAI({
  apiKey: config.openai.apiKey || ''
});

export const analyzeCode = async (diff: string, customInstructions?: string) => {
  try {
    const modelName = config.openai.model || 'gpt-4o-mini';
    logger.info('Starting AI analysis', { model: modelName, apiKeyPresent: !!config.openai.apiKey });

    const prompt = `
    You are an expert Senior Software Engineer acting as a Code Reviewer.
    Your task is to review the following Pull Request diff and provide structured feedback.

    Instructions:
    1. Focus on Bugs, Security Issues, and Performance Bottlenecks.
    2. Every finding MUST have a "file" (relative path from diff) and a "line" (the line number in the NEW version of the file).
    3. If a finding is general, include it in the "summary" instead of the "reviews" array.
    4. Ignore minor style or formatting nitpicks.
    5. Provide specific, actionable suggestions with code snippets where possible.
    6. Return your response in valid JSON format with the following structure:
    {
      "reviews": [
        {
          "file": "relative/path/to/file.ts",
          "line": 10,
          "severity": "HIGH" | "MEDIUM" | "LOW",
          "message": "Description of the issue.",
          "suggestion": "Optional code snippet for the fix."
        }
      ],
      "summary": "A concise summary of the overall review."
    }

    ${customInstructions ? `Custom Instructions for this repo: ${customInstructions}` : ''}

    Diff:
    ${diff}
    `;

    const response = await openai.chat.completions.create({
      model: modelName,
      messages: [{ role: "user", content: prompt }],
      response_format: { type: "json_object" }
    });

    const text = response.choices[0].message.content || '{}';
    return JSON.parse(text);
  } catch (error: any) {
    logger.error('AI Analysis Failed', { error: error.message });
    throw error; // Let the worker retry
  }
};
