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
- The default bootstrap and accepted guidance remain v1. CAK-301 explicitly
  permits experimental v2 increments 0–2 in `v2_retain/` and its focused tests,
  governed by `v2_retain/README.md`, on the dedicated development branch.
  This exception does not promote provisional architecture or authorize live
  provider qualification, default cutover, merge, release, or issue closure.

## File Placement

- Put core reusable guidance in `docs/`.
- Put tool-specific guidance in `docs/tool-adapters/`.
- Before editing agent-read content, apply
  [Agent-Read Documentation](docs/engineering-baseline.md#agent-read-documentation)
  to the complete affected rule across its current surfaces.
- Keep experimental v2 code and its contract together in `v2_retain/`; otherwise
  do not add project-specific logic or implementation examples.

## Local Execution

- Run commands from this repository working directory by default.
- For implementation changes, use one repository, one branch, one dedicated
  repo-local worktree under `.worktrees/`, and one pull request per change; see
  `docs/repo-readiness.md#pr-readiness`.
- Keep repository-owned working state repo-local and tool-owned working state
  under its tool's contract. Use attempt-local disposable scratch only for
  private mechanics that have no required post-attempt role; see
  `docs/repo-readiness.md#repo-local-workflow-state`.
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
- Run `make v2-setup` once in a fresh worktree. `make check` runs Markdown
  lint, existing unit tests, and experimental v2 local/fake acceptance tests.
  Live provider qualification is excluded and remains separately authorized.
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

- Target `main` by default. An eligible stack layer may target the preceding
  branch; follow
  `docs/orchestration-and-parallelism.md#optional-stacked-pull-requests`.
- Include a clear summary and rationale.
- Include validation notes.
- Add `Closes #[issue number]` when applicable.

## Playbook Reference

- Start here: `docs/start-here.md`
- This playbook builds on the engineering baseline defined in
  `docs/engineering-baseline.md`.
- Codex runs must apply `docs/tool-adapters/codex.md` as part of startup.
- Claude runs must apply `docs/tool-adapters/claude.md` as part of startup.
- For general workflow rules, refer to the playbook documents instead of
  duplicating them here. Use `docs/core-model.md`,
  `docs/feature-lifecycle.md`, `docs/alignment-checkpoints.md`, and
  `docs/review-packet.md` as reference material for deeper workflow details.
