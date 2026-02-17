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
    // Mock for Simulation Script
    if (owner === 'test-user' && repo === 'test-repo') {
        logger.info('Returning MOCK DIFF for simulation');
        return `diff --git a/test.js b/test.js
index 83db48f..f1b2c3d 100644
--- a/test.js
+++ b/test.js
@@ -1,5 +1,5 @@
-const x = 1;
+var x = 1; // Bad practice: var
 function test() {
-  console.log("hello");
+  console.log("hello"); 
 }`;
    }

    const response = await octokit.rest.pulls.get({
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
    // Mock for Simulation Script
    if (owner === 'test-user' && repo === 'test-repo') {
        logger.info('Mock Comment Posted:', { body });
        return;
    }

    await octokit.rest.issues.createComment({
        owner,
        repo,
        issue_number: pullNumber,
        body,
    });
};
