# Engineering Baseline

## Purpose

Define shared engineering expectations across repositories. This baseline forms the foundation for workflow rules in this playbook.

## Core Principles

- Small, scoped changes
  - One PR = one reason.
- Validate before PR
  - Use repo-defined validation, such as `make check`.
- Repository isolation
  - One repository per PR.
  - No cross-repo commits.
- Deterministic behavior
  - Prefer explicit, predictable outputs.
- Fail fast and clearly
  - Avoid silent no-ops.
- Minimal surface area
  - Avoid unnecessary features or complexity.
- Documentation for user-facing behavior
  - If behavior changes, document it.

## Git and PR Expectations

- Branch from current `main`.
- Update the branch against current `main` before PR.
- Keep commits clean and focused.
- PRs are ready for review by default.

## Relationship to Playbook

- The AI workflow playbook builds on this baseline.
- Repo-local `AGENTS.md` adds repo-specific constraints.
