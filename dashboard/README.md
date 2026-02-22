# GitHub AI Trend Tracker Dashboard

A professional Streamlit dashboard for visualizing AI/ML repository trends from GitHub.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

## 🚀 Live Demo

**Coming soon:** Deployed on Streamlit Cloud

## 🏃 Run Locally

```bash
cd dashboard
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501

## 📊 Features

- **🔥 Trending Tab**: Top repositories by stars/day with activity badges
- **📊 Analytics Tab**: Language statistics and charts
- **📋 All Repositories**: Full searchable/filterable table
- **🎨 Modern UI**: Dark theme with gradient accents
- **🔍 Interactive Filters**: Sidebar filters for language, status, stars

## 🔧 Environment Variables

Create `.env` file:
```
MOTHERDUCK_TOKEN=your_motherduck_token
```

## 🌐 Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set environment variables in Streamlit Cloud dashboard
5. Deploy!

## 📁 Structure

```
dashboard/
├── streamlit_app.py      # Main app
├── requirements.txt      # Python deps
├── .streamlit/
│   └── config.toml       # Theme config
└── README.md
```
