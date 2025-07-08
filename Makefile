# Eddi Development Makefile

.PHONY: help install test test-watch lint format lint-check docs docs-serve clean setup push workflow-status watch-workflows status

help:
	@echo "eddi Makefile targets:"
	@echo "  install         Install development dependencies"
	@echo "  test            Run tests with coverage"
	@echo "  test-watch      Run tests in watch mode"
	@echo "  lint            Run linting checks (mypy + ruff)"
	@echo "  format          Format code with ruff"
	@echo "  lint-check      Same as lint (compatibility)"
	@echo "  push            Push changes with workflow monitoring"
	@echo "  workflow-status Check CI workflow status"
	@echo "  watch-workflows Watch active workflows"
	@echo "  status          Show git status"
	@echo "  setup           Setup development environment"
	@echo "  docs            Build documentation"
	@echo "  docs-serve      Build and serve documentation locally"
	@echo "  clean           Clean build artifacts"

install:
	uv sync --dev --extra docs

setup: install
	@echo "✅ Development environment setup complete"

test:
	uv run pytest -v --cov=src --cov-report=xml --cov-report=term-missing

test-watch:
	@echo "Running tests in watch mode..."
	uv run pytest-watch

lint:
	uv run mypy .
	uv run ruff check .

lint-check: lint

format:
	uv run ruff check --fix .
	uv run ruff format .

docs:
	uv run sphinx-build docs/source docs/build/html

docs-serve: docs
	@echo "Documentation built successfully!"
	@echo "Opening in browser..."
	@python -c "import webbrowser; webbrowser.open('file://$(PWD)/docs/build/html/index.html')"

clean:
	rm -rf docs/build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Git operations with CI monitoring
push:
	@echo "Pushing changes with workflow monitoring..."
	@git push && gh run list || echo "No workflows found or gh not available"

workflow-status:
	@echo "Checking workflow status..."
	@gh run list --limit 5 || echo "No workflows found or gh not available"

watch-workflows:
	@echo "Watching workflows..."
	@gh run watch || echo "No active workflows or gh not available"

status:
	@echo "Git status:"
	@git status