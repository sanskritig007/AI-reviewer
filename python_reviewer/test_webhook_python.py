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
    "before": "7473123807dc363e5d070cef68761403587f5897",
    "after": "4211d77d704fc199279075775f0a35dbf0a0d426",
    "repository": {
        "id": 12345,
        "name": "AI-reviewer",
        "full_name": "sanskritig007/AI-reviewer",
        "url": "https://github.com/sanskritig007/AI-reviewer"
    },
    "commits": [
        {
            "id": "4211d77d704fc199279075775f0a35dbf0a0d426",
            "message": "fix: return 400 Bad Request on malformed webhook payload",
            "url": "https://github.com/sanskritig007/AI-reviewer/commit/4211d77d704fc199279075775f0a35dbf0a0d426",
            "author": {
                "name": "test",
                "email": "test@test.com"
            }
        }
    ],
    "head_commit": {
        "id": "4211d77d704fc199279075775f0a35dbf0a0d426",
        "message": "fix: return 400 Bad Request on malformed webhook payload",
        "url": "https://github.com/sanskritig007/AI-reviewer/commit/4211d77d704fc199279075775f0a35dbf0a0d426",
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
