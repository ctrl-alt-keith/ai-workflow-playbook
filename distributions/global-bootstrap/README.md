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

## Canonical Router And Destinations

[`bootstrap-router.md`](bootstrap-router.md) is the one copy-ready router body.
Do not maintain provider-specific copies of its text. Project that exact body
into each applicable destination:

- **Codex user-global instructions:** place it in `~/.codex/AGENTS.md` between
  the managed markers described below.
- **Claude Code user-global instructions:** place it in
  `~/.claude/CLAUDE.md` between the same managed markers.
- **ChatGPT account custom instructions:** install and verify the body through
  the hosted Personalization surface.
- **ChatGPT CAK project instructions:** install and verify the body through the
  hosted project-instructions surface.

The two ChatGPT destinations are distinct hosted configuration surfaces even
when they intentionally use the same reviewed router body. Record and verify
them separately; do not collapse them into one ambiguous "project/custom"
surface.

Use these markers around the exact router body in the Codex and Claude local
files:

```text
<!-- ai-workflow-playbook:global-bootstrap:start -->
[exact contents of bootstrap-router.md]
<!-- ai-workflow-playbook:global-bootstrap:end -->
```

The read-only validator compares only the marked body, permitting unrelated
personal instructions before or after it. Preserve the markers when installing
or updating the router.

## Read-Only Validation

Run:

```text
make check-local-bootstrap
```

The check reads the current Codex and Claude user-global files, extracts the
managed body, and compares it byte-for-byte with
[`bootstrap-router.md`](bootstrap-router.md). It does not create, edit, or
replace local files. Missing files, missing or duplicate markers, and content
drift fail with a remediation path.

Use explicit paths when validating staged or fixture files:

```text
python3 scripts/check_global_bootstrap.py \
  --codex-file /path/to/AGENTS.md \
  --claude-file /path/to/CLAUDE.md
```

The ChatGPT account and CAK project instructions are each validated by direct
comparison during manual installation because the provider does not expose
either hosted surface as a local file.

## Installation Boundary

The templates and validator are repository deliverables. Updating live
provider-global files is a separate local reconciliation action: review the
merged projection, replace only the marked block in the applicable user-global
file, and run the read-only check. Do not edit repo-local `AGENTS.md` or
`CLAUDE.md` files merely to install this global router.
