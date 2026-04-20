# New Repo Bootstrap

Use this pattern when bootstrapping a brand-new repository from a fresh project directory rather than from inside an existing repo context.

## Recommended Flow

1. Start in a clean, repo-specific Codex project or working context tied to the new project directory, with no existing git history.
2. Create the repository under the target org.
3. Initialize local git on `main`.
4. Create a minimal initial `main` commit.
5. Push `main` to establish the base branch remotely.
6. Create a feature branch for the real bootstrap work.
7. Open a PR for the bootstrap content rather than merging directly.

This keeps the actual bootstrap reviewable while avoiding ambiguity about where the repository starts.

## Lessons

### Base Branch First

GitHub needs a base branch before a PR can exist. For a brand-new repo, use a minimal initial `main` commit so the real bootstrap work can land through a normal PR.

### Ready-For-Review By Default

If the bootstrap work is complete, the PR should be ready for review by default. Use draft only when the bootstrap is intentionally incomplete or early feedback is needed.

### Relative Links From The Start

Repo docs should use relative links from the start. Absolute local filesystem paths are not portable and can leak machine-specific context into the repository.

### Validation In A Docs-First Repo

A brand-new docs-first repo may not have a repo-local validation path yet. Until it does, validation falls back to:

- internal consistency review
- path portability checks
- scope review against the repo guardrails

### Connector And GitHub Behavior

Keep the bootstrap workflow tool-aware but practical:

- repo and PR metadata may be easier to inspect through a connector when available
- repo creation, branch publishing, or current-branch PR actions may still need `gh`
- if a connector mutation misbehaves, use the simplest working CLI fallback and verify the resulting state

## Reuse

Treat this as a reusable bootstrap pattern for new repositories, not as a one-off retrospective. Reapply it when a new repo needs a clean starting point, a reviewable bootstrap PR, and lightweight validation before richer tooling exists.
