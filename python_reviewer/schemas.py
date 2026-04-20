from pydantic import BaseModel, Field
from typing import List, Optional

class CommitAuthor(BaseModel):
    name: str
    email: str
    username: Optional[str] = None

class Commit(BaseModel):
    id: str
    message: str
    url: str
    author: CommitAuthor

class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    url: str

class WebhookPayload(BaseModel):
    ref: str
    before: str
    after: str
    repository: Repository
    commits: List[Commit]
    head_commit: Optional[Commit] = None

class AIReviewIssue(BaseModel):
    type: str = Field(description="Type of the issue: bug, breaking_change, edge_case, readability, security, etc.")
    description: str = Field(description="Detailed description of the issue or impact.")
    file: str = Field(description="The file name where the issue was found.")
    line_number: Optional[int] = Field(None, description="The specific line number if applicable. Null if it's a general file issue.")
    suggestion: str = Field(description="Suggested code fix or actionable advice.")

class AIReviewResponse(BaseModel):
    summary: str = Field(description="A high-level summary of the code changes and overall quality.")
    issues: List[AIReviewIssue] = Field(default_factory=list, description="List of detected issues.")
    fixes: List[str] = Field(default_factory=list, description="General recommendations and fixes to apply.")
