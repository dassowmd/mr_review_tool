# GitHub Pull Request Review Tool

A Streamlit application that uses Claude AI to automatically review GitHub Pull Requests.

## Features

- Fetch PR data from GitHub API
- AI-powered code review using Claude
- Clean, intuitive web interface
- Detailed analysis including:
  - Code quality assessment
  - Potential issues identification
  - Improvement suggestions
  - Overall recommendation

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your GitHub Personal Access Token
   - Add your Anthropic API key

3. **Get API Keys:**
   - **GitHub Token**: Go to GitHub Settings > Developer settings > Personal access tokens > Generate new token
     - Required scopes: `repo` (for private repos) or `public_repo` (for public repos only)
   - **Anthropic API Key**: Get from https://console.anthropic.com/

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the application in your browser
2. Paste a GitHub Pull Request URL (format: `https://github.com/owner/repo/pull/123`)
3. Click "Review PR"
4. View the AI-generated review and PR details

## Requirements

- Python 3.7+
- GitHub Personal Access Token
- Anthropic API Key