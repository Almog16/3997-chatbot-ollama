# DEVELOPMENT & OPERATIONS
all:
	lint

help:
	@echo "Available targets:"
	@echo "  install    : Sets up environment (uv sync) and installs pre-commit hooks."
	@echo "  run        : Runs the FastAPI server using uvicorn with hot-reload."
	@echo "  lint       : Checks source code quality with Ruff (no fixes applied)."
	@echo "  format     : Checks and automatically fixes code with Ruff."
	@echo "  clean      : Removes the virtual environment and built files."

install:
	@echo "👉 Initializing project with uv…"
	# Syncs all dependencies defined in pyproject.toml
	uv sync --all-groups

run:
	@echo "--- Starting Uvicorn server (https://www.google.com/search?q=http://127.0.0.1:8000) ---"
	uvicorn src.server:app --reload

test:
	@echo "--- Running backend tests with coverage ---"
	uv run pytest

# REACT FRONTEND
install-client:
	@echo "👉 Installing React frontend dependencies (npm install)…"
	npm --prefix client install

run-client:
	@echo "--- Starting React development server ---…"
	npm --prefix client run dev

test-client:
	@echo "--- Running Playwright E2E suite ---"
	npm --prefix client run test:e2e

# CODE QUALITY & LINTING
lint:
	@echo "--- Running Ruff checks (Linting) ---"
	ruff check src/

format:
	@echo "--- Running Ruff checks and fixes (Formatting) ---"
	ruff check src/ --fix

clean:
	@echo "--- Cleaning up environment ---"
	rm -rf $(VENV_DIR)
	find . -name 'pycache' -exec rm -rf {} +
	find . -name '*.pyc' -delete
