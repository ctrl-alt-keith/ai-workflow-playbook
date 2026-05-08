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

## Local Execution

- Run commands from this repository working directory by default.
- Keep temporary workflow state repo-local, for example `.worktrees/`.
- Follow the command-form rule in `docs/repo-readiness.md`: prefer direct
  `git ...`, `gh ...`, `make ...`, `python ...`, and tool commands; reserve
  wrapper shells for commands that genuinely require shell behavior.

## Validation

- Use `make check` as the canonical local validation entrypoint.
- Run `make check` before opening or updating a PR.
- `make check` runs Markdown lint and scanner unit tests.
- Treat direct validation tool calls as implementation details of the Makefile
  target.
- Authoritative-source scanning is advisory and non-blocking unless a caller
  configures that workflow to be stricter.
- CI remains the enforcing authority if local tooling is unavailable.

## Branches

- Follow the branch naming guidance in `docs/feature-lifecycle.md`.
- For playbook documentation work, use concise descriptive branch names such as
  `docs/<short-name>` or `chore/<short-name>`.

## Pull Requests

- Target `main`.
- Include a clear summary and rationale.
- Include validation notes.
- Add `Closes #[issue number]` when applicable.

## Playbook Reference

- Start here: `docs/start-here.md`
- This playbook builds on the engineering baseline defined in
  `docs/engineering-baseline.md`.
- For general workflow rules, refer to the playbook documents instead of
  duplicating them here.
- After `docs/start-here.md`, use `docs/core-model.md`,
  `docs/feature-lifecycle.md`, `docs/alignment-checkpoints.md`,
  `docs/review-packet.md`, and `docs/tool-adapters/codex.md` as reference
  material for deeper workflow details.
