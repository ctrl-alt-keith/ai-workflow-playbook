# Reusable Workflow Prompt Templates

This file holds reusable prompt shapes. Keep workflow rules in the core
playbook docs, Codex-specific execution guidance in `docs/tool-adapters/codex.md`,
and repo-local execution rules in `AGENTS.md`.

Use lint-safe placeholders such as `[repository]`, `[validation_path]`, or
backticked tokens in Markdown templates. Angle-bracket placeholders can be
interpreted as inline HTML by Markdown tooling.

## Quick Navigation

- [Codex Implementation Task](#codex-implementation-task)
- [Parallel Batch Add-On](#parallel-batch-add-on)
- [Orchestration Handoff](#orchestration-handoff)
- [Implementation Delivery Add-On](#implementation-delivery-add-on)
- [PR Review](#pr-review)

## Codex Implementation Task

Use this template only when the intended interaction mode is direct
implementation. For review or orchestration, use the matching template instead.

```text
Role:
- You are implementing a scoped repository change in [repository].

Goal:
- [desired outcome]

Success criteria:
- [observable condition that proves the goal is met]
- The diff is limited to the intended repository and scope.
- Canonical validation has run or any inability to run it is reported.
- PR delivery is complete unless explicitly excluded.

Context:
- Repository: [repository]
- Working directory: [working_directory]
- Relevant background: [short context]
- GitHub issues or planning references: [none or identifiers]

Retrieval:
- Read `ai-workflow-playbook/docs/start-here.md`, the target repo's
  `AGENTS.md`, and any required tool adapter before acting.
- Retrieve or revalidate authoritative repository, issue, PR, file, CI, log, or
  artifact state before relying on it.
- Treat summaries, memory, and pasted descriptions as navigation, not proof of
  current source state.
- Stop broad search once the target files, constraints, validation path, and
  delivery expectation are clear.

Scope:
- In scope: [files, behavior, or workflow area]
- Out of scope: [explicit non-goals]

Constraints:
- Keep the change minimal, scoped, and structurally local.
- Follow existing repo patterns and canonical validation.
- Follow `docs/repo-readiness.md`, `docs/tool-adapters/codex.md`, and
  repo-local `AGENTS.md` for interaction mode, command form, worktree,
  validation, and delivery.
- Report blockers, validation failures, residual risks, and uncertainty.

Tasks:
1. Inspect the existing structure and relevant source material.
2. Make the smallest scoped change that satisfies the goal.
3. Update nearby docs or tests only when they are part of the same change.

Validation:
- Run [validation_path].
- Report the exact result.

Delivery:
- [branch, commit, push, and PR expectation, or explicit exclusion]
- Include a concise summary, validation results, and residual risks.

Stop rules:
- Stop before merge, release, tag, destructive, externally visible, or
  permissions-sensitive actions unless explicitly authorized.
- Stop and report if required source state cannot be retrieved, the repo
  context is mismatched, or validation failure implies broader work.
```

## Parallel Batch Add-On

Use this compact add-on when asking an implementation agent to coordinate a
parallel batch. Keep the concrete lane count and topology task-specific.
Use [`orchestration-and-parallelism.md`](orchestration-and-parallelism.md) to
decide whether the work should be split at all.

```text
Parallel execution:
- Separate lanes by repository, file area, behavior surface, or risk surface.
- Define any merge-order dependencies before launch.
- Keep one repository, one branch, one worktree, and one PR per lane.
- Validate each lane with the repository's canonical validation path.
- Workers stop at PR readiness and report changed files, validation, overlap,
  blockers, residual risk, and merge-order dependencies.
- The orchestrator inspects outputs directly, reconciles sequentially, reruns
  canonical validation after updates, and stops before merge unless explicitly
  authorized.
```

## Orchestration Handoff

Use this prompt when the deliverable is a complete downstream task envelope, not
direct mutation by the current agent.

Required inputs:

- `repository`
- `working_directory`
- `canonical_source`
- `source_evidence`
- `interaction_mode`
- `validation_path`
- `delivery_expectation`

```text
Role:
- You are a downstream agent completing a bounded task for [repository].

Goal:
- [clear user-visible outcome]

Success criteria:
- [what must be true before final response]
- The work stays within the named repository and scope.
- Required validation has run or a blocker is reported.
- The final answer includes the requested artifact, PR, review packet, or
  handoff evidence.

Inputs:
- Repository: [repository]
- Working directory: [working_directory]
- Canonical source: [canonical_source]
- Repo-local guidance: [AGENTS.md or equivalent]
- Source evidence: [source_evidence]
- Interaction mode: [implementation, review/audit, or orchestration]
- Validation path: [validation_path]
- Delivery expectation: [delivery_expectation]

Retrieval:
- Read the shared playbook startup guidance and repo-local `AGENTS.md` first.
- Inspect only the files, issues, PRs, docs, or artifacts needed for the goal.
- Retrieve authoritative source state before relying on it; treat summaries as
  navigation only.
- Stop once the target surface, constraints, validation path, and delivery
  expectation are clear.

Scope:
- In scope: [files, behavior, docs, or workflow area]
- Out of scope: [explicit exclusions]

Constraints:
- Keep changes minimal, scoped, and structurally local.
- Do not rely on staging, runtime, generated, or local instruction surfaces as
  policy unless the rule has been promoted into the canonical source.
- Follow the referenced playbook, adapter, and repo-local guidance.
- Report blockers, validation failures, residual risks, and uncertainty.

Tasks:
1. [ordered task]
2. [ordered task]
3. [ordered task]

Validation:
- Run [validation_path], or report why it cannot run.

Delivery:
- [branch, commit, push, PR, review packet, or report expectation]
- Include summary, validation, source evidence, and residual risks.

Stop rules:
- Stop before merge, release, tag, destructive, externally visible, or
  permissions-sensitive actions unless explicitly authorized.
- Ask for human input when required evidence is unavailable or the next step
  depends on a human judgment call.
```

## Implementation Delivery Add-On

Append this only when the task is implementation mode and normal PR delivery is
expected.

```text
Delivery:
- Follow the branch, worktree, validation, and PR delivery rules in
  `docs/repo-readiness.md`, `docs/tool-adapters/codex.md`, and repo-local
  `AGENTS.md`.
- Stage, commit, push, and open or update the intended PR only with relevant
  changes.
- Include expected GitHub issue closing keywords and planning references when
  those identifiers are provided.
- Report the PR link, files changed, validation results, and residual risks.
```

## PR Review

Use this prompt when the task is to review, check, assess, approve, or comment
on an existing pull request.

Required inputs:

- `repository`
- `pull_request`
- `task_or_issue_context` (`none` when unavailable)
- `summary_only` (`yes` or `no`)

```text
Task:
Review pull request [pull_request] in [repository].

Inputs:
- Repository: [repository]
- Pull request: [pull_request]
- Task or issue context: [task_or_issue_context]
- Summary-only requested: [summary_only]

Success criteria:
- Review feedback is grounded in direct PR evidence.
- Findings are severity-ordered and distinguish blockers from non-blocking
  risks or follow-ons.
- Merge readiness is stated only when supported by current PR evidence.

Retrieval:
- Inspect the PR through the GitHub connector first when available and not
  explicitly forbidden.
- Use local checkout, `git diff`, and `gh` only as supplemental evidence.
- Stop once PR metadata, changed files, relevant diffs, discussion, checks,
  mergeability, and task fit are clear enough for the requested depth.

Instructions:
- Apply `docs/review-packet.md#direct-pr-inspection`.
- Stay in review/audit mode unless the human explicitly changes the task.
- Treat user summaries and pasted excerpts as navigation, not PR evidence.
- Do not mutate the PR unless explicitly asked.
- If required PR evidence is unavailable, state that blocker and caveat any
  feedback from already-present information.

Output format:
1. Review findings: severity-ordered findings with file or PR references where
   possible.
2. Scope and evidence notes: inspected PR surface, checks, mergeability, and
   task fit.
3. Recommendation: `ready to merge`, `needs decision`, or `blocked`, only when
   direct PR evidence supports it.
```
