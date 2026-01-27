# ==============================================================================
# AUTO-blogger Makefile
# Professional WordPress Automation Tool
# Copyright (c) 2025 AryanVBW
# ==============================================================================

.PHONY: all install dev-install test-install clean run test lint format \
        type-check build upload upload-test docs help setup dev-setup \
        pre-commit check verify

# Configuration
PYTHON := python3
PIP := pip
VENV_DIR := venv
PACKAGE_NAME := auto_blogger
PROJECT_NAME := auto-blogger

# Detect OS
ifeq ($(OS),Windows_NT)
    ACTIVATE := $(VENV_DIR)/Scripts/activate
    PYTHON_VENV := $(VENV_DIR)/Scripts/python
    RM := rmdir /s /q
    MKDIR := mkdir
else
    ACTIVATE := $(VENV_DIR)/bin/activate
    PYTHON_VENV := $(VENV_DIR)/bin/python
    RM := rm -rf
    MKDIR := mkdir -p
endif

# Default target
all: help

# ==============================================================================
# Installation
# ==============================================================================

## install: Install the package with base dependencies
install:
	@echo "Installing $(PROJECT_NAME)..."
	$(PIP) install -e .
	@echo "Done!"

## dev-install: Install with development dependencies
dev-install:
	@echo "Installing $(PROJECT_NAME) with dev dependencies..."
	$(PIP) install -e ".[dev]"
	@echo "Done!"

## test-install: Install with test dependencies
test-install:
	@echo "Installing $(PROJECT_NAME) with test dependencies..."
	$(PIP) install -r requirements/test.txt
	$(PIP) install -e .
	@echo "Done!"

## deps: Install base dependencies only
deps:
	@echo "Installing base dependencies..."
	$(PIP) install -r requirements/base.txt
	@echo "Done!"

## dev-deps: Install development dependencies
dev-deps:
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements/dev.txt
	@echo "Done!"

## test-deps: Install test dependencies
test-deps:
	@echo "Installing test dependencies..."
	$(PIP) install -r requirements/test.txt
	@echo "Done!"

## upgrade-deps: Upgrade all dependencies
upgrade-deps:
	@echo "Upgrading dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements/base.txt
	@echo "Done!"

# ==============================================================================
# Setup
# ==============================================================================

## setup: Full setup (venv + install)
setup:
	@echo "Running full setup..."
	./setup.sh
	@echo "Done!"

## dev-setup: Full development setup
dev-setup:
	@echo "Running development setup..."
	./setup.sh --dev
	@echo "Done!"

## venv: Create virtual environment
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Activate with: source $(ACTIVATE)"

## clean-venv: Remove virtual environment
clean-venv:
	@echo "Removing virtual environment..."
	$(RM) $(VENV_DIR) 2>/dev/null || true
	@echo "Done!"

# ==============================================================================
# Running
# ==============================================================================

## run: Run the application
run:
	@echo "Starting AUTO-blogger..."
	$(PYTHON) -m $(PACKAGE_NAME)

## run-gui: Run the GUI application
run-gui:
	@echo "Starting AUTO-blogger GUI..."
	$(PYTHON) -m $(PACKAGE_NAME).gui_blogger

## run-cli: Run in CLI mode (if available)
run-cli:
	autoblog

# ==============================================================================
# Testing
# ==============================================================================

## test: Run all tests
test:
	@echo "Running tests..."
	pytest tests/ -v

## test-cov: Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=$(PACKAGE_NAME) --cov-report=html --cov-report=term

## test-fast: Run tests without slow tests
test-fast:
	@echo "Running fast tests..."
	pytest tests/ -v -m "not slow"

## test-unit: Run unit tests only
test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

## test-integration: Run integration tests only
test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v

# ==============================================================================
# Code Quality
# ==============================================================================

## lint: Run all linters
lint: flake8 pylint

## flake8: Run flake8 linter
flake8:
	@echo "Running flake8..."
	flake8 $(PACKAGE_NAME)/ --max-line-length=100 --ignore=E501,W503

## pylint: Run pylint
pylint:
	@echo "Running pylint..."
	pylint $(PACKAGE_NAME)/ --disable=C0114,C0115,C0116 || true

## format: Format code with black and isort
format:
	@echo "Formatting code..."
	black $(PACKAGE_NAME)/ tests/
	isort $(PACKAGE_NAME)/ tests/
	@echo "Done!"

## format-check: Check code formatting
format-check:
	@echo "Checking code format..."
	black --check $(PACKAGE_NAME)/ tests/
	isort --check-only $(PACKAGE_NAME)/ tests/

## type-check: Run type checking with mypy
type-check:
	@echo "Running type check..."
	mypy $(PACKAGE_NAME)/ --ignore-missing-imports

## check: Run all checks (lint, format-check, type-check)
check: lint format-check type-check
	@echo "All checks passed!"

## pre-commit: Run pre-commit hooks
pre-commit:
	@echo "Running pre-commit..."
	pre-commit run --all-files

## pre-commit-install: Install pre-commit hooks
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Done!"

# ==============================================================================
# Building & Publishing
# ==============================================================================

## build: Build distribution packages
build: clean-build
	@echo "Building distribution packages..."
	$(PYTHON) -m build
	@echo "Done!"

## upload: Upload to PyPI
upload: build
	@echo "Uploading to PyPI..."
	twine upload dist/*
	@echo "Done!"

## upload-test: Upload to TestPyPI
upload-test: build
	@echo "Uploading to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "Done!"

## verify-build: Verify the built package
verify-build:
	@echo "Verifying build..."
	twine check dist/*
	@echo "Done!"

# ==============================================================================
# Documentation
# ==============================================================================

## docs: Build documentation
docs:
	@echo "Building documentation..."
	cd docs && make html
	@echo "Done! Open docs/_build/html/index.html"

## docs-serve: Serve documentation locally
docs-serve:
	@echo "Serving documentation..."
	$(PYTHON) -m http.server --directory docs/_build/html 8080

# ==============================================================================
# Cleanup
# ==============================================================================

## clean: Clean all build artifacts
clean: clean-build clean-pyc clean-test

## clean-build: Clean build artifacts
clean-build:
	@echo "Cleaning build artifacts..."
	$(RM) build/ 2>/dev/null || true
	$(RM) dist/ 2>/dev/null || true
	$(RM) *.egg-info 2>/dev/null || true
	$(RM) $(PACKAGE_NAME).egg-info 2>/dev/null || true
	find . -name '*.egg' -delete 2>/dev/null || true
	@echo "Done!"

## clean-pyc: Clean Python cache files
clean-pyc:
	@echo "Cleaning Python cache..."
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	find . -type f -name '*~' -delete 2>/dev/null || true
	@echo "Done!"

## clean-test: Clean test artifacts
clean-test:
	@echo "Cleaning test artifacts..."
	$(RM) .pytest_cache 2>/dev/null || true
	$(RM) .coverage 2>/dev/null || true
	$(RM) htmlcov 2>/dev/null || true
	$(RM) .mypy_cache 2>/dev/null || true
	@echo "Done!"

## clean-all: Clean everything including venv
clean-all: clean clean-venv
	@echo "All cleaned!"

# ==============================================================================
# Verification
# ==============================================================================

## verify: Verify installation and imports
verify:
	@echo "Verifying installation..."
	$(PYTHON) -c "import $(PACKAGE_NAME); print('Package version:', $(PACKAGE_NAME).__version__)"
	$(PYTHON) -c "from $(PACKAGE_NAME) import automation_engine; print('automation_engine: OK')"
	$(PYTHON) -c "from $(PACKAGE_NAME) import gui_blogger; print('gui_blogger: OK')"
	@echo "Verification complete!"

## version: Show package version
version:
	@$(PYTHON) -c "import $(PACKAGE_NAME); print($(PACKAGE_NAME).__version__)"

## info: Show project information
info:
	@echo "Project: $(PROJECT_NAME)"
	@echo "Package: $(PACKAGE_NAME)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"

# ==============================================================================
# Help
# ==============================================================================

## help: Show this help message
help:
	@echo ""
	@echo "AUTO-blogger Makefile"
	@echo "====================="
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Installation:"
	@grep -E '^## (install|dev-install|test-install|deps|dev-deps|test-deps|upgrade-deps):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Setup:"
	@grep -E '^## (setup|dev-setup|venv|clean-venv):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Running:"
	@grep -E '^## (run|run-gui|run-cli):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Testing:"
	@grep -E '^## (test|test-cov|test-fast|test-unit|test-integration):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Code Quality:"
	@grep -E '^## (lint|flake8|pylint|format|format-check|type-check|check|pre-commit):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Building:"
	@grep -E '^## (build|upload|upload-test|verify-build):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Cleanup:"
	@grep -E '^## (clean|clean-build|clean-pyc|clean-test|clean-all):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
	@echo "Other:"
	@grep -E '^## (verify|version|info|help|docs):' Makefile | sed 's/## /  /' | sed 's/: /\t/'
	@echo ""
