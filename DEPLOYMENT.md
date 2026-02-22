# 🚀 Deployment Guide

Deploy your GitHub AI Trend Tracker to run daily with free cloud services.

**Live Dashboard URL:** `https://YOUR_USERNAME.github.io/github-ai-trend-tracker`

---

## What Gets Deployed

| Component | Service | Purpose |
|-----------|---------|---------|
| Data Pipeline | GitHub Actions | Runs daily to fetch new data |
| Database | MotherDuck | Cloud storage for all data |
| Dashboard | GitHub Pages | Public-facing visualizations |

**Cost:** $0/month (all free tiers)

---

## Prerequisites

You need 2 accounts (both free):

1. **GitHub** - You already have this
2. **MotherDuck** - Sign up at https://app.motherduck.com/ (takes 2 minutes)

---

## Step 1: Get Your Tokens

### 1.1 MotherDuck Token

1. Go to https://app.motherduck.com/
2. Sign up with Google or GitHub
3. Click your profile (top right) → **Account Settings**
4. Copy the token (long string)

### 1.2 GitHub Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Check only: `public_repo`
4. Click **Generate token**
5. Copy the token (starts with `ghp_`)

---

## Step 2: Add Secrets to GitHub

These tokens are stored securely in your repo:

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add both:

| Secret Name | Value |
|-------------|-------|
| `GH_TOKEN` | Your GitHub token (ghp_xxx...) |
| `MOTHERDUCK_TOKEN` | Your MotherDuck token |

---

## Step 3: Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Under **"Build and deployment"**:
   - **Source**: Select **"GitHub Actions"**
3. Click **Save**

---

## Step 4: Push Your Code

```bash
git add .
git commit -m "Deploy to cloud"
git push origin main
```

The workflow runs automatically. Wait about 5 minutes.

---

## Step 5: View Your Dashboard

Go to: `https://YOUR_USERNAME.github.io/github-ai-trend-tracker`

(Replace `YOUR_USERNAME` with your actual GitHub username)

---

## How It Works

### Daily at 2 AM UTC:

```
GitHub Actions wakes up
    ↓
Fetches data from GitHub API
    ↓
Stores in MotherDuck cloud database
    ↓
Runs dbt transformations
    ↓
Builds Evidence dashboard
    ↓
Deploys to GitHub Pages
```

### Manual Trigger:

You can run it anytime:
1. Go to **Actions** tab
2. Click **"Daily Data Ingestion"**
3. Click **"Run workflow"**

---

## Troubleshooting

### Workflow Fails

1. Go to **Actions** tab
2. Click the failed run (red X)
3. Read the error message

**Common fixes:**
- **"Rate limit exceeded"** → Wait 1 hour, GitHub limits reset
- **"Invalid token"** → Check secrets are correct in Settings
- **"Database connection failed"** → Verify MotherDuck token

### Dashboard Not Showing

1. Check the workflow completed (green checkmark)
2. Go to **Settings** → **Pages**
3. Make sure it says "Your site is published"
4. Wait 5 minutes for cache, then hard refresh: `Ctrl+Shift+R`

### No Data in Dashboard

Test the database connection:
```bash
# Install DuckDB
brew install duckdb

# Connect to MotherDuck
duckdb "md:github_ai_analytics?motherduck_token=YOUR_TOKEN"

# Test query
SELECT COUNT(*) FROM prod.dim_repositories;
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub Actions (Daily Schedule)                                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Fetch Data  │→ │ Transform    │→ │ Build Dashboard      │   │
│  │ (GitHub API)│  │ (dbt)        │  │ (Evidence)           │   │
│  └─────────────┘  └──────────────┘  └──────────────────────┘   │
│         ↓                ↓                    ↓                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ MotherDuck Cloud Database                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ GitHub Pages (Public Dashboard)                         │   │
│  │ https://yourname.github.io/github-ai-trend-tracker      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files You Should Know

| File | Purpose |
|------|---------|
| `.github/workflows/daily-ingestion.yml` | Runs the daily pipeline |
| `pipelines/github_ai_repos.py` | Fetches data from GitHub |
| `dbt/profiles.yml` | Database connections |
| `dashboard/pages/index.md` | Dashboard layout |
| `requirements.txt` | Python packages |

---

## Support

- **Issues:** https://github.com/YOUR_USERNAME/github-ai-trend-tracker/issues
- **MotherDuck Docs:** https://motherduck.com/docs/
- **Evidence Docs:** https://docs.evidence.dev/

---

**You're done!** Your dashboard updates automatically every day. 🎉
