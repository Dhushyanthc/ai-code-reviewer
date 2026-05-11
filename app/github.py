from app.config import GITHUB_PAT
import httpx

GITHUB_API_BASE = "https://api.github.com"

BASE_HEADERS = {
  "Authorization": f"Bearer {GITHUB_PAT}",
  "Accept": "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28"
}


async def fetch_pr_diff(repo_full_name: str, pr_number: int) -> str:
  """
  Fetches the unified diff for a pull request.
  Returns the raw diff as a string.

  repo_full_name: "owner/repo"
  pr_number: 42
  """

  url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/pulls/{pr_number}"

  diff_header = {
    **BASE_HEADERS,
    "Accept": "application/vnd.github.diff"
  }

  async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=diff_header)

    response.raise_for_status()

    return response.text
  

async def post_pr_comment(repo_full_name: str, pr_number: int, comment: str) -> None:
    """
    Posts a comment on the pull request.

    repo_full_name: "owner/repo"
    pr_number: 42
    body: markdown string - Gemini's code review
    """

    url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/issues/{pr_number}/comments"

    async with httpx.AsyncClient() as client: 
      response = await client.post(
        url,
        headers = BASE_HEADERS,
        json = {"body": body}
      )

      response.raise_for_status()