from fastapi import FastAPI, BackgroundTasks, Request, Depends
from pydantic import BaseModel

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
    print(f"Processing PR #{pr_number} in {repo_full_name}")