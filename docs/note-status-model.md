# Note Status Model

Use this optional model when a notes repository needs a lightweight status pass
without running a full cleanup workflow.

This model is intentionally smaller than a full `remove / trim / keep / defer`
audit. It helps mark what should stay in active notes, what should be tightened,
and what should wait on a later decision. If a cleanup pass is ready to decide
deletion, use the fuller alignment audit in [`prompts.md`](prompts.md).

## Goal

Give notes a simple status vocabulary that keeps the staging layer usable
without turning it into a second canonical system.

Apply the model at the file or section level. Keep it lightweight and optional.

## Statuses

### Keep

Use `keep` when the note still serves a valid staging purpose and does not
conflict with the canonical playbook or other settled guidance.

Examples:

- a working note with unresolved synthesis that has not yet been promoted
- a local capture with team-specific context that should stay in notes
- a comparison note that still informs an open decision

### Trim

Use `trim` when the note should remain, but some portion is now redundant,
stale, or noisier than the value it provides.

Examples:

- a long note whose promoted guidance can be removed while local follow-up stays
- a research note that should keep conclusions but drop copied source material
- a recurring log that should keep current action items but lose repeated setup

### Defer

Use `defer` when the status depends on a separate decision, missing context, or
unfinished follow-up work.

Examples:

- a note referenced by an active branch or PR that has not settled yet
- a draft capture that still needs human confirmation before cleanup
- a folder owned by another collaborator where local intent is still unclear

## How To Use It

1. Stay inside the notes repository or project root you are reviewing.
2. Classify only the files or sections you actually inspected.
3. Add a short rationale with each status.
4. Prefer `trim` over churn when a note still contains mixed-value material.
5. Revisit `defer` after the blocking decision or follow-up work lands.

## Lightweight Output Shape

Use a short, file-specific list such as:

- `keep`: still useful as staging material for open synthesis
- `trim`: remove duplicated playbook guidance and keep local follow-up
- `defer`: wait for the active PR to merge before deciding cleanup

The goal is not perfect categorization. The goal is to keep notes reviewable,
reduce accidental duplication, and preserve a clear boundary between staging
material and canonical guidance.
