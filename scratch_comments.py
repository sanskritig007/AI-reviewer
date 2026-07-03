import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv(r"c:\Users\Friends\ai-reviewer\.env")
headers = {
    'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github.v3+json'
}
resp = httpx.get('https://api.github.com/repos/sanskritig007/AI-reviewer/commits/71a9d33/comments', headers=headers)
print(json.dumps(resp.json(), indent=2))
