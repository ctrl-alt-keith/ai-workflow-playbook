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

When conversational state materially participates in a workflow failure, the
affected thread can be a useful diagnostic witness. A focused diagnostic may
ask it to describe the observable decision seam in concrete workflow terms or,
after current sources have been retrieved, whether a candidate correction
would have changed the earlier decision and where. Its explanation remains
contaminated by the failed context and may be post-hoc. Treat it as
supplementary diagnostic or
counterfactual-review evidence, never as authoritative internal causation,
acceptance, approval, or execution authority.

For behavior intended to generalize across conversational histories, compare
that evidence where useful with a deterministic fail-before/pass-after
regression at the meaningful semantic or control seam under
[`Regression Fixture Fidelity`](engineering-baseline.md#regression-fixture-fidelity),
and with behavioral acceptance from a genuinely fresh or purged thread using
ordinary task phrasing. The regression establishes only the path it exercises;
the fresh thread is the stronger signal that the behavior survives a different
history. Disagreement can reveal contamination, execution-path divergence,
incomplete semantic repair, or unmodeled state rather than invalidating one
surface by default.

A richer shared workflow vocabulary can make a thread's diagnostic account
more precise by naming activation, authority, interaction mode, handoff,
source-ownership, transport, evidence, and completion seams. That vocabulary
improves diagnostic resolution; it does not increase the authority of model
self-report or require disclosure of private reasoning.

## Minimum-Sufficient Retrieval

Source-first retrieval means obtaining the minimum sufficient authoritative
evidence needed for the current claim or decision. Name that claim or decision,
identify the source that owns each required fact, and set the evidence boundary
before retrieval. Inspect only the state needed to satisfy that boundary, and
stop when the claim or decision is supported. More provider objects do not make
the evidence more authoritative.

This boundary does not weaken a mandatory trigger or permit an essential
unknown to be ignored. If a materially necessary fact cannot be verified, mark
the gate partial or blocked. If a fact is not necessary to the current claim or
decision, omit it instead of expanding retrieval into a speculative inventory.

For ordinary repository inspection and delivery, prefer the narrowest normal
supported surface that owns or directly exposes the required fact:

- repository-native `git` commands for repository, ref, and worktree facts;
- high-level provider CLI commands for supported hosted facts;
- connected GitHub reads for hosted state they expose; and
- repository-native validation or workflow commands for facts they own.

The absence of a high-level convenience command does not by itself justify
`gh api`, an equivalent raw provider API, or a provider-wide inventory. In
ordinary repository inspection, use a lower-level provider read only when a
concrete fact is materially necessary for the current claim or decision and
normal supported surfaces cannot establish it. Before that escalation, state
the exact missing fact, why it matters, and why the first-class surfaces are
insufficient. When those conditions are not met, omit the fact or report the
capability gap.

Specialized evidence-surface audits may intentionally use a separately
constrained low-level read path when their required evidence classes are not
available through ordinary surfaces. Investigations where provider API behavior
is itself the subject may also inspect that API directly. Those workflows name
the low-level surface and its safeguards as part of their task; they are not
ordinary-repository fallback precedent.

For overlap or collision risk, current `main`, relevant pull requests, target
files, and specifically identified refs are normally sufficient. Do not require
an inventory of every active branch, ref, workflow, or provider object unless
the inventory itself is materially necessary to the decision.

## Triggers

Classify triggers before using prior conversation, summaries, memory, or pasted
descriptions to reason about repository state.

Mandatory source-first triggers require authoritative retrieval before
stateful reasoning or recommendations:

- GitHub pull request URLs, pull request numbers, or requests such as "review
  this PR", "review directly", "take a look", "check this PR", "continue this
  PR", or "is this ready?"
- GitHub issue URLs, issue numbers, or requests such as "continue from this
  issue", "implement this issue", or "what is left on this issue?"
- repository identifiers, repository URLs, or local repository paths
- repo-aware advisory or evaluation requests where a repository is explicitly
  named and the answer depends on that repository's actual state
- branch names, refs, tags, commit SHAs, comparison ranges, or release refs
- requests to assess mergeability, CI status, review state, changed files,
  issue closure, validation status, or current implementation scope
- requests involving PRs, issues, branches, workflows, checks, validation
  state, merge sequencing, or implementation quality; treat these as mandatory
  source-first triggers and select the appropriate repo-readiness interaction
  mode rather than defaulting to conversational analysis
- claims or requested changes that depend on current external provider,
  public API, SDK, CLI, package, or hosted-platform behavior

Optional triggers may guide retrieval when the next action depends on current
state, but they do not require source inspection for purely conversational
answers:

- pasted summaries, completion reports, copied diffs, screenshots, or release
  notes without a live artifact identifier
- references to earlier conversation, prior work, a remembered plan, previous
  operational synthesis, or broad repository names without a state-dependent
  action
- conceptual questions about workflow patterns, review posture, or tradeoffs

Ambiguous cases must be resolved before stateful conclusions. If "continue",
"the branch", "the PR", or similar wording points to a clear source, inspect
that source. If the target is unclear, ask a narrow clarifying question or
report the missing identifier. Do not fill the gap with conversational
inference.

## Ordering

1. Detect mandatory, optional, or ambiguous triggers in the request, visible
   context, and supplied artifacts.
2. Resolve ambiguity and directly inspect every mandatory source.
3. Verify live state and report verified findings and remaining unknowns.
4. Only then interpret, prioritize, recommend, or explain using continuity for
   intent, constraints, tone, decisions, and output shape.

### Existing Checkout Freshness And Bounded Recovery

Before beginning work in an existing local repository or worktree, reconcile
the local checkout with the repository's current GitHub default branch. Treat
stale local repository state as a recoverable cached-state condition, not by
itself as a reason to abandon local inspection. A clean working tree or a
cached remote-tracking ref does not prove that the checkout reflects current
hosted GitHub state.

When a task requires a named existing checkout or supplied worktree, that
locality is part of the execution contract. Inspection, freshness, or recovery
authority does not permit cloning, replacement worktree or branch creation,
checkout substitution, remote rewiring, or hosted substitution unless current
human direction or explicit task posture permits acquisition/substitution.
Preserve the required locality; if permitted non-destructive recovery cannot
make it usable, stop with the blocker. Hosted evidence does not satisfy required
local execution.

Use this bounded recovery sequence before falling back to hosted-only
inspection:

1. Before using local Git or `gh` to contact GitHub, verify the active
   authentication state with `gh auth status`. The authentication check does
   not make any local or remote ref fresh. If active authentication cannot be
   verified, report that limitation and use another permitted source or leave
   the affected claims blocked.
2. Identify the current hosted default branch, then inspect the checked-out
   working tree, current branch, configured remotes, upstream configuration,
   and divergence. Keep observations about the working tree and cached
   remote-tracking refs separate from claims about GitHub.
3. When repo-local policy permits synchronization, select the smallest
   non-destructive action that can restore a useful inspection surface. A
   bounded safe synchronization attempt may fetch current remote refs, prune
   stale remote-tracking refs, fast-forward an eligible clean local branch, or
   use another repository-documented non-destructive synchronization command.
   Reinspect the worktree, branch, upstream, and divergence after the attempt.
4. If repository shell or zsh wrappers interfere with sandbox permissions or
   command execution, direct `git` and `gh` commands without repository shell
   wrappers are permitted for this recovery path. Follow the command-form and
   execution-layer guidance in
   [`repo-readiness.md`](repo-readiness.md#command-form-and-intent-visibility)
   and the matching tool adapter.

This recovery path does not authorize destructive or unrelated mutation merely
to obtain freshness. Unless the explicit task or repo-local policy separately
authorizes the operation, do not:

- discard uncommitted changes or local commits;
- reset a branch or rewrite history;
- switch branches;
- overwrite files to force synchronization; or
- alter remote configuration.

If safe synchronization cannot be completed, preserve the checkout and report
the blocker. Fall back to a freshly fetched remote ref or current hosted GitHub
state only for claims that source can support. A cached remote-tracking ref may
still describe last-known local state, but it must not be presented as current
without a successful fetch in the current recovery attempt.

Keep these evidence surfaces explicit when the distinction matters:

- **Checked-out working tree:** the files and `HEAD` inspected in the local
  worktree.
- **Cached remote-tracking ref:** the last locally recorded remote state before
  a successful fetch in the current recovery attempt.
- **Freshly fetched remote ref:** the remote state and commit identity recorded
  by a successful fetch in the current recovery attempt.
- **Current hosted GitHub state:** state inspected directly from GitHub, which
  may change after a fetch and owns hosted metadata such as the current default
  branch, pull requests, issues, checks, and reviews.

Successfully refreshing a checkout restores an inspection surface only. It
does not independently authorize implementation, file edits, history changes,
branch changes, or broader repository mutation. Repo-local `AGENTS.md` and
other repo-local policy may narrow or replace these shared recovery defaults.

When a material prompt is governed by the versioned semantics in
[`prompt-contracts.md`](prompt-contracts.md), source-first retrieval still
controls selection evidence. A fresh attempt selects exact compatible source
identities once before hydration; replay resolves the recorded source manifest
without rereading current mutable sources. Neither source selection nor a
source-manifest digest grants authority.

When a mandatory trigger is present, verification blocks:

- statements about current PR, issue, branch, commit, CI, mergeability, review,
  release, or validation state
- merge, readiness, approval, closure, or implementation-scope
  recommendations
- claims about which files changed, which comments remain unresolved, or what
  the branch currently contains
- decisions that depend on current external API, SDK, CLI, provider, or hosted
  platform behavior

No evaluative commentary may come before live inspection. Evaluative
commentary includes architecture assessment, correctness claims,
implementation quality judgments, merge guidance, prioritization, risk
analysis, validation confidence, workflow recommendations, and
scope/completeness claims.

Continuity may help interpret intent, constraints, tone, previous decisions,
and desired output shape after retrieval. It must not substitute for direct
repository, GitHub, CI, runtime, or provider evidence.

## Repo-Aware Advisory

For analysis, review, evaluation, architecture, suggestions, or prioritization
about a named repository, inspect enough current source to ground the answer.
Match depth to the question; do not broaden into an unrequested audit.
Conceptual discussion needs retrieval only for state-dependent claims.

If retrieval was missed, retrieve first, then correct, discard, or mark prior
repo-specific advice unverified before explaining the failure.

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

- Repository files, local `git` state, and checked-out refs are authoritative
  for the inspected local worktree only.
- GitHub PRs, issues, review threads, CI, mergeability, and branch metadata are
  authoritative for current remote PR and issue state.
- CI systems and validation command output are authoritative for the checks
  they actually ran.
- Official provider documentation, schemas, SDK docs, CLI docs, changelogs, or
  release notes are authoritative for external public API behavior.

For pull requests and issues, do not infer implementation quality, scope, risk,
merge readiness, or correctness from titles, summaries, commit messages,
reported check status, or conversational descriptions. Inspect changed files,
validation or check state, scope boundaries, and overlap or conflict risk
directly.

If the required source is unavailable, blocked, or access is declined, stop the
stateful workflow and report the blocker. Do not provide readiness,
mergeability, approval, closure, or implementation-completeness conclusions
from secondhand context.

If only part of the source can be verified, return a partial result. Separate
verified facts from unknowns, avoid recommendations that depend on missing
state, and say what retrieval would complete the gate.

If local and remote state disagree, state which source supports each fact and
which one controls the decision. For repository completion, GitHub PR and issue
state usually controls remote readiness, while local `git` state controls only
the current checkout.

## State Language

When source status could blur, add a few plain words to the claim itself:
whether the state was directly verified, inferred from continuity, or unknown
because retrieval did not happen. Use this only when it changes what the next
action should trust. Preserve unknowns when retrieval did not happen. Do not
add confidence scores, fixed tiers, required labels, templates, audit
requirements, or governance process.

## Recovery

<!-- generated: pb.retrieval-recovery -->
> Generated section. Edit the [semantic source](../experiments/code-first-playbook/semantics/source-retrieval.yaml) (`action.retrieval-recovery/does`).

Recovery is required when source-first ordering has already been missed or a
selected retrieval transport fails before a required fact is verified. This
includes:

- the assistant answered before opening the referenced PR, issue, repository,
  branch, commit, path, or provider source
- conversational continuity outran verification
- inferred state was used before retrieval
- a human explicitly calls out missing source inspection
- conversational context conflicts with authoritative state
- a repository, provider CLI, connector, or raw provider API transport fails
  before the exact required fact is established

A transport failure is evidence about that mechanism only. It is not evidence
that every route to the authoritative source is unavailable. Keep three states
separate: the selected transport failed; the required fact remains unverified;
and the authoritative source is unavailable because no materially applicable
permitted route can establish that fact without weakening evidence, authority,
authentication, or safety guarantees.

When retrieval remains available, recovery restores verified state before
conversational repair:

1. Halt continuity reasoning.
2. Identify every unresolved mandatory trigger and the exact fact still needed.
3. Identify the source that owns the fact and select its narrowest normal
   supported retrieval surface.
4. If that transport fails, record the failure as transport or capability
   evidence without classifying the authoritative source as unavailable.
5. Use another permitted surface when it can establish the same fact with the
   required evidence semantics; stop after the exact claim is sufficiently
   verified rather than trying every tool.
6. Discard, correct, or mark unverified any assumptions made before retrieval,
   then resume from the restored verified state and stated unknowns.

Fail closed only when the required fact remains materially unverified after the
applicable qualified routes are unavailable, insufficient, or blocked. Report
the missing fact and the routes actually unavailable. Preserve the scope of each
route: hosted evidence must not invent local checkout freshness, and freshly
fetched Git evidence must not invent hosted-only metadata.

Do not prompt, re-prompt, escalate, mutate authentication, or enter an auth loop
merely because a speculative lower-level transport failed. Authentication
failure on one surface is not evidence that every other qualified route is
unauthenticated. Preserve any narrower authentication preflight explicitly
required by the owning workflow.

Ordinary successful first-class retrieval needs no speculative raw provider API
call for confirmation. Direct low-level API inspection remains permitted when
provider API behavior is itself the subject or a specialized workflow explicitly
requires that evidence surface.

Acknowledgment alone is not recovery. Explaining the violation is not
remediation. Recovery must perform the missing retrieval or inspection when it
is available, then explain only remaining blockers, uncertainty, or corrections
that still matter after inspection.

<!-- /generated: pb.retrieval-recovery -->

## Failure Modes

Treat continuity-first answers, stale carry-forward, inferred state,
summary-for-source substitution, local/hosted confusion, and acknowledgment or
meta-analysis without retrieval as source-first drift. Apply [Recovery](#recovery)
before continuing.

## Rules

Apply [Triggers](#triggers), [Ordering](#ordering), and the
[Verification Gate](#verification-gate). Preserve partial/unknown results,
separate local from hosted claims, and block dependent conclusions when required
verification fails. After drift, perform [Recovery](#recovery); acknowledgment
alone is insufficient.
