import httpx
import os
from typing import Dict, List, Optional

try:
    from .observability import logger
except ImportError:
    from observability import logger

GITHUB_API_URL = "https://api.github.com"

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def get_compare_diff(self, full_name: str, base: str, head: str) -> Optional[str]:
        """Fetch the unified diff between two commits using GitHub Compare API."""
        url = f"{GITHUB_API_URL}/repos/{full_name}/compare/{base}...{head}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=15.0)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.warning(f"Diff not found for {base}...{head} on {full_name}. Missing or no changes.")
                    return None
                else:
                    logger.error(f"GitHub API Error [{response.status_code}]: {response.text}")
                    return None
            except httpx.RequestError as e:
                logger.error(f"Request error fetching diff from GitHub: {e}")
                return None

    async def post_commit_comment(self, full_name: str, commit_sha: str, body: str) -> bool:
        """Post a comment on a specific commit."""
        url = f"{GITHUB_API_URL}/repos/{full_name}/commits/{commit_sha}/comments"
        payload = {"body": body}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=15.0)
                if response.status_code == 201:
                    logger.info(f"Successfully posted comment on commit {commit_sha}")
                    return True
                else:
                    logger.error(f"Failed to post comment. API Error [{response.status_code}]: {response.text}")
                    return False
            except httpx.RequestError as e:
                logger.error(f"Request error posting comment to GitHub: {e}")
                return False

    async def set_commit_status(self, full_name: str, commit_sha: str, state: str, description: str) -> bool:
        """Sets the status of a commit (pending, success, failure, error)."""
        url = f"{GITHUB_API_URL}/repos/{full_name}/statuses/{commit_sha}"
        
        # Determine github api version required headers for statuses if any, mostly standard.
        # However, the Accept header for statuses is standard v3 json, not diff.
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3+json"
        
        payload = {
            "state": state,
            "description": description[:140],  # GitHub limits description to 140 chars
            "context": "AI Reviewer"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if response.status_code == 201:
                    logger.info(f"Set commit {commit_sha} status to {state}")
                    return True
                else:
                    logger.error(f"Failed to set commit status. API Error [{response.status_code}]: {response.text}")
                    return False
            except httpx.RequestError as e:
                logger.error(f"Request error setting commit status: {e}")
                return False

    def parse_unified_diff(self, diff_text: str) -> Dict[str, str]:
        """
        Parses a unified diff string and splits it by file.
        Returns a dictionary mapping filename to its diff block.
        """
        if not diff_text:
            return {}
            
        file_diffs = {}
        current_file = None
        current_lines = []
        
        for line in diff_text.splitlines():
            if line.startswith("diff --git"):
                # Save previous file diff
                if current_file and current_lines:
                    file_diffs[current_file] = "\n".join(current_lines)
                
                current_lines = [line]
                
                # Extract filename. format: diff --git a/filepath b/filepath
                parts = line.split(" ")
                if len(parts) >= 4:
                    # Using b/filepath as the canonical name
                    current_file = parts[-1].removeprefix("b/")
                else:
                    current_file = f"unknown_file_{len(file_diffs)}"
            else:
                if current_file is not None:
                    current_lines.append(line)
        
        # Save last file
        if current_file and current_lines:
            file_diffs[current_file] = "\n".join(current_lines)
            
        return file_diffs
