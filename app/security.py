import hashlib
import hmac
import os
from fastapi import Request, HTTPException
from app.config import WEBHOOK_SECRET

async def verify_signature(request: Request):
  """FastAPI dependency runs before the webhook handler.
  Verifies the request is from the GitHub. 
  Return 401 if the signature is invalid or missing."""

  signature_header = request.headers.get("X-Hub-Signature-256")

  if not signature_header:
    raise HTTPException(
      status_code=401,
      detail="Missing X-Hub-Signature-256 header"
    )
  
  body = await request.body()

  expected_signature = "sha256=" + hmac.new(
    key = WEBHOOK_SECRET.encode("utf-8"),
    msg = body,
    digestmod = hashlib.sha256
  ).hexdigest()

  if not hmac.compare_digest(expected_signature, signature_header):
    HTTPException(
      status_code=401,
      detail= "Invalid signature - request not from GitHub"
    )