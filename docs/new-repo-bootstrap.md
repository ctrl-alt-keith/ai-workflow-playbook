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

## Bootstrap Content Checklist

Include only the durable repo-shaping decisions needed before normal feature
work begins:

- purpose and audience
- public or private posture
- license selection for public repositories
- non-affiliation language when the repository could be mistaken for an
  official, vendor-owned, or endorsed project
- scope boundaries and explicit non-goals
- safety model for mutation-capable workflows
- credential handling expectations
- validation entrypoint or current validation gap
- ecosystem registration needs after bootstrap

Keep these decisions short and operational. Repo-specific examples,
implementation details, provider behavior, and legal analysis belong outside
the reusable playbook.

## Lessons

### Base Branch First

GitHub needs a base branch before a PR can exist. For a brand-new repo, use a minimal initial `main` commit so the real bootstrap work can land through a normal PR.

### Ready-For-Review By Default

If the bootstrap work is complete, the PR should be ready for review by default. Use draft only when the bootstrap is intentionally incomplete or early feedback is needed.

### Relative Links From The Start

Repo docs should use relative links from the start. Absolute local filesystem paths are not portable and can leak machine-specific context into the repository.

### Positioning Before Features

Establish the repository's public posture before feature growth. A public
infrastructure-adjacent repository should state what it is, who owns it, and
what it is not. If readers could confuse it with an official provider,
upstream, customer, or employer project, include a brief non-affiliation
statement in repo-local docs.

Do not turn positioning into legal policy. The reusable requirement is clarity:
avoid implied endorsement, hidden ownership assumptions, or ambiguous safety
claims.

### Scope And Non-Goals

Define the first working boundary before adding implementation weight:

- what workflows the repository intentionally supports
- what workflows it intentionally excludes
- what live-service, production, destructive, or credentialed behavior is out
  of scope by default
- what assumptions must remain explicit until verified

Use non-goals to prevent accidental expansion, not to document every possible
future idea.

### Public-Safe Operating Posture

For public repositories near infrastructure, automation, credentials, or
mutable external systems, default to conservative safety boundaries:

- dry-run or inspect-first behavior before mutation
- deterministic manifests or reports for reviewable output
- environment-only credential handling
- no committed secrets, local paths, account identifiers, or private topology
- explicit confirmation for destructive or irreversible operations
- clear separation between observed behavior and documented guarantees

The playbook guidance is the posture, not a mandate for a specific
architecture.

### Validation In A Docs-First Repo

A brand-new docs-first repo often does not have a repo-local validation path yet. Until it does, validation falls back to:

- internal consistency review
- path portability checks
- scope review against the repo guardrails

### Connector And GitHub Behavior

Keep the bootstrap workflow tool-aware but practical:

- repo and PR metadata may be easier to inspect through a connector when available
- repo creation, branch publishing, or current-branch PR actions may still need `gh`
- if a connector mutation misbehaves, use the simplest working CLI fallback and verify the resulting state

### Ecosystem Registration After Bootstrap

A repository is not fully integrated when the first bootstrap PR merges. After
bootstrap, check that surrounding workflow systems recognize the repository
consistently:

- repo inventories or org briefs
- automation inventories or scheduled maintenance lists
- cross-repo prompts or context refresh inputs
- sibling-repo references, when they intentionally name the repository
- validation or advisory workflow adoption, when applicable

Keep this lightweight. The reusable lesson is to distinguish intentionally
excluded repositories from accidentally invisible ones, then update only the
systems that should know about the repo.

## Reuse

Treat this as a reusable bootstrap pattern for new repositories, not as a one-off retrospective. Reapply it when a new repo needs a clean starting point, a reviewable bootstrap PR, and lightweight validation before richer tooling exists. Review it with [`playbook-integrity-check.md`](playbook-integrity-check.md) if similar bootstrap capture docs start to accumulate.
