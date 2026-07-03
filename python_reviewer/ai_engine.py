import os
import re
import json
import asyncio
from typing import Dict, List, Optional
from pydantic import ValidationError
from google import genai
from google.genai import types

try:
    from .schemas import AIReviewResponse
    from .observability import logger, log_failure
    from .metrics import get_metrics_tracker
except ImportError:
    from schemas import AIReviewResponse
    from observability import logger, log_failure
    from metrics import get_metrics_tracker

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_RETRIES = 3
MAX_FILES_PER_REQUEST = 10
MAX_CHARACTERS_PER_FILE = 50000  # Increased for Gemini

# You need GEMINI_API_KEY in your environment variables
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """
You are an expert Senior Staff Software Engineer and System Architect reviewing pull request code changes.
Review the following code diff for potential bugs, breaking changes, edge cases, and maintainability issues.

Guidelines:
1. ONLY return a valid JSON object matching the requested schema.
2. DO NOT wrap your response in markdown code blocks or add any plain text outside the JSON.
3. Be strict and specific. Include file names and line numbers where possible.

Response JSON Schema:
{
  "summary": "string - high level summary of changes",
  "issues": [
    {
      "type": "string - bug|breaking_change|edge_case|readability|security",
      "description": "string - detailed issue description",
      "file": "string - file name",
      "line_number": "integer or null",
      "suggestion": "string - how to fix it"
    }
  ],
  "fixes": ["string - general recommendations"]
}

Files diff:
{diff_content}
"""

def extract_json(raw_text: str) -> str:
    """Extracts JSON structure from markdown formatted or mangled response."""
    # Try finding markdown JSON block
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Try finding the first { and last }
    first_brace = raw_text.find('{')
    last_brace = raw_text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return raw_text[first_brace:last_brace+1]
        
    return raw_text # Fallback to raw text if no braces found

async def call_ai_with_retry(diff_content: str, attempt: int = 1) -> Optional[AIReviewResponse]:
    tracker = get_metrics_tracker()
    try:
        prompt = PROMPT_TEMPLATE.replace("{diff_content}", diff_content)
        
        # Phase 3: Inject custom company guidelines if ai_rules.txt exists
        rules_path = os.path.join(os.path.dirname(__file__), '..', 'ai_rules.txt')
        if os.path.exists(rules_path):
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = f.read()
                prompt += f"\n\nCRITICAL COMPANY GUIDELINES (MUST OBEY):\n{rules}\n"
        
        # We use run_in_executor if AsyncClient is not readily available in genai,
        # but modern google-genai supports async client. Let's use the synchronous API properly in a thread,
        # or just async client if available. The simplest is client.aio.models.generate_content
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            )
        )
        
        content = response.text or ""
        
        # Track Tokens
        usage = response.usage_metadata
        if usage:
            tracker.add_tokens(usage.prompt_token_count, usage.candidates_token_count)
            
        json_str = extract_json(content)
        parsed_json = json.loads(json_str)
        validated_response = AIReviewResponse(**parsed_json)
        return validated_response
        
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"Failed to parse AI response on attempt {attempt}: {e}")
        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            return await call_ai_with_retry(diff_content, attempt + 1)
        else:
            logger.error("Max retries exceeded for AI validation.")
            log_failure({"diff": diff_content, "raw_response": content}, str(e))
            return get_fallback_response()
    except Exception as e:
        logger.error(f"Gemini API Error on attempt {attempt}: {e}")
        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 ** attempt)
            return await call_ai_with_retry(diff_content, attempt + 1)
        return get_fallback_response()

def get_fallback_response() -> AIReviewResponse:
    return AIReviewResponse(
        summary="Automated review failed due to AI or parsing errors. Please review manually.",
        issues=[],
        fixes=["Unable to process AI response. System fallback activated."]
    )

async def review_diffs(file_diffs: Dict[str, str]) -> AIReviewResponse:
    """Orchestrates review, applying chunking logic and cost control."""
    files_to_process = list(file_diffs.items())[:MAX_FILES_PER_REQUEST]
    if len(file_diffs) > MAX_FILES_PER_REQUEST:
        logger.warning(f"Diff too large. Limiting to first {MAX_FILES_PER_REQUEST} files out of {len(file_diffs)}.")
        
    merged_summary = []
    merged_issues = []
    merged_fixes = []
    
    # Process files individually or merged as chunk (simplifying to merge chunk for token efficiency here,
    # but we will cap the total string length)
    
    current_chunk_str = ""
    for fname, diff in files_to_process:
        # Skip absurdly large files
        if len(diff) > MAX_CHARACTERS_PER_FILE:
            logger.info(f"Skipping large file {fname} ({len(diff)} chars)")
            continue
            
        if len(current_chunk_str) + len(diff) > 80000: # ~20k tokens for Gemini
            # Send current chunk
            resp = await call_ai_with_retry(current_chunk_str)
            if resp:
                merged_summary.append(resp.summary)
                merged_issues.extend(resp.issues)
                merged_fixes.extend(resp.fixes)
            current_chunk_str = ""
            
        current_chunk_str += f"\nFile: {fname}\n{diff}\n"
        
    if current_chunk_str:
        resp = await call_ai_with_retry(current_chunk_str)
        if resp:
            merged_summary.append(resp.summary)
            merged_issues.extend(resp.issues)
            merged_fixes.extend(resp.fixes)
            
    final_summary = " | ".join(merged_summary) if merged_summary else "No meaningful changes reviewed."
    
    return AIReviewResponse(
        summary=final_summary,
        issues=merged_issues,
        fixes=list(set(merged_fixes)) # deduplicate fixes
    )
