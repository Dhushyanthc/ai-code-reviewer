from fastapi import FastAPI, BackgroundTasks, Request, Depends
from pydantic import BaseModel
from app.security import verify_github_signature
from app.github import fetch_pr_diff, post_pr_comment
from app.gemini import generate_code_review

from app.security import verify_signature

app = FastAPI()

class Repository(BaseModel):
    full_name: str

class PullRequest(BaseModel):
    number: int

class WebhookPayload(BaseModel):
    action: str
    pull_request: PullRequest
    repository: Repository

@app.get("/health")
async def health_check():
    return {"status":"ok"}

@app.post("/webhook")
async def webhook(payload: WebhookPayload, background_tasks: BackgroundTasks, _:None = Depends(verify_signature)):
    
    if payload.action not in ["opened", "synchronize"]:
        return {"status":"ignored", "action": payload.action}
    
    repo_full_name = payload.repository.full_name
    pr_number = payload.pull_request.number

    background_tasks.add_task(review_pr, repo_full_name, pr_number)

    return {"status":"accepted", "pr": pr_number}


async def review_pr(repo_full_name: str, pr_number: int):
    print(f"[review_pr] Starting review for PR #{pr_number} in {repo_full_name}")

    
    print(f"[review_pr] Fetching diff...")
    diff = await fetch_pr_diff(repo_full_name, pr_number)
    print(f"[review_pr] Diff fetched — {len(diff)} characters")

    
    print(f"[review_pr] Generating review with Gemini...")
    review = await generate_code_review(diff)
    print(f"[review_pr] Review generated — {len(review)} characters")

    
    print(f"[review_pr] Posting comment to PR...")
    await post_pr_comment(repo_full_name, pr_number, review)
    print(f"[review_pr] Done. Review posted to PR #{pr_number}")