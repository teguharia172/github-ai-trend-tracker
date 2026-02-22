# 🚀 GitHub AI Trend Tracker

Track trending AI/ML repositories from GitHub with automated daily ingestion and a live dashboard.

[![Daily Ingestion](https://github.com/YOUR_USERNAME/github-ai-trend-tracker/actions/workflows/daily-ingestion.yml/badge.svg)](https://github.com/YOUR_USERNAME/github-ai-trend-tracker/actions/workflows/daily-ingestion.yml)

## 📊 What It Does

- **Ingests** AI repository data from GitHub API daily
- **Transforms** raw data into analytics-ready models using dbt
- **Stores** everything in MotherDuck cloud database
- **Visualizes** trends via an interactive dashboard

## 🏗️ Architecture

```
GitHub API → Python/dlt → MotherDuck Cloud → dbt → Dashboard
     ↑___________________________|
         (Daily via GitHub Actions)
```

**Tech Stack:**
- **Ingestion**: Python + dlt (data loading tool)
- **Orchestration**: GitHub Actions (free, runs daily)
- **Database**: MotherDuck (cloud DuckDB, free tier)
- **Transformations**: dbt (data build tool)
- **Dashboard**: Evidence.dev
- **CI/CD**: GitHub Actions (free tier)

## 📁 Repository Structure

```
github-ai-trend-tracker/
├── .github/workflows/          # CI/CD automation
│   └── daily-ingestion.yml     # Runs pipeline daily
├── dbt/                        # Data transformations
│   ├── models/                 # SQL models (staging, intermediate, marts)
│   └── profiles.yml            # Database connections
├── dashboard/                  # Evidence dashboard
│   ├── pages/
│   │   └── index.md           # Dashboard definition
│   └── evidence.config.yaml   # Dashboard config
├── pipelines/                  # Data ingestion
│   └── github_ai_repos.py     # Main pipeline code
├── requirements.txt            # Python dependencies
├── Makefile                    # Useful commands
└── DEPLOYMENT.md              # Deployment guide
```

## 🚀 Quick Start (Local Development)

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/github-ai-trend-tracker.git
cd github-ai-trend-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make setup
```

### 2. Configure Environment

```bash
# Copy example
cp .env.example .env

# Edit .env with your tokens:
# GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
# MOTHERDUCK_TOKEN=md_token_xxxxxxxx (optional for local)
```

### 3. Run Pipeline Locally

```bash
# Run full pipeline (saves to local DuckDB)
make pipeline

# Run dbt transformations
make dbt-build

# Start dashboard
make dashboard
```

## ☁️ Deploy to Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete cloud deployment instructions.

**Quick summary:**
1. Sign up for [MotherDuck](https://app.motherduck.com/) (cloud DB)
2. Sign up for [Prefect Cloud](https://app.prefect.cloud/) (scheduler)
3. Add 2 secrets to GitHub repo settings
4. Pipeline runs automatically every day!

## 📊 Data Model

### Raw Data (from GitHub API)
- Repository metadata (stars, forks, language)
- Search context (which query found it)
- Timestamps

### Analytics Models (dbt)
| Model | Description |
|-------|-------------|
| `dim_repositories` | Clean repo dimension table |
| `fct_trending_repos` | Growth metrics, velocity |
| `fct_language_trends` | Language breakdown stats |

### AI Categories
- **LLMs** - GPT, Claude, Llama, etc.
- **Agents & RAG** - LangChain, AutoGen, etc.
- **Machine Learning** - Traditional ML
- **Deep Learning Frameworks** - PyTorch, TensorFlow
- **Infrastructure & Tools** - Vector DBs, MLOps
- And more...

## 🛠️ Available Commands

```bash
make help              # Show all commands
make setup             # Install dependencies
make pipeline          # Run data ingestion
make dbt-run           # Run dbt models
make dbt-test          # Run dbt tests
make dbt-build         # Run models + tests
make dashboard         # Start local dashboard
make test              # Run Python tests
make clean             # Clean up generated files
```

## 📈 Current Stats

Tracking **1,079 AI repositories** across **31 programming languages** and **10 categories**.

**Top Categories:**
- LLMs: 369 repos
- Agents & RAG: 188 repos
- Machine Learning: 129 repos

**Top Languages:**
- Python: 511 repos (53.8%)
- TypeScript: 130 repos (12.6%)
- Jupyter Notebook: 108 repos (10.6%)

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GH_TOKEN` | Yes | GitHub Personal Access Token |
| `MOTHERDUCK_TOKEN` | For cloud | MotherDuck API token |


## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment guide
- [dbt docs](dbt/README.md) - Data model documentation
- [Pipeline docs](pipelines/README.md) - Ingestion code details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

Built with ❤️ using open source tools
