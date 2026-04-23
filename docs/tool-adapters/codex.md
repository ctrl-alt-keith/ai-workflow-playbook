# Codex Adapter

This document explains how Codex maps onto the core playbook. It is adapter-specific guidance, not part of the core operating model.

## Codex-Specific Quirks

- Codex can move quickly from brief to implementation, so phase boundaries need to be stated explicitly
- Codex benefits from narrow, well-shaped tasks with clear validation targets
- Codex can produce fluent output that still needs human judgment on scope, tradeoffs, and completeness
- small tasks stay small when they extend a single existing seam or module, avoid cross-cutting changes, and avoid new abstractions unless clearly required

Tasks that extend a clean documented seam are more likely to remain small. Tasks that must create or reshape seams tend to expand and should be treated that way during estimation.

## Project-Context Check

- before making changes, confirm the current Codex project or working context matches the intended task target
- if the task appears to target a different repository, a new repository, or a cross-repo comparison while the current context is repo-scoped, pause and confirm with the human before proceeding
- when multiple Codex projects, worktrees, or isolated directories are active, treat repository identity and execution-container identity as separate checks: confirm that the active execution container belongs to the repository named in the task before making changes; do not treat directory naming or a clean checkout alone as proof; if the active project or worktree does not match the intended repository, pause and switch before proceeding
- keep this lightweight for normal same-repo work; a quick sanity check is enough
- at the start of repo-scoped work, inspect the current git state
- for every new repo-scoped arc, fetch `origin/main` once at the start and treat that fetched tip as the canonical base for the run
- only remain on or reuse the current branch when the task explicitly says to continue that branch or PR
- otherwise, create a new branch for the arc
- if the active worktree or directory is not on up-to-date `main`, switch or recreate the branch from current `origin/main` before making changes
- for medium or large arcs, verify the working branch is based on current `origin/main` before meaningful edits begin
- after the run, check whether the resulting branch or PR is still mergeable against current `main`; if upstream moved in the meantime, treat that as a final-state mergeability check rather than a reason to restart or rebase mid-run by default
- make exceptions only when the task explicitly requires rebasing or when a real conflict or blocker appears that prevents finishing the requested work cleanly
- if normalization is unsafe or the state is unclear, pause and report rather than forcing cleanup
- when parallel repo-scoped work targets the same repository, prefer one worktree per issue or task from current `origin/main`; keep the main checkout clean and on `main`, do not run concurrent arcs against the same checkout, and treat each worktree as its own execution container with its own branch, validation run, and PR or review surface
- before starting a same-repo worktree batch, inspect `git worktree list` and
  the underlying worktree metadata so stale entries from an earlier attempt do
  not confuse setup or cleanup
- when checking a worktree experiment at the end, distinguish the worktrees that
  belong to the experiment from unrelated pre-existing entries so success does
  not depend on an artificially empty global worktree list

## Local Permissions Model

Codex operates inside a local permissions model. Some actions require approval, especially for network access, privileged writes, or potentially destructive commands.

Treat permission boundaries as part of the execution environment, not as incidental friction. If a task depends on elevated access, surface that early and keep the requested action narrowly scoped.

Worktree cleanup can require elevated permission even when the visible worktree
paths sit inside the repository, because Git also updates internal worktree
metadata outside the leaf directories being removed.

## Autonomous Lane

Codex should continue executing without pausing for human input when:

- the task scope is clear and bounded
- the current repo or project context matches the intended target
- there is no meaningful ambiguity about the requested outcome
- a validation path is available and the relevant checks pass
- no security-, policy-, release-, tag-, or merge-sensitive decision is required

This is a low-risk execution lane. It is not a reason to widen scope, reinterpret intent, or take ownership of human-gated decisions.

When an existing documented seam already fits the task, prefer extending it over introducing a new abstraction. For small or medium tasks, do not invent a new layer when a clean extension point already exists.

Do not turn small or medium tasks into "while I'm here" refactors. Keep changes within the requested scope unless a stop condition is triggered.

## Stop Conditions

Codex should pause and ask for human input when:

- the repo or project context appears to be wrong or mismatched
- the requested scope is ambiguous or appears to have shifted
- more than one valid implementation path exists and the choice depends on human judgment
- validation fails in a way that suggests broader changes than the requested task
- the next step is a merge, release, or tag decision
- the work touches sensitive auth, secrets, permissions, or policy interpretation

## PR Expectations

- keep PRs phase-shaped and reviewable
- summarize intent, scope, validation, and known risks
- make PRs ready for review by default when the phase objective is met
- use draft PRs only for intentionally incomplete work or early feedback
- when refining an active PR within the same arc, update the existing branch and PR rather than opening a new PR; open a new PR only when the work changes phase, scope, or review surface
- avoid bundling unrelated cleanup into the same PR
- before calling the work complete, verify the PR diff contains only the intended arc; if `main` moved underneath the branch and overlap occurred, sync with current `main`, resolve conflicts, and rerun validation; if the branch carries unrelated history, rebuild the work onto a clean branch from current `main`

When behavior or supported capability changes, quickly check the existing docs for that area and update any statements that would become inaccurate before calling the work complete.

## CI Expectations

- run the repo-local validation path when it exists
- attempt local validation when the needed tools are clearly available; if a tool is missing locally, do not treat that as a failure and rely on required CI checks as the source of truth
- in this repo, the current minimal CI path is the `markdownlint` GitHub Actions check
- report clearly when no local validation path exists
- until a formal validation path exists, use internal consistency review, path checks, and scope review
- treat passing CI as necessary but not sufficient
- use hardening to close gaps exposed by CI, review, or edge cases

## Git And GitHub Workflow Notes

- use a fresh branch for each lifecycle phase after merge
- keep commit messages and PR titles clear and phase-oriented
- adapt branch, commit, and PR naming to repo context: in playbook or workflow repos, use Codex-explicit naming such as `codex/<topic>` and `[codex] docs: ...` to make automation-driven changes obvious; in product or implementation repos, follow standard development naming such as `feat/<topic>`, `fix/<topic>`, `feat: ...`, and `fix: ...`
- preserve a clean review narrative rather than one long-running branch
- open a new PR when the work changes phase or review surface
- for same-repo worktree batches, prefer opening PRs serially unless parallel
  creation materially reduces latency and the connector flow is known to be
  stable

## Repo Baseline

After bootstrap, configure these as the basic merge-safety baseline:

- protect `main`
- require PR-based changes to `main`
- require CI or checks before merge when available
- keep release and tag actions human-gated

This repository now enforces the `main` branch-protection portion of that baseline, including the required `markdownlint` check. Release and tag actions remain human-gated as an operational rule rather than something enforced by branch protection. Apply the same baseline after bootstrap when creating a new repo.

Codex should follow the core model, but this adapter exists to document the tooling realities that shape how the model is applied in practice.
