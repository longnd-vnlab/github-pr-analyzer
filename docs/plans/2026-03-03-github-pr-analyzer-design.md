# GitHub PR Analyzer - Design Document

## Overview
Streamlit application to analyze GitHub Pull Requests for any repository within a specific month.

## Requirements

### Functional Requirements
- Input: GitHub repo URL
- Select: Month and Year from dropdown
- Display metrics:
  - Total PRs
  - Merged PRs
  - Open PRs
  - Closed PRs (not merged)
  - AI PRs (branch starts with `claude/` OR author is `devin-ai-integration`)
- Visualizations: Bar charts for PR status and AI vs Human breakdown

### Non-Functional Requirements
- Support both public and private repositories
- Use GITHUB_TOKEN from .env
- Handle errors gracefully

## Architecture

```
Streamlit UI Layer
    ↓
GitHub API Client (PyGithub)
    ↓
GitHub REST API
    ↓
Data Processing
    ↓
Streamlit Charts
```

## Tech Stack
- streamlit - UI framework
- PyGithub - GitHub API wrapper
- python-dotenv - Environment variables
- pandas - Data processing

## Components

| Component | Description |
|-----------|-------------|
| `config.py` | Load GITHUB_TOKEN from .env |
| `github_client.py` | Initialize PyGithub client with auth |
| `pr_fetcher.py` | Fetch PRs by state and filter by month |
| `pr_analyzer.py` | Analyze PR counts and detect AI PRs |
| `app.py` | Streamlit UI with forms, metrics, charts |

## Data Flow
1. User inputs repo URL + selects month/year
2. Parse owner/repo from URL
3. Fetch all PRs (all states) within selected month
4. Analyze:
   - merged: PR with `merged_at` in month
   - open: PR with `state=open` AND `created_at` in month
   - closed (not merged): `state=closed`, `merged_at=None`, `created_at` in month
   - AI PRs: branch starts with `claude/` OR author is `devin-ai-integration`
5. Render metrics + bar charts

## Error Handling

| Scenario | Handling |
|----------|----------|
| Invalid repo URL | Validate format, display clear error |
| Repo not found/private | Catch 404, display "Repo not found or private" |
| Rate limit exceeded | Catch 403, display rate limit message |
| No PRs in month | Display "No PRs found for this month" |
| GITHUB_TOKEN missing | Check at startup, display warning |

## UI Layout

```
┌─────────────────────────────────────┐
│  🔧 GitHub PR Analyzer              │
├─────────────────────────────────────┤
│  Repo URL: [____________________]   │
│  Month: [Dropdown ▼] Year: [▼]      │
│  [Analyze]                          │
├─────────────────────────────────────┤
│  📊 Results                         │
│  ┌────────┬────────┬────────┐       │
│  │ Total  │ Merged │ Open   │       │
│  │   42   │   35   │   3    │       │
│  └────────┴────────┴────────┘       │
│  ┌────────┬────────┐                │
│  │ Closed │ AI PRs │                │
│  │   4    │   12   │                │
│  └────────┴────────┘                │
├─────────────────────────────────────┤
│  [Bar Chart: PR Status]             │
│  [Bar Chart: AI vs Human PRs]       │
└─────────────────────────────────────┘
```

## Date
2026-03-03

## Approved By
User
