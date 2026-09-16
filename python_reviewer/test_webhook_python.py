# pyrefly: ignore [missing-import]
import httpx
import os
import hmac
import hashlib
import json
import asyncio
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load from the parent directory where your .env is
load_dotenv("../.env")

SECRET = os.getenv("WEBHOOK_SECRET") # Usually called WEBHOOK_SECRET in your .env
# Note: we used GITHUB_WEBHOOK_SECRET in main.py, let's load it just in case:
if not SECRET:
    SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

payload = {
    "ref": "refs/heads/main",
    "before": "45df1338784f2b26195051b067f2375b850bb516",
    "after": "2c4e42f1e72ac5bc5d767faee15ff1c65e58490b",
    "repository": {
        "id": 12345,
        "name": "AI-reviewer",
        "full_name": "sanskritig007/AI-reviewer",
        "url": "https://github.com/sanskritig007/AI-reviewer"
    },
    "commits": [
        {
            "id": "2c4e42f1e72ac5bc5d767faee15ff1c65e58490b",
            "message": "Setting up the server",
            "url": "https://github.com/sanskritig007/AI-reviewer/commit/2c4e42f1e72ac5bc5d767faee15ff1c65e58490b",
            "author": {
                "name": "test",
                "email": "test@test.com"
            }
        }
    ],
    "head_commit": {
        "id": "2c4e42f1e72ac5bc5d767faee15ff1c65e58490b",
        "message": "Setting up the server",
        "url": "https://github.com/sanskritig007/AI-reviewer/commit/2c4e42f1e72ac5bc5d767faee15ff1c65e58490b",
        "author": {
            "name": "test",
            "email": "test@test.com"
        }
    }
}

async def main():
    body = json.dumps(payload).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push"
    }

    if SECRET:
        signature = "sha256=" + hmac.new(SECRET.encode('utf-8'), body, hashlib.sha256).hexdigest()
        headers["X-Hub-Signature-256"] = signature

    async with httpx.AsyncClient() as client:
        print("Sending raw push webhook payload to local FastAPI server...")
        try:
            response = await client.post("http://127.0.0.1:8000/webhook", content=body, headers=headers, timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
        except Exception as e:
            print(f"Request failed! Is the FastAPI server running? Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
