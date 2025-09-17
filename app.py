import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

class GitHubPRReviewer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        if not self.github_token:
            st.error("Please set GITHUB_TOKEN in your environment variables")
        if not self.anthropic_api_key:
            st.error("Please set ANTHROPIC_API_KEY in your environment variables")

        self.client = Anthropic(api_key=self.anthropic_api_key) if self.anthropic_api_key else None

    def parse_github_url(self, url):
        pattern = r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.match(pattern, url)
        if match:
            return match.groups()
        return None, None, None

    def fetch_pr_data(self, owner, repo, pr_number):
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        pr_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
        files_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files'

        try:
            pr_response = requests.get(pr_url, headers=headers)
            files_response = requests.get(files_url, headers=headers)

            if pr_response.status_code != 200:
                return None, f"Error fetching PR: {pr_response.status_code}"

            if files_response.status_code != 200:
                return None, f"Error fetching PR files: {files_response.status_code}"

            pr_data = pr_response.json()
            files_data = files_response.json()

            return {
                'pr': pr_data,
                'files': files_data
            }, None

        except Exception as e:
            return None, f"Error: {str(e)}"

    def format_pr_for_review(self, data):
        pr = data['pr']
        files = data['files']

        formatted = f"""
## Pull Request Information
**Title:** {pr['title']}
**Author:** {pr['user']['login']}
**State:** {pr['state']}
**Created:** {pr['created_at']}
**Updated:** {pr['updated_at']}

**Description:**
{pr['body'] or 'No description provided'}

## Files Changed ({len(files)} files):
"""

        for file in files:
            formatted += f"\n### {file['filename']}"
            formatted += f"\n- **Status:** {file['status']}"
            formatted += f"\n- **Additions:** {file['additions']}, **Deletions:** {file['deletions']}"

            if file['status'] != 'removed' and 'patch' in file:
                formatted += f"\n\n**Changes:**\n```diff\n{file['patch']}\n```\n"

        return formatted

    def generate_review(self, pr_text):
        if not self.client:
            return "Claude API key not configured"

        prompt = f"""Please review this GitHub Pull Request and provide:

1. **Summary**: A brief overview of what this PR does
2. **Code Quality**: Assessment of code quality, patterns, and best practices
3. **Potential Issues**: Any bugs, security concerns, or problems you identify
4. **Suggestions**: Recommendations for improvements
5. **Overall Assessment**: Your overall recommendation (Approve, Request Changes, Comment)

Here's the PR data:

{pr_text}"""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating review: {str(e)}"

def main():
    st.set_page_config(
        page_title="MR Review Tool",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 GitHub Pull Request Review Tool")
    st.markdown("Enter a GitHub Pull Request URL to get an AI-powered code review using Claude")

    reviewer = GitHubPRReviewer()

    github_url = st.text_input(
        "GitHub PR URL",
        placeholder="https://github.com/owner/repo/pull/123",
        help="Enter the full URL of the GitHub Pull Request you want to review"
    )

    if st.button("Review PR", type="primary"):
        if not github_url:
            st.error("Please enter a GitHub PR URL")
            return

        owner, repo, pr_number = reviewer.parse_github_url(github_url)

        if not owner or not repo or not pr_number:
            st.error("Invalid GitHub PR URL format. Please use: https://github.com/owner/repo/pull/123")
            return

        with st.spinner("Fetching PR data from GitHub..."):
            data, error = reviewer.fetch_pr_data(owner, repo, pr_number)

        if error:
            st.error(error)
            return

        st.success("✅ PR data fetched successfully!")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📋 PR Details")
            pr = data['pr']

            st.markdown(f"**Title:** {pr['title']}")
            st.markdown(f"**Author:** {pr['user']['login']}")
            st.markdown(f"**State:** {pr['state']}")
            st.markdown(f"**Files Changed:** {len(data['files'])}")

            total_additions = sum(f['additions'] for f in data['files'])
            total_deletions = sum(f['deletions'] for f in data['files'])
            st.markdown(f"**Changes:** +{total_additions} -{total_deletions}")

            if pr['body']:
                st.markdown("**Description:**")
                st.markdown(pr['body'])

        with col2:
            st.subheader("🤖 AI Review")

            with st.spinner("Generating AI review with Claude..."):
                pr_text = reviewer.format_pr_for_review(data)
                review = reviewer.generate_review(pr_text)

            st.markdown(review)

        with st.expander("📁 View Changed Files"):
            for file in data['files']:
                st.markdown(f"### {file['filename']}")
                st.markdown(f"**Status:** {file['status']} | **+{file['additions']} -{file['deletions']}**")

                if file['status'] != 'removed' and 'patch' in file:
                    st.code(file['patch'], language='diff')

if __name__ == "__main__":
    main()