.PHONY: help check check-env check-local-bootstrap authoritative-source-check scanner-test

.DEFAULT_GOAL := check

help: ## List available repo-local Makefile targets with short descriptions.
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-28s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: code-first-check code-first-recovery-check ## Run canonical local validation for local work and CI.
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
.PHONY: code-first-setup code-first-tools code-first-check code-first-source-check code-first-render code-first-diff code-first-rehearse

code-first-setup: ## Set up the isolated CAK-233 parser dependency.
	python3 -m venv $(CFP)/.venv
	$(CFP_PY) -m pip install --disable-pip-version-check -r $(CFP)/requirements.txt

code-first-tools: ## Report missing pilot tooling before any dependent check.
	@test -x "$(CFP_PY)" || { echo "CAK-233 pilot tooling unavailable. Run make code-first-setup; dependent checks were not run."; exit 1; }

code-first-check: code-first-tools ## Check the bounded shadow compiler and exact previews.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) -m unittest discover -s $(CFP)/tests
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/pilot.py check

code-first-source-check: code-first-tools ## Check current prose binding for pilot claims.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/pilot.py source-check

code-first-render: code-first-tools ## Generate non-operational review previews.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/pilot.py render

code-first-diff: code-first-tools ## Exercise the two bounded semantic edit rounds.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/pilot.py diff --old-bundle cases/baseline.json --bundle cases/edit-round-1.json
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/pilot.py diff --old-bundle cases/edit-round-1.json --bundle cases/edit-round-2.json

code-first-rehearse: code-first-tools ## Report simulation-only authority-transition rehearsal.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/pilot.py rehearse

RECOVERY_BASE ?= origin/main
.PHONY: code-first-recovery-rehearse code-first-recovery-check code-first-recovery-render code-first-recovery-source-check code-first-recovery-diff

code-first-recovery-check: code-first-tools ## Check generated Recovery prose and its exact provenance.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py check

code-first-recovery-render: code-first-tools ## Explicitly regenerate only the owned Recovery section.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py render

code-first-recovery-source-check: code-first-tools ## Check surrounding prose bindings and generated Recovery identity.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py source-check

code-first-recovery-diff: code-first-tools ## Demonstrate a Recovery definition change in the shared semantic diff.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery.py diff

code-first-recovery-rehearse: code-first-tools ## Rehearse the exact committed Recovery cutover and reverse patch.
	PYTHONDONTWRITEBYTECODE=1 $(CFP_PY) $(CFP)/recovery_transition.py --base-ref $(RECOVERY_BASE) --head-ref HEAD
