# Source-First Retrieval

## Purpose

For repository/software work, detect source triggers, retrieve authoritative
state, then interpret intent using conversational continuity. General chat,
brainstorming, and conceptual discussion need no live retrieval unless they
depend on current repository, PR, issue, ref, validation, runtime, provider, or
external API state.

## Scope

This governs observable repository workflow, not platform internals.

## Authority Selection

Before ordering evidence, apply the core model's
[question-typed authority](core-model.md#authority-follows-the-question) and
[Evidence Classification Invariant](core-model.md#evidence-classification-invariant).
Identify each fact's owner; the hierarchy below ranks evidence only within
that scope. Retrieve separate planning, repository, runtime, and historical
owners when a question crosses boundaries. This document owns repository
retrieval triggers, ordering, gates, and recovery.

## Evidence Hierarchy

Prefer evidence in this order when repository state is available:

1. Live connector or tool inspection of the referenced artifact.
2. Direct repository state from the inspected worktree or remote ref.
3. Validation output executed in the current session.
4. Raw logs or artifacts.
5. User summaries.
6. Prior-thread summaries.
7. Agent-generated summaries, completion reports, or status claims.

Summaries and reports from users, prior tasks, or agents are navigation, not
evidence. When the underlying artifact is inspectable, verify it before review,
approval, critique, validation, merge/readiness/completion advice, or
implementation judgment.

For direct review of GitHub state, inspect the artifact through the available
connector or source-of-truth tool first. Before claiming unavailable access,
apply [runtime capability verification](start-here.md#connector-availability-is-runtime-evidence).
If access is verified unavailable, disclose that before any summary-based
analysis; never imply inspection occurred.

Reasoning traces, telemetry, and self-reports are supplementary. Verified source
state and observed actions/outcomes control when they conflict.

### Failed-thread diagnostic evidence

An affected thread may describe an observable workflow-failure seam after
current sources are retrieved, but its account may be contaminated or post-hoc.
Treat it only as supplementary diagnostic or counterfactual evidence, never as
authoritative causation, acceptance, approval, or execution authority.

For behavior meant to generalize across histories, combine such evidence where
useful with a faithful fail-before/pass-after regression under
[`Regression Fixture Fidelity`](engineering-baseline.md#regression-fixture-fidelity)
and behavioral acceptance from a fresh or purged thread using ordinary task
phrasing. The regression proves only its path; disagreement among surfaces is
evidence to investigate, not grounds to discard one by default. Fresh or purged
evidence is the stronger signal of behavior across histories.

## Minimum-Sufficient Retrieval

Retrieve only the authoritative evidence needed for the current claim or
decision. Name the claim, each required fact and owner, and the evidence
boundary; stop when that boundary is satisfied. Mandatory triggers and
essential unknowns still control: mark a materially necessary unverified fact
partial or blocked, and omit nonessential facts instead of inventorying them.

For ordinary repository work, use the narrowest normal surface that owns or
directly exposes the fact: repository-native `git`, high-level provider CLI or
connected GitHub reads for hosted facts, and repository-native validation or
workflow commands for the facts they own.

A missing convenience command does not justify `gh api`, an equivalent raw
provider API, or provider-wide inventory. Use a lower-level provider read only
when a concrete fact is materially necessary and normal surfaces cannot
establish it; first state the missing fact, why it matters, and why first-class
surfaces are insufficient. Otherwise omit the fact or report the capability
gap. A specialized evidence audit or investigation of provider API behavior
may use its explicitly constrained low-level surface; that is not ordinary
fallback precedent.

For overlap or collision risk, current `main`, relevant pull requests, target
files, and specifically identified refs normally suffice. Inventory broader
state only when that inventory is materially necessary to the decision.

## Triggers

Classify triggers before using prior conversation, summaries, memory, or pasted
descriptions to reason about repository state.

Mandatory source-first triggers require authoritative retrieval before
stateful reasoning or recommendations:

- a referenced GitHub pull request or issue, including requests to review,
  continue, implement, assess readiness, or identify remaining work;
- a repository identifier, URL, or local path; a branch, ref, tag, commit,
  comparison, or release ref; or repository-aware advice dependent on current
  state;
- current pull-request, issue, branch, workflow, check, validation, merge,
  sequencing, changed-file, implementation-quality, scope, or closure claims;
  and
- claims or changes dependent on current external-provider, public-API, SDK,
  CLI, package, or hosted-platform behavior.

For repository workflows, select the applicable interaction mode from
[`repo-readiness.md`](repo-readiness.md#interaction-mode-preflight).

Optional triggers may guide retrieval when the next action depends on current
state, but they do not require source inspection for purely conversational
answers:

- summaries, reports, copied diffs, screenshots, or release notes without a
  live artifact identifier;
- earlier conversation, prior work, remembered plans, previous synthesis, or
  broad repository names without a state-dependent action; and
- conceptual workflow, review, or tradeoff questions, which still activate
  [`start-here.md`](start-here.md#global-bootstrap-persistence) when about the
  Playbook.

Ambiguous cases must be resolved before stateful conclusions. If "continue",
"the branch", "the PR", or similar wording points to a clear source, inspect
that source. If the target is unclear, ask a narrow clarifying question or
report the missing identifier. Do not fill the gap with conversational
inference.

A bounded lookup may characterize or eliminate a candidate when that limited
fact is needed, but its result is evidence only about that candidate or
namespace. A returned object, including a successful hit, does not by itself
resolve the ambiguity that made the lookup necessary. Before making a stateful
conclusion that treats a candidate as the user's referent, establish a
selection basis independent of that lookup; otherwise ask narrowly or keep the
result candidate-only.

## Ordering

1. Detect mandatory, optional, or ambiguous triggers in the request, visible
   context, and supplied artifacts.
2. Resolve ambiguity and directly inspect every mandatory source.
3. Verify live state and report verified findings and remaining unknowns.
4. Only then interpret, prioritize, recommend, or explain using continuity for
   intent, constraints, tone, decisions, and output shape.

Do not make state-dependent evaluations or recommendations before required
live inspection.

### Named Repository Resolution From A Failed Local Candidate

When a task explicitly names a repository and required source, a non-root local
candidate, including a parent or container, is evidence only about that
candidate: it neither resolves the named repository nor makes its source
unavailable.

Before escalating, use only the narrowest normal supported route already
exposed by the current execution surface to resolve that exact repository. Do
not broaden this into filesystem wandering or workspace-wide repository
enumeration, cloning, replacement checkouts or worktrees, branch creation,
remote rewiring, or hosted facts in place of a required local checkout.

Perform this bounded recovery before asking the human to locate the repository.
If the routes cannot establish the source, stop with the exact missing source
and attempted or unavailable routes.

### Existing Checkout Freshness And Bounded Recovery

Reconcile an existing repository or worktree with the current hosted default
branch before work. Stale local state is a recoverable cached-state condition;
a clean tree or cached remote-tracking ref does not prove current hosted state.

A required named checkout or supplied worktree is part of the execution
contract. Without separate authority, recovery does not permit cloning,
replacement checkouts, worktrees, or branches, checkout substitution, remote
rewiring, or hosted substitution. Preserve required locality; if permitted
non-destructive recovery cannot make it usable, stop with the blocker.

Use this bounded recovery sequence:

1. Before local Git or `gh` contacts GitHub, verify active authentication with
   `gh auth status`. This does not make any ref fresh. If authentication cannot
   be verified, report it and use another permitted source or block the affected
   claims.
2. Identify the current hosted default branch; inspect the checked-out tree and
   `HEAD`, current branch, configured remotes, upstream, and divergence. Keep
   working-tree and cached-ref observations separate from hosted claims.
3. When repo-local policy permits, use the smallest non-destructive
   synchronization that restores a useful inspection surface: fetch current
   refs, prune stale remote-tracking refs, fast-forward an eligible clean local
   branch, or use a repository-documented equivalent. Reinspect the tree,
   branch, upstream, and divergence afterward.
4. Follow the direct-command rule in
   [`repo-readiness.md`](repo-readiness.md#command-form-and-intent-visibility)
   and the matching adapter; wrapper interference does not require abandoning
   direct `git` or `gh` recovery.

Unless separately authorized, do not discard uncommitted changes or local
commits, reset or rewrite history, switch branches, overwrite files, or alter
remote configuration. If safe synchronization fails, preserve the checkout and
report the blocker. Use a freshly fetched ref or current hosted state only for
claims it supports; never present a cached remote-tracking ref as current
without a successful fetch in the current attempt.

When material, distinguish:

- **Checked-out working tree:** inspected local files and `HEAD`.
- **Cached remote-tracking ref:** last locally recorded remote state before a
  successful fetch in the current attempt.
- **Freshly fetched remote ref:** remote state and commit identity recorded by
  that fetch.
- **Current hosted GitHub state:** directly inspected hosted state, including
  default branch, pull requests, issues, checks, and reviews.

Refresh restores an inspection surface only; it does not authorize edits,
implementation, history or branch changes, or broader mutation. Repo-local
policy may narrow or replace these defaults.

## Verification Gate

Use this gate whenever a mandatory trigger is present:

- Trigger: name the artifact or request that activated retrieval.
- Source: name the authoritative source used for current state.
- Checks: list the state checks required by the task.
- Result: mark the gate `verified`, `partial`, or `blocked`.
- Unknowns: state anything required for the task that remains unverified.

If direct verification did not happen, say exactly:
`unknown → referenced repo state was not verified`.

Acceptable authoritative sources depend on the claim:

- repository files, local `git`, and checked-out refs for the inspected local
  worktree only;
- GitHub PRs, issues, reviews, checks, mergeability, and branch metadata for
  current hosted state;
- CI and validation output for the checks they ran; and
- official provider documentation, schemas, SDK or CLI docs, changelogs, or
  release notes for external public API behavior.

For pull requests and issues, do not infer implementation quality, scope, risk,
merge readiness, or correctness from titles, summaries, commit messages,
reported check status, or conversational descriptions. Inspect changed files,
validation or check state, scope boundaries, and overlap or conflict risk
directly.

If the required source is unavailable, blocked, or declined, stop and report
the blocker; do not conclude readiness, mergeability, approval, closure, or
implementation completeness from secondhand context. For partial verification,
separate verified facts from unknowns, avoid conclusions dependent on missing
state, and identify the retrieval needed to complete the gate.

When local and hosted state disagree, state which source supports each fact and
which controls the decision; local `git` controls only the inspected checkout,
while hosted PR and issue state usually controls hosted readiness. When source
status could affect the next action, say whether the claim is directly verified,
inferred, or unknown. Preserve unknowns without adding confidence scores,
fixed tiers, templates, audits, or governance process.

## Recovery

Recover when source-first ordering was missed, continuity or inferred state
outran verification, authoritative state conflicts with context, a human flags
missing inspection, or a selected transport fails before the required fact is
verified.

Keep three states distinct: the selected transport failed; the required fact
remains unverified; and the authoritative source is unavailable because no
applicable permitted route can establish the fact without weakening evidence,
authority, authentication, or safety.

When retrieval remains available:

1. Halt continuity reasoning and identify each unresolved mandatory trigger and
   exact missing fact.
2. Select the narrowest normal surface for the fact's owner. Record a failed
   transport as mechanism or capability evidence, not source unavailability.
3. Use another permitted surface only when it preserves the required evidence
   semantics, and stop when the exact claim is sufficiently verified.
4. Discard, correct, or mark prior assumptions unverified; resume from verified
   state and stated unknowns.

Fail closed when the fact remains materially unverified after applicable routes
are unavailable, insufficient, or blocked. Report the missing fact and those
routes. Hosted evidence cannot establish local checkout freshness, and fetched
Git evidence cannot establish hosted-only metadata.

Do not prompt, re-prompt, escalate, mutate authentication, or enter an
authentication loop because a speculative lower-level transport failed. One
surface's authentication failure does not establish that all qualified routes
are unauthenticated; preserve any owning-workflow authentication preflight.
Successful first-class retrieval needs no raw-API confirmation, except when
provider API behavior is the subject or a specialized workflow requires that
surface.

Acknowledgment or explanation alone is not recovery. Perform available missing
retrieval, then report only remaining blockers, uncertainty, or corrections.
