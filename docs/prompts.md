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
- [Repo Readiness Audit](#repo-readiness-audit)
- [Playbook Update](#playbook-update)
- [Notes vs Playbook Alignment Audit](#notes-vs-playbook-alignment-audit)
- [Deferred Notes Issue Promotion](#deferred-notes-issue-promotion)
- [AGENTS Update](#agents-update)
- [Workflow Scaffolding](#workflow-scaffolding)
- [Implementation Delivery Footer](#implementation-delivery-footer)
- [PR Creation](#pr-creation)

## Context Refresh Primitive

Canonical guidance for the validated org context refresh pattern lives in
[`docs/context-refresh.md`](context-refresh.md). Use that page for when to run
it, required verification inputs, failure handling, and the self-contained
prompt block.

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

Use this prompt when a validated workflow lesson from one or more repositories should
be promoted into the shared playbook as reusable guidance.

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
Promote validated workflow rules into the playbook for <repository>.

Inputs:
- Source repository: <repository>
- Playbook reference: <playbook_reference>
- Repo type: <repo_type>
- Target files: <target_files>

Instructions:
- Review the existing playbook reference and the source repository context.
- Identify workflow rules or patterns that have already been validated in practice and are reusable across repositories.
- Update the playbook only where the lesson is durable, generic, and better captured centrally than locally.
- Prefer tightening or extending existing playbook guidance over adding fragmented one-off notes.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Do not copy project-specific implementation details, repo names, or local exceptions into the playbook.
- Do not promote rules that are still speculative, unvalidated, or narrowly tied to one repository.
- Keep the change scoped to one logical documentation update.

Validation:
- Verify that each promoted rule is reusable across at least two plausible repository contexts.
- Verify that any repo-local rule remains outside the shared playbook.
- Verify that updated wording does not conflict with existing core playbook documents.
- Verify that the resulting file placement matches the playbook structure.

Output format:
1. Proposed playbook changes: brief summary paragraph.
2. Rules promoted: short bullets with rationale.
3. Files to update: list of target files and why.
4. Validation notes: short bullets covering reuse, scope, and conflict checks.
5. Open questions: only if a rule boundary is still unclear.
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
- Cross-repo workflow lessons should remain playbook candidates until validated
  by repo work; do not skip straight from raw notes to playbook updates.

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
  reusable rule that still needs repo validation before promotion.

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
   for repo validation.
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

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Explicitly distinguish shared playbook rules from repo-local rules.
- Do not duplicate broad workflow guidance in AGENTS when the playbook already covers it.
- Do not remove necessary repo-local instructions that the playbook cannot supply.
- Keep the document concise, operational, and easy to maintain.

Validation:
- Verify that AGENTS points readers to the relevant playbook documents instead of restating them.
- Verify that repo-local rules are specific to this repository's files, validation path, and workflow shape.
- Verify that the updated AGENTS file does not introduce conflicting guidance relative to the playbook.
- Verify that the document still works as a practical execution layer for this repo type.

Output format:
1. AGENTS change summary: short paragraph.
2. Shared-vs-local split: bullets showing what belongs in the playbook and what stays local.
3. Files updated: list of touched files.
4. Validation notes: short bullets.
5. Residual gaps: optional bullets only if something still needs a human decision.
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

## Implementation Delivery Footer

### Implementation Delivery Footer Use When

Append this footer to implementation prompts when the task is expected to make
repo changes and deliver them through the normal branch, commit, push, and PR
flow.

### Implementation Delivery Footer Do Not Use When

Do not append this footer for exploration, design, or review-only tasks unless
they are also expected to make and deliver repo changes.

### Implementation Delivery Footer Snippet

```text
Delivery:
- Create a focused branch.
- Stage only the relevant changes.
- Commit with a clear message.
- Push the branch.
- Open a PR against the intended base branch, usually `main`.
- Report the PR link, files changed, and validation results.
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
- If needed, create a fresh branch from current main, keep only the intended diff, and prepare a clear commit and PR description.
- Summarize the change in a way that supports quick human review and accurate merge decisions.

Constraints:
- Treat <playbook_reference> as the canonical source for cross-repo workflow rules.
- Do not widen scope with opportunistic cleanup or unrelated fixes.
- Do not hide uncertainty about validation, branch ancestry, or diff hygiene.
- Keep commit and PR messaging concise, specific, and aligned with the repository context.

Validation:
- Verify that the diff contains only the intended files and changes.
- Verify that the branch is suitable for review and based on an appropriate mainline state.
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
