.PHONY: help setup pipeline dbt-run dbt-test dbt-build dashboard test lint format clean

help: ## Show this help message
	@echo "GitHub AI Trend Tracker - Available Commands"
	@echo "============================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Run initial setup
	@echo "Setting up GitHub AI Trend Tracker..."
	pip install --upgrade pip
	pip install -r requirements.txt
	cd dbt && dbt deps
	@echo "Setup complete!"

pipeline: ## Run the pipeline locally with DuckDB
	@echo "Running pipeline locally..."
	python pipelines/github_ai_repos.py

dbt-run: ## Run dbt models locally
	cd dbt && dbt run --target dev

dbt-test: ## Run dbt tests
	cd dbt && dbt test

dbt-build: ## Run dbt build (models + tests)
	cd dbt && dbt build --target dev

dbt-build-prod: ## Run dbt build for production (MotherDuck)
	cd dbt && dbt build --target prod

dashboard: ## Start Streamlit dashboard locally
	streamlit run dashboard/streamlit_app.py

test: ## Run Python tests
	pytest tests/ -v

lint: ## Lint Python code with ruff
	ruff check .

format: ## Format Python code with black and ruff
	black pipelines/ tests/ dashboard/
	ruff check --fix .

clean: ## Clean up generated files
	rm -rf github_ai_trends.duckdb
	rm -rf dbt/target/
	rm -rf dbt/dbt_packages/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Cloud deployment helpers
deploy-setup: ## Setup guide for cloud deployment
	@echo "See DEPLOYMENT.md for cloud deployment instructions"
