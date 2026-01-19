# Makefile for sphinx-typesense
# Python library project using uv as package manager

.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

# Project settings
PROJECT_NAME := sphinx-typesense
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)$(PROJECT_NAME)$(RESET) - Development Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "$(YELLOW)Usage:$(RESET)\n  make $(GREEN)<target>$(RESET)\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Installation

.PHONY: install
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	uv sync --no-dev

.PHONY: dev
dev: ## Install all development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	uv sync --group dev

.PHONY: dev-all
dev-all: ## Install all dependency groups explicitly
	@echo "$(BLUE)Installing all dependency groups...$(RESET)"
	uv sync --group docs --group lint --group test --group dev

##@ Code Quality

.PHONY: lint
lint: ## Run ruff check and mypy
	@echo "$(BLUE)Running linters...$(RESET)"
	uv run ruff check $(SRC_DIR) $(TESTS_DIR) && \
	uv run mypy $(SRC_DIR)

.PHONY: lint-fix
lint-fix: ## Run ruff check with auto-fix
	@echo "$(BLUE)Running ruff check with auto-fix...$(RESET)"
	uv run ruff check --fix $(SRC_DIR) $(TESTS_DIR)

.PHONY: fmt
fmt: ## Run ruff format and ruff check --fix
	@echo "$(BLUE)Formatting code...$(RESET)"
	uv run ruff format $(SRC_DIR) $(TESTS_DIR) && \
	uv run ruff check --fix $(SRC_DIR) $(TESTS_DIR)

.PHONY: fmt-check
fmt-check: ## Check formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	uv run ruff format --check $(SRC_DIR) $(TESTS_DIR)

.PHONY: typecheck
typecheck: ## Run mypy type checking
	@echo "$(BLUE)Running type checker...$(RESET)"
	uv run mypy $(SRC_DIR)

##@ Testing

.PHONY: test
test: ## Run pytest with coverage
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	uv run pytest $(TESTS_DIR) --cov=$(SRC_DIR)/sphinx_typesense --cov-report=term-missing --cov-report=html

.PHONY: test-smoke
test-smoke: ## Quick smoke test (not full suite)
	@echo "$(BLUE)Running smoke tests...$(RESET)"
	uv run pytest $(TESTS_DIR) -x -q --no-cov -m "not slow and not integration"

.PHONY: test-fast
test-fast: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running tests (no coverage)...$(RESET)"
	uv run pytest $(TESTS_DIR) --no-cov

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(RESET)"
	uv run pytest $(TESTS_DIR) -v --cov=$(SRC_DIR)/sphinx_typesense --cov-report=term-missing

.PHONY: test-parallel
test-parallel: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(RESET)"
	uv run pytest $(TESTS_DIR) -n auto --cov=$(SRC_DIR)/sphinx_typesense --cov-report=term-missing

##@ Local Infrastructure

.PHONY: infra-up
infra-up: ## Start local Typesense for development
	@echo "$(BLUE)Starting local Typesense...$(RESET)"
	docker compose up -d
	@echo "$(YELLOW)Waiting for Typesense to be healthy...$(RESET)"
	@timeout 60 sh -c 'until curl -sf http://127.0.0.1:8108/health > /dev/null 2>&1; do sleep 1; done' || \
		(echo "$(RED)Typesense failed to start$(RESET)" && exit 1)
	@echo "$(GREEN)Typesense is ready at http://127.0.0.1:8108$(RESET)"
	@echo "$(YELLOW)API Key: local_dev_key$(RESET)"

.PHONY: infra-down
infra-down: ## Stop local Typesense
	@echo "$(BLUE)Stopping local Typesense...$(RESET)"
	docker compose down
	@echo "$(GREEN)Typesense stopped$(RESET)"

.PHONY: infra-clean
infra-clean: ## Stop Typesense and remove data volumes
	@echo "$(BLUE)Stopping Typesense and removing volumes...$(RESET)"
	docker compose down -v
	@echo "$(GREEN)Typesense stopped and data removed$(RESET)"

.PHONY: infra-logs
infra-logs: ## View Typesense logs
	docker compose logs -f typesense

##@ Integration Testing

.PHONY: typesense-up
typesense-up: infra-up ## Alias for infra-up (backward compat)

.PHONY: typesense-down
typesense-down: infra-down ## Alias for infra-down (backward compat)

.PHONY: typesense-clean
typesense-clean: infra-clean ## Alias for infra-clean (backward compat)

.PHONY: test-integration
test-integration: infra-up ## Run integration tests (starts Typesense first)
	@echo "$(BLUE)Running integration tests...$(RESET)"
	uv run pytest $(TESTS_DIR) -m "integration" -v --no-cov || (make infra-down && exit 1)
	@make infra-down

##@ Documentation

.PHONY: docs
docs: ## Build documentation with Sphinx
	@echo "$(BLUE)Building documentation...$(RESET)"
	uv run sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html

.PHONY: docs-serve
docs-serve: ## Serve docs with sphinx-autobuild
	@echo "$(BLUE)Starting documentation server...$(RESET)"
	uv run sphinx-autobuild $(DOCS_DIR) $(DOCS_DIR)/_build/html --open-browser --port 0 --watch $(SRC_DIR)

.PHONY: docs-clean
docs-clean: ## Clean documentation build artifacts
	@echo "$(BLUE)Cleaning documentation build...$(RESET)"
	rm -rf $(DOCS_DIR)/_build

.PHONY: showcase
showcase: ## Build all theme examples and serve showcase with theme switcher
	@echo "$(BLUE)Building and serving theme showcase...$(RESET)"
	$(MAKE) -C examples showcase

##@ Build & Release

.PHONY: build
build: clean-build ## Build wheel and sdist with uv
	@echo "$(BLUE)Building package...$(RESET)"
	uv build

.PHONY: build-check
build-check: build ## Build and check package with twine
	@echo "$(BLUE)Checking built package...$(RESET)"
	uv run twine check dist/*

##@ Cleanup

.PHONY: clean
clean: clean-build clean-pyc clean-test clean-cache ## Remove all build artifacts
	@echo "$(GREEN)All clean!$(RESET)"

.PHONY: clean-build
clean-build: ## Remove build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf $(SRC_DIR)/*.egg-info

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	@echo "$(BLUE)Cleaning Python artifacts...$(RESET)"
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-test
clean-test: ## Remove test and coverage artifacts
	@echo "$(BLUE)Cleaning test artifacts...$(RESET)"
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf coverage.xml

.PHONY: clean-cache
clean-cache: ## Remove cache directories
	@echo "$(BLUE)Cleaning cache directories...$(RESET)"
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

##@ CI/CD

.PHONY: check
check: lint test ## Run all checks (lint + test)
	@echo "$(GREEN)All checks passed!$(RESET)"

.PHONY: ci
ci: fmt-check lint test ## Full CI pipeline (fmt check, lint, test)
	@echo "$(GREEN)CI pipeline passed!$(RESET)"

.PHONY: pre-commit
pre-commit: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	@if command -v prek >/dev/null 2>&1; then \
		prek run --all-files; \
	else \
		uv run pre-commit run --all-files; \
	fi

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	uv run pre-commit install

##@ Development Workflow

.PHONY: setup
setup: dev pre-commit-install ## Complete development setup
	@echo "$(GREEN)Development environment ready!$(RESET)"

.PHONY: refresh
refresh: clean dev ## Clean and reinstall dependencies
	@echo "$(GREEN)Environment refreshed!$(RESET)"

.PHONY: all
all: fmt lint test docs build ## Run all targets (fmt, lint, test, docs, build)
	@echo "$(GREEN)All tasks completed!$(RESET)"
