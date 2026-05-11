from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
GITHUB_PAT = os.environ.get("GITHUB_PAT")