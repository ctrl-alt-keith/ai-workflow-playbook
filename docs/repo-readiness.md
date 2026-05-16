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

## Governance Operating Model

Prefer meaningful protections over inherited process friction. Governance
defaults should reflect the repository's actual operating model and risk
surface, not process assumptions copied from larger-team workflows.

Adopt large-team or enterprise-style requirements only when they materially
improve safety, integrity, recoverability, auditability, or operational clarity.
When evaluating governance, CI, release, or review process, distinguish:

- integrity and safety controls, such as protected source history, required
  validation before merge, explicit visibility policy, rollback paths, release
  correctness, secret exposure safeguards, and durable audit evidence
- coordination and process controls, such as approval counts, strict
  up-to-date gates, broad CI version matrices, duplicated repo-local policy,
  handoff gates, or sequencing rules whose primary value is coordinating
  multiple people

Default toward preserving integrity and safety controls while minimizing
coordination overhead when the operating model does not need it. Explicit
policy still matters: document the intended posture, the rationale for any
exception, and which layer owns the rule.

### Solo-Operator Governance Profile

A solo-operated repository can be strongly governed without copying
coordination-heavy process. Match governance to the actual operational risk and
team size; do not frame a solo profile as a weaker safety posture.

For solo-operated repositories, the following protections remain valuable by
default:

- pull request workflow for reviewability, change packaging, and durable
  discussion history
- required checks before merge, with one canonical local validation path where
  practical
- squash-only merges to keep `main` reviewable and easy to reason about
- explicit repository visibility policy
- force-push and default-branch deletion protection
- centralized governance policy where practical, with repo-local governance
  only for local rationale, transition notes, or explicit exceptions
- recoverability and auditability for branch cleanup, hosted settings, release
  decisions, and other operational changes

The following can also be intentional in a solo-operated repository when
documented:

- zero required approving reviews
- owner or administrator self-merge after required checks pass
- omitting strict branch up-to-date checks when they create rebase churn
  without materially improving safety
- using a focused runtime or CI matrix when multi-version coverage does not
  justify the maintenance cost
- lightweight governance declarations instead of duplicated coordination
  process in every repository

This profile does not relax caution for security-sensitive changes, destructive
automation, data-loss risks, irreversible migrations, credentialed workflows,
public release behavior, or high-blast-radius operational changes. It preserves
explicit policy and auditability while avoiding operational drag that exists
only to coordinate a larger team.

### Automation And Orchestration

When proposing or implementing governance changes, automation and Codex workers
should classify each proposed requirement as either an integrity/safety control
or coordination/process overhead. Do not silently import enterprise defaults.

Before widening governance or process, compare repo-family precedent and the
documented operating model. Prefer the narrowest rule that preserves safety,
integrity, recoverability, auditability, and operational clarity without
creating unnecessary drag for solo-maintainer repositories.

When governance behavior already has an authoritative tool, module, workflow,
or CLI, invoke that executable source directly. Orchestration layers may
enumerate targets, invoke canonical commands, collect outputs, and summarize
or report results, but they should not partially reimplement the canonical
logic, fork parser behavior, duplicate validation semantics, or create a
competing audit engine.

### Enforcement Relationship

The playbook defines the philosophy, operating model, and reusable workflow
expectations. `ai-workflow-enforcement` defines centralized governance policy,
read-only audit implementation, and advisory drift reporting.

Repo-local governance should exist only when the repository needs local
rationale, a documented transition, or an explicit exception from central
policy. Do not duplicate centralized governance prose into repo-local files only
to restate inherited policy.

## Interaction Mode Preflight

Before acting on any repository or software task, determine the interaction
mode. Do this before editing files, creating branches, committing, opening pull
requests, or running implementation-oriented workflows.

This preflight applies the role framing from
[`core-model.md`](core-model.md#roles): humans own intent, standards, and
completion decisions; AI should match its execution behavior to the mode the
human has actually delegated.

Use one of these modes:

- Implementation mode: directly make repo changes, validate them, commit them,
  push the branch, and open or update a pull request from a dedicated
  repo-local worktree when repo guidance calls for PR delivery.
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

Examples:

- Implementation mode: "Implement issue #42, run validation, commit it, and
  open the PR" authorizes repo mutation and PR delivery.
- Review/audit mode: "Review PR #42 for merge readiness" means inspect the PR
  surface and report findings without changing the branch or PR.
- Orchestration/prompt-authoring mode: "Write a handoff for another agent to
  fix issue #42" means gather enough context to produce the complete prompt,
  not to make the fix.
- Ambiguous task handling: "Can we fix this?" stays in review/audit or
  orchestration/prompt-authoring mode until the human explicitly asks for
  implementation.

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

When the requested artifact is a prompt, spec, plan, implementation brief,
review brief, automation prompt, or agent instruction, provide the full
drop-in version by default. This remains true when the human asks how to "add",
"incorporate", "fold in", or otherwise update something in an existing
artifact. Do not assume the human will manually stitch prior context,
conversation history, or earlier snippets into the final artifact. Use a delta,
patch, diff, targeted edit, or terse "change X to Y" response only when the
human explicitly asks for that form.

Keep this policy in the shared playbook. Repo-local `AGENTS.md` files should
reference or rely on it rather than duplicate it, except where a repository
truly requires different behavior.

## Single-Operator Review Posture

For repository ecosystems primarily operated by one maintainer with rapid
iteration, clear rollback paths, and low coordination overhead, reviews should
bias toward actionable experimentation and cohesive improvement.

Prefer cohesive, locally testable changes over artificial PR splitting when
the blast radius is understood and rollback is straightforward. Reviewers
should surface concrete implementation opportunities early, recommend
practical follow-on improvements freely, and avoid deferring useful cleanup
only because it is adjacent to the requested change.

This posture does not weaken rigor for security-sensitive changes, data-loss
risks, irreversible migrations, compatibility hazards, destructive automation,
release behavior, or high-blast-radius operational changes. In those cases,
reviewers should apply the normal conservative review posture.

When using this posture, distinguish blocking issues from non-blocking
experiments, risks, and follow-on opportunities. The goal is faster
operational learning without hiding real safety or maintainability concerns.

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
- planning-ticket status should not delay a completed implementation PR unless
  it reflects real sequencing, overlap, or completion risk

Before opening or updating a pull request, fetch current `origin/main` and
verify whether the branch is mergeable against current `main`. Update or rebase
only for conflicts, overlapping upstream changes, repo policy, or explicit
human request. Keep any conflict resolution within the original task scope,
avoid unrelated cleanup, rerun the canonical validation entrypoint after the
update, then push.

In coordinated pull request batches, later pull requests can become behind
`main` after earlier pull requests merge even when there are no file conflicts.
When strict branch protection requires branches to be current, repeat this loop
for each queued pull request after its dependency is merged:

- fetch current `origin/main`
- rebase the next branch onto updated `origin/main`
- rerun the canonical validation entrypoint
- push with `--force-with-lease`
- wait for required checks to pass
- re-check readiness before continuing the merge sequence

Run independent capability lanes before semantic reconciliation or
consolidation lanes. Defer consolidation until upstream semantic work has
landed, and use staged merge ordering when lanes share contract surfaces,
generated artifacts, public API or client behavior, or sequencing dependencies.

Open a pull request as draft when any of the following are true:

- work is incomplete
- the change is part of a coordinated batch with sequencing risk
- reconciliation with other pending work is likely
- the branch is intentionally staged for later promotion

Docs-only changes should default to ready for review when canonical validation
passes and the diff is isolated.

Implementation agents may open or update ready-for-review pull requests by
default when repository guidance calls for PR delivery. Ready-for-review status
does not authorize merge. Do not merge pull requests or enable auto-merge
unless the human explicitly instructs that action for the specific pull request
or workflow step. Sequential workflows that depend on merges must pause for
explicit human confirmation before merge and before continuing to downstream
steps.

When working in a multi-repo workspace, treat each repository as an independent
unit of change. Even if multiple repositories are visible, commits, branches,
worktrees, and PRs must be created and managed per repository. Do not create
cross-repo commits or PRs.

Before opening a PR, ensure that all staged changes belong to a single
repository. If changes span multiple repositories, split them into separate
branches, worktrees, and PRs, one per repository.

Every implementation change must use a dedicated repo-local git worktree: one
repository, one branch, one worktree, and one PR per change. The only
exceptions are read-only inspection or explicit human instruction not to modify
files.

## Workspace Boundary Discovery

When work spans multiple repositories, determine the active managed workspace
set from authoritative repository inventory sources before broad scans or
updates begin.

Prefer organization-level repository enumeration and explicit inventory owned by
the consuming workflow, such as enforcement scanner configs, automation
allowlists, or caller-supplied manifests. Reconcile those sources before
treating local checkouts as part of the active workspace scope.

Do not treat raw local filesystem layout as authoritative workspace scope.
Local checkout trees may contain stale repositories, archived repositories,
detached worktrees, experiments, incomplete clones, temporary operational
state, or local-only scratch repositories.

Reconcile local workspace state against the owning inventory source before
cross-repo audits, `AGENTS.md` alignment, enforcement scans, or broad workflow
updates.

For repository additions, removals, role changes, or governance checks, use the
repo-awareness and onboarding refresh procedure in
[`repo-awareness-onboarding-refresh.md`](repo-awareness-onboarding-refresh.md).
That procedure keeps inventory refresh separate from onboarding and org-admin
governance follow-up.

## Repo-Family Policy Alignment

Local repository metadata is not always the full policy. Before changing
policy-sensitive surfaces, check repo-local guidance and nearby sibling
repositories for an established ecosystem direction.

This applies when a change would widen or reinterpret:

- Python or runtime support policy
- CI version matrices
- packaging, release, publication, install, or distribution posture
- branch protection, governance, or review settings
- provider-live validation policy
- compatibility shims, legacy dependencies, or support floors

For governance and process changes, apply the governance operating model above:
identify which parts are safety or integrity protections and which parts are
coordination overhead before changing defaults.

Prefer intentional consistency across a repo family unless the human or
repo-local guidance explicitly asks for divergence. Do not silently widen
compatibility, support, release, or governance scope only because local
metadata permits it.

If local metadata points one way and sibling precedent points another, stop and
report the mismatch before implementing the policy-sensitive change. Example:
a package metadata floor such as `>=3.10` may describe installability, while a
repo family may be intentionally using a current-runtime-only CI and support
posture.

## Repo-Local Workflow State

For implementation changes, run commands from inside the target repository's
dedicated worktree. Keep temporary workflow artifacts scoped to that repository
whenever practical.
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

Run commands from inside the target repository worktree by default. For
ordinary repository operations, use direct `git ...`, `gh ...`, `make ...`,
`python ...`, repo-local scripts, and tool-specific commands. Before choosing a
wrapper shell, check whether the command has a direct form and use that direct
form when it does. Do not wrap those commands in `zsh`, `bash`, `sh`, shell
aliases, or equivalent wrapper shells only for convenience. In particular,
`zsh -lc`, `bash -lc`, `sh -c`, or equivalent forms are not normal wrappers for
ordinary repo commands.

For standard Git or GitHub CLI work, choose the `git` or `gh` command directly
instead of substituting alternate APIs, helper tools, wrapper scripts, or
connector-specific operations. Use alternate APIs or tools only when the task
explicitly calls for capabilities the CLI cannot provide or when direct CLI
access is unavailable and the fallback is reported clearly.

Preserve that directness at the execution layer too. Prefer native argv-style
execution, such as `["git", "status"]` or `["gh", "pr", "create"]`, when the
environment supports it. If an execution tool defaults to a shell, login shell,
or shell-like command string, explicitly disable that behavior for `git` and
`gh` where supported, using settings such as `shell=false`, `login=false`,
`use_shell=false`, or the platform's equivalent direct-exec option.

This keeps operational intent visible in logs, prompts, review notes, and local
approval surfaces. It also lets permission or approval systems reason about the
specific operation being requested, instead of treating a simple repository
action as a broad shell execution.

Preserve the same directness for canonical tooling. When an authoritative
module, CLI, reusable workflow, or Makefile target owns executable behavior,
call it instead of building a wrapper, aggregation script, or orchestration
layer that duplicates part of its logic. Helper artifacts are acceptable when
they are orchestration-only or report-only: they may cache raw outputs, collate
command results, or format summaries, but should not reinterpret core
semantics independently.

Before executing any shell-wrapped command, perform a command-form preflight:

- determine whether the operation genuinely needs shell semantics, such as
  pipes, redirects, glob expansion, command chaining, shell builtins, inline
  environment assignment, compound shell conditionals, or other shell-only
  composition
- if shell semantics are not required, rewrite the command into direct argv
  form before execution
- if shell semantics are required, keep the wrapped command narrow enough that
  the operational intent remains inspectable

Examples:

- incorrect: `zsh -lc 'git status'`
- correct: `git status`
- preferred native argv form where supported: `["git", "status"]`
- incorrect: `bash -lc 'make check'`
- correct: `make check`
- incorrect: `sh -c 'gh pr view 145'`
- correct: `gh pr view 145`
- preferred native argv form where supported: `["gh", "pr", "view", "145"]`

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

Reusable workflow rules belong in the playbook, not duplicated into each
repository's `AGENTS.md`. Canonical playbook updates and `AGENTS.md` edits are
separate work types; do not infer repo-local guidance rollout from a playbook
docs change. Reviews and delivery notes for workflow changes should state
whether the change is canonical playbook guidance only or an explicitly
authorized `AGENTS.md` update/enforcement task.

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
they apply, including PR readiness, implementation isolation, scoped diffs,
human-readable review summaries, no unrelated cleanup, and public artifact path
hygiene.

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

## Contract Groundwork

For contract-bearing repositories, prefer inventory, compatibility mapping, and
documented boundaries before generating or enforcing schemas, fixtures, or other
contract artifacts. Avoid freezing an unstable contract from a single golden
example. Generated artifacts should follow stabilized semantics and have
deterministic validation.

Small synchronization tests can keep documentation aligned with emitted or
current behavior. Use them as lightweight drift guards, not as broad gates that
freeze entire implementations, unstable contracts, or documentation workflows.

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

### Solo-Operator Iteration Economics

For solo-operated workflows, choose the validation loop that answers the
current question fastest without hiding real risk.

Early integration-heavy validation is appropriate when the work is still
proving workflow semantics, validating governance or trust boundaries, or
establishing confidence in a new pipeline. Full environment checks,
cross-system exercises, live smoke tests, and review environments are useful
while the question is whether the workflow behaves correctly end to end.

Once failures are mostly deterministic parsing, integration, normalization,
state-transition, deployment, or automation behavior, move the primary
iteration loop into fast local regression fixtures. Use representative
real-world examples as a regression corpus where useful, keep those fixtures
deterministic, and reserve full-environment validation for milestone checks,
boundary checks, or confidence revalidation after meaningful changes.

Review, replay, staging, or live-like environments validate usefulness and
operational fit; implementation repositories absorb noisy iteration. Use those
broader environments for milestone validation, governance or trust-boundary
review, promotion decisions, and durable provenance. Use the implementation
repository for deterministic reproduction, fixture iteration, bounded
corrections, and observability or debugging loops.

Bounded hardening may require multiple tightly coupled passes before opening a
pull request. Keep those passes in one PR when each pass directly enables or
validates the next: detect an observed issue or failure mode, preserve evidence
through tests, fixtures, logs, or metadata, apply a bounded correction, then
validate non-regression and live behavior where appropriate.

This pattern applies across implementation domains: parsers and extractors,
API integrations, schema migrations, deployment workflows, infrastructure
automation, CI/CD hardening, observability and debugging loops,
synchronization or reconciliation systems, and state repair or recovery logic.

One PR is appropriate when the phases share one goal, one affected behavior or
boundary, one validation story, and one rollback unit. Split the work when
phases have independent goals, different risk profiles, unrelated files, or
different validation or rollback boundaries.

In solo-operator workflows, prefer completing the coherent task before opening
the PR when it is safe to do so. Avoid stopping after a diagnostic-only partial
implementation when the safe bounded correction is part of the same task and
can be validated locally.

Pause and confirm before external discovery or crawling, destructive behavior,
irreversible state changes, ambiguous automation decisions,
security/trust-boundary expansion, or high-blast-radius architectural change.
Multi-pass hardening is not permission for grab-bag PRs, unrelated cleanup,
repo-hopping, or hidden scope expansion.

Intermediate passes should leave evidence through fixtures or tests where
useful. The final PR should include the relevant docs, tests, live checks, and
non-regression evidence, and should explain the phases and why they form one
cohesive task.

For ingestion, extraction, ETL, scraping, OCR, export/import, and normalization
systems, the source-shape hardening lifecycle in
[`knowledge-ingestion-patterns.md`](knowledge-ingestion-patterns.md#source-shape-hardening-lifecycle)
is one application of this broader rule. New source types should become
diagnostic, review-ready, and promotion-capable inside the implementation
repository before they become routine replay inputs.

If broader validation repeatedly produces unchanged review outcomes, stop
accumulating low-yield evidence PRs. Move the failing behavior into the
implementation repository, make it a deterministic fixture or regression case
there, and iterate until the output crosses the relevant reviewability,
operability, or safety threshold. Return to broader validation for milestone
verification, promotion review, live confidence checks, or retained-content
decisions.

Warning signs that broad validation has become a rabbit hole:

- repeated full-environment loops with little workflow learning
- high-latency validation cycles that slow each small correction
- deterministic bugs discovered only after broad integration runs
- review, replay, or live-check artifacts quietly becoming the de facto
  regression suite
- evidence PRs adding provenance without changing the review, release,
  retention, or promotion decision

The preferred steady state is fast local fixtures for day-to-day correction, a
representative real-world regression corpus where useful, explicit milestone
checkpoints, and occasional broad revalidation to confirm the local loop still
reflects end-to-end behavior.

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
