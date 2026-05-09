# Reusable Workflow Prompt Templates

This file contains reusable prompt templates for repeatable workflow tasks in a
generic, parameterized form. Keep core workflow rules in the core playbook docs,
tool-specific execution guidance in `docs/tool-adapters/`, and repo-local
execution rules in `AGENTS.md`. Prompts here should reference those canonical
sources rather than duplicate them.

Use the placeholders shown in each prompt as inputs. In plain-text prompt bodies,
angle-bracket placeholders are acceptable, but in markdown templates or copied
instructions prefer lint-safe placeholders such as `[repository]` or backticked
tokens. Angle-bracket placeholders can be interpreted as inline HTML by markdown
tooling.

## Quick Navigation

- [Context Refresh Primitive](#context-refresh-primitive)
- [Filesystem-Scoped Audit Boundaries](#filesystem-scoped-audit-boundaries)
- [Prompt Output Contract](#prompt-output-contract)
- [Codex Task Prompt Format](#codex-task-prompt-format)
- [Repo Readiness Audit](#repo-readiness-audit)
- [Playbook Update](#playbook-update)
- [Notes vs Playbook Alignment Audit](#notes-vs-playbook-alignment-audit)
- [Deferred Notes Issue Promotion](#deferred-notes-issue-promotion)
- [AGENTS Update](#agents-update)
- [Workflow Scaffolding](#workflow-scaffolding)
- [Orchestration Handoff Prompt](#orchestration-handoff-prompt)
- [Implementation Delivery Footer](#implementation-delivery-footer)
- [PR Review](#pr-review)
- [PR Creation](#pr-creation)

## Context Refresh Primitive

Canonical guidance for the verified org context refresh pattern lives in
[`docs/context-refresh.md`](context-refresh.md). Use that page for when to run
it, how to generate the current-state snapshot, and how to interpret blocked,
unavailable, or stale output.

## Filesystem-Scoped Audit Boundaries

When a prompt drives an audit over filesystem data rather than a fixed list of
named files, define the intended dataset boundary before traversal begins.

- State the traversal boundary explicitly in the prompt.
- When the intended scope is a repository or working tree, treat the current
  working directory or project root as the complete dataset unless the prompt
  says otherwise.
- Do not traverse outside the intended root into sibling repositories or user
  directories unless the task explicitly asks for broader coverage.
- If the boundary is unclear, tighten the prompt or ask for clarification rather
  than widening the scan.

For multi-repo audits or workspace-wide operations, define workspace scope from
authoritative inventory sources before filesystem traversal. Reconcile
organization-level repository enumeration with explicit workspace manifests such
as `config/workspace-repos.txt`, and do not treat raw local checkout layout as
authoritative scope.

## Prompt Output Contract

Prompt, spec, plan, implementation brief, review brief, automation prompt, agent
instruction, and orchestration deliverables must be complete, self-contained,
and directly usable by default. A downstream agent should not need to
reconstruct the task from conversation history, hidden assumptions, earlier
partial output, or unstated repository context.

When prompt or instruction text is the deliverable, provide the full drop-in
version in one contiguous copyable block. If the human asks how to "add",
"incorporate", "fold in", or otherwise update something in an existing prompt,
spec, instruction, or task envelope, still return the full updated artifact by
default. Do not assume the human will manually stitch prior context or earlier
snippets into the final artifact. Do not split the artifact across multiple
fragments, follow-up messages, or continuation blocks unless the human
explicitly requests an incremental draft.

Avoid these forms unless explicitly requested:

- partial prompts
- continuation fragments
- "change X to Y" pseudo-prompts
- diffs
- partial edits
- delta-only responses
- targeted edits without the full updated artifact
- instructions that require the receiver to infer missing context from earlier
  discussion

Prefer copy/paste-safe output over terse conversational deltas for
agent-facing prompts. Preserve brevity only when it does not risk omitting
required context.

When a prompt is intended for implementation, include enough context for the
receiver to start safely: repository, working directory, canonical source,
interaction mode, goal, scope, constraints, command-form expectations,
validation path, delivery expectations, source evidence, and any blockers or
uncertainty.

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

### Codex Task Prompt Format Sections

- `Context`: repository, current situation, relevant background, and any known
  boundaries.
- `Goal`: the desired outcome in one or two clear sentences.
- `Scope`: optional when the goal is already precise; useful for naming included
  and excluded work.
- `Constraints`: guardrails that prevent overengineering, unrelated cleanup, and
  behavior drift.
- `Tasks`: ordered work items when the path matters.
- `Validation`: the canonical repo command, such as `make check`, when
  available, plus any explicitly advisory, CI-only, release-only, or manual
  review expectations.
- `Deliverable`: branch, commit, PR, review packet, or handoff expectations.

Keep prompts concise but complete. The goal is to remove ambiguity that would
cause retries, not to turn every task into a process document.

Any implementation task that modifies repository files MUST include the
Implementation Delivery Footer unless PR delivery is explicitly excluded.
Omitting the footer can leave delivery incomplete: changes made locally but not
pushed and opened for review in a PR.

### Optional: Trust and Evidence Context

Include trust and evidence context when prior work should shape how cautiously
Codex implements a task. This is useful when a prompt depends on earlier PRs,
notes, repeated patterns, or validation history, especially when confidence
level affects whether to preserve, extend, or re-check an approach.

This context can be short prose. Name the evidence that explains why the
approach is believed to work, such as prior validation, related artifacts, or an
informal confidence level. Do not add this section for simple tasks where it
would only repeat the main context.

Example prompt snippet:

```text
Context:
- Repository: knowledge-adapters
- Relevant background: Chaos replay fingerprints are already used during
  replay comparison, but the reporting text needs to be clearer.
- Additional context when helpful: This pattern was used in knowledge-adapters
  PR #248 and passed `make chaos-all`. Confidence is medium; behavior is stable
  but not yet promoted to the playbook. Related private staging notes mention
  chaos replay fingerprints.
```

### Codex Task Prompt Template

```text
Context:
- Repository: [repository]
- Relevant background: [short context]

Goal:
- [desired outcome]

Scope:
- In scope: [files, behavior, or workflow area]
- Out of scope: [explicit non-goals]

Constraints:
- Do not include unrelated changes or opportunistic cleanup.
- Make the smallest possible change that satisfies the goal.
- Default behavior must remain unchanged unless explicitly required.
- Follow existing repo patterns and validation paths.
- Do not silently skip required steps; report any blockers or incomplete work.

External State Verification:
- Determine the interaction mode before repo work begins. Implementation mode
  requires explicit user intent; ambiguous ctrl-alt-keith repo tasks default to
  review/audit or orchestration/prompt-authoring.
- Verify live external state, such as GitHub repository or pull request state,
  before relying on it.
- Run commands directly from the target repository and follow the command-form
  rule in `docs/repo-readiness.md`; do not wrap ordinary repo commands in
  `zsh`, `bash`, `sh`, or equivalent shell forms.
- Follow the direct PR inspection rule in `docs/review-packet.md` when a task
  asks for PR review, readiness, approval, or merge advice.
- Follow the public API baseline in `docs/engineering-baseline.md` when code,
  tests, docs, risks, or user-facing claims depend on external public API
  behavior.
- If live state cannot be verified, explicitly state that limitation and do not
  infer PR status, CI status, or branch protection from summaries or local
  files.

Parallel Execution Plan:
- Follow the parallel execution and merge-order rules in
  `docs/engineering-baseline.md`.
- Before parallel work begins, classify each task by lane and define merge order
  or state why merge order is flexible.
- Preserve one-repo/one-branch/one-PR scope integrity, workspace isolation,
  canonical validation, direct PR inspection, and authoritative source
  requirements.

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
- Ensure the PR contains only intended changes.
- Include a summary, validation results, and any residual risks.
```

### Codex Task Prompt Example

```text
Context:
- Repository: [application repository]
- The project already has a settings page and validation command.

Goal:
- Add a small user preference to the existing settings flow.

Scope:
- Reuse the current settings storage and UI patterns.
- Do not redesign the settings page or introduce a new state-management layer.

Constraints:
- Do not include unrelated changes or opportunistic cleanup.
- Preserve existing preference behavior unless explicitly required.
- Keep copy and controls consistent with the current interface.
- Report blockers or incomplete work instead of skipping required steps.

Tasks:
1. Inspect the settings implementation and tests.
2. Add the new preference through the smallest existing path.
3. Update focused tests or docs if needed.

Validation:
- Run `make check`.
- Report the actual result, including failure details if it fails.

Deliverable:
- Open a PR in the appropriate readiness state against `main` with summary,
  validation results, and residual risks.
```

### Model Selection And Cost Guidance

Use the strongest available model, such as a GPT-5.5-class model, for
implementation tasks, changes to existing systems, work with constraints such as
"must not change behavior," tasks that require tests to pass, and anything
involving state, caching, or edge cases.

Use cheaper or faster models for ideation, backlog generation, documentation
drafting, exploratory analysis, and throwaway work where a partial answer is
still useful.

Optimize for cost per successful outcome, not cost per token. Prefer fewer
high-quality runs over many partial attempts, keep prompts concise but complete
to reduce retries, avoid detail that does not affect the task, and include
validation steps so mistakes are caught before another run is needed.

Rule of thumb: prefer correctness per run over minimizing token cost.

## Repo Readiness Audit

### Repo Readiness Audit Use When

Use this prompt when a repository needs a quick readiness pass before new work,
automation, or process hardening.

### Repo Readiness Audit Required Inputs

- `repository`
- `playbook_reference`
- `repo_type` (`code`, `docs`, `workflow`, or `mixed`)
- `target_files` (optional; use `entire repository` when broad)

### Repo Readiness Audit Repo-Type Notes

- Code repos: emphasize validation paths, CI coverage, branch protection, and PR hygiene.
- Docs or playbook repos: emphasize scope clarity, canonical guidance placement, and markdown checks.
- Mixed repos: balance implementation safety with documentation accuracy and workflow consistency.

### Repo Readiness Audit Prompt

```text
Task:
Run a repo readiness audit for <repository>.

Inputs:
- Repository: <repository>
- Playbook reference: <playbook_reference>
- Repo type: <repo_type>
- Target files: <target_files>

Instructions:
- Inspect the current repository state and identify whether the repo is ready for normal feature work under the referenced playbook.
- Compare the repo's current workflow, validation path, branch hygiene, PR hygiene, and key documentation against the playbook reference.
- Focus on reusable workflow expectations rather than project-specific implementation choices.
- Call out missing or weak workflow elements only when they materially affect reliability, reviewability, or maintainability.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Do not invent repo facts that are not visible in the repository or supplied inputs.
- Do not propose repo-specific process rules as if they belong in the shared playbook.
- Define the filesystem dataset boundary when the audit relies on traversal;
  treat the current working directory or project root as the complete dataset
  when that is the intended scope.
- Do not traverse outside the intended root unless the task explicitly asks for
  broader filesystem coverage.
- Keep the audit concise, actionable, and evidence-based.

Validation:
- Verify whether a documented validation path exists and whether it appears current.
- Verify whether branch and PR practices are documented clearly enough for repeatable use.
- Verify whether workflow guidance is placed in the right files for this repo type.
- Verify whether any recommended follow-up is actually supported by the observed repo state.

Output format:
1. Readiness summary: one short paragraph.
2. Findings: a severity-ordered list with file references where possible.
3. Recommended next actions: a short numbered list of the highest-leverage fixes.
4. Playbook capture candidates: optional bullets only if a reusable cross-repo lesson is clearly present.
```

### Repo Readiness Audit Notes

Use this prompt for workflow shape and readiness, not for deep code review.

## Playbook Update

### Playbook Update Use When

Use this prompt when an evidence-supported workflow lesson from one or more
repositories should be promoted into the shared playbook as reusable guidance.

### Playbook Update Required Inputs

- `repository`
- `playbook_reference`
- `repo_type`
- `target_files` (usually the candidate playbook files to create or update)

### Playbook Update Repo-Type Notes

- Code repos: promote only rules that generalize beyond one implementation stack or codebase.
- Docs or playbook repos: tighten language, placement, and reuse boundaries; avoid duplicative rules.
- Mixed repos: separate reusable workflow guidance from implementation-specific or documentation-only details.

### Playbook Update Prompt

```text
Task:
Promote evidence-supported workflow rules into the playbook for <repository>.

Inputs:
- Source repository: <repository>
- Playbook reference: <playbook_reference>
- Repo type: <repo_type>
- Target files: <target_files>

Instructions:
- Review the existing playbook reference and the source repository context.
- Identify workflow rules or patterns that have concrete evidence from real use,
  review, repeated successful application, or merged repo work and are reusable
  across repositories.
- Update the playbook only where the lesson is durable, generic, and better captured centrally than locally.
- Prefer tightening or extending existing playbook guidance over adding fragmented one-off notes.
- Treat playbook updates and `AGENTS.md` rollout as separate work types.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Do not copy project-specific implementation details, repo names, or local exceptions into the playbook.
- Do not promote rules that are still speculative, unsupported by concrete
  evidence, or narrowly tied to one repository.
- Do not update `AGENTS.md` files as part of this playbook update, including
  the playbook repository's own `AGENTS.md`, unless the user explicitly
  authorizes that edit or the task's primary purpose is `AGENTS.md` update,
  rollout, or enforcement.
- Keep the change scoped to one logical documentation update.

Validation:
- Verify that each promoted rule is backed by concrete cited evidence, not only
  plausible reuse.
- Verify that any repo-local rule remains outside the shared playbook.
- Verify that the change does not treat canonical playbook updates as implicit
  `AGENTS.md` update or rollout.
- Verify that updated wording does not conflict with existing core playbook documents.
- Verify that the resulting file placement matches the playbook structure.
- Verify that the update includes a notes cleanup follow-up or explicitly says
  no notes cleanup is needed.

Output format:
- Proposed playbook changes: brief summary paragraph.
- Rules promoted: short bullets with rationale.
- Files to update: list of target files and why.
- Change classification: canonical playbook guidance only, unless there is
  explicit authorization for an `AGENTS.md` update/enforcement task.
- Validation notes: short bullets covering evidence, reuse, scope, conflict
  checks, rollout boundary, and notes cleanup.
- Open questions: only if a rule boundary is still unclear.
```

### Playbook Update Notes

This prompt is strongest after a rule has already survived real repo use, review, or CI friction.

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

Instructions:
- Audit the notes project against the playbook reference after promotion work has already been completed.
- Treat the notes project as a staging layer and the playbook reference as the canonical source for promoted workflow guidance.
- Review only files inside <notes_project_root>.
- For each relevant file, classify it as remove, trim, keep, or defer.
- Use remove when the file is fully superseded by canonical playbook guidance and no longer needs to remain in notes.
- Use trim when the file should stay but only after redundant or already-promoted material is removed.
- Use keep when the file still serves a valid notes-layer purpose without conflicting with the canonical playbook.
- Use defer when cleanup depends on a separate local decision, missing context, or unfinished follow-up work.
- Do not re-evaluate whether content should be promoted into the playbook. This audit is for cleanup and alignment after promotion, not for promotion decisions.
- When a file overlaps with promoted guidance, reference the canonical playbook location that now owns that guidance.
- Recommend only cleanup actions that can be justified from the observed notes files and the referenced playbook.

Constraints:
- Do not inspect, traverse, or recommend changes outside <notes_project_root>.
- Do not treat the notes repository as a second canonical source.
- Do not reopen already-settled promotion decisions during this audit.
- Keep the audit operational, concise, and file-specific.

Validation:
- Verify that each remove or trim recommendation points to the canonical playbook location that replaced or now owns the guidance.
- Verify that keep recommendations preserve only notes-layer material that still belongs in staging.
- Verify that defer recommendations explain the specific blocker or unresolved local dependency.
- Verify that the audit output can drive a cleanup pass followed by a re-audit to confirm convergence.

Output format:
1. Summary: one short paragraph describing the overall alignment state.
2. Per-file classification: a list of files with one of remove, trim, keep, or defer and a short rationale for each.
3. Cleanup recommendations: a short numbered list of the highest-leverage remove or trim actions, including canonical playbook references where applicable.
4. Re-audit trigger: one short sentence stating when to rerun the audit to confirm convergence.
```

### Notes vs Playbook Alignment Audit Notes

This audit is for cleanup, not promotion. Run it after promotion work, then use a
follow-up re-audit to confirm the notes set has converged on the playbook as the
canonical source.

## Deferred Notes Issue Promotion

### Deferred Notes Issue Promotion Use When

Use this prompt when notes or deferred ideas should be reviewed for possible
promotion into bounded GitHub issues without turning every captured thought into
backlog work.

### Deferred Notes Issue Promotion Required Inputs

- `source_material_root`
- `target_repositories`
- `duplicate_check_scope` (for example open issues, recent closed issues, or a
  named backlog board)
- `arc_suggestions` (optional; use `none` when not needed)

### Deferred Notes Issue Promotion Repo-Type Notes

- The source material stays a staging layer, not a commitment queue.
- Target repositories own actionable issues only when the work is ready for a
  bounded repo change.
- Cross-repo workflow lessons should remain playbook candidates until supported
  by repo evidence; do not skip straight from raw notes to playbook updates.

### Deferred Notes Issue Promotion Prompt

```text
Task:
Review deferred notes and propose or create bounded GitHub issues where the
work is ready.

Inputs:
- Source material / notes root: [source_material_root]
- Target repository or repositories: [target_repositories]
- Duplicate check scope: [duplicate_check_scope]
- Optional arc suggestions: [arc_suggestions]

Instructions:
- Review the source material inside [source_material_root] and identify notes
  or deferred ideas that may be ready for issue promotion.
- Distinguish among raw notes, deferred ideas, bounded repo issues, and
  playbook candidates.
- Keep raw notes as raw notes when they are still capture, rough thinking, or
  incomplete observations.
- Keep items as deferred ideas when they are still speculative, blocked,
  duplicated, or too broad for one bounded repo change.
- Promote an item into a bounded repo issue only when repeated friction, clear
  value, or readiness for action makes repo work justified now.
- Check [duplicate_check_scope] before proposing or creating any issue.
- Group closely related notes by theme instead of creating one issue per line
  item.
- For each proposed issue, name the owning repository, define a narrow scope,
  and include concise acceptance criteria.
- When useful, suggest an optional arc that groups several related issues into
  a coherent sequence, but do not force arc structure when standalone issues are
  clearer.
- Identify playbook candidates separately when the note points to a possible
  reusable rule that still needs concrete repo evidence before promotion.

Constraints:
- Do not create issues for every interesting idea.
- Do not reopen duplicate or already-covered backlog items.
- Do not turn vague themes into oversized umbrella issues.
- Do not treat deferred-note triage as a general backlog-management rewrite.
- Keep recommendations concise, operational, and tied to visible source
  material.

Validation:
- Verify that each proposed or created issue maps to a specific repository.
- Verify that each issue is small enough to support a focused PR or short arc.
- Verify that acceptance criteria describe what done looks like.
- Verify that grouped items belong together and are not masking unrelated work.
- Verify that any playbook candidate is called out separately from repo issue
  promotion.

Output format:
1. Triage summary: one short paragraph.
2. Keep deferred: short bullets for items that should remain notes or deferred
   ideas.
3. Proposed or created issues: short bullets with repository, scope,
   acceptance criteria, and duplicate-check result.
4. Optional arcs: short bullets only when grouping adds real clarity.
5. Playbook candidates: optional bullets for reusable lessons that should wait
   for repo evidence.
```

### Deferred Notes Issue Promotion Notes

Use this prompt to decide when deferred material should become repo work. Use
the notes cleanup audit separately after promotion or implementation work lands.

## AGENTS Update

### AGENTS Update Use When

Use this prompt when a repository's `AGENTS.md` needs to be synced with the shared
playbook while preserving repo-local execution details.

### AGENTS Update Required Inputs

- `repository`
- `playbook_reference`
- `repo_type`
- `target_files` (typically `AGENTS.md` and any closely related repo-local docs)

### AGENTS Update Repo-Type Notes

- Code repos: keep repo-local sections focused on validation commands, file placement rules, and release or merge boundaries.
- Docs or playbook repos: keep repo-local sections focused on documentation scope, canonical file locations, and markdown workflow.
- Mixed repos: keep local rules narrow and explicit where docs and implementation practices differ.

### AGENTS Update Prompt

```text
Task:
Update AGENTS guidance for <repository> so it stays aligned with the shared playbook.

Inputs:
- Repository: <repository>
- Playbook reference: <playbook_reference>
- Repo type: <repo_type>
- Target files: <target_files>

Instructions:
- Review the repository's current AGENTS guidance and the referenced playbook.
- Keep playbook-level rules in the playbook and repo-local execution rules in AGENTS.
- Update AGENTS so it clearly acts as the thin repo-local execution layer on top of the shared playbook.
- Preserve useful repo-specific instructions such as validation commands, file placement rules, and local workflow constraints.
- Treat this as explicit rollout or enforcement work for the named repository,
  not as a side effect of a generic playbook update.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Explicitly distinguish shared playbook rules from repo-local rules.
- Do not duplicate broad workflow guidance in AGENTS when the playbook already covers it.
- Do not remove necessary repo-local instructions that the playbook cannot supply.
- For global rollout, keep one repository, one branch, and one pull request per
  target repository unless the target repository's documented process says
  otherwise.
- Keep the document concise, operational, and easy to maintain.

Validation:
- Verify that AGENTS points readers to the relevant playbook documents instead of restating them.
- Verify that repo-local rules are specific to this repository's files, validation path, and workflow shape.
- Verify repeated AGENTS wording by authority ownership and operational effect before trimming or promoting it; preserve necessary repo-local execution constraints, and remove broad playbook restatements.
- Verify that command-form guidance preserves the playbook's preflight rule:
  shell-wrapped commands are used only when shell semantics are required, and
  ordinary repository commands are rewritten to direct argv form before
  execution.
- Verify that the updated AGENTS file does not introduce conflicting guidance relative to the playbook.
- Verify that the document still works as a practical execution layer for this repo type.

Output format:
1. AGENTS change summary: short paragraph.
2. Shared-vs-local split: bullets showing what belongs in the playbook and what stays local.
3. Change classification: explicitly authorized `AGENTS.md` update/enforcement
   for the named repository.
4. Files updated: list of touched files.
5. Validation notes: short bullets.
6. Residual gaps: optional bullets only if something still needs a human decision.
```

### AGENTS Update Notes

If a rule feels important but still repo-specific, keep it local and avoid promoting it automatically.

## Workflow Scaffolding

### Workflow Scaffolding Use When

Use this prompt when a repository needs baseline workflow scaffolding such as PR
templates, issue templates, release guidance, or related lightweight process docs.

### Workflow Scaffolding Required Inputs

- `repository`
- `playbook_reference`
- `repo_type`
- `target_files` (for example PR templates, issue templates, release docs, or workflow docs)

### Workflow Scaffolding Repo-Type Notes

- Code repos: bias toward review quality, validation visibility, release safety, and clear issue intake.
- Docs or playbook repos: bias toward scope control, content quality checks, and change-summary prompts.
- Mixed repos: ensure templates cover both documentation and implementation deltas without overfitting either side.

### Workflow Scaffolding Prompt

```text
Task:
Add or refine workflow scaffolding for <repository>.

Inputs:
- Repository: <repository>
- Playbook reference: <playbook_reference>
- Repo type: <repo_type>
- Target files: <target_files>

Instructions:
- Inspect the repository's current workflow scaffolding.
- Add or update only the smallest set of files needed to support clear PRs, issue intake, and release or change-management guidance.
- Keep templates generic enough to support repeated use in this repository without embedding one-off project details.
- Align the scaffolding with the referenced playbook and the repository's actual workflow maturity.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Do not add heavyweight process for a repository that only needs a lightweight baseline.
- Do not create templates that imply unsupported validation, release, or ownership behavior.
- Keep wording direct and operational.

Validation:
- Verify that each scaffolded file has a clear job and does not duplicate another file.
- Verify that placeholders and instructions match the repository's real workflow.
- Verify that markdown-facing placeholders use lint-safe forms such as `[issue number]`
  or backticked tokens instead of angle-bracket placeholders that markdown tooling
  can interpret as inline HTML.
- Verify that release guidance stays human-gated unless the repository already documents automation.
- Verify that the resulting scaffolding is appropriate for the stated repo type.

Output format:
1. Scaffolding summary: short paragraph.
2. Files to create or update: bullets with purpose.
3. Design choices: short bullets explaining repo-type-specific decisions.
4. Validation notes: short bullets covering fit, scope, and realism.
5. Follow-up items: optional bullets for later hardening.
```

### Workflow Scaffolding Notes

Prefer a minimal baseline that can be extended later over an elaborate template set that no one will keep current.

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
Task:
[clear action the downstream agent should complete]

Working directory:
[absolute or repo-relative working directory]

Repository:
[repository]

Canonical sources:
- Shared workflow policy: [canonical_source]
- Repo-local execution guidance: [repo-local AGENTS.md or equivalent]
- Source evidence: [source_evidence]

Required startup:
1. Read the shared playbook startup guidance first.
2. Read the repo-local AGENTS.md before acting.
3. Select the interaction mode before acting.
4. Identify the canonical source for reusable workflow rules.
5. Confirm command form for ordinary repo commands.
6. Identify the canonical validation path.
7. Act only after these checks are clear, or report the blocker.

Interaction mode:
- [implementation, review/audit, or orchestration/prompt-authoring]

Goal:
- [desired outcome]

Context:
- [relevant facts discovered by the orchestrator]
- [issue, PR, evidence note, or prior-art context the receiver needs]

Scope:
- In scope: [files, behavior, docs, or workflow area]
- Out of scope: [explicit exclusions]

Constraints:
- Keep changes minimal, scoped, and structurally local.
- Do not include unrelated cleanup.
- Do not rely on noncanonical staging, runtime, generated, or local instruction
  surfaces as policy unless the rule has been promoted into the canonical
  source.
- Use direct command execution for ordinary `git`, `gh`, `make`, `python`,
  repo-local script, and tool commands.
- Do not use `zsh -lc`, `bash -lc`, `sh -c`, or equivalent shell wrappers for
  ordinary repo commands.
- Use shell wrappers only when shell syntax is genuinely required.
- Report blockers, validation failures, residual risks, and uncertainty.

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

Deliverable:
- [complete expected final output]
- Provide the full drop-in artifact by default, even when the task asks to add,
  incorporate, or fold new material into existing prompt or instruction text.
- Do not provide partial prompts, continuation fragments, diffs, partial edits,
  delta-only responses, targeted edits without the full updated artifact, or
  "change X to Y" pseudo-prompts unless explicitly requested.
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
- Run ordinary `git`, `gh`, `make`, `python`, repo-local script, and tool
  commands directly from the target repository; reserve shell wrapping for
  commands that genuinely require shell syntax.
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

Instructions:
- Unless Summary-only requested is `yes`, inspect the PR directly before giving
  any review, approval, readiness, or merge recommendation.
- Stay in review/audit mode. Do not implement changes while performing the PR
  review unless the human explicitly changes the task to implementation.
- Treat user-provided summaries as navigation and context only, not review
  evidence.
- Inspect the PR title and body, changed files, relevant diffs, CI and check
  status, mergeability, and scope against the task or issue where those inputs
  are available.
- If direct PR access is unavailable and Summary-only requested is not `yes`,
  stop the PR review, state that direct PR access is unavailable, and ask for
  access to be restored or for the PR and files to be made available.
- Do not claim the PR is safe to merge, ready to merge, or approved without
  direct evidence from the PR itself.
- If Summary-only requested is `yes`, state that the response is based only on
  the supplied summary and does not establish merge readiness.

Output format:
1. Review findings: severity-ordered findings with file or PR references where
   possible.
2. Scope and evidence notes: concise notes on inspected PR surface, CI/checks,
   mergeability, and task fit.
3. Recommendation: `ready to merge`, `needs decision`, or `blocked`, only when
   direct PR evidence supports it.
```

## PR Creation

### PR Creation Use When

Use this prompt when changes already exist in a working tree and the next step is to
wrap them in a clean branch, commit, push, and PR flow.

### PR Creation Required Inputs

- `repository`
- `playbook_reference`
- `repo_type`
- `target_files` (the intended diff scope, if known)

### PR Creation Repo-Type Notes

- Code repos: emphasize test evidence, behavioral risk, and keeping the diff narrowly scoped.
- Docs or playbook repos: emphasize content scope, placement, and markdown or link checks.
- Mixed repos: explain both implementation and documentation effects clearly in the PR summary.

### PR Creation Prompt

```text
Task:
Create a pull request for existing changes in <repository>.

Inputs:
- Repository: <repository>
- Playbook reference: <playbook_reference>
- Repo type: <repo_type>
- Target files: <target_files>

Instructions:
- Inspect the current git state, existing diff, and branch context.
- Confirm that the intended changes form one logical PR and identify any unrelated files or accidental scope.
- If needed, create a fresh branch from current `origin/main`, keep only the
  intended diff, and prepare a clear commit and PR description.
- Summarize the change in a way that supports quick human review and accurate merge decisions.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Do not widen scope with opportunistic cleanup or unrelated fixes.
- Do not hide uncertainty about validation, branch ancestry, or diff hygiene.
- Keep commit and PR messaging concise, specific, and aligned with the repository context.

Validation:
- Verify that the diff contains only the intended files and changes.
- Verify that the branch is suitable for review, anchored to the intended
  mainline state, and checked for current mergeability before PR.
- Verify that the reported validation matches what was actually run or observed.
- Verify that the PR summary explains user-facing, workflow, or documentation impact as appropriate for the repo type.

Output format:
1. PR scope summary: short paragraph.
2. Included files: bullet list of the intended diff.
3. Validation notes: short bullets with any gaps called out plainly.
4. Proposed commit message: one line.
5. Proposed PR title and body: ready to use.
```

### PR Creation Notes

This prompt is for packaging existing work cleanly, not for doing the implementation itself.
For implementation prompts that are expected to ship repo changes, append the
Implementation Delivery Footer instead of assuming branch and PR delivery are
implied.
