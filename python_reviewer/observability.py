import sqlite3
import logging
import json
import os
from datetime import datetime

# Configure standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AIReviewer")

# Silence noisy HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

DB_PATH = "processed_commits.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_commits (
            commit_id TEXT PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_commit_processed(commit_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_commits WHERE commit_id = ?", (commit_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_commit_processed(commit_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO processed_commits (commit_id) VALUES (?)", (commit_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already processed
    finally:
        conn.close()

def log_failure(payload: dict, error_message: str):
    logger.error(f"Review Failure: {error_message}")
    if not os.path.exists("failures"):
        os.makedirs("failures")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"failures/failure_{timestamp}.json"
    data = {
        "error": error_message,
        "payload": payload
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    logger.info(f"Failed payload stored in {file_path}")

init_db()
