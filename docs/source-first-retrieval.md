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
[`core-model.md`](core-model.md#authority-follows-the-question) before using the
evidence hierarchy below. The hierarchy orders evidence for a claim only after
the source that owns that kind of fact has been identified; it is not a global
system-of-record ranking. When a question spans planning, repository, runtime,
or historical evidence boundaries, retrieve each applicable owner and preserve
their separate claims during reconciliation.

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
available. If connector or source access is unavailable, say so explicitly
before offering any summary-based analysis. Do not imply direct inspection
happened unless it actually did.

Reasoning traces, telemetry, generated summaries, and agent self-reports are
supplementary evidence only. They are not authoritative proof of source state,
intent, or correctness. When they conflict with verified source state or
observed action and outcome, the verified source state or action and outcome
control. This matters because reasoning traces can be post-hoc, incomplete, or
optimized toward what the workflow appears to reward.

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

Before beginning work in an existing local repository or worktree, reconcile
the local checkout with the repository's current GitHub default branch. Do not
assume an existing clone or worktree reflects authoritative repository state;
treat local repositories as cached working copies that may require
synchronization. This principle intentionally does not prescribe a specific Git
command or implementation sequence.

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

Recovery is required when source-first ordering has already been missed. This
includes:

- the assistant answered before opening the referenced PR, issue, repository,
  branch, commit, path, or provider source
- conversational continuity outran verification
- inferred state was used before retrieval
- a human explicitly calls out missing source inspection
- conversational context conflicts with authoritative state

When retrieval remains available, recovery restores verified state before
conversational repair:

1. Halt continuity reasoning.
2. Identify every unresolved mandatory trigger.
3. Retrieve the authoritative source state for those triggers.
4. Discard, correct, or mark unverified any assumptions made before retrieval.
5. Resume from the restored verified state and stated unknowns.

Acknowledgment alone is not recovery. Explaining the violation is not
remediation. Recovery must perform the missing retrieval or inspection when it
is available, then explain only remaining blockers, uncertainty, or corrections
that still matter after inspection.

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
