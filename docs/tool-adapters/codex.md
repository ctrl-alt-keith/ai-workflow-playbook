# Codex Adapter

This document explains how Codex maps onto the core playbook. It is adapter-specific guidance, not part of the core operating model.

## Codex-Specific Quirks

- Codex can move quickly from brief to implementation, so phase boundaries need to be stated explicitly
- Codex benefits from narrow, well-shaped tasks with clear validation targets
- Codex can produce fluent output that still needs human judgment on scope, tradeoffs, and completeness
- small tasks stay small when they extend a single existing seam or module, avoid cross-cutting changes, and avoid new abstractions unless clearly required

Tasks that extend a clean documented seam are more likely to remain small. Tasks that must create or reshape seams tend to expand and should be treated that way during estimation.

## Interaction Mode Selection

Before repo-scoped work, apply the interaction mode preflight in
[`repo-readiness.md`](../repo-readiness.md#interaction-mode-preflight).

Codex should not treat vague repair language as permission to mutate a repo
when the surrounding context indicates advisory review, audit, orchestration,
or prompt authoring. In ctrl-alt-keith workflows, ambiguous repo tasks default
to read-only review/audit or orchestration/prompt-authoring unless the human
explicitly asks Codex to implement, commit, push, or open the PR.

When acting in orchestration/prompt-authoring mode, Codex should still inspect
enough live repository, issue, pull request, and documentation context to write
a complete downstream prompt. The deliverable is the prompt or handoff itself,
not a branch or PR, unless the human separately asks Codex to implement the
change.

## Project-Context Check

- before making changes, confirm the current Codex project or working context matches the intended task target
- if the task appears to target a different repository, a new repository, or a cross-repo comparison while the current context is repo-scoped, pause and confirm with the human before proceeding
- when multiple Codex projects, worktrees, or isolated directories are active, treat repository identity and execution-container identity as separate checks: confirm that the active execution container belongs to the repository named in the task before making changes; do not treat directory naming or a clean checkout alone as proof; if the active project or worktree does not match the intended repository, pause and switch before proceeding
- keep this lightweight for normal same-repo work; a quick sanity check is enough
- at the start of repo-scoped work, inspect the current git state
- for every new repo-scoped arc, fetch current `origin/main` at task start and
  anchor implementation to that fetched baseline
- only remain on or reuse the current branch when the task explicitly says to continue that branch or PR
- otherwise, create a new branch for the arc
- if the active worktree or directory is not on up-to-date `main`, switch or recreate the branch from current `origin/main` before making changes
- for medium or large arcs, verify the working branch is based on current `origin/main` before meaningful edits begin
- before opening or updating the PR, verify whether the resulting branch is
  mergeable against current `main`
- distinguish local execution state from remote PR state: a clean local branch means the run completed cleanly against its anchored base, while GitHub mergeability reflects the current remote state after newer `main` movement, required checks, and review requirements
- update or rebase only when there is a conflict, overlapping upstream change,
  repo policy requirement, or explicit human request; rerun canonical validation
  after any update or rebase
- do not treat transient GitHub `BLOCKED` or pending states as mid-run failures by default; inspect whether the cause is pending checks, pending review requirements, dependency ordering, or a true merge conflict, then wait or act accordingly
- if normalization is unsafe or the state is unclear, pause and report rather than forcing cleanup

## Workspace Isolation

- read-only exploration, audit, or review work may use the active checkout when
  no repo changes are required
- for repo-changing implementation work, always use `git worktree` from the
  target repository and place every repo-changing worktree under
  `<repo>/.worktrees/`; do not create sibling repo directories, sibling
  worktree directories, or ad hoc full-copy repositories under the project root
- before creating or reusing a repo-changing worktree, run `git worktree list`,
  select a repo-local `.worktrees/...` path, and report that selected path in
  setup or delivery notes
- when parallel repo-scoped work targets the same repository, use one worktree
  per issue or task from current `origin/main`, with each worktree located
  under the repository's `.worktrees/` directory; keep the main checkout clean
  and on `main`, do not run concurrent arcs against the same checkout, and treat
  each worktree as its own execution container with its own branch, validation
  run, and PR or review surface
- before launching a Codex parallel batch, apply the engineering baseline's
  parallel execution guidance: classify each task by lane, confirm the work can
  be separated by repository, file area, or risk surface, and define the merge
  order before work starts
- do not run parallel Codex arcs across shared mutation paths, release state,
  schema contracts, or fragile overlapping files unless a clear merge order and
  dependency chain have been stated up front
- if Codex PRs in a parallel batch overlap unexpectedly, pause the batch,
  update or rebase in the intended order, rerun the repository's canonical
  validation in each affected worktree, and inspect the current PR surfaces
  before recommending or performing any merge
- if `<repo>/.worktrees/` cannot be used, stop before making changes and report
  why the required repo-local worktree location is not possible, what
  alternative workspace is proposed, where it would be created, and how it will
  be cleaned up
- wait for explicit human approval before proceeding with a full copy or clone
- before starting a same-repo worktree batch, inspect `git worktree list` and
  the underlying worktree metadata so stale entries from an earlier attempt do
  not confuse setup or cleanup
- reuse an existing same-repo worktree only when it is clearly the same active
  issue, PR, or arc and its state is still clean and intelligible; otherwise
  recreate from current `origin/main`, with a bias toward clarity over clever
  reuse
- recreate rather than recover when the worktree belongs to a different arc,
  the state is stale or unclear, or cleanup and recovery would be more
  confusing than starting fresh
- when checking a worktree experiment at the end, distinguish the worktrees that
  belong to the experiment from unrelated pre-existing entries so success does
  not depend on an artificially empty global worktree list
- treat worktree cleanup as successful when the experiment or task worktrees
  created for that run are removed or clearly accounted for
- if removal is blocked or deferred, report it clearly, avoid deleting
  unrelated worktrees, and leave the repo in a known, intelligible state
- when a PR created from a Codex worktree is merged and the worktree is no
  longer needed, remove the worktree and prune stale worktree metadata when
  appropriate

## GitHub Access Preflight

- before repo- or PR-dependent work, verify GitHub access instead of relying on
  cached context, summaries, or local branch state
- apply the command-form guidance in
  [`repo-readiness.md`](../repo-readiness.md#command-form-and-intent-visibility):
  keep normal repository operations in their structurally minimal form, and
  reserve shell wrapping for operations that need shell semantics
- prefer clear direct invocations for normal repository operations, such as
  `git status`, `git merge --ff-only origin/main`, `gh repo view`,
  `gh pr view`, `make check`, `python ...`, and repo-local scripts
- for standard Git and GitHub CLI flows, use `git` and `gh` directly rather
  than alternate APIs, helper scripts, connectors, or tool substitutions unless
  the task requires a non-CLI capability or direct CLI access is blocked and
  the fallback is reported
- when the execution tool supports native argv arrays, prefer direct argv forms
  such as `["git", "status"]` or `["gh", "pr", "view", "145"]`
- if the execution surface defaults to shell or login-shell behavior, disable
  that behavior for `git` and `gh` where supported, using options such as
  `shell=false`, `login=false`, `use_shell=false`, or the platform-native
  equivalent
- do not use `zsh -lc`, `bash -lc`, `sh -c`, or equivalent wrapper forms for
  ordinary repo commands
- before executing a shell-wrapped command, perform a command-form preflight:
  decide whether shell semantics are genuinely required; if not, rewrite the
  operation into direct argv form before execution
- treat pipes, redirects, glob expansion, command chaining, shell builtins,
  inline environment assignment, and compound shell conditionals as examples of
  shell semantics that can justify a wrapper when no direct command form is
  sufficient
- when a `git` or `gh` operation needs shell composition, keep the wrapped
  command narrow enough that the requested operation remains visible to local
  approval and review surfaces
- examples: use `git status`, not `zsh -lc 'git status'`; use `make check`, not
  `bash -lc 'make check'`; use `gh pr view 145`, not
  `sh -c 'gh pr view 145'`
- when the human posts a GitHub PR link, provides a PR number, or asks to
  review, check, assess, approve, or comment on a PR, Codex must use connector
  inspection and must open the PR through the GitHub connector before giving
  review feedback
- local checkouts, `git diff`, and `gh` commands may be used as supplemental
  evidence for PR review, but they must not replace connector inspection
- treat "open the PR" as read-only connector inspection, not opening the PR in
  a browser and not submitting a GitHub review
- treat "review this PR" as inspect the PR and provide feedback in chat, unless
  the human explicitly asks to post the review to GitHub
- Codex must inspect the actual PR metadata, title and body, changed files,
  relevant diffs, comments and unresolved review discussion, CI and check
  status, mergeability, and scope against the task or issue where those inputs
  are available
- treat user-provided PR summaries, pasted titles, local path snippets, and
  copied diff excerpts as navigation and context only, not review evidence,
  when a PR link or PR number is available
- Codex must not mutate the PR: do not submit, approve, request changes,
  comment on, label, merge, close, or otherwise change the PR unless the human
  explicitly asks for that GitHub action
- if GitHub connector access is unavailable or declined for a PR review, stop
  the review, state that connector access is unavailable, and provide only
  clearly caveated feedback from the information already present
- if the required `gh` commands fail on a non-review PR task, stop and report
  the access or state blocker instead of inferring remote state
- do not assume mergeability, checks, or branch protection without verification

## Public API Baseline Check

- before changing code, tests, docs, risks, or user-facing claims that depend on
  external public API behavior, verify the current behavior from official
  sources
- use official docs, API references, SDK docs, provider changelogs, or official
  release notes as the baseline; do not rely on model memory or inferred
  provider behavior where official docs are available
- include the verified source in PR notes or docs when it materially supports
  the change
- if official docs are ambiguous or unavailable for the behavior, state that
  limitation and avoid encoding guessed guarantees or limitations
- skip this check for purely internal refactors that do not depend on external
  API semantics

## Local Permissions Model

Codex operates inside a local permissions model. Some actions require approval, especially for network access, privileged writes, or potentially destructive commands.

Treat permission boundaries as part of the execution environment, not as incidental friction. If a task depends on elevated access, surface that early and keep the requested action narrowly scoped.

Worktree cleanup can require elevated permission even when the visible worktree
paths sit inside the repository, because Git also updates internal worktree
metadata outside the leaf directories being removed.

### Sandbox Writable Roots

In `workspace-write` mode, do not assume
`[sandbox_workspace_write].writable_roots` is the complete effective writable
root list. Codex may also have implicit writable roots from the active project
root and platform temp locations such as `/tmp` or `$TMPDIR`; on macOS, `/tmp`
may appear in diagnostics as `/private/tmp`.

Inspect the effective policy when sandbox boundaries matter:

```sh
codex debug prompt-input effective-sandbox-check
```

For stricter isolation, local Codex config can explicitly exclude the implicit
temp roots:

```toml
[sandbox_workspace_write]
exclude_slash_tmp = true
exclude_tmpdir_env_var = true
```

Then verify the empty-explicit-roots case so temp roots do not silently
reappear:

```sh
codex debug prompt-input -c 'sandbox_workspace_write.writable_roots=[]' effective-sandbox-check
```

Use repo-local scratch paths for workflow artifacts that need review later.
Excluding temp roots can break tools that require writable temp directories, so
redirect those tools to repo-local temp state when stricter isolation is
required.

The detailed runtime note lives in
`ai-workflow-incubator/runtime-artifacts/codex-local-policy/sandbox-writable-roots.md`.

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

## Optional Execution Inefficiency Signals

When the prompt asks for it, Codex may briefly note obvious inefficiencies seen during execution when they are clearly visible and relevant to the run.

- keep any observation to 1-2 sentences
- do not expand it into deep analysis or optimization discussion
- examples include repeated rebases or restarts mid-run, redundant fetches of `origin/main`, unnecessary worktree creation or churn, and repeated validation or file scans with no intervening change

Prompt snippet example: "During execution, briefly note any obvious wasted work you observe, but only when it is clearly visible and relevant."

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
- do not open draft PRs for completed implementation work
- if a PR for completed work is draft, mark it ready for review before
  reporting completion
- use draft PRs only when the human explicitly requests one or the work is
  clearly incomplete or early-feedback-only
- for implementation tasks that change repo files, do not stop at local edits
  and local validation; finish the delivery path by using a focused branch,
  staging only the relevant changes, creating a clear commit, pushing, and
  opening or updating the PR against the intended base branch, usually `main`
- when reporting completion for implementation tasks, include the PR link,
  files changed, and validation results
- for exploration, design, audit, or review-only tasks, do not force a PR when
  no repo changes are required; report findings, recommendations, and any
  validation or evidence gathered instead
- if an exploration, design, audit, or review-only task produces repo changes,
  switch back to the implementation delivery path before calling it complete
- do not recommend merge readiness on an existing PR without direct evidence
  from the PR itself
- before recommending merge readiness on an existing PR, confirm current remote
  mergeability and required checks rather than relying on local branch
  cleanliness alone
- when refining an active PR within the same arc, update the existing branch and PR rather than opening a new PR; open a new PR only when the work changes phase, scope, or review surface
- avoid bundling unrelated cleanup into the same PR
- before calling the work complete, verify the PR diff contains only the intended arc; if `main` moved underneath the branch and overlap occurred, sync with current `main`, resolve conflicts, and rerun validation; if the branch carries unrelated history, rebuild the work onto a clean branch from current `origin/main`

When behavior or supported capability changes, quickly check the existing docs for that area and update any statements that would become inaccurate before calling the work complete.

## CI Expectations

- use the repository's canonical validation command, such as `make check`, when
  one exists
- when the canonical validation command exists and can run locally, run it
  before opening or updating a PR; do not treat CI as a replacement for that
  local step
- do not introduce, invoke, or rely on alternate local validation tools unless
  they are explicitly part of the repository-defined workflow
- if a tool needed by the canonical command is missing locally, report that
  limitation, do not substitute another parser, linter, or manual validation
  path, and rely on required CI checks for enforcement of checks that cannot be
  run locally
- treat checks as CI-only only when the repository does not expose a local
  canonical path for them or the local canonical path cannot run in the current
  environment
- do not infer merge or release gates from check names alone; use the
  repository's documented validation taxonomy and required CI status
- report clearly when no local validation path exists
- until a formal validation path exists, report that gap and keep any review to
  scope and consistency notes rather than presenting it as substitute
  validation
- treat passing CI as necessary but not sufficient
- use hardening to close gaps exposed by CI, review, or edge cases

## Git And GitHub Workflow Notes

- use a fresh branch for each lifecycle phase after merge
- keep commit messages and PR titles clear and phase-oriented
- adapt branch, commit, and PR naming to repo context: use purpose-based
  branch names such as `docs/<topic>`, `fix/<topic>`, `chore/<topic>`, or
  repo-local equivalents, and avoid Codex-branded branch or PR-title prefixes
  unless a repository intentionally requires them
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

Codex should follow the core model, but this adapter exists to document the tooling realities that shape how the model is applied in practice.
