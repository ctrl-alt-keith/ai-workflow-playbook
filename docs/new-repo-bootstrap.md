# New Repo Bootstrap

Use this pattern when bootstrapping a brand-new repository from a fresh project directory rather than from inside an existing repo context.

## Recommended Flow

1. Start in a clean, repo-specific Codex project or working context tied to the new project directory, with no existing git history.
2. Create the repository under the target org.
3. Initialize local git on `main`.
4. Create a minimal initial `main` commit.
5. Push `main` to establish the base branch remotely.
6. Create a feature branch for the real bootstrap work.
7. Add the narrow local workflow artifact ignore baseline before worktree or
   automation use begins.
8. Open a PR for the bootstrap content rather than merging directly.

This keeps the actual bootstrap reviewable while avoiding ambiguity about where the repository starts.

## Bootstrap Posture Checklist

For public, infrastructure-adjacent, or externally dependent repositories,
bootstrap should connect public positioning, operational posture, and technical
shape before feature work begins. Include only the durable repo-shaping
decisions needed to make that posture clear:

- purpose and audience
- public or private posture
- license selection for public repositories
- non-affiliation language when the repository could be mistaken for an
  official, vendor-owned, or endorsed project
- scope boundaries and explicit non-goals
- safety model and mutation boundaries
- reviewable artifacts, such as deterministic manifests or reports, when the
  repository produces operational output
- credential handling expectations
- authoritative external documentation boundaries
- validation entrypoint or current validation gap
- local workflow artifact ignore baseline
- lightweight ecosystem registration needs after bootstrap

Keep these decisions short and operational. Repo-specific examples,
implementation details, provider behavior, and legal analysis belong outside
the reusable playbook.

## Lessons

### Base Branch First

GitHub needs a base branch before a PR can exist. For a brand-new repo, use a minimal initial `main` commit so the real bootstrap work can land through a normal PR.

### Ready-For-Review By Default

If the bootstrap work is complete, the PR should be ready for review by default. Use draft only when the bootstrap is intentionally incomplete or early feedback is needed.

### Relative Links From The Start

Repo docs should use relative links from the start. For public bootstrap
artifacts, apply the baseline path-hygiene rule: avoid machine-local absolute
paths in docs, examples, manifests, validation notes, and reusable workflow
guidance.

### Local Workflow Artifact Hygiene

Bootstrap should include ignore rules for standardized workflow-local
infrastructure that the repo expects humans, Codex, or maintenance automation to
create locally. Keep this intentionally narrow: include repo-local workflow paths
such as `.worktrees/`, and avoid expanding bootstrap into generic workstation,
editor, runtime, or temporary-file policy.

Dirty-tree safety checks depend on this baseline. If standardized local workflow
artifacts appear as untracked files, conservative automation should skip rather
than mutate the repository, but the repo has lost the predictable clean state the
workflow expects.

### Positioning, Scope, And Architecture

Establish one coherent posture before feature growth. A repository should state
what it is, what it is not, and how its technical choices reinforce that
boundary. If readers could confuse it with an official provider, upstream,
customer, or employer project, include a brief non-affiliation statement in
repo-local docs.

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

Use non-goals to prevent accidental expansion, especially platform gravity
toward orchestration systems, desired-state platforms, automation frameworks,
or generalized control planes. Include that evolution only when it is an
explicit repository goal.

### Public-Safe Operating Posture

For public repositories near infrastructure, automation, credentials, or
mutable external systems, default to conservative safety boundaries. The
architecture should match the stated posture:

- dry-run or inspect-first behavior before mutation
- explicit mutation boundaries
- deterministic manifests or reports for reviewable output
- environment-only credential handling
- no committed secrets, local paths, account identifiers, or private topology
- explicit confirmation for destructive or irreversible operations
- clear separation between observed behavior and documented guarantees

The playbook guidance is the posture, not a mandate for a specific
architecture. Avoid hidden destructive behavior and do not let implementation
convenience contradict the public scope or safety claim.

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

### Lightweight Ecosystem Registration

A repository is not fully integrated when the first bootstrap PR merges. After
bootstrap, check that surrounding workflow systems know the repository exists
where that awareness matters:

- repo inventories or org briefs
- automation inventories or scheduled maintenance lists, when the repo is
  intentionally covered
- cross-repo prompts or context refresh inputs
- sibling-repo references, when they intentionally name the repository
- validation or advisory workflow adoption, when applicable

Keep this lightweight. Registration means inventories, audits, and context
systems can classify the repo correctly. It does not imply mature automation
support, operational ownership, or service guarantees. Distinguish
intentionally excluded repositories from accidentally invisible ones, then
update only the systems that should know about the repo.

## Reuse

Treat this as a reusable bootstrap pattern for new repositories, not as a one-off retrospective. Reapply it when a new repo needs a clean starting point, a reviewable bootstrap PR, and lightweight validation before richer tooling exists. Review it with [`playbook-integrity-check.md`](playbook-integrity-check.md) if similar bootstrap capture docs start to accumulate.
