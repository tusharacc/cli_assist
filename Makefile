# Lumos CLI Makefile
# Provides convenient commands for testing and development

.PHONY: help test test-quick test-all test-feature test-smoke test-unit test-integration clean install

# Default target
help:
	@echo "🌟 Lumos CLI - Available Commands"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test-quick      - Run quick functionality test"
	@echo "  make test-smoke      - Run smoke test (basic functionality)"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-all        - Run comprehensive test suite"
	@echo "  make test-feature    - Test specific feature (usage: make test-feature FEATURE=github)"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install         - Install Lumos CLI in development mode"
	@echo "  make clean           - Clean up temporary files"
	@echo "  make lint            - Run linting checks"
	@echo ""
	@echo "CLI Commands:"
	@echo "  make cli-help        - Show CLI help"
	@echo "  make cli-test        - Test CLI basic functionality"

# Quick test - fastest way to verify functionality
test-quick:
	@echo "🚀 Running quick functionality test..."
	python test_lumos.py --quick

# Smoke test - basic functionality check
test-smoke:
	@echo "🔥 Running smoke test..."
	python tests/test_runner.py --smoke

# Unit tests only
test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v

# Integration tests
test-integration:
	@echo "🔗 Running integration tests..."
	python -m pytest tests/integration/ -v

# All tests
test-all:
	@echo "🚀 Running comprehensive test suite..."
	python test_lumos.py --all

# Test specific feature
test-feature:
	@echo "🎯 Testing $(FEATURE) feature..."
	python test_lumos.py --feature $(FEATURE)

# Default test command
test: test-quick

# Install in development mode
install:
	@echo "📦 Installing Lumos CLI in development mode..."
	pip install -e .

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	python -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	python -m black --check src/ tests/

# Format code
format:
	@echo "🎨 Formatting code..."
	python -m black src/ tests/

# CLI help
cli-help:
	@echo "📖 Showing CLI help..."
	lumos-cli --help

# Test CLI basic functionality
cli-test:
	@echo "🧪 Testing CLI basic functionality..."
	lumos-cli --help > /dev/null && echo "✅ CLI help works" || echo "❌ CLI help failed"
	python -c "from src.lumos_cli.cli_refactored_v2 import main; print('✅ CLI imports work')" || echo "❌ CLI import failed"

# Show test categories
test-list:
	@echo "📋 Available test categories:"
	python test_lumos.py --list

# Development setup
dev-setup: install
	@echo "🛠️ Setting up development environment..."
	pip install pytest pytest-cov black flake8
	@echo "✅ Development environment ready!"

# Run tests with coverage
test-coverage:
	@echo "📊 Running tests with coverage..."
	python -m pytest tests/ --cov=src/lumos_cli --cov-report=html --cov-report=term

# Show project status
status:
	@echo "📊 Lumos CLI Project Status"
	@echo "=========================="
	@echo "Source files: $(shell find src/ -name '*.py' | wc -l)"
	@echo "Test files: $(shell find tests/ -name '*.py' | wc -l)"
	@echo "Documentation files: $(shell find docs/ -name '*.md' | wc -l)"
	@echo "Demo files: $(shell find demos/ -name '*.py' | wc -l)"
	@echo "Script files: $(shell find scripts/ -name '*.py' | wc -l)"
	@echo ""
	@echo "CLI Status:"
	@make cli-test
