# Start Here

## Purpose

- This playbook defines the canonical workflow for AI-assisted repository work.
- Use this page to quickly orient before performing tasks.

## Read Order

- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/repo-readiness.md` -> repository workflow expectations
- `docs/maintenance-automations.md` -> recurring Codex maintenance automation expectations
- `docs/prompts.md` -> reusable prompt templates

## Execution Model

- Use `ai-workflow-playbook` as the canonical source of reusable workflow rules.
- Treat `AGENTS.md` as the repo-local execution layer.
- Repo-local rules take precedence only for repo-specific behavior.

## Notes vs Playbook

- `cross-repo-threads` is a staging layer for ideas and experiments.
- It is not canonical; treat repository code, tests, and docs as the source of truth and verify against playbook guidance.

## Rule of Thumb

- Prefer small, scoped changes.
- Validate with the repo's Makefile.
- Open PRs ready for review by default unless explicitly instructed otherwise.
