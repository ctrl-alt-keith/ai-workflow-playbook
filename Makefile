.PHONY: check check-env authoritative-source-check

# Canonical validation entrypoint for local work and CI.
check:
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

# Environment probe for the tool behind check; not a validation substitute.
check-env:
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		echo "Found markdownlint-cli2"; \
	elif command -v markdownlint >/dev/null 2>&1; then \
		echo "Found markdownlint"; \
	else \
		echo "markdownlint is not installed."; \
		echo "Install markdownlint-cli2 or markdownlint to enable local validation."; \
		exit 1; \
	fi

# Advisory source scan; CI runs this separately from required make check.
authoritative-source-check:
	python3 scripts/check_authoritative_sources.py --base-ref origin/main --head-ref HEAD
