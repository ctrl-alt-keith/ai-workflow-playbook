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

## Incubator vs Playbook

- `ai-workflow-incubator` is the private staging/incubation repo for ideas and experiments.
- It is not canonical and is not a direct path into playbook guidance.
- Durable workflow guidance follows this order: idea -> notes staging ->
  bounded repo issue or PR -> evidence-supported reusable lesson -> playbook
  promotion -> notes cleanup.
- Treat repository code, tests, docs, reviews, and merged PRs as the evidence
  source for reusable lessons before promoting them into the playbook.

## Rule of Thumb

- Prefer small, scoped changes.
- Run repository validation through the repo's Makefile when it provides the
  canonical entrypoint.
- Open PRs ready for review by default unless explicitly instructed otherwise.
