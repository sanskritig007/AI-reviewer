import { analyzeCode } from '../src/services/ai';
import { logger } from '../src/utils/logger';

async function testAI() {
    console.log('Testing AI analysis directly...');
    const mockDiff = `diff --git a/hello.js b/hello.js
index 0000000..e69de29
--- a/hello.js
+++ b/hello.js
@@ -0,0 +1 @@
+console.log("hello world");`;

    try {
        const result = await analyzeCode(mockDiff, "Be very brief.");
        console.log('AI Result:', JSON.stringify(result, null, 2));
    } catch (err: any) {
        console.error('AI Test Failed:', err.message);
    }
}

testAI();
