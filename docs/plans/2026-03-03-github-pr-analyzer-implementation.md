# GitHub PR Analyzer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Streamlit app that analyzes GitHub PRs for any repository within a specific month, displaying metrics and visualizations.

**Architecture:** Use PyGithub to fetch PR data from GitHub REST API, process with pandas, and display with Streamlit components (metrics, bar charts). Modular design with separate modules for config, client, fetching, analysis, and UI.

**Tech Stack:** Python, Streamlit, PyGithub, python-dotenv, pandas

---

## Prerequisites

Before starting, ensure:
- Python 3.9+ installed
- GITHUB_TOKEN exists in `.env` file

---

### Task 1: Create requirements.txt

**Files:**
- Create: `requirements.txt`

**Step 1: Write requirements**

```txt
streamlit>=1.28.0
PyGithub>=2.1.0
python-dotenv>=1.0.0
pandas>=2.0.0
```

**Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add requirements.txt with dependencies"
```

---

### Task 2: Create config.py - Environment Configuration

**Files:**
- Create: `config.py`
- Test: `test_config.py`

**Step 1: Write the failing test**

```python
# test_config.py
import os
from unittest.mock import patch, mock_open

def test_load_github_token():
    with patch('builtins.open', mock_open(read_data='GITHUB_TOKEN=ghp_test123\n')):
        with patch.dict(os.environ, {}, clear=True):
            from config import GITHUB_TOKEN
            assert GITHUB_TOKEN == 'ghp_test123'

def test_load_github_token_missing():
    with patch('builtins.open', mock_open(read_data='OTHER_VAR=value\n')):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.GITHUB_TOKEN is None or config.GITHUB_TOKEN == ''
```

**Step 2: Run test to verify it fails**

Run: `pytest test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'config'"

**Step 3: Write minimal implementation**

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
```

**Step 4: Run test to verify it passes**

Run: `pytest test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add config.py test_config.py
git commit -m "feat: add config module for environment variables"
```

---

### Task 3: Create github_client.py - GitHub API Client

**Files:**
- Create: `github_client.py`
- Test: `test_github_client.py`

**Step 1: Write the failing test**

```python
# test_github_client.py
from unittest.mock import patch, MagicMock

def test_get_github_client():
    with patch('github_client.Github') as mock_github:
        mock_client = MagicMock()
        mock_github.return_value = mock_client

        from github_client import get_github_client
        client = get_github_client('fake_token')

        mock_github.assert_called_once_with('fake_token')
        assert client == mock_client

def test_get_github_client_no_token():
    from github_client import get_github_client

    with patch('github_client.GITHUB_TOKEN', ''):
        try:
            client = get_github_client()
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'GITHUB_TOKEN' in str(e)
```

**Step 2: Run test to verify it fails**

Run: `pytest test_github_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_client'"

**Step 3: Write minimal implementation**

```python
# github_client.py
from github import Github
from config import GITHUB_TOKEN

def get_github_client(token=None):
    """Initialize and return GitHub client with authentication."""
    token = token or GITHUB_TOKEN
    if not token:
        raise ValueError("GITHUB_TOKEN is required. Set it in .env file.")
    return Github(token)
```

**Step 4: Run test to verify it passes**

Run: `pytest test_github_client.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add github_client.py test_github_client.py
git commit -m "feat: add GitHub API client module"
```

---

### Task 4: Create pr_fetcher.py - PR Fetching Module

**Files:**
- Create: `pr_fetcher.py`
- Test: `test_pr_fetcher.py`

**Step 1: Write the failing test**

```python
# test_pr_fetcher.py
from unittest.mock import MagicMock, patch
from datetime import datetime

def test_parse_repo_url():
    from pr_fetcher import parse_repo_url

    # Test HTTPS URL
    owner, repo = parse_repo_url('https://github.com/owner/repo-name')
    assert owner == 'owner'
    assert repo == 'repo-name'

    # Test SSH URL
    owner, repo = parse_repo_url('git@github.com:owner/repo.git')
    assert owner == 'owner'
    assert repo == 'repo'

def test_is_pr_in_month():
    from pr_fetcher import is_pr_in_month
    from datetime import datetime

    # PR created in target month
    pr = MagicMock()
    pr.created_at = datetime(2024, 3, 15)

    assert is_pr_in_month(pr, 2024, 3) == True
    assert is_pr_in_month(pr, 2024, 4) == False
    assert is_pr_in_month(pr, 2023, 3) == False

def test_fetch_prs_for_month():
    from unittest.mock import MagicMock, patch
    from datetime import datetime

    with patch('pr_fetcher.get_github_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_repo = MagicMock()
        mock_client.get_repo.return_value = mock_repo

        # Mock PRs
        pr1 = MagicMock()
        pr1.created_at = datetime(2024, 3, 10)
        pr1.state = 'open'

        pr2 = MagicMock()
        pr2.created_at = datetime(2024, 2, 10)  # Different month
        pr2.state = 'open'

        mock_repo.get_pulls.return_value = [pr1, pr2]

        from pr_fetcher import fetch_prs_for_month
        result = fetch_prs_for_month('owner/repo', 2024, 3)

        assert len(result) == 1
        assert result[0].created_at.month == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest test_pr_fetcher.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'pr_fetcher'"

**Step 3: Write minimal implementation**

```python
# pr_fetcher.py
import re
from datetime import datetime
from typing import List, Tuple
from github import PullRequest
from github_client import get_github_client


def parse_repo_url(url: str) -> Tuple[str, str]:
    """Parse owner and repo name from GitHub URL."""
    # Handle HTTPS: https://github.com/owner/repo
    https_match = re.match(r'https?://github\.com/([^/]+)/([^/]+)/?', url)
    if https_match:
        return https_match.group(1), https_match.group(2).replace('.git', '')

    # Handle SSH: git@github.com:owner/repo.git
    ssh_match = re.match(r'git@github\.com:([^/]+)/([^/]+)\.?', url)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2).replace('.git', '')

    # Handle simple owner/repo format
    simple_match = re.match(r'^([^/]+)/([^/]+)$', url)
    if simple_match:
        return simple_match.group(1), simple_match.group(2)

    raise ValueError(f"Invalid GitHub URL format: {url}")


def is_pr_in_month(pr: PullRequest, year: int, month: int) -> bool:
    """Check if PR was created in the specified month."""
    return pr.created_at.year == year and pr.created_at.month == month


def fetch_prs_for_month(repo_identifier: str, year: int, month: int, state: str = 'all') -> List[PullRequest]:
    """Fetch all PRs for a repo created in the specified month."""
    # Parse owner/repo
    if '/' in repo_identifier:
        owner, repo_name = parse_repo_url(repo_identifier)
    else:
        raise ValueError(f"Invalid repo identifier: {repo_identifier}")

    # Initialize client
    client = get_github_client()

    # Get repository
    repo = client.get_repo(f"{owner}/{repo_name}")

    # Fetch PRs
    all_prs = repo.get_pulls(state=state, sort='created', direction='desc')

    # Filter by month
    prs_in_month = [
        pr for pr in all_prs
        if is_pr_in_month(pr, year, month)
    ]

    return prs_in_month
```

**Step 4: Run test to verify it passes**

Run: `pytest test_pr_fetcher.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pr_fetcher.py test_pr_fetcher.py
git commit -m "feat: add PR fetching module with URL parsing and month filtering"
```

---

### Task 5: Create pr_analyzer.py - PR Analysis Module

**Files:**
- Create: `pr_analyzer.py`
- Test: `test_pr_analyzer.py`

**Step 1: Write the failing test**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest test_pr_analyzer.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'pr_analyzer'"

**Step 3: Write minimal implementation**

```python
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

    # Check author
    if author == 'devin-ai-integration':
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
```

**Step 4: Run test to verify it passes**

Run: `pytest test_pr_analyzer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pr_analyzer.py test_pr_analyzer.py
git commit -m "feat: add PR analysis module with AI detection"
```

---

### Task 6: Create app.py - Streamlit UI

**Files:**
- Create: `app.py`

**Step 1: Write implementation**

```python
# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from pr_fetcher import fetch_prs_for_month, parse_repo_url
from pr_analyzer import analyze_prs
from config import GITHUB_TOKEN


def main():
    st.set_page_config(
        page_title="GitHub PR Analyzer",
        page_icon="🔧",
        layout="wide"
    )

    st.title("🔧 GitHub PR Analyzer")
    st.markdown("Analyze Pull Requests for any GitHub repository by month")

    # Check for GitHub token
    if not GITHUB_TOKEN:
        st.error("⚠️ GITHUB_TOKEN not found. Please set it in your .env file.")
        st.stop()

    # Sidebar for inputs
    with st.sidebar:
        st.header("Configuration")

        # Repo URL input
        repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/owner/repo",
            help="Enter the full GitHub repository URL"
        )

        # Month and Year selection
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))
        months = list(range(1, 13))
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        selected_month = st.selectbox(
            "Month",
            options=months,
            format_func=lambda x: month_names[x - 1],
            index=datetime.now().month - 1
        )

        selected_year = st.selectbox(
            "Year",
            options=years,
            index=len(years) - 1
        )

        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

    # Main content
    if analyze_button:
        if not repo_url:
            st.error("Please enter a repository URL")
            return

        try:
            # Validate URL
            owner, repo = parse_repo_url(repo_url)
            st.info(f"Analyzing **{owner}/{repo}** for {month_names[selected_month - 1]} {selected_year}...")

            # Show progress
            with st.spinner("Fetching PR data from GitHub..."):
                prs = fetch_prs_for_month(repo_url, selected_year, selected_month)

            if not prs:
                st.warning(f"No PRs found for {month_names[selected_month - 1]} {selected_year}")
                return

            # Analyze PRs
            metrics = analyze_prs(prs)

            # Display metrics
            st.subheader("📊 Summary")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total PRs", metrics['total'])
            with col2:
                st.metric("Merged", metrics['merged'])
            with col3:
                st.metric("Open", metrics['open'])

            col4, col5 = st.columns(2)
            with col4:
                st.metric("Closed (not merged)", metrics['closed'])
            with col5:
                st.metric("AI PRs", metrics['ai_prs'])

            st.divider()

            # Charts
            st.subheader("📈 Visualizations")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("**PR Status**")
                status_data = pd.DataFrame({
                    'Status': ['Merged', 'Open', 'Closed'],
                    'Count': [metrics['merged'], metrics['open'], metrics['closed']]
                })
                st.bar_chart(status_data.set_index('Status'))

            with col_chart2:
                st.markdown("**AI vs Human PRs**")
                ai_data = pd.DataFrame({
                    'Type': ['AI PRs', 'Human PRs'],
                    'Count': [metrics['ai_prs'], metrics['human_prs']]
                })
                st.bar_chart(ai_data.set_index('Type'))

            st.divider()

            # PR List
            st.subheader("📝 Pull Request Details")

            pr_data = []
            for pr in prs:
                pr_data.append({
                    'Number': f"#{pr.number}",
                    'Title': pr.title,
                    'Author': pr.user.login,
                    'Branch': pr.head.ref,
                    'State': 'Merged' if pr.merged_at else pr.state.capitalize(),
                    'AI': '✅' if (pr.head.ref.startswith('claude/') or pr.user.login == 'devin-ai-integration') else '❌',
                    'URL': pr.html_url
                })

            df = pd.DataFrame(pr_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        except ValueError as e:
            st.error(f"Invalid URL: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Make sure the repository exists and your GITHUB_TOKEN has access to it.")


if __name__ == "__main__":
    main()
```

**Step 2: Test the app runs**

Run: `streamlit run app.py --server.headless true &`
Expected: App starts without errors (may see network warning, that's OK)

Kill the process after verification: `pkill -f "streamlit run app"`

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add Streamlit UI with metrics and visualizations"
```

---

### Task 7: Create README.md

**Files:**
- Create: `README.md`

**Step 1: Write README**

```markdown
# GitHub PR Analyzer

A Streamlit application to analyze GitHub Pull Requests for any repository within a specific month.

## Features

- 📊 Analyze PRs by month and year
- 📈 View metrics: Total, Merged, Open, Closed PRs
- 🤖 Identify AI-generated PRs (branch prefix `claude/` or author `devin-ai-integration`)
- 📉 Visual bar charts for PR status and AI vs Human breakdown
- 🔍 Detailed PR list with filterable data table

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with your GitHub token:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter a GitHub repository URL (e.g., `https://github.com/owner/repo`)
2. Select the month and year to analyze
3. Click "Analyze" to fetch and analyze PRs
4. View metrics, charts, and detailed PR list

## Requirements

- Python 3.9+
- GitHub Personal Access Token with `repo` scope (for private repos)
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```

---

### Task 8: Final Integration Test

**Files:**
- Test: Manual test with real repo

**Step 1: Run all unit tests**

Run: `pytest test_*.py -v`
Expected: All tests PASS

**Step 2: Manual test with sample repo**

Run: `streamlit run app.py`

Manual steps:
1. Enter: `https://github.com/Oshiete-AI/sophia-client`
2. Select a recent month/year
3. Click Analyze
4. Verify metrics display correctly

**Step 3: Commit any final changes**

```bash
git add .
git commit -m "test: verify integration and finalize"
```

---

## Summary

This implementation creates a modular Streamlit application with:

| File | Purpose |
|------|---------|
| `config.py` | Environment configuration |
| `github_client.py` | GitHub API client |
| `pr_fetcher.py` | PR fetching with URL parsing |
| `pr_analyzer.py` | PR analysis and AI detection |
| `app.py` | Streamlit UI |
| `requirements.txt` | Dependencies |
| `README.md` | Documentation |

All modules follow TDD with corresponding test files.
