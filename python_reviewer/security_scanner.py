import re
from typing import Dict, Optional
try:
    from .schemas import AIReviewResponse, AIReviewIssue
except ImportError:
    from schemas import AIReviewResponse, AIReviewIssue

# Common secret patterns
SECRET_PATTERNS = {
    "AWS Access Key": r"(?i)AKIA[0-9A-Z]{16}",
    "Google/Gemini API Key": r"(?i)AIza[0-9A-Za-z-_]{35}",
    "OpenAI API Key": r"(?i)sk-[A-Za-z0-9]{48}",
    "Generic Secret / Token": r"(?i)(secret|token|password|api_key|access_key)[a-z0-9_ .\-,]{0,25}['\"][a-zA-Z0-9_\-]{16,128}['\"]"
}

def scan_diffs(file_diffs: Dict[str, str]) -> Optional[AIReviewResponse]:
    """
    Scans the diff for potential leaked secrets.
    Returns an AIReviewResponse with issues if secrets are found, else None.
    """
    detected_issues = []

    for file_name, diff_content in file_diffs.items():
        # Only check additions (lines starting with + but not +++)
        added_lines = [
            line[1:] for line in diff_content.splitlines() 
            if line.startswith('+') and not line.startswith('+++')
        ]
        
        for i, line in enumerate(added_lines, 1):
            for secret_name, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, line):
                    detected_issues.append(
                        AIReviewIssue(
                            type="security",
                            description=f"CRITICAL: Possible {secret_name} leaked in the code! To prevent data breaches, the AI review was aborted and this code was not sent to external APIs.",
                            file=file_name,
                            line_number=None, # Diff line mapping is complex, leaving None for now
                            suggestion=f"Remove the hardcoded secret immediately. Use environment variables (e.g., .env files) or a secret manager to inject credentials."
                        )
                    )

    if detected_issues:
        return AIReviewResponse(
            summary="🚨 CRITICAL SECURITY ALERT: Automated review blocked because hardcoded secrets were detected in the pull request. The code was NOT sent to the AI for review.",
            issues=detected_issues,
            fixes=[
                "Revoke any exposed keys immediately. Even if you delete them from the file, they are in the git history.",
                "Rotate the secrets in your provider's dashboard.",
                "Use python-dotenv to load environment variables locally."
            ]
        )
    
    return None
