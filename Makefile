# Eddi Development Makefile

.PHONY: help install test lint format docs docs-serve clean

help:
	@echo "Available commands:"
	@echo "  install     Install development dependencies"
	@echo "  test        Run tests with coverage"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and ruff"
	@echo "  docs        Build documentation"
	@echo "  docs-serve  Build and serve documentation locally"
	@echo "  clean       Clean build artifacts"

install:
	uv sync --dev --extra docs

test:
	uv run pytest -v --cov=src --cov-report=xml --cov-report=term-missing

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff check --fix .
	uv run ruff format .
	uv run black .

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