try:
    from .schemas import AIReviewResponse
    from .metrics import get_metrics_tracker
except ImportError:
    from schemas import AIReviewResponse
    from metrics import get_metrics_tracker

def format_review_markdown(response: AIReviewResponse, commit_id: str) -> str:
    tracker = get_metrics_tracker()
    
    md = f"## 🤖 AI Code Review Report (Commit: `{commit_id[:8]}`)\n\n"
    md += f"### Summary\n{response.summary}\n\n"
    
    if response.issues:
        md += "### ⚠️ Issues Detected\n"
        for i, issue in enumerate(response.issues, 1):
            line_ref = f":{issue.line_number}" if issue.line_number else ""
            md += f"**{i}. [{issue.type.upper()}] File: `{issue.file}{line_ref}`**\n"
            md += f"- **Description:** {issue.description}\n"
            md += f"- **Suggestion:** {issue.suggestion}\n\n"
    else:
        md += "### ⚠️ Issues Detected\nNo major issues found! 🎉\n\n"
        
    if response.fixes:
        md += "### 💡 General Fixes & Recommendations\n"
        for fix in response.fixes:
            md += f"- {fix}\n"
            
    md += "\n---\n"
    md += f"*Metrics: Execution Time: {tracker.elapsed_time:.2f}s | Tokens Used: {tracker.total_tokens} (In: {tracker.input_tokens}, Out: {tracker.output_tokens})*"
    
    return md

def print_review_results(response: AIReviewResponse, commit_id: str):
    tracker = get_metrics_tracker()
    
    print("\n" + "="*60)
    print(f"  AI CODE REVIEW REPORT - COMMIT: {commit_id[:8]}")
    print("="*60)
    
    print("\n[SUMMARY]")
    print(response.summary)
    
    if response.issues:
        print("\n[ISSUES DETECTED]")
        for i, issue in enumerate(response.issues, 1):
            print(f"  {i}. [{issue.type.upper()}] File: {issue.file}" + (f":{issue.line_number}" if issue.line_number else ""))
            print(f"     Description: {issue.description}")
            print(f"     Suggestion:  {issue.suggestion}")
            print("-" * 50)
    else:
        print("\n[ISSUES DETECTED] No major issues found! 🎉")
        
    if response.fixes:
        print("\n[GENERAL FIXES & RECOMMENDATIONS]")
        for fix in response.fixes:
            print(f"  - {fix}")
            
    print("\n" + "="*60)
    print(f"  METRICS")
    print(f"  Execution Time: {tracker.elapsed_time:.2f} seconds")
    print(f"  Tokens Used:    {tracker.total_tokens} (In: {tracker.input_tokens}, Out: {tracker.output_tokens})")
    print("="*60 + "\n")
