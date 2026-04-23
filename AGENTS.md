# AGENTS.md

This repository uses the shared playbook in `docs/` as the canonical source for general workflow rules. This file is the thin repo-local execution layer.

## Repo Scope

- This repo contains reusable AI workflow and playbook guidance.
- It does not contain implementation code or project-specific automation.

## Start State

- Verify the working directory is `ctrl-alt-keith/ai-workflow-playbook`.
- Start from fresh `origin/main` unless intentionally continuing an existing branch or PR.

## File Placement Rules

- Put core reusable guidance in `docs/`.
- Put tool-specific guidance in `docs/tool-adapters/`.
- Do not add project-specific logic or implementation examples.

## Validation

- CI uses `markdownlint`.
- Ensure `markdownlint` passes before opening or updating a PR.
- If no local wrapper exists, run `markdownlint` in a standard way when available or rely on CI.

## Pull Requests

- Keep each PR scoped to one logical change.
- Include a clear summary and rationale.
- Include validation notes.
- Add `Closes #<issue number>` when applicable.

## Playbook Reference

- For general workflow rules, refer to the playbook documents instead of duplicating them here.
- Start with `docs/core-model.md`, `docs/feature-lifecycle.md`, `docs/alignment-checkpoints.md`, `docs/review-packet.md`, and `docs/tool-adapters/codex.md`.
