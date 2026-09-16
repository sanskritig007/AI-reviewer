# 🤖 AI Code Reviewer — Architecture, Simulation & Future Roadmap

---

## 📌 1. Project Overview & Working

This project is an **Automated AI-Powered Code Review System** built with **FastAPI**, **Google Gemini (`gemini-2.5-flash`)**, and the **GitHub REST API**.

### 🔄 End-to-End Flow:
```
1. Developer runs `git push`
        ↓
2. GitHub Webhook triggers POST request → FastAPI Server (`/webhook`) via ngrok
        ↓
3. Security & Validation (HMAC SHA-256 signature + SQLite idempotency check)
        ↓
4. Background Review Task:
   ├── a. Fetches Unified Diff from GitHub Compare API
   ├── b. Pre-AI Security Scanner: Checks for leaked API keys, tokens, or passwords
   ├── c. Prompt Engine: Injects `ai_rules.txt` ("God Mode" rules) + Diff
   ├── d. Google Gemini AI: Analyzes bugs, breaking changes, and code quality
   └── e. GitHub Client:
          - Sets commit status (`pending` → `success` ✅ / `failure` ❌)
          - Posts structured Markdown review report on the commit
```

---

## 🧪 2. What is `test_webhook_python.py` & Why is it used?

[`python_reviewer/test_webhook_python.py`](file:///Users/sanskritigoswami/Developer/AI-reviewer/python_reviewer/test_webhook_python.py) is a **Local Webhook Simulator / Mock Testing Tool**.

### 🔴 The Problem Without It:
To test code review changes without a simulator, you must:
1. Make a dummy code change.
2. Run `git commit` and `git push`.
3. Keep ngrok running and wait for GitHub webhooks.
*(Doing this 10–20 times during development is slow and pollutes git commit history).*

### 🟢 The Solution:
`test_webhook_python.py` **simulates GitHub's exact webhook payload**:
1. Reads `WEBHOOK_SECRET` from `.env`.
2. Constructs the standard GitHub webhook JSON payload (repository, commit SHAs, author).
3. Computes the valid **HMAC-SHA256 signature** (`X-Hub-Signature-256`).
4. Sends the request directly to `http://127.0.0.1:8000/webhook`.

**Result:** You can instantly trigger and test the full AI review pipeline for any past or present commit locally in less than 2 seconds!

---

## 💻 3. How to Run the System

### Tab 1: Start FastAPI Server
```bash
cd ~/Developer/AI-reviewer/python_reviewer
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Tab 2: Start ngrok Tunnel
```bash
ngrok http 8000
```
> Set your public ngrok URL in GitHub Repo **Settings → Webhooks**:  
> `https://<your-ngrok-subdomain>.ngrok-free.dev/webhook` (Content-type: `application/json`, Secret: `ai-reviewer-secret-123`).

### Local Instant Test (Without git push):
```bash
cd ~/Developer/AI-reviewer/python_reviewer
.venv/bin/python test_webhook_python.py
```

---

## 🚀 4. Future Potential & Advanced Use Cases

Because the core engine is modular and event-driven, you can easily expand it into any of the following high-value tools:

### 💡 1. Pull Request (PR) Inline Comments
* **Current:** Posts a single summary comment at the bottom of a commit.
* **Next Level:** Hook into GitHub PR review events (`pull_request`) and post line-by-line inline code comments with diff suggestions.

### 💡 2. Automated Bug-Fix PR Generator ("AI Auto-Fix")
* When Gemini detects a bug or syntax issue, it doesn't just comment — it creates a new git branch, commits the fix, and opens a Pull Request automatically.

### 💡 3. Automated Unit Test Case Generator
* For every newly committed function or module, Gemini automatically generates unit test files (e.g., `pytest`, `PHPUnit`, `Jest`) and includes them in the review comment.

### 💡 4. Real-time Security & Incident Alerts (Slack / Discord)
* If hardcoded secrets (AWS keys, Stripe secrets, passwords) are detected in diffs:
  - Block the commit immediately.
  - Send an instant high-priority alert to your team's Slack/Discord channel.

### 💡 5. Multi-Model AI Consensus Engine
* Send diffs in parallel to **Google Gemini 2.5 Flash**, **Anthropic Claude 3.5 Sonnet**, and **OpenAI GPT-4o**.
* Aggregate their findings to filter out false positives and produce enterprise-grade reviews.

### 💡 6. Pre-Commit Hook (Local Guardrail)
* Run a lightweight review locally on `git commit` before code even leaves the developer's laptop, preventing bad commits from reaching GitHub.

---

## 🎯 5. How Do We Know the AI Review is Accurate & Reliable? (Review Accuracy & Quality Assurance)

How can developers and teams trust that the AI's review is correct, not hallucinated, and actually catching real issues?

### 🛡️ 1. Multi-Layered Quality Control in the Architecture

| Mechanism | How It Ensures Accuracy |
|---|---|
| **Pydantic Schema Validation** | Enforces strict JSON output (`type`, `description`, `file`, `line_number`, `suggestion`). Hallucinated or broken formats are caught and retried automatically. |
| **Low Temperature (`temperature=0.2`)** | Set in `ai_engine.py` to make Gemini highly deterministic, analytical, and focused strictly on facts rather than creative guessing. |
| **Deterministic Security Scanner** | Regex scanner (`security_scanner.py`) catches critical leaks (API keys, passwords) with 100% mathematical accuracy before the AI is even called. |
| **"God Mode" Rule Filtering (`ai_rules.txt`)** | Controls the AI's strictness and explicitly forbids nitpicking or false warnings on standard library code. |

---

### 🧪 2. How to Benchmark and Measure AI Review Quality

1. **Gold Standard Test Suite (Ground Truth Commits):**
   - Create a test repository with 10–20 known commits:
     - **Clean Commits:** Must result in `0 issues` and Green Tick ✅.
     - **Known Bug Commits:** (e.g. missing error handling, wrong HTTP status, memory leak) — AI must identify the exact file and line number.
     - **Security Commits:** (e.g. hardcoded secrets) — Must be blocked immediately.
   - Run these periodically to measure **Precision** (avoiding false alarms) and **Recall** (catching real bugs).

2. **Real-world Example of Accuracy in Action:**
   - In our test commit `7473123`, the AI accurately flagged that returning `200 OK` on malformed webhook JSON was semantically incorrect and suggested returning `400 Bad Request`.
   - Once we fixed it to `raise HTTPException(status_code=400)`, the next commit `4211d77` was re-reviewed and immediately received `0 issues` with a Green Tick ✅!

3. **Developer Feedback Loop:**
   - Track developer reactions (👍 / 👎) on GitHub comments. If developers reject a suggestion, update `ai_rules.txt` to teach the AI the team's preferences.

4. **Multi-LLM Cross-Verification (Consensus):**
   - If high precision is required, run two different models (e.g. Gemini 2.5 Flash + Claude 3.5 Sonnet). Only flag an issue if both models independently agree.

