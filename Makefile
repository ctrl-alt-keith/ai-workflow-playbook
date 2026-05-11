.PHONY: help check check-env authoritative-source-check scanner-test dist-check workspace-bootstrap context-refresh github-context dist

.DEFAULT_GOAL := check

WORKSPACE_REPOS_MANIFEST := config/workspace-repos.txt

help: ## List available repo-local Makefile targets with short descriptions.
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-28s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: ## Run canonical local validation for local work and CI.
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		echo "Running markdownlint-cli2"; \
		markdownlint-cli2 "**/*.md" "#dist"; \
	elif command -v markdownlint >/dev/null 2>&1; then \
		echo "Running markdownlint"; \
		markdownlint --ignore dist "**/*.md"; \
	else \
		echo "markdownlint is not installed."; \
		echo "Install markdownlint-cli2 or markdownlint, then rerun 'make check'."; \
		exit 1; \
	fi
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_dist_artifacts.py --repo-manifest $(WORKSPACE_REPOS_MANIFEST)

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

dist-check: ## Check existing generated distribution context artifacts for drift.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_dist_artifacts.py --repo-manifest $(WORKSPACE_REPOS_MANIFEST)

workspace-bootstrap: ## Generate fresh-thread and project-source bootstrap context.
	python3 scripts/generate_workspace_bootstrap.py --output dist/workspace-bootstrap.md

context-refresh: ## Generate repository orientation brief for fresh-thread handoff.
	python3 scripts/generate_context_refresh.py --repo-manifest $(WORKSPACE_REPOS_MANIFEST) --output dist/context-refresh.md

github-context: ## Generate GitHub connector repo hydration snippet.
	python3 scripts/generate_github_context.py --repo-manifest $(WORKSPACE_REPOS_MANIFEST) --output dist/github-context.md

dist: workspace-bootstrap context-refresh github-context ## Generate all distribution context artifacts.
