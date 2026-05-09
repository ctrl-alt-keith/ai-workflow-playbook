# Repo Readiness Baseline

## Purpose

Define the smallest reusable baseline a repository should have before normal AI-assisted delivery work begins.

## Scope

- This is a practical baseline, not a full policy or checklist.
- It covers pull request flow, readiness state, validation, branch protection expectations, and the role of `AGENTS.md`.
- Repo-specific security, compliance, release, or approval rules should be defined only when needed by that repository.

## Baseline Expectations

- All changes go through pull requests.
- Validation must pass before a pull request is considered complete.
- Pull requests should stay small, scoped, and single-purpose.
- Public repositories include a root `LICENSE` file, defaulting to Apache License
  2.0 unless the repository documents another choice.
- Repositories with a Makefile include `make help` for local target discovery.
- Defaults should favor safe, explicit behavior over implied shortcuts.

## Interaction Mode Preflight

Before acting on any repository or software task, determine the interaction
mode. Do this before editing files, creating branches, committing, opening pull
requests, or running implementation-oriented workflows.

Use one of these modes:

- Implementation mode: directly make repo changes, validate them, commit them,
  push the branch, and open or update a pull request when repo guidance calls
  for PR delivery.
- Review/audit mode: inspect the requested repository, pull request, issue, or
  file surface and report findings, evidence, risks, and recommendations
  without mutating the repository.
- Orchestration/prompt-authoring mode: inspect enough issue, repository, pull
  request, and workflow context to decide the right course of action, then
  produce a complete, self-contained prompt or handoff for another agent or
  tool.

Tool-role boundaries follow the selected mode:

- Implementation agents implement explicit repository changes directly and
  carry them through validation, commit, push, and PR delivery when repo
  guidance calls for it.
- Review or audit agents inspect and report findings, evidence, risks, and
  recommendations without implementing changes.
- Orchestration or prompt-authoring agents produce a complete handoff prompt or
  task envelope unless the human explicitly asks them to implement the change.

Do not infer implementation mode from vague wording such as "fix this",
"handle this", or "let's fix the bug" when the surrounding context suggests
advisory review, audit, orchestration, or prompt generation.

For ctrl-alt-keith workflows, default ambiguous repository tasks to
review/audit mode or orchestration/prompt-authoring mode unless the human
explicitly asks for direct implementation. Implementation mode requires clear
user intent, such as "make the change", "implement it", "open the PR",
"commit this", or equivalent wording.

In orchestration/prompt-authoring mode, do enough direct inspection to make the
handoff usable without hidden assumptions. A prompt that asks another agent to
act should include the repository, goal, relevant context, constraints,
validation path, deliverable expectations, and any known blockers or
uncertainty. The handoff must be complete, self-contained, and directly usable.
Do not produce partial prompts, continuation fragments, diffs, partial edits,
or "change X to Y" pseudo-prompts unless the human explicitly requested that
form.

Keep this policy in the shared playbook. Repo-local `AGENTS.md` files should
reference or rely on it rather than duplicate it, except where a repository
truly requires different behavior.

## Makefile Discoverability

Any repository with a Makefile should include a `make help` target. `make help`
lists available repo-local Makefile targets with short descriptions so a fresh
worker can discover setup, validation, generation, and maintenance commands
without reading the whole file first.

Prefer the self-documenting `##` comment pattern when it fits the existing
Makefile style, for example `check: ## Run canonical local validation`.

## PR Readiness

Open a pull request as ready for review when all of the following are true:

- implementation is complete
- validation passes
- no known follow-up work is required before merge
- overlap and coordination risk are low
- issue lifecycle should not affect pull request readiness; using `Closes #<issue>` follows standard GitHub behavior and should not delay marking a pull request as ready

Before opening or updating a pull request, fetch current `origin/main` and
verify whether the branch is mergeable against current `main`. Update or rebase
only for conflicts, overlapping upstream changes, repo policy, or explicit
human request. Keep any conflict resolution within the original task scope,
avoid unrelated cleanup, rerun the canonical validation entrypoint after the
update, then push.

Open a pull request as draft when any of the following are true:

- work is incomplete
- the change is part of a coordinated batch with sequencing risk
- reconciliation with other pending work is likely
- the branch is intentionally staged for later promotion

Docs-only changes should default to ready for review when canonical validation
passes and the diff is isolated.

When working in a multi-repo workspace, treat each repository as an independent unit of change. Even if multiple repositories are visible, commits, branches, and PRs must be created and managed per repository. Do not create cross-repo commits or PRs.

Before opening a PR, ensure that all staged changes belong to a single repository. If changes span multiple repositories, split them into separate branches and PRs, one per repository.

## Workspace Boundary Discovery

When work spans multiple repositories, determine the active managed workspace
set from authoritative repository inventory sources before broad scans or
updates begin.

Prefer organization-level repository enumeration and explicit workspace
manifests such as `config/workspace-repos.txt`. Reconcile those sources before
treating local checkouts as part of the active workspace scope.

Do not treat raw local filesystem layout as authoritative workspace scope.
Local checkout trees may contain stale repositories, archived repositories,
detached worktrees, experiments, incomplete clones, temporary operational
state, or local-only scratch repositories.

Reconcile local workspace state against the canonical workspace inventory
before cross-repo audits, `AGENTS.md` alignment, enforcement scans, or broad
workflow updates.

## Repo-Local Workflow State

Run commands from the target repository working directory by default. Keep
temporary workflow artifacts scoped to that repository whenever practical.
Examples include local worktree directories, generated review artifacts,
transient manifests, and task-specific scratch state.

Use repo-local temporary state when artifacts belong to one repository's
execution workflow and that repository's instructions support the local path.
When temporary workflow material spans repositories or should remain visible
during execution, prefer the workspace scratch area:
`~/src/ctrl-alt-keith/scratch/`. Suitable scratch material includes generated
reports, orchestration helpers, prompt packs, transient automation outputs, and
other disposable workflow artifacts that may need later inspection,
provenance, reconciliation, or cleanup review.

Avoid `/tmp`, `/private/tmp`, or ad hoc temporary directories for workflow
artifacts that may need later inspection. Use disposable OS temp locations only
for short-lived process-local files whose path and contents do not matter after
the command finishes.

For Codex specifically, configured
`[sandbox_workspace_write].writable_roots` may not be the full effective
writable root set. The active project root and platform temp directories can be
implicit writable roots unless local config excludes them. When stricter
isolation matters, inspect the effective policy with
`codex debug prompt-input effective-sandbox-check` and use the Codex adapter's
sandbox guidance for temp-root exclusions.

Avoid spreading workflow state across sibling repositories or other ad hoc
shared locations unless the task explicitly requires broader coordination. When
broader coordination is required, state where the shared state lives and why
repo-local state is insufficient.

## Command Form And Intent Visibility

Use the structurally minimal command form that still expresses the intended
operation clearly. Normal repository operations must be invoked as the command
itself, rather than hidden inside an extra shell layer.

Run commands from the target repository working directory by default. For
ordinary repository operations, use direct `git ...`, `gh ...`, `make ...`,
`python ...`, repo-local scripts, and tool-specific commands. Before choosing a
wrapper shell, check whether the command has a direct form and use that direct
form when it does. Do not wrap those commands in `zsh`, `bash`, `sh`, shell
aliases, or equivalent wrapper shells only for convenience. In particular,
`zsh -lc`, `bash -lc`, `sh -c`, or equivalent forms are not normal wrappers for
ordinary repo commands.

This keeps operational intent visible in logs, prompts, review notes, and local
approval surfaces. It also lets permission or approval systems reason about the
specific operation being requested, instead of treating a simple repository
action as a broad shell execution.

Before executing any shell-wrapped command, perform a command-form preflight:

- determine whether the operation genuinely needs shell semantics, such as
  pipes, redirects, glob expansion, command chaining, shell builtins, inline
  environment assignment, compound shell conditionals, or other shell-only
  composition
- if shell semantics are not required, rewrite the command into direct argv
  form before execution
- if shell semantics are required, keep the wrapped command narrow enough that
  the operational intent remains inspectable

Use a shell wrapper when the operation genuinely needs shell semantics, such as
pipes, redirection, glob expansion, command chaining, shell builtins, inline
environment assignment, compound conditionals, or other composition that the
command cannot express directly. When shell semantics are needed, keep the
wrapped command narrow enough that the operational intent remains inspectable.

Examples:

- incorrect: `zsh -lc 'git status'`
- correct: `git status`
- incorrect: `bash -lc 'make check'`
- correct: `make check`
- incorrect: `sh -c 'gh pr view 145'`
- correct: `gh pr view 145`

Avoid inflating simple commands into larger execution forms only for habit or
convenience. The goal is not to forbid shells; it is to preserve clarity,
reviewability, and policy precision around what work is actually being
performed.

## Branch Protection

Treat the following as the default branch protection baseline for `main`:

- pull requests are required for changes to `main`
- the repository validation check is required, typically `make check`; if a
  repository uses a different single entrypoint, that repo's `AGENTS.md` owns it
- additional CI-only checks block merge only when branch protection or
  repo-local guidance explicitly makes them required
- admins follow the same merge rules
- required approvals are not part of the default baseline unless a repository defines stricter repo-specific rules

This document defines expectations, not exact GitHub settings.

## AGENTS.md Responsibilities

`AGENTS.md` should stay thin and repo-specific. It should define:

- repo-local execution rules
- the canonical validation entrypoint, typically `make check`
- what the canonical validation entrypoint includes
- justified exclusions from local validation
- CI-only, advisory, smoke, chaos, or release-only checks that are not part of
  the local blocking path, including whether they block merge or release
- branch or commit conventions that are specific to the repository
- repo-specific constraints, boundaries, or file placement rules

Reusable workflow rules belong in the playbook, not duplicated into each repository's `AGENTS.md`.

## Repository Categories

Most repositories fit one or more broad surfaces: docs or workflow guidance,
implementation code, API or provider-facing contracts, or a mix of those
surfaces. Apply the shared workflow baseline to each repository, then let
repo-local `AGENTS.md` describe only the local execution details that make that
repository different.

Org infrastructure repositories are special-purpose repositories that hold
organization-level platform material. Examples include GitHub `.github`
repositories for org profile content, community health files, templates,
metadata, or GitHub-supported defaults.

Org infrastructure repositories still follow the shared workflow rules where
they apply: one repo, one branch, one pull request; current `origin/main` as the
base; purpose-based branch names; small scoped diffs; human-readable review
summaries; no unrelated cleanup; and public artifact path hygiene.

Normal project-repository expectations may not apply until the repository grows:
`make check`, tests, package, build, release, or implementation-specific file
placement rules may be absent. Do not add a Makefile, CI, package scaffold, or
release workflow only to satisfy expectations that the repository does not yet
need.

When an org infrastructure repository has no documented canonical validation
command, validation may be inspection-based. Repo-local `AGENTS.md` should say
what to inspect, such as Markdown rendering, links, repository scope, and
public-safe content. If the repository later documents a canonical command, use
that command as the local validation path instead.

Org infrastructure repositories should not own project-specific docs,
implementation code, or reusable workflow policy for other repositories.
Reusable workflow guidance belongs in this playbook; project-specific rules
belong in the affected project repository.

## Validation

- `make check` is the canonical validation entrypoint when the repository provides one.
- When the canonical entrypoint exists and can run locally, run it before
  opening or updating a pull request; do not treat CI as a replacement for
  available local validation.
- Use repository Makefile targets for validation. Do not invoke underlying tools directly when a Makefile target exists; tools such as `pytest`, `ruff`, `mypy`, `markdownlint`, or `npx` are implementation details of the repo validation contract.
- Do not introduce or rely on alternate local validation tools unless they are
  explicitly part of the repository-defined workflow.
- If a local tool required by the canonical command is unavailable, report the
  limitation, do not substitute another tool, and rely on CI for enforcement of
  checks that cannot be run locally.
- CI-only checks are acceptable only when the repository does not expose a local
  canonical path for them or the local canonical path cannot run in the current
  environment.
- CI is the enforcement layer.
- Local validation should match CI behavior as closely as practical.

### Check Taxonomy And Gates

Use one clear role for each check:

- Canonical local validation is the repo-owned local command, typically
  `make check`. When it exists and can run locally, it blocks local readiness
  and PR completion until it passes.
- CI-only checks run remotely because they have no practical local canonical
  path, require hosted infrastructure, depend on credentials, or are too slow or
  disruptive for normal local work. They block merge only when branch protection
  or repo-local guidance explicitly requires them.
- Advisory checks surface risk or missing evidence. They do not block local
  readiness, merge, or release unless the repository deliberately promotes them
  into a documented required check.
- Smoke checks are narrow confidence checks. Their gate depends on placement:
  inside `make check` they block local readiness, as required CI they block
  merge, and otherwise they remain advisory.
- Chaos checks exercise resilience, stress, failure modes, or long-running
  scenarios. Default them to advisory, scheduled, or release-only unless the
  repository explicitly documents a stricter merge or release gate.
- Release-only checks run for release preparation or publish decisions. They
  block release when documented, but they do not block ordinary PR readiness or
  merge unless repo-local guidance says so.

Do not create hidden validation gates. If a check is expected to block local
readiness, merge, or release, document the check name, when it runs, what it
blocks, and what to report when it is unavailable. Otherwise report the result
as informational or advisory evidence, not as an unstated requirement.

### Minimum `make check` Coverage By Repo Type

`make check` should be a single repo-local contract, not a mandate to use the
same tools everywhere. Its minimum coverage depends on the repository's
surface:

- Docs and workflow repositories should check Markdown or structured docs,
  links or generated docs when the repo maintains them locally, and any scripts
  or tests that enforce reusable workflow behavior.
- Code repositories should check the code paths the repository ships or
  supports through the repo's normal test, lint, type, build, or equivalent
  local quality gates.
- API or provider-facing repositories should include the code-repo baseline and
  local checks for provider-facing contracts, generated clients or schemas, and
  public API behavior claims that the repository can verify without live
  credentials or external mutable state.
- Mixed repositories should include the applicable local checks for each
  changed surface, with `AGENTS.md` documenting which surfaces are covered by
  `make check`.

Repo-local `AGENTS.md` should document what `make check` includes, any
justified exclusions, and any CI-only or advisory checks such as live provider
integration, credentialed workflows, slow release checks, or source-evidence
scans that are intentionally outside the local blocking path. Those deviations
should explain why the check is excluded locally without weakening `make check`
as the canonical local validation entrypoint.

## Notes

- Repositories can add stricter rules, but they should start from a small default baseline.
- Keep this baseline easy to apply and easy to explain.
- Use more specific playbook docs only when the repository needs guidance beyond these primitives.
