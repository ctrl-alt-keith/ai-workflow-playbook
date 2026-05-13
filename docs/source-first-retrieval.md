# Source-First Retrieval

## Purpose

Define the execution-ordering rule for repository workflows that include a
source-of-truth trigger. The rule is simple: detect deterministic triggers
first, retrieve authoritative state next, and only then use conversational
continuity to interpret intent or explain the result.

This page addresses an observed workflow failure mode: fresh-thread
continuation from a GitHub PR URL resumed from conversational continuity first
and reconciled against repository state afterward. That ordering is unsafe for
repository work because it can produce coherent but unverified answers.

## Scope

This applies to repository and software workflows. It does not require live
source retrieval for ordinary general chat, brainstorming, or conceptual
discussion unless the answer depends on current repository, pull request,
issue, branch, commit, validation, runtime, provider, or external API state.

This guidance describes observable workflow behavior and operational
safeguards. It does not assume or describe platform internals.

## Trigger Classification

Classify triggers before using prior conversation, summaries, memory, or pasted
descriptions to reason about repository state.

Mandatory source-first triggers require authoritative retrieval before stateful
reasoning or recommendations:

- GitHub pull request URLs, pull request numbers, or requests such as "review
  this PR", "check this PR", "continue this PR", or "is this ready?"
- GitHub issue URLs, issue numbers, or requests such as "continue from this
  issue", "implement this issue", or "what is left on this issue?"
- repository identifiers, repository URLs, or local repository paths
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
- references to earlier conversation, prior work, or a remembered plan
- broad repository names without an action that depends on current state
- conceptual questions about workflow patterns, review posture, or tradeoffs

Ambiguous cases must be resolved before stateful conclusions:

- "continue", "the branch", "the PR", or "the issue" without a visible
  artifact identifier
- words that could be ordinary prose or a branch, tag, or repository name
- stale local checkouts whose relationship to the requested remote artifact is
  not clear
- conflicting pasted context and live artifact references

Resolve ambiguity by inspecting the likely authoritative source when the
target is clear. If the target is not clear, ask a narrow clarifying question
or report the missing identifier. Do not fill the gap with conversational
inference.

## Ordering Model

For repository workflows, execute in this order:

1. Detect deterministic triggers in the user request, visible context, and
   provided artifacts.
2. Classify each trigger as mandatory, optional, or ambiguous.
3. For every mandatory trigger, identify the authoritative source and perform
   the required retrieval or inspection.
4. Block stateful reasoning until the required source checks complete or fail.
5. Use conversational continuity only after the source gate establishes the
   current state.
6. Treat any source that could not be checked as unknown or unverified.

The following are blocked pending verification when a mandatory trigger is
present:

- statements about current PR, issue, branch, commit, CI, mergeability, review,
  release, or validation state
- merge, readiness, approval, closure, or implementation-scope
  recommendations
- claims about which files changed, which comments remain unresolved, or what
  the branch currently contains
- decisions that depend on current external API, SDK, CLI, provider, or hosted
  platform behavior

Continuity is allowed after the gate to interpret the human's intent,
constraints, tone, previous decisions, and desired output shape. Continuity is
not allowed to substitute for source state. Summaries, memory, generated
context-refresh output, and pasted descriptions may help navigate, but they
must not outrank direct repository, GitHub, CI, runtime, or provider evidence.

## Verification Gate Pattern

Use this reusable gate whenever a mandatory trigger is present:

- Trigger: name the artifact or request that activated source-first retrieval.
- Source: name the authoritative source used for the current state.
- Checks: list the specific state checks required by the task.
- Result: mark the gate `verified`, `partial`, or `blocked`.
- Unknowns: state anything required for the task that remains unverified.

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

## Failure Modes

Watch for these observable failure patterns:

- Continuity-first resumption: answering from prior thread flow before opening
  the referenced PR, issue, branch, path, or provider source.
- Stale conversational carry-forward: treating an earlier plan, summary, or
  status report as current after repo or remote state may have changed.
- Inferred repo or PR state: claiming files, checks, comments, mergeability, or
  readiness from expectations instead of inspection.
- Summary substitution for live state: using generated context refresh output,
  pasted PR summaries, or copied diffs as the source of truth when a live
  artifact is available.
- Local-state versus remote-state confusion: treating a clean local checkout as
  proof of GitHub mergeability, CI success, review resolution, or issue
  closure.
- Coherent but unverified responses: producing plausible, well-structured
  recommendations without naming the verified source state that supports them.

## Enforceable Workflow Rules

Use these short rules in startup docs, adapter guidance, review checklists, and
future automation hooks:

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
