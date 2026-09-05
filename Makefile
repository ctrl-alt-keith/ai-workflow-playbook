.PHONY: help check check-env check-local-bootstrap authoritative-source-check scanner-test

.DEFAULT_GOAL := check

help: ## List available repo-local Makefile targets with short descriptions.
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-28s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: code-first-recovery-check ## Run canonical local validation for local work and CI.
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		echo "Running markdownlint-cli2"; \
		markdownlint-cli2 "**/*.md" "!.worktrees/**" "!experiments/code-first-playbook/.build/**" "!experiments/code-first-playbook/.venv/**"; \
	elif command -v markdownlint >/dev/null 2>&1; then \
		echo "Running markdownlint"; \
		markdownlint --ignore ".worktrees" --ignore "experiments/code-first-playbook/.build" --ignore "experiments/code-first-playbook/.venv" "**/*.md"; \
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

check-local-bootstrap: ## Compare local global routers with canonical projections.
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_global_bootstrap.py

authoritative-source-check: ## Run advisory authoritative-source scanning.
	python3 scripts/check_authoritative_sources.py --base-ref origin/main --head-ref HEAD

scanner-test: ## Run scanner unit tests.
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

CFP := experiments/code-first-playbook
CFP_PY := $(CFP)/.venv/bin/python
.PHONY: code-first-setup code-first-tools

code-first-setup: ## Set up the isolated Recovery semantic tooling.
	python3 -m venv $(CFP)/.venv
	$(CFP_PY) -m pip install --disable-pip-version-check -r $(CFP)/requirements.txt

code-first-tools: ## Report missing Recovery tooling before any dependent check.
	@test -x "$(CFP_PY)" || { echo "Recovery semantic tooling unavailable. Run make code-first-setup; dependent checks were not run."; exit 1; }

RECOVERY_BASE ?= origin/main
.PHONY: code-first-recovery-rehearse code-first-recovery-check code-first-recovery-render code-first-recovery-source-check code-first-recovery-diff

code-first-recovery-check: code-first-tools ## Check generated Recovery prose and its exact provenance.
	cd $(CFP) && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py check

code-first-recovery-render: code-first-tools ## Explicitly regenerate only the owned Recovery section.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py render

code-first-recovery-source-check: code-first-tools ## Check surrounding prose bindings and generated Recovery identity.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py source-check

code-first-recovery-diff: code-first-tools ## Demonstrate a Recovery definition change in the shared semantic diff.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py diff

code-first-recovery-rehearse: code-first-tools ## Rehearse the exact committed Recovery cutover and reverse patch.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery_transition.py --base-ref $(RECOVERY_BASE) --head-ref HEAD
