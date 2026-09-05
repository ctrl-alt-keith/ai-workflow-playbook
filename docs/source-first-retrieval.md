# Source-First Retrieval

## Purpose

For repository workflows with a source-of-truth trigger, detect the trigger
first, retrieve authoritative state next, and only then use conversational
continuity to interpret intent or explain the result.

This avoids coherent but unverified answers about PRs, issues, branches,
files, validation, CI, runtime state, or external provider/API behavior.

## Scope

This applies to repository and software workflows. It does not require live
source retrieval for ordinary general chat, brainstorming, or conceptual
discussion unless the answer depends on current repository, pull request,
issue, branch, commit, validation, runtime, provider, or external API state.

This guidance describes observable workflow behavior and operational
safeguards. It does not assume or describe platform internals.

## Authority Selection

Apply the question-typed authority rule in
[`core-model.md`](core-model.md#authority-follows-the-question) and its
[`Evidence Classification Invariant`](core-model.md#evidence-classification-invariant)
before using the evidence hierarchy below. The core model owns those semantic
requirements; this document owns repository retrieval triggers, source
ordering, verification gates, and recovery mechanics. The hierarchy orders
evidence for a claim only after the source that owns that kind of fact has been
identified; it is not a global system-of-record ranking. When a question spans
planning, repository, runtime, or historical evidence boundaries, retrieve
each applicable owner and preserve their separate claims during
reconciliation.

## Evidence Hierarchy

Prefer evidence in this order when repository state is available:

1. Live connector or tool inspection of the referenced artifact.
2. Direct repository state from the inspected worktree or remote ref.
3. Validation output executed in the current session.
4. Raw logs or artifacts.
5. User summaries.
6. Prior-thread summaries.
7. Agent-generated summaries, completion reports, or status claims.

Summaries, reports, and completion narratives, including user-provided PR,
implementation, repository, issue, audit, status, and change summaries, are
navigation rather than evidence for source-verifiable judgments. They may guide
what to inspect, but when a live artifact, repository, check, workflow, log, or
file can be inspected directly, verify the underlying source before reviewing,
approving, critiquing, validating, recommending merge, assessing completion, or
making implementation judgments.

When a task asks for direct review of GitHub state, pull requests, issues,
repository files, checks, comments, or review threads, inspect the GitHub
artifact through the available connector or source-of-truth tool before giving
a conclusion. PR receipts, implementation summaries, validation summaries, and
automation reports are navigation aids, not evidence, when that access is
available. Before claiming connector access is unavailable, apply the runtime
verification rule in
[`start-here.md`](start-here.md#connector-availability-is-runtime-evidence).
If verified connector or source access is unavailable, say so explicitly
before offering any summary-based analysis. Do not imply direct inspection
happened unless it actually did.

Reasoning traces, telemetry, generated summaries, and agent self-reports are
supplementary evidence only. They are not authoritative proof of source state,
intent, or correctness. When they conflict with verified source state or
observed action and outcome, the verified source state or action and outcome
control. This matters because reasoning traces can be post-hoc, incomplete, or
optimized toward what the workflow appears to reward.

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

For repository workflows:

1. Detect deterministic triggers in the request, visible context, and provided
   artifacts.
2. Classify each trigger as mandatory, optional, or ambiguous.
3. For every mandatory trigger, inspect referenced PRs, issues, branches,
   checks, workflows, files, or other authoritative sources directly.
4. Verify current live state.
5. Summarize verified findings first.
6. Only then interpret, prioritize, recommend, or explain.
7. Use conversational continuity only after source retrieval establishes the
   current state.
8. Treat any source that could not be checked as unknown or unverified.

### Existing Checkout Freshness And Bounded Recovery

Before beginning work in an existing local repository or worktree, reconcile
the local checkout with the repository's current GitHub default branch. Treat
stale local repository state as a recoverable cached-state condition, not by
itself as a reason to abandon local inspection. A clean working tree or a
cached remote-tracking ref does not prove that the checkout reflects current
hosted GitHub state.

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

Treat repo-aware suggestions as retrieval tasks first and advisory tasks
second. When a repository is explicitly named and the human asks for analysis,
review, suggestions, evaluation, "what should we add", "what do you think",
architecture direction, or repo-aware prioritization, inspect enough current
repository state to ground the answer.

Keep inspection proportional to the question. Do not turn this into a full
audit unless the request calls for one. Purely conceptual discussion remains
optional unless the answer claims or depends on current repository state.

If this step was missed, recovery starts by retrieving the referenced
repository state. Then correct, discard, or mark prior repo-specific advice as
unverified before explaining the failure pattern.

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

Watch for these observable failure patterns:

- continuity-first resumption: answering from prior thread flow before opening
  the referenced PR, issue, branch, path, or provider source
- stale conversational carry-forward: treating an earlier plan, summary, or
  status report as current after repo or remote state may have changed
- inferred repo or PR state: claiming files, checks, comments, mergeability, or
  readiness from expectations instead of inspection
- summary substitution for live state: using cached summaries, completion
  reports, pasted PR summaries, or copied diffs as the source of truth when a
  live artifact is available
- local-state versus remote-state confusion: treating a clean local checkout as
  proof of GitHub mergeability, CI success, review resolution, or issue closure
- coherent but unverified responses: producing plausible recommendations
  without verified source state
- acknowledged-but-unrecovered drift: recognizing the source-first violation
  while continuing from the same conversational state
- explanation replacing remediation: describing the correct ordering instead
  of re-entering it
- meta-analysis replacing action: discussing a concrete operational request
  instead of inspecting, reviewing, updating, or generating the requested
  artifact

## Rules

- Detect repository triggers before continuity.
- Retrieve authoritative source state before stateful reasoning.
- Treat summaries as leads, not state, whenever live inspection is available.
- Provide no evaluative commentary before direct live inspection.
- Block readiness, mergeability, approval, closure, and implementation-scope
  claims until verification completes.
- Use summaries and memory only as navigation aids after source retrieval.
- Mark unavailable source state as unknown; do not infer it.
- Separate local checkout facts from remote PR, issue, CI, and review facts.
- Treat partial verification as partial; do not issue full recommendations from
  missing checks.
- Stop on source-access failure when the requested output depends on that
  source.
- After source-first drift, halt continuity and re-enter retrieval before
  continuing.
