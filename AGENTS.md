# AGENTS.md

This repository uses the shared playbook in `docs/` as the canonical source for
general workflow rules. This file is the thin repo-local execution layer.
Repo-local rules take precedence only for repo-specific behavior.

## Repo Scope

- This repo contains reusable AI workflow and playbook guidance.
- It does not contain implementation code or project-specific automation.

## File Placement

- Put core reusable guidance in `docs/`.
- Put tool-specific guidance in `docs/tool-adapters/`.
- Do not add project-specific logic or implementation examples.

## Validation

- CI uses `markdownlint`.
- Use `make check` as the canonical local validation entrypoint.
- Run `make check` before opening or updating a PR.
- Treat direct `markdownlint` invocation as an implementation detail of the
  Makefile target.
- CI remains the enforcing authority if local tooling is unavailable.

## Branches

- Use `codex/<short-name>` for automation-driven playbook or documentation work.
- Use concise descriptive branch names for human-driven work, such as
  `docs/<short-name>` or `chore/<short-name>`.

## Pull Requests

- Target `main`.
- Include a clear summary and rationale.
- Include validation notes.
- Add `Closes #[issue number]` when applicable.

## Playbook Reference

- This playbook builds on the engineering baseline defined in
  `docs/engineering-baseline.md`.
- For general workflow rules, refer to the playbook documents instead of
  duplicating them here.
- Start with `docs/core-model.md`, `docs/feature-lifecycle.md`,
  `docs/alignment-checkpoints.md`, `docs/review-packet.md`, and
  `docs/tool-adapters/codex.md`.
