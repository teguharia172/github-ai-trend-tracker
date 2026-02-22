#!/bin/bash

# GitHub AI Trend Tracker - Setup Script
set -e

echo "🚀 Setting up GitHub AI Trend Tracker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met!${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your tokens:${NC}"
    echo "   - GITHUB_TOKEN from https://github.com/settings/tokens"
    echo "   - MOTHERDUCK_TOKEN from https://app.motherduck.com/"
    echo ""
fi

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install dbt packages
echo "📦 Installing dbt packages..."
cd dbt
dbt deps || echo "⚠️  dbt deps failed, will retry on first run"
cd ..

# Setup Evidence dashboard
echo "📦 Setting up Evidence dashboard..."
cd dashboard
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your tokens"
echo "2. Run: docker-compose up -d"
echo "3. Run: source venv/bin/activate && python pipelines/github_ai_repos.py"
echo "4. Run: cd dbt && dbt build"
echo ""
echo "Access your services:"
echo "- Prefect UI: http://localhost:4200"
echo "- Dashboard: http://localhost:3000"
