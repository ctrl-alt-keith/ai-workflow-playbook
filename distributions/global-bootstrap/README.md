# Global Bootstrap Distribution

## Purpose

This distribution projects the Playbook's repository startup entry point onto
provider-global instruction surfaces. Installing the applicable projection
once gives every repository the same thin router without copying shared
doctrine into every repo-local instruction file.

The canonical timing rule remains in
[`docs/start-here.md`](../../docs/start-here.md#global-bootstrap-persistence):

> Before the first project action, and again only when the task/repository
> materially changes.

The router persists after successful bootstrap. A new conversational turn,
follow-up message, reasoning step, or tool call does not independently trigger
another retrieval.

## Provider Projections

- [`codex-AGENTS.md`](codex-AGENTS.md) projects the router into
  `~/.codex/AGENTS.md`.
- [`claude-CLAUDE.md`](claude-CLAUDE.md) projects the router into
  `~/.claude/CLAUDE.md`.
- [`chatgpt-custom-instructions.md`](chatgpt-custom-instructions.md) is the
  copy-ready ChatGPT custom-instructions projection.

The Codex and Claude files use managed markers so the read-only validator can
compare only this distribution's block while permitting unrelated personal
instructions before or after it. Preserve the markers when installing or
updating those projections.

## Read-Only Validation

Run:

```text
make check-local-bootstrap
```

The check reads the current Codex and Claude user-global files, extracts the
managed block, and compares it byte-for-byte with the corresponding canonical
projection. It does not create, edit, or replace local files. Missing files,
missing or duplicate markers, and content drift fail with a remediation path.

Use explicit paths when validating staged or fixture files:

```text
python3 scripts/check_global_bootstrap.py \
  --codex-file /path/to/AGENTS.md \
  --claude-file /path/to/CLAUDE.md
```

ChatGPT custom instructions are validated by direct comparison during manual
installation because the provider does not expose them as a local file.

## Installation Boundary

The templates and validator are repository deliverables. Updating live
provider-global files is a separate local reconciliation action: review the
merged projection, replace only the marked block in the applicable user-global
file, and run the read-only check. Do not edit repo-local `AGENTS.md` or
`CLAUDE.md` files merely to install this global router.
