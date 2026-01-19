# Makefile for sphinx-typesense examples
# Build and serve documentation for each supported theme

.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

# Directory settings
DOCS_DIR := docs
SOURCE_DIR := $(DOCS_DIR)/source

# Theme list
THEMES := rtd furo alabaster pydata shibuya

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)sphinx-typesense examples$(RESET) - Theme Documentation Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "$(YELLOW)Usage:$(RESET)\n  make $(GREEN)<target>$(RESET)\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Build Documentation

.PHONY: docs-rtd
docs-rtd: ## Build RTD theme docs
	@echo "$(BLUE)Building RTD theme documentation...$(RESET)"
	uv run sphinx-build -b html -c $(DOCS_DIR)/docs-rtd $(SOURCE_DIR) $(DOCS_DIR)/docs-rtd/_build/html
	@echo "$(GREEN)RTD docs built at $(DOCS_DIR)/docs-rtd/_build/html$(RESET)"

.PHONY: docs-furo
docs-furo: ## Build Furo theme docs
	@echo "$(BLUE)Building Furo theme documentation...$(RESET)"
	uv run sphinx-build -b html -c $(DOCS_DIR)/docs-furo $(SOURCE_DIR) $(DOCS_DIR)/docs-furo/_build/html
	@echo "$(GREEN)Furo docs built at $(DOCS_DIR)/docs-furo/_build/html$(RESET)"

.PHONY: docs-alabaster
docs-alabaster: ## Build Alabaster theme docs
	@echo "$(BLUE)Building Alabaster theme documentation...$(RESET)"
	uv run sphinx-build -b html -c $(DOCS_DIR)/docs-alabaster $(SOURCE_DIR) $(DOCS_DIR)/docs-alabaster/_build/html
	@echo "$(GREEN)Alabaster docs built at $(DOCS_DIR)/docs-alabaster/_build/html$(RESET)"

.PHONY: docs-pydata
docs-pydata: ## Build PyData theme docs
	@echo "$(BLUE)Building PyData theme documentation...$(RESET)"
	uv run sphinx-build -b html -c $(DOCS_DIR)/docs-pydata $(SOURCE_DIR) $(DOCS_DIR)/docs-pydata/_build/html
	@echo "$(GREEN)PyData docs built at $(DOCS_DIR)/docs-pydata/_build/html$(RESET)"

.PHONY: docs-shibuya
docs-shibuya: ## Build Shibuya theme docs
	@echo "$(BLUE)Building Shibuya theme documentation...$(RESET)"
	uv run sphinx-build -b html -c $(DOCS_DIR)/docs-shibuya $(SOURCE_DIR) $(DOCS_DIR)/docs-shibuya/_build/html
	@echo "$(GREEN)Shibuya docs built at $(DOCS_DIR)/docs-shibuya/_build/html$(RESET)"

.PHONY: docs-all
docs-all: docs-rtd docs-furo docs-alabaster docs-pydata docs-shibuya ## Build all theme docs
	@echo "$(GREEN)All theme documentation built!$(RESET)"

##@ Serve Documentation

.PHONY: serve-rtd
serve-rtd: ## Serve RTD docs with sphinx-autobuild
	@echo "$(BLUE)Starting RTD theme documentation server...$(RESET)"
	uv run sphinx-autobuild -b html -c $(DOCS_DIR)/docs-rtd $(SOURCE_DIR) $(DOCS_DIR)/docs-rtd/_build/html --port 0 --open-browser

.PHONY: serve-furo
serve-furo: ## Serve Furo docs with sphinx-autobuild
	@echo "$(BLUE)Starting Furo theme documentation server...$(RESET)"
	uv run sphinx-autobuild -b html -c $(DOCS_DIR)/docs-furo $(SOURCE_DIR) $(DOCS_DIR)/docs-furo/_build/html --port 0 --open-browser

.PHONY: serve-alabaster
serve-alabaster: ## Serve Alabaster docs with sphinx-autobuild
	@echo "$(BLUE)Starting Alabaster theme documentation server...$(RESET)"
	uv run sphinx-autobuild -b html -c $(DOCS_DIR)/docs-alabaster $(SOURCE_DIR) $(DOCS_DIR)/docs-alabaster/_build/html --port 0 --open-browser

.PHONY: serve-pydata
serve-pydata: ## Serve PyData docs with sphinx-autobuild
	@echo "$(BLUE)Starting PyData theme documentation server...$(RESET)"
	uv run sphinx-autobuild -b html -c $(DOCS_DIR)/docs-pydata $(SOURCE_DIR) $(DOCS_DIR)/docs-pydata/_build/html --port 0 --open-browser

.PHONY: serve-shibuya
serve-shibuya: ## Serve Shibuya docs with sphinx-autobuild
	@echo "$(BLUE)Starting Shibuya theme documentation server...$(RESET)"
	uv run sphinx-autobuild -b html -c $(DOCS_DIR)/docs-shibuya $(SOURCE_DIR) $(DOCS_DIR)/docs-shibuya/_build/html --port 0 --open-browser

##@ Cleanup

.PHONY: clean
clean: ## Clean all build artifacts
	@echo "$(BLUE)Cleaning all documentation build artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/docs-rtd/_build
	rm -rf $(DOCS_DIR)/docs-furo/_build
	rm -rf $(DOCS_DIR)/docs-alabaster/_build
	rm -rf $(DOCS_DIR)/docs-pydata/_build
	rm -rf $(DOCS_DIR)/docs-shibuya/_build
	@echo "$(GREEN)All build artifacts cleaned!$(RESET)"

.PHONY: clean-rtd
clean-rtd: ## Clean RTD build artifacts
	@echo "$(BLUE)Cleaning RTD build artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/docs-rtd/_build

.PHONY: clean-furo
clean-furo: ## Clean Furo build artifacts
	@echo "$(BLUE)Cleaning Furo build artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/docs-furo/_build

.PHONY: clean-alabaster
clean-alabaster: ## Clean Alabaster build artifacts
	@echo "$(BLUE)Cleaning Alabaster build artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/docs-alabaster/_build

.PHONY: clean-pydata
clean-pydata: ## Clean PyData build artifacts
	@echo "$(BLUE)Cleaning PyData build artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/docs-pydata/_build

.PHONY: clean-shibuya
clean-shibuya: ## Clean Shibuya build artifacts
	@echo "$(BLUE)Cleaning Shibuya build artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/docs-shibuya/_build

##@ Theme Showcase

.PHONY: showcase
showcase: docs-all serve-showcase ## Build all themes and serve showcase with theme switcher

.PHONY: serve-showcase
serve-showcase: ## Serve showcase (assumes themes already built)
	@echo "$(GREEN)Starting showcase server...$(RESET)"
	@echo ""
	@echo "$(YELLOW)Theme Showcase Controls:$(RESET)"
	@echo "  - Click theme buttons to switch between themes"
	@echo "  - Press $(GREEN)1-5$(RESET) keys to quickly switch themes"
	@echo "  - Press $(GREEN)Ctrl+K$(RESET) in any theme to test search"
	@echo ""
	@cd $(DOCS_DIR) && uv run python -c "\
import http.server, socketserver, webbrowser, threading; \
PORT = 0; \
handler = http.server.SimpleHTTPRequestHandler; \
httpd = socketserver.TCPServer(('127.0.0.1', PORT), handler); \
port = httpd.server_address[1]; \
print(f'\033[0;32mShowcase running at: http://127.0.0.1:{port}/showcase.html\033[0m'); \
threading.Timer(0.5, lambda: webbrowser.open(f'http://127.0.0.1:{port}/showcase.html')).start(); \
httpd.serve_forever()"
