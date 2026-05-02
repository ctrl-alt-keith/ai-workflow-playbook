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

## Public API Baselines

When a task changes code, tests, docs, risks, or user-facing claims that depend
on external public API behavior, establish the current behavior from official
sources before making the change.

- Applies to public APIs, SDKs, SaaS APIs, cloud providers, GitHub APIs, CLIs,
  package managers, and other external systems.
- Prefer official docs, API references, SDK docs, provider changelogs, and
  official release notes.
- Check official sources for behavior such as resource lifecycle or status
  semantics, region or location availability, pagination, rate limits and
  retryability, auth or token error behavior, deletion and idempotency
  semantics, eventual consistency or timing behavior, and SDK or CLI command
  behavior.
- Do not rely on model memory, stale historical knowledge, or inference where
  official docs are available.
- If official docs are ambiguous or cannot confirm the behavior, state that
  uncertainty, choose conservative behavior, and avoid encoding a false
  guarantee or limitation.
- PR notes or docs should summarize the verified official source when relevant.

This requirement does not apply to purely internal refactors that do not depend
on external API semantics.

## Relationship to Playbook

- The AI workflow playbook builds on this baseline.
- Repo-local `AGENTS.md` adds repo-specific constraints.
