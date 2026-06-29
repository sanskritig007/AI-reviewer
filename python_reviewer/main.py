from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Header
from dotenv import load_dotenv
import hmac
import hashlib
import os

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

try:
    from .schemas import WebhookPayload
    from .github_client import GitHubClient
    from .ai_engine import review_diffs
    from .output_formatter import print_review_results
    from .observability import is_commit_processed, mark_commit_processed, logger
    from .metrics import get_metrics_tracker
except ImportError:
    from schemas import WebhookPayload
    from github_client import GitHubClient
    from ai_engine import review_diffs
    from output_formatter import print_review_results
    from observability import is_commit_processed, mark_commit_processed, logger
    from metrics import get_metrics_tracker

app = FastAPI(title="AI GitHub Code Reviewer")
github_client = GitHubClient()
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

async def process_review_task(payload: WebhookPayload, commit_id: str, base_sha: str, head_sha: str):
    tracker = get_metrics_tracker()
    tracker.reset()
    tracker.start_timer() #kitna time lg rha h usse measure kr rha h 
    logger.info(f"Starting review for commit {commit_id}")
    
    try:
        # Fetch diff purane aur nayae code ke bich ka difference
        diff_text = await github_client.get_compare_diff(
            full_name=payload.repository.full_name,
            base=base_sha,
            head=head_sha
        )
        
        if not diff_text:
            logger.info("No actionable diff found. Skipping.")
            mark_commit_processed(commit_id)
            logger.info(f"Commit {commit_id} marked as processed (no actionable diff).")
            return

        # Parse diff into chunks
        file_diffs = github_client.parse_unified_diff(diff_text) #Diff text ko files aur lines mein organize kiya jata hai
        
        # Analyze
        review_result = await review_diffs(file_diffs) #AI code ko read karta hai aur galtiyan/suggestions nikalta hai.
        
        tracker.stop_timer()
        
        # Print results
        print_review_results(review_result, commit_id)
        mark_commit_processed(commit_id)
        logger.info(f"Commit {commit_id} marked as processed.")
        
    except Exception as e:
        logger.error(f"Error during async review processing: {e}")

@app.post("/webhook")
async def github_webhook(
    request: Request,
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None)
):
    # Optional Validation of GitHub Secret
    if WEBHOOK_SECRET:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="Missing signature header")
        
        body = await request.body()
        expected_signature = "sha256=" + hmac.new(
            WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(x_hub_signature_256, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Only process push events with commits
    if x_github_event := request.headers.get("X-GitHub-Event"):
        if x_github_event != "push":
            return {"status": "ignored", "reason": "Not a push event"}

    if not payload.commits or not payload.head_commit:
        return {"status": "ignored", "reason": "No commits in push"}
        
    commit_id = payload.head_commit.id
    
    # Idempotency check
    if is_commit_processed(commit_id):
        logger.info(f"Commit {commit_id} already processed. Skipping.")
        return {"status": "skipped", "reason": "Already processed"}
        
    base_sha = payload.before
    head_sha = payload.after
    
    # Spawn background task
    background_tasks.add_task(process_review_task, payload, commit_id, base_sha, head_sha)
    
    return {"status": "accepted", "message": f"Review task queued for commit {commit_id}"}
