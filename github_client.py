# github_client.py
from github import Github
from config import GITHUB_TOKEN


def get_github_client(token=None):
    """Initialize and return GitHub client with authentication."""
    token = token or GITHUB_TOKEN
    if not token:
        raise ValueError("GITHUB_TOKEN is required. Set it in .env file.")
    return Github(token)
