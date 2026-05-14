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

## Triggers

Classify triggers before using prior conversation, summaries, memory, or pasted
descriptions to reason about repository state.

Mandatory source-first triggers require authoritative retrieval before
stateful reasoning or recommendations:

- GitHub pull request URLs, pull request numbers, or requests such as "review
  this PR", "check this PR", "continue this PR", or "is this ready?"
- GitHub issue URLs, issue numbers, or requests such as "continue from this
  issue", "implement this issue", or "what is left on this issue?"
- repository identifiers, repository URLs, or local repository paths
- repo-aware advisory or evaluation requests where a repository is explicitly
  named and the answer depends on that repository's actual state
- branch names, refs, tags, commit SHAs, comparison ranges, or release refs
- requests to assess mergeability, CI status, review state, changed files,
  issue closure, validation status, or current implementation scope
- claims or requested changes that depend on current external provider,
  public API, SDK, CLI, package, or hosted-platform behavior

Optional triggers may guide retrieval when the next action depends on current
state, but they do not require source inspection for purely conversational
answers:

- pasted summaries, copied diffs, screenshots, or release notes without a live
  artifact identifier
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
3. For every mandatory trigger, identify and inspect the authoritative source.
4. Block stateful reasoning until required checks complete or fail.
5. Use conversational continuity only after source retrieval establishes the
   current state.
6. Treat any source that could not be checked as unknown or unverified.

When a mandatory trigger is present, verification blocks:

- statements about current PR, issue, branch, commit, CI, mergeability, review,
  release, or validation state
- merge, readiness, approval, closure, or implementation-scope
  recommendations
- claims about which files changed, which comments remain unresolved, or what
  the branch currently contains
- decisions that depend on current external API, SDK, CLI, provider, or hosted
  platform behavior

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

When source status could blur, add a few plain words to the claim itself. The
goal is not a new report format; it is to keep directly verified state,
continuity-based assumptions, and unknowns from collapsing into one fluent
answer.

Useful phrases:

- "verified from direct PR inspection"
- "mergeability inferred from cached state; not revalidated"
- "repo state not verified after branch update"
- "continuity assumption only"
- "remote CI status unknown because retrieval did not occur"

Use this when it changes what the next action should trust. Preserve unknowns
when retrieval did not happen. Do not add confidence scores, fixed tiers,
required labels, templates, audit requirements, or governance process.

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
- summary substitution for live state: using generated context refresh output,
  pasted PR summaries, or copied diffs as the source of truth when a live
  artifact is available
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
