import { Octokit } from 'octokit';
import { createAppAuth } from '@octokit/auth-app';
import { config } from '../config';
import { logger } from '../utils/logger';

export const getGitHubClient = async (installationId: number) => {
    try {
        const octokit = new Octokit({
            authStrategy: createAppAuth,
            auth: {
                appId: config.github.appId,
                privateKey: config.github.privateKey,
                installationId,
            },
        });
        return octokit;
    } catch (error: any) {
        logger.error('Failed to create GitHub client', { error: error.message });
        throw error;
    }
};

export const getPRDiff = async (octokit: Octokit, owner: string, repo: string, pullNumber: number) => {
    const response = await octokit.pulls.get({
        owner,
        repo,
        pull_number: pullNumber,
        mediaType: {
            format: 'diff',
        },
    });
    return response.data as unknown as string; // diff format
};

export const postComment = async (octokit: Octokit, owner: string, repo: string, pullNumber: number, body: string) => {
    await octokit.issues.createComment({
        owner,
        repo,
        issue_number: pullNumber,
        body,
    });
};
