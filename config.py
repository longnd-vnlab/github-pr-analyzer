# config.py
import os
from dotenv import load_dotenv

load_dotenv()


def _get_env_or_default(key: str, default: str = '') -> str:
    """Get environment variable value, return default if empty or not set."""
    value = os.getenv(key, '')
    return value if value.strip() else default


# GitHub Token (optional if OAuth is configured)
GITHUB_TOKEN = _get_env_or_default('GITHUB_TOKEN', '')

# GitHub OAuth App credentials
GITHUB_CLIENT_ID = _get_env_or_default('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = _get_env_or_default('GITHUB_CLIENT_SECRET', '')
REDIRECT_URI = _get_env_or_default('REDIRECT_URI', 'http://localhost:8501/component/streamlit_oauth.authorize_button')

# ============================================
# AI Detection Configuration
# ============================================

# Enable/disable AI PR detection
AI_DETECTION_ENABLED = _get_env_or_default('AI_DETECTION_ENABLED', 'true').lower() == 'true'

# Branch prefixes that indicate AI PRs (comma-separated)
# Default: claude/, ai/, gpt/, copilot/
_branch_prefixes = _get_env_or_default('AI_BRANCH_PREFIXES', 'claude/')
AI_BRANCH_PREFIXES = [
    prefix.strip().lower()
    for prefix in _branch_prefixes.split(',')
    if prefix.strip()
]

# Author patterns that indicate AI PRs (comma-separated, substring match)
# Default: devin-ai-integration
_author_patterns = _get_env_or_default('AI_AUTHOR_PATTERNS', 'devin-ai-integration')
AI_AUTHOR_PATTERNS = [
    pattern.strip().lower()
    for pattern in _author_patterns.split(',')
    if pattern.strip()
]
