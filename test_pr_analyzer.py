# test_pr_analyzer.py
from unittest.mock import MagicMock
from datetime import datetime

def test_is_ai_pr_by_branch():
    from pr_analyzer import is_ai_pr

    pr = MagicMock()
    pr.head.ref = 'claude/feature-123'
    pr.user.login = 'human-user'

    assert is_ai_pr(pr) == True

def test_is_ai_pr_by_author():
    from pr_analyzer import is_ai_pr

    pr = MagicMock()
    pr.head.ref = 'feature/abc'
    pr.user.login = 'devin-ai-integration'

    assert is_ai_pr(pr) == True

def test_is_ai_pr_not_ai():
    from pr_analyzer import is_ai_pr

    pr = MagicMock()
    pr.head.ref = 'feature/abc'
    pr.user.login = 'human-user'

    assert is_ai_pr(pr) == False

def test_analyze_prs():
    from pr_analyzer import analyze_prs
    from datetime import datetime

    # Create mock PRs
    pr1 = MagicMock()  # Merged AI PR
    pr1.created_at = datetime(2024, 3, 1)
    pr1.merged_at = datetime(2024, 3, 5)
    pr1.state = 'closed'
    pr1.head.ref = 'claude/feature-1'
    pr1.user.login = 'human'

    pr2 = MagicMock()  # Open human PR
    pr2.created_at = datetime(2024, 3, 2)
    pr2.merged_at = None
    pr2.state = 'open'
    pr2.head.ref = 'feature/xyz'
    pr2.user.login = 'developer'

    pr3 = MagicMock()  # Closed (not merged) human PR
    pr3.created_at = datetime(2024, 3, 3)
    pr3.merged_at = None
    pr3.state = 'closed'
    pr3.head.ref = 'bugfix/abc'
    pr3.user.login = 'developer'

    result = analyze_prs([pr1, pr2, pr3])

    assert result['total'] == 3
    assert result['merged'] == 1
    assert result['open'] == 1
    assert result['closed'] == 1
    assert result['ai_prs'] == 1
    assert result['human_prs'] == 2
