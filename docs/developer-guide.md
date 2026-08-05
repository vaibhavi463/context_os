# ContextOS Developer Guide

## Development Environment Setup
1. Clone repository and install dependencies using `uv` or `pip`:
   ```bash
   pip install -e .[dev]
   ```
2. Start local Postgres and Redis containers:
   ```bash
   make dev
   ```
3. Run tests and linter:
   ```bash
   make lint
   make test
   ```
4. Run AI Evaluation Benchmark:
   ```bash
   make eval
   ```
