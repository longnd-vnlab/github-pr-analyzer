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
