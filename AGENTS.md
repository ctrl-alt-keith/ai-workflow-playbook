# AGENTS.md

This repository uses the shared playbook in `docs/` as the canonical source for
general workflow rules. This file is the thin repo-local execution layer.
Repo-local rules take precedence only for repo-specific behavior.

## Startup And Interaction Mode

- Start with `docs/start-here.md` before repository or software work.
- Before acting, select the interaction mode from `docs/repo-readiness.md`:
  implementation, review/audit, or orchestration/prompt-authoring.
- Implementation agents make explicit repo changes and carry them through
  validation, commit, push, and PR delivery.
- Review/audit agents inspect and report findings without mutating the repo.
- Orchestration/prompt-authoring agents produce complete, self-contained
  handoffs or prompts unless explicitly asked to implement.

## Repo Scope

- This repo contains reusable AI workflow and playbook guidance.
- It does not contain implementation code or project-specific automation.

## File Placement

- Put core reusable guidance in `docs/`.
- Put tool-specific guidance in `docs/tool-adapters/`.
- Do not add project-specific logic or implementation examples.

## Local Execution

- Run commands from this repository working directory by default.
- For implementation changes, use one repository, one branch, one dedicated
  repo-local worktree under `.worktrees/`, and one pull request per change; see
  `docs/repo-readiness.md#pr-readiness`.
- Keep temporary workflow state repo-local.
- Follow the command-form preflight rule in `docs/repo-readiness.md`: use direct
  `git ...`, `gh ...`, `make ...`, `python ...`, repo-local scripts, and tool
  commands for ordinary repository operations.
- For standard `git` and `gh` work, preserve direct CLI execution at both the
  command-selection and execution-tool layers; disable implicit shell or
  login-shell behavior where the environment supports that.
- Before using `zsh`, `bash`, `sh`, `zsh -lc`, `bash -lc`, `sh -c`, aliases, or
  equivalent wrapper shells, confirm shell semantics are genuinely required;
  otherwise rewrite the operation into direct argv form.

## Validation

- Use `make check` as the canonical local validation entrypoint.
- Run `make check` before opening or updating a PR.
- `make check` runs Markdown lint and scanner unit tests.
- Treat direct validation tool calls as implementation details of the Makefile
  target.
- `make authoritative-source-check` runs advisory authoritative-source scanning;
  it is separate from `make check` and non-blocking unless a caller configures
  that workflow to be stricter.
- CI is the enforcement layer for required remote checks and for checks that
  local tooling cannot run.

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
- Codex runs must apply `docs/tool-adapters/codex.md` as part of startup.
- For general workflow rules, refer to the playbook documents instead of
  duplicating them here. Use `docs/core-model.md`,
  `docs/feature-lifecycle.md`, `docs/alignment-checkpoints.md`, and
  `docs/review-packet.md` as reference material for deeper workflow details.
