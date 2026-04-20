try:
    from .schemas import AIReviewResponse
    from .metrics import get_metrics_tracker
except ImportError:
    from schemas import AIReviewResponse
    from metrics import get_metrics_tracker

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
