# Codex Adapter

This document explains how Codex maps onto the core playbook. It is adapter-specific guidance, not part of the core operating model.

## Codex-Specific Quirks

- Codex can move quickly from brief to implementation, so phase boundaries need to be stated explicitly
- Codex benefits from narrow, well-shaped tasks with clear validation targets
- Codex can produce fluent output that still needs human judgment on scope, tradeoffs, and completeness

## Local Permissions Model

Codex operates inside a local permissions model. Some actions may require approval, especially for network access, privileged writes, or potentially destructive commands.

Treat permission boundaries as part of the execution environment, not as incidental friction. If a task depends on elevated access, surface that early and keep the requested action narrowly scoped.

## PR Expectations

- keep PRs phase-shaped and reviewable
- summarize intent, scope, validation, and known risks
- prefer draft PRs until the phase objective is actually met
- avoid bundling unrelated cleanup into the same PR

## CI Expectations

- run the repo-local validation path when it exists
- report clearly when no local validation path exists
- treat passing CI as necessary but not sufficient
- use hardening to close gaps exposed by CI, review, or edge cases

## Git And GitHub Workflow Notes

- use a fresh branch for each lifecycle phase after merge
- keep commit messages and PR titles clear and phase-oriented
- preserve a clean review narrative rather than one long-running branch
- open a new PR when the work changes phase or review surface

Codex should follow the core model, but this adapter exists to document the tooling realities that shape how the model is applied in practice.
