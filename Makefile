.PHONY: help check check-env authoritative-source-check scanner-test

.DEFAULT_GOAL := check

help: ## List available repo-local Makefile targets with short descriptions.
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-28s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: ## Run canonical local validation for local work and CI.
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		echo "Running markdownlint-cli2"; \
		markdownlint-cli2 "**/*.md"; \
	elif command -v markdownlint >/dev/null 2>&1; then \
		echo "Running markdownlint"; \
		markdownlint "**/*.md"; \
	else \
		echo "markdownlint is not installed."; \
		echo "Install markdownlint-cli2 or markdownlint, then rerun 'make check'."; \
		exit 1; \
	fi
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

check-env: ## Verify local tools needed by make check are available.
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		echo "Found markdownlint-cli2"; \
	elif command -v markdownlint >/dev/null 2>&1; then \
		echo "Found markdownlint"; \
	else \
		echo "markdownlint is not installed."; \
		echo "Install markdownlint-cli2 or markdownlint to enable local validation."; \
		exit 1; \
	fi

authoritative-source-check: ## Run advisory authoritative-source scanning.
	python3 scripts/check_authoritative_sources.py --base-ref origin/main --head-ref HEAD

scanner-test: ## Run scanner unit tests.
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
