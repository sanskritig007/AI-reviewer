import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.join(__dirname, "../.env") });

async function listModels() {
    try {
        console.log("Listing available models...");

        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models?key=${process.env.GEMINI_API_KEY}`
        );

        const data = await response.json();
        console.log(JSON.stringify(data, null, 2));
    } catch (err: any) {
        console.error("List Models Failed:", err.message);
    }
}

listModels();