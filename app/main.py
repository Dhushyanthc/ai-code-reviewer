# app/main.py
from fastapi import FastAPI, BackgroundTasks, Request, Depends, Header
from typing import Optional
from app.security import verify_signature
from app.github import fetch_pr_diff, post_pr_comment
from app.gemini import generate_code_review

app = FastAPI()


# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- Webhook Endpoint ---
@app.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_signature),
    x_github_event: Optional[str] = Header(None)
):
    # Handle ping — GitHub sends this when webhook is first registered
    if x_github_event == "ping":
        return {"status": "pong"}

    # Ignore everything except pull_request events
    if x_github_event != "pull_request":
        return {"status": "ignored", "event": x_github_event}

    # Safe to parse body now — we know it's a pull_request event
    body = await request.json()

    action = body.get("action")
    print(f"[webhook] PR action received: {action}")

    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "action": action}

    repo_full_name = body["repository"]["full_name"]
    pr_number = body["pull_request"]["number"]

    print(f"[webhook] Queuing review for PR #{pr_number} in {repo_full_name}")
    background_tasks.add_task(review_pr, repo_full_name, pr_number)

    return {"status": "accepted", "pr": pr_number}


# --- Background Task ---
async def review_pr(repo_full_name: str, pr_number: int):
    print(f"[review_pr] Starting review — PR #{pr_number} in {repo_full_name}")

    try:
        diff = await fetch_pr_diff(repo_full_name, pr_number)
        print(f"[review_pr] Diff fetched — {len(diff)} characters")
    except Exception as e:
        print(f"[review_pr] FAILED fetch_pr_diff — PR #{pr_number} — {e}")
        return

    try:
        review = await generate_code_review(diff)
        print(f"[review_pr] Review generated — {len(review)} characters")
    except Exception as e:
        print(f"[review_pr] FAILED generate_code_review — PR #{pr_number} — {e}")
        return

    try:
        await post_pr_comment(repo_full_name, pr_number, review)
        print(f"[review_pr] Done — comment posted to PR #{pr_number}")
    except Exception as e:
        print(f"[review_pr] FAILED post_pr_comment — PR #{pr_number} — {e}")
        return


# --- Debug endpoint — remove after testing ---
@app.post("/debug-webhook")
async def debug_webhook(request: Request):
    raw_body = await request.body()
    print(f"[debug] content-type: {request.headers.get('content-type')}")
    print(f"[debug] body length: {len(raw_body)}")
    print(f"[debug] raw body: {raw_body[:500]}")
    return {"status": "ok"}