# Reusable Workflow Prompt Templates

This file contains high-signal prompt templates for repeatable workflow tasks in
a generic, parameterized form. Keep core workflow rules in the core playbook
docs, tool-specific execution guidance in `docs/tool-adapters/`, and repo-local
execution rules in `AGENTS.md`. Prompts here should reference those canonical
sources rather than duplicate them.

Use the placeholders shown in each prompt as inputs. In plain-text prompt bodies,
angle-bracket placeholders are acceptable, but in markdown templates or copied
instructions prefer lint-safe placeholders such as `[repository]` or backticked
tokens. Angle-bracket placeholders can be interpreted as inline HTML by markdown
tooling.

## Quick Navigation

- [Codex Task Prompt Format](#codex-task-prompt-format)
- [Notes vs Playbook Alignment Audit](#notes-vs-playbook-alignment-audit)
- [Orchestration Handoff Prompt](#orchestration-handoff-prompt)
- [Implementation Delivery Footer](#implementation-delivery-footer)
- [PR Review](#pr-review)

## Codex Task Prompt Format

Use this format for non-trivial Codex implementation tasks: work that changes an
existing system, has meaningful constraints, needs validation, or should end in a
branch and PR. Simple one-step tasks do not need this much structure.

Before writing or using a Codex task prompt, apply the interaction mode
preflight in [`docs/repo-readiness.md`](repo-readiness.md#interaction-mode-preflight).
Use this implementation prompt format only when the intended mode is direct
implementation. For review/audit work, use the review or audit templates. For
orchestration or prompt-authoring work, use the orchestration handoff prompt
template instead of appending implementation delivery instructions by habit.

Keep prompts concise but complete. The goal is to remove ambiguity that would
cause retries, not to turn every task into a process document.

Any implementation task that modifies repository files MUST include the
Implementation Delivery Footer unless PR delivery is explicitly excluded.
Omitting the footer can leave delivery incomplete: changes made locally but not
pushed and opened for review in a PR.

### Codex Task Prompt Template

```text
Role:
- You are implementing a scoped repository change in [repository].

Goal:
- [desired outcome]

Success criteria:
- [observable condition that proves the goal is met]
- The diff is limited to the intended repo and scope.
- Canonical validation has run or any inability to run it is reported.
- A ready-for-review PR is opened unless PR delivery is explicitly excluded.

Available context:
- Repository: [repository]
- Relevant background: [short context]

Coordination:
- GitHub issues: [none, or issues such as #163]
- Planning tickets: [none, or IDs such as Linear CAK-5]
- PR linkage: [closing keywords and planning references expected in the PR]
- Post-merge notes: [none, or planning/status updates to verify after merge]

Retrieval budget:
- Read `ai-workflow-playbook/docs/start-here.md`, the target repo's
  `AGENTS.md`, and the repo-local files needed for this change.
- Verify live external state, such as GitHub repository or pull request state,
  before relying on it.
- Stop broad search once the target files, validation path, branch/PR
  expectations, and any external-state dependencies are clear.
- Do not traverse sibling repositories unless this task explicitly names them.

Scope:
- In scope: [files, behavior, or workflow area]
- Out of scope: [explicit non-goals]

Constraints:
- Do not include unrelated changes or opportunistic cleanup.
- Make the smallest possible change that satisfies the goal.
- Default behavior must remain unchanged unless explicitly required.
- Follow existing repo patterns and validation paths.
- Do not silently skip required steps; report any blockers or incomplete work.

Side-effect constraints:
- Follow `docs/repo-readiness.md`, `docs/tool-adapters/codex.md`, and
  repo-local `AGENTS.md` for interaction mode, direct command execution,
  dedicated worktrees, validation, and PR delivery.
- Follow `docs/review-packet.md` when a task asks for PR review, readiness,
  approval, or merge advice.
- Follow `docs/engineering-baseline.md` when code, tests, docs, risks, or
  user-facing claims depend on external public API behavior.

Preamble/update expectations:
- For multi-step or tool-heavy work, provide brief progress updates before
  grouped tool use and before file edits.

Tasks:
1. Inspect the existing structure and related docs or code.
2. Make the smallest scoped change that satisfies the goal.
3. Update nearby docs or tests only when they are part of the same change.

Validation:
- Follow the validation rules in `docs/repo-readiness.md` and repo-local
  `AGENTS.md`.
- Run the repository's canonical validation command, such as `make check`, when
  it exists and can run locally.
- Report the actual result of validation; do not assume success.
- If validation fails, include the failure details.
- If validation cannot be run, explain why.

Deliverable:
- Follow the branch, workspace, and PR delivery rules in
  `docs/feature-lifecycle.md`, `docs/repo-readiness.md`, and
  `docs/tool-adapters/codex.md`.
- Stage only relevant changes.
- Commit and push only the intended changes.
- Open a PR in the appropriate readiness state against the intended base
  branch, usually `main`.
- When GitHub issues and planning tickets are both provided, reference both in
  the PR. Use GitHub closing keywords such as `Closes #163` for GitHub issue
  closure and include planning identifiers such as `Linear: CAK-5` as
  coordination context.
- Ensure the PR contains only intended changes.
- Include a summary, validation results, and any residual risks.

Stop rules:
- Pause before merge, release, tag, destructive, or permissions-sensitive
  actions unless the human explicitly requested that action.
- Stop and report if the repo context is mismatched, validation failure implies
  broader work than requested, or live external state cannot be verified where
  it is required.
```

## Notes vs Playbook Alignment Audit

### Notes vs Playbook Alignment Audit Use When

Use this prompt when a notes repository needs cleanup after workflow rules were
promoted into the playbook and the remaining notes should be aligned to the
canonical source.

### Notes vs Playbook Alignment Audit Required Inputs

- `notes_project_root` (working directory)
- `playbook_reference` (this repository)

### Notes vs Playbook Alignment Audit Repo-Type Notes

- The notes repo is a staging layer for material that may later become reusable guidance.
- The playbook repo is the canonical source for promoted cross-repo workflow rules.
- The audit must stay inside the notes project root and must not traverse outside it.

### Notes vs Playbook Alignment Audit Prompt

```text
Task:
Run a notes vs playbook alignment audit for <notes_project_root>.

Inputs:
- Notes project root: <notes_project_root>
- Playbook reference: <playbook_reference>

Success criteria:
- Each relevant notes file is classified as remove, trim, keep, or defer.
- Remove and trim recommendations cite the canonical playbook location that
  now owns the promoted guidance.
- Deferred items name the blocker or missing local decision.

Retrieval budget:
- Inspect only files inside <notes_project_root> plus the playbook sections
  needed to verify canonical ownership.
- Do not re-audit unrelated repositories or reopen promotion decisions.
- Stop once each relevant file has a justified classification.

Instructions:
- Audit the notes project against the playbook reference after promotion work
  has already been completed.
- Treat the notes project as a staging layer and the playbook reference as the
  canonical source for promoted workflow guidance.
- Review only files inside <notes_project_root>.
- For each relevant file, classify it as remove, trim, keep, or defer.
- Use remove when the file is fully superseded by canonical playbook guidance
  and no longer needs to remain in notes.
- Use trim when the file should stay but only after redundant or
  already-promoted material is removed.
- Use keep when the file still serves a valid notes-layer purpose without
  conflicting with the canonical playbook.
- Use defer when cleanup depends on a separate local decision, missing context,
  or unfinished follow-up work.
- Do not re-evaluate whether content should be promoted into the playbook. This
  audit is for cleanup and alignment after promotion, not for promotion
  decisions.
- When a file overlaps with promoted guidance, reference the canonical playbook
  location that now owns that guidance.
- Recommend only cleanup actions that can be justified from the observed notes
  files and the referenced playbook.

Constraints:
- Do not inspect, traverse, or recommend changes outside <notes_project_root>.
- Do not treat the notes repository as a second canonical source.
- Do not reopen already-settled promotion decisions during this audit.
- Keep the audit operational, concise, and file-specific.

Validation:
- Verify that each remove or trim recommendation points to the canonical
  playbook location that replaced or now owns the guidance.
- Verify that keep recommendations preserve only notes-layer material that still belongs in staging.
- Verify that defer recommendations explain the specific blocker or unresolved local dependency.
- Verify that the audit output can drive a cleanup pass followed by a re-audit
  to confirm convergence.

Stop rules:
- If the notes root boundary is unclear, stop and ask for the intended root
  instead of widening the traversal.
- Do not mutate files during the audit unless the task explicitly changes to
  implementation.

Output format:
1. Summary: one short paragraph describing the overall alignment state.
2. Per-file classification: a list of files with one of remove, trim, keep, or
   defer and a short rationale for each.
3. Cleanup recommendations: a short numbered list of the highest-leverage
   remove or trim actions, including canonical playbook references where
   applicable.
4. Re-audit trigger: one short sentence stating when to rerun the audit to confirm convergence.
```

### Notes vs Playbook Alignment Audit Notes

This audit is for cleanup, not promotion. Run it after promotion work, then use a
follow-up re-audit to confirm the notes set has converged on the playbook as the
canonical source.

## Orchestration Handoff Prompt

### Orchestration Handoff Prompt Use When

Use this prompt when the deliverable is a complete downstream task envelope for
another implementation agent or tool, rather than direct repository mutation by
the current agent.

Do not use this template as a substitute for implementation delivery when the
human explicitly asked the current agent to make the change, validate it,
commit, push, and open a PR.

### Orchestration Handoff Prompt Required Inputs

- `repository`
- `working_directory`
- `canonical_source`
- `source_evidence`
- `interaction_mode`
- `validation_path`
- `delivery_expectation`

### Orchestration Handoff Prompt Template

Deliver the downstream prompt as one contiguous copyable block.

```text
Role:
- You are a downstream agent completing a bounded task for [repository].

Goal:
- [clear user-visible outcome the downstream agent should complete]

Success criteria:
- [what must be true before final response]
- The work stays within the named repository, branch, and scope.
- Required validation has run or a blocker is reported.
- The final answer includes the requested artifact, PR, review packet, or
  handoff evidence.

Working directory:
[absolute or repo-relative working directory]

Repository:
[repository]

Required context:
- Canonical reusable workflow policy: [canonical_source]
- Repo-local execution guidance: [repo-local AGENTS.md or equivalent]
- Reference evidence: [source_evidence]
- Available source material: [specific files, issues, PRs, notes, or docs]

Retrieval budget:
- Read the shared playbook startup guidance and repo-local `AGENTS.md` first.
- Inspect only the files, issues, PRs, docs, or generated artifacts needed to
  satisfy the goal and validation requirements.
- For implementation, confirm the dedicated repo-local worktree and canonical
  validation path before editing.
- For `git` and `gh`, confirm execution settings avoid implicit shell or
  login-shell wrapping where supported.
- Stop retrieving once the target surface, constraints, validation path, and
  delivery expectation are clear.
- Do not broaden into sibling repos or noncanonical staging material unless it
  is explicitly named as context.

Interaction mode:
- [implementation, review/audit, or orchestration/prompt-authoring]

Context:
- [relevant facts discovered by the orchestrator]
- [issue, PR, evidence note, or prior-art context the receiver needs]
- [GitHub issue IDs, planning-ticket IDs, PR linkage expectations, and
  post-merge coordination notes, when relevant]

Scope:
- In scope: [files, behavior, docs, or workflow area]
- Out of scope: [explicit exclusions]

Constraints:
- Keep changes minimal, scoped, and structurally local.
- Do not include unrelated cleanup.
- Do not rely on noncanonical staging, runtime, generated, or local instruction
  surfaces as policy unless the rule has been promoted into the canonical
  source.
- Follow `docs/repo-readiness.md`, `docs/tool-adapters/codex.md`, and
  repo-local `AGENTS.md` for worktree, command-form, validation, and delivery
  rules.
- Report blockers, validation failures, residual risks, and uncertainty.

Preamble/update expectations:
- For multi-step, long-running, or tool-heavy work, give short progress updates
  before grouped tool use and before file edits.

Tasks:
1. [ordered task]
2. [ordered task]
3. [ordered task]

Validation:
- Run [validation_path].
- Report exactly what was run and the result.
- If validation cannot run, explain why and do not substitute an undocumented
  validation path.

Delivery:
- [branch, commit, push, PR, review packet, or report expectation]
- Include summary, validation, source evidence, and residual risks or
  follow-ups.
- When both GitHub issues and planning tickets are in scope, include both in
  the PR or handoff. Use GitHub closing keywords for GitHub issue closure and
  treat planning tickets as coordination state unless repo-local guidance says
  otherwise.

Deliverable:
- [complete expected final output]
- Provide the full drop-in artifact by default, even when the task asks to add,
  incorporate, or fold new material into existing prompt or instruction text.

Stop rules:
- Stop before merge, release, tag, destructive, externally visible, or
  permissions-sensitive actions unless explicitly authorized.
- Ask for human input when the repo context is wrong, required evidence is
  unavailable, or the next step depends on a human judgment call.
```

## Implementation Delivery Footer

### Implementation Delivery Footer Use When

Append this footer to implementation prompts when the task is expected to make
repo changes and deliver them through the normal branch, commit, push, and PR
flow.

Use this footer only after the interaction mode is clearly implementation mode.

### Implementation Delivery Footer Do Not Use When

Do not append this footer for exploration, design, or review-only tasks unless
they are also expected to make and deliver repo changes.

Do not append this footer for orchestration or prompt-authoring tasks whose
deliverable is a complete downstream prompt rather than repo mutation.

### Implementation Delivery Footer Snippet

```text
Delivery:
- Follow the branch, PR readiness, and workspace rules in
  `docs/feature-lifecycle.md`, `docs/repo-readiness.md`, and
  `docs/tool-adapters/codex.md`.
- Follow the dedicated worktree rule in `docs/repo-readiness.md#pr-readiness`
  for implementation changes: one repository, one branch, one dedicated
  repo-local worktree, and one PR per change. Run commands from inside the
  target worktree and keep temporary or scratch state repo-local.
- Run ordinary `git`, `gh`, `make`, `python`, repo-local script, and tool
  commands directly from the target worktree; reserve shell wrapping for
  commands that genuinely require shell syntax.
- For standard `git` and `gh` work, use the CLI directly rather than alternate
  APIs, helper scripts, or connector substitutions; where supported, use native
  argv-style execution and disable implicit shell or login-shell defaults with
  settings such as `shell=false`, `login=false`, `use_shell=false`, or the
  platform-native equivalent.
- Before executing a shell-wrapped command, perform the command-form preflight
  from `docs/repo-readiness.md`; when shell semantics are unnecessary, rewrite
  the operation into direct argv form before execution.
- Fetch current `origin/main` at task start, anchor implementation to that
  fetched baseline, and verify current mergeability before PR.
- Stage only the relevant changes.
- Commit with a clear message.
- Push the branch.
- Open a PR in the appropriate readiness state against the intended base branch,
  usually `main`.
- Include expected GitHub issue closing keywords and planning-ticket references
  in the PR body when those identifiers are provided.
- Report the PR link, files changed, and validation results.
```

## PR Review

### PR Review Use When

Use this prompt when the task is to review, check, assess, approve, or comment
on an existing pull request.

### PR Review Required Inputs

- `repository`
- `pull_request`
- `task_or_issue_context` (optional; use `none` when not available)
- `summary_only` (`yes` or `no`)

### PR Review Prompt

```text
Task:
Review pull request [pull_request] in [repository].

Inputs:
- Repository: [repository]
- Pull request: [pull_request]
- Task or issue context: [task_or_issue_context]
- Summary-only requested: [summary_only]

Success criteria:
- Review feedback is grounded in direct PR evidence when a PR link, name, or
  number is available.
- Findings are severity-ordered and distinguish blockers from non-blocking
  risks or follow-ons.
- Merge readiness is stated only when supported by current PR evidence.

Retrieval budget:
- Inspect the PR through the GitHub connector first when available and not
  explicitly forbidden by the human.
- Use local checkout, `git diff`, and `gh` only as supplemental evidence.
- Stop once PR metadata, changed files, relevant diffs, discussion, checks,
  mergeability, and task fit are clear enough for the requested review depth.

Instructions:
- Apply the canonical direct PR inspection rule in
  `docs/review-packet.md#direct-pr-inspection`.
- Stay in review/audit mode. Do not implement changes while performing the PR
  review unless the human explicitly changes the task to implementation.
- Treat user-provided summaries, pasted titles, local path snippets, and copied
  diff excerpts as navigation and context only, not review evidence, when a PR
  link, name, or number is available.
- Use local checkout, `git diff`, and `gh` only as supplemental evidence after
  direct PR inspection.
- Apply the single-operator review posture from `docs/repo-readiness.md` when
  it fits the repository context.
- Do not mutate the PR unless the human explicitly asks for that GitHub action.
- If GitHub connector access is unavailable, fails, is declined, or is
  explicitly forbidden by the human, state that clearly and provide only
  clearly caveated feedback from the information already present.
- Do not claim the PR is safe to merge, ready to merge, or approved without
  direct evidence from the PR itself through the connector.

Stop rules:
- If connector access is required but unavailable, stop the review and report
  the access blocker instead of inferring readiness.
- Do not mutate the PR unless the human explicitly asks for that GitHub action.

Output format:
1. Review findings: severity-ordered findings with file or PR references where
   possible. Distinguish blockers from non-blocking risks, implementation
   opportunities, and practical follow-ons.
2. Scope and evidence notes: concise notes on inspected PR surface, CI/checks,
   mergeability, and task fit.
3. Recommendation: `ready to merge`, `needs decision`, or `blocked`, only when
   direct PR evidence supports it.
```
