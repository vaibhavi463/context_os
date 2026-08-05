.PHONY: help dev build test lint format seed clean

help:
	@echo "ContextOS Makefile Commands:"
	@echo "  make dev      - Start Docker Compose dev environment"
	@echo "  make build    - Build all Docker images"
	@echo "  make test     - Run pytest test suite"
	@echo "  make lint     - Run ruff linter & mypy type checker"
	@echo "  make format   - Run ruff code formatter"
	@echo "  make seed     - Seed local database with demo data"
	@echo "  make eval     - Run AI Evaluation Benchmark Suite"
	@echo "  make clean    - Stop containers and cleanup temporary files"

dev:
	docker compose up -d

build:
	docker compose build

test:
	pytest tests/ --cov=backend/app --cov-report=term-missing

lint:
	ruff check backend/ app/ evals/
	mypy backend/app

format:
	ruff format backend/ app/ evals/

seed:
	python scripts/seed_demo_data.py

eval:
	python evals/run_evals.py

clean:
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
