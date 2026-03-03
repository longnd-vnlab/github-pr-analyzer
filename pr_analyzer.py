# pr_analyzer.py
from typing import List, Dict, Any
from github import PullRequest


def is_ai_pr(pr: PullRequest) -> bool:
    """Check if PR is AI-generated based on branch prefix or author."""
    branch = pr.head.ref.lower()
    author = pr.user.login.lower()

    # Check branch prefix
    if branch.startswith('claude/'):
        return True

    # Check author (substring match to catch variations like [bot])
    if 'devin-ai-integration' in author:
        return True

    return False


def analyze_prs(prs: List[PullRequest]) -> Dict[str, Any]:
    """Analyze PRs and return metrics."""
    total = len(prs)
    merged = 0
    open_count = 0
    closed = 0
    ai_prs = 0
    human_prs = 0

    for pr in prs:
        # Count by state
        if pr.merged_at is not None:
            merged += 1
        elif pr.state == 'open':
            open_count += 1
        else:
            closed += 1

        # Count AI vs Human
        if is_ai_pr(pr):
            ai_prs += 1
        else:
            human_prs += 1

    return {
        'total': total,
        'merged': merged,
        'open': open_count,
        'closed': closed,
        'ai_prs': ai_prs,
        'human_prs': human_prs
    }
