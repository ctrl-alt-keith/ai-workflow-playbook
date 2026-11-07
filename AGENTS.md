# AGENTS.md

Start with `docs/start-here.md` before repository work.

## Repo Scope

- This repo contains reusable AI workflow and playbook guidance.
- The default bootstrap remains v1. The accepted v2 semantic foundation is
  `docs/v2-architecture-foundation.md`; CAK-301's opt-in retention implementation
  and focused tests live in `v2_retain/`, governed by `v2_retain/README.md`.
  A bounded Mac-local run on the separately reviewed pre-rebase head is
  evidenced there, with uncertain outcomes held. This exception does not
  authorize this development lane to consume the credential, contact Dropbox,
  cut over defaults, merge, release, or close the issue.

## File Placement

- Put core reusable guidance in `docs/`.
- Put tool-specific guidance in `docs/tool-adapters/`.
- Keep experimental v2 code and its contract together in `v2_retain/`; otherwise
  do not add project-specific logic or implementation examples.

## Validation

- Use `make check` as the canonical local validation entrypoint.
- Run `make v2-setup` once in a fresh implementation checkout. `make check`
  runs Markdown lint, existing unit tests, and experimental v2 local/loopback
  acceptance tests. Live provider qualification is excluded from validation
  and requires a separately authorized Mac-local session.
- `make authoritative-source-check` runs advisory authoritative-source scanning;
  it is separate from `make check` and non-blocking unless a caller configures
  that workflow to be stricter.

## Pull Requests

- Include a clear summary and rationale.
- Include validation notes.
