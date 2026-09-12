.PHONY: help check check-env check-local plan-local apply-local check-local-bootstrap plan-local-bootstrap apply-local-bootstrap authoritative-source-check scanner-test v2-check v2-setup

.DEFAULT_GOAL := check

V2_PYTHON := .venv/bin/python

help: ## List available repo-local Makefile targets with short descriptions.
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-28s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: ## Run canonical local validation for local work and CI.
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		echo "Running markdownlint-cli2"; \
		markdownlint-cli2 "**/*.md" "!.worktrees/**" "!.venv/**"; \
	elif command -v markdownlint >/dev/null 2>&1; then \
		echo "Running markdownlint"; \
		markdownlint --ignore ".worktrees" --ignore ".venv" "**/*.md"; \
	else \
		echo "markdownlint is not installed."; \
		echo "Install markdownlint-cli2 or markdownlint, then rerun 'make check'."; \
		exit 1; \
	fi
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
	$(MAKE) v2-check

v2-setup: ## Explicitly install the pinned experimental v2 test dependencies.
	python3 -m venv .venv
	$(V2_PYTHON) -m pip install --no-cache-dir -r v2_retain/requirements.txt

v2-check: ## Run experimental v2 local/fake acceptance; never contacts Dropbox.
	@test -x $(V2_PYTHON) || (echo "Run make v2-setup first."; exit 1)
	PYTHONDONTWRITEBYTECODE=1 $(V2_PYTHON) -m unittest discover -s v2_retain/tests

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

check-local-bootstrap: ## Compare local global routers with canonical projections.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_global_bootstrap.py

check-local: ## Check every qualified Playbook-managed local projection.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_projections.py --mode check

plan-local: ## Show read-only component-owned local reconciliation plans.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_projections.py --mode plan

apply-local: ## Explicitly apply safe component-owned local reconciliation.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_projections.py --mode apply

plan-local-bootstrap: ## Show the read-only exact managed-block reconciliation plan.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_global_bootstrap.py --mode plan

apply-local-bootstrap: ## Explicitly apply and verify safe managed-block reconciliation.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_global_bootstrap.py --mode apply

authoritative-source-check: ## Run advisory authoritative-source scanning.
	python3 scripts/check_authoritative_sources.py --base-ref origin/main --head-ref HEAD

scanner-test: ## Run scanner unit tests.
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
