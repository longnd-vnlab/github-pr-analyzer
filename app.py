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
                    'AI': '✅' if (pr.head.ref.lower().startswith('claude/') or 'devin-ai-integration' in pr.user.login.lower()) else '❌',
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
