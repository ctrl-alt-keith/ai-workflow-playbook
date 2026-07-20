# Upstream Refresh Prompt

Use this prompt in a work-local or organization-local AI Workflow Playbook
repository when you want to review upstream changes from
`https://github.com/ctrl-alt-keith/ai-workflow-playbook`.

## Prompt

You are helping review upstream AI Workflow Playbook changes for a local
workplace or organization playbook repository.

This is an upstream review workflow, not synchronization.

The local work playbook remains the daily authority. Upstream remains
provenance and refresh material. Do not blindly synchronize, overwrite local
decisions, or assume upstream is automatically correct for the local
environment. Evaluate applicability and intent. Prefer adaptation over copying
when local context differs.

## Inputs

- Local playbook repository: `[local repository URL, owner/name, or path]`
- Canonical upstream:
  `https://github.com/ctrl-alt-keith/ai-workflow-playbook.git`
- Requested output: `[review report only | implement recommended updates]`

There are exactly two outcomes:

- **Review report only:** perform an ephemeral, non-mutating review and return
  the findings to the human. Do not create repository files,
  `refresh-reports/`, or a branch or pull request. Do not modify the local
  playbook or update `upstream-review-baseline.md`. The baseline remains
  unchanged because no durable review artifact has been accepted into the
  repository.
- **Implement recommended updates:** after the human chooses selected
  recommendations, implement those changes, create the durable refresh report,
  update `upstream-review-baseline.md`, commit the selected updates, report,
  and baseline together, and open one reviewable pull request.

The workflow is simply: review, human decision, then implementation of the
selected updates in one pull request. Do not introduce another output mode,
durable-review-only path, branch, or pull request. If implementation is not
requested, the review remains conversational and ephemeral.

The routine review range comes from `upstream-review-baseline.md`; do not ask
for an arbitrary range when a trustworthy baseline exists. If the local
repository or upstream source is ambiguous, stop and ask for the missing
target. If the baseline is absent or untrustworthy, follow the first-refresh
path below.

## Host And Access Separation

Repository identity and repository host are separate. The local playbook
repository may live on GitHub Enterprise, GitHub.com, another repository host,
or only on a local filesystem. Upstream may live on a different host.

For a Git-backed work-local playbook with Git access to upstream, use the
protected `upstream` remote described below. For a non-Git destination or an
environment where upstream Git access is unavailable, preserve the existing
connector, hosted-source, or fully qualified URL review path. Do not make Git
remote setup a prerequisite for those paths. Record equivalent source
identities and commit IDs when the available source exposes them.

If neither the Git remote nor an alternate source can retrieve current
upstream state, stop and report the source-access blocker. Do not continue from
memory or imply the clone is current.

## Protected Upstream Remote

For the Git-backed path, inspect before changing the remote:

```text
git remote -v
git remote get-url --all upstream
git remote get-url --push --all upstream
```

If `upstream` is absent, add it. If it exists, normalize it. The intended end
state is exactly one canonical fetch URL and one invalid push URL:

```text
git remote add upstream https://github.com/ctrl-alt-keith/ai-workflow-playbook.git
git remote set-url upstream https://github.com/ctrl-alt-keith/ai-workflow-playbook.git
git remote set-url --push upstream DISABLED
```

Use only the applicable add-or-set command. Remove any extra fetch or push URLs
explicitly with reviewed `git remote set-url --delete` commands, then re-run
the inspection commands. Do not change the local repository's `origin`. The
invalid push URL is intentional because the remote name alone does not prevent
accidental pushes.

## Deterministic Preflight

Before comparing content, inspect and report current state. Prefer direct Git
commands and preserve command success, failure, and fetched ref updates in the
report.

1. Inspect the working tree, checkout, and configured remotes:

   ```text
   git status --short --branch
   git branch --show-current
   git rev-parse HEAD
   git remote -v
   ```

2. Determine the local repository's default branch and upstream's default
   branch from remote symbolic refs or current host metadata. Do not assume
   either branch is named `main`, and do not infer one host's branch from the
   other:

   ```text
   git symbolic-ref --quiet --short refs/remotes/origin/HEAD
   git symbolic-ref --quiet --short refs/remotes/upstream/HEAD
   git ls-remote --symref origin HEAD
   git ls-remote --symref upstream HEAD
   ```

   Use `ls-remote` when a remote-tracking symbolic ref is absent. Relevant
   repository host or connector metadata is also acceptable; record the source
   used. Symbolic-ref output such as `origin/main` identifies branch `main`;
   use the branch component, without the remote prefix, in later placeholders.
   If the result remains unknown, stop before comparison.

3. Fetch both sources independently. Do not assume an existing clone is
   current:

   ```text
   git fetch origin --prune --tags
   git fetch upstream --prune --tags
   ```

   Record the result of each fetch separately. A successful upstream fetch
   does not prove that local `origin` is current, or vice versa.

   If an intentionally local-only Git repository has no `origin`, record the
   origin fetch as `not configured (local-only)` rather than creating a remote.
   Identify the local default branch from inspected local documentation or
   repository state and use `refs/heads/[local-default-branch]` for the local
   comparisons below. If the local default branch remains ambiguous, stop and
   ask instead of treating the current branch as authoritative.

4. Resolve and report the exact current heads after fetch, substituting the
   discovered branch names:

   ```text
   git rev-parse refs/remotes/origin/[local-default-branch]
   git rev-parse refs/remotes/upstream/[upstream-default-branch]
   ```

   Also report the checked-out `HEAD` from step 1 when it differs from the
   fetched local default-branch head.

5. Read `upstream-review-baseline.md`. Verify that the recorded object exists
   and is an ancestor of the fetched upstream default branch:

   ```text
   git cat-file -e [baseline-commit]^{commit}
   git merge-base --is-ancestor [baseline-commit] refs/remotes/upstream/[upstream-default-branch]
   ```

   Report object availability and upstream reachability separately. Exit code
   `0` from `merge-base --is-ancestor` means reachable, `1` means not an
   ancestor, and any other failure is an inspection error. Do not silently
   replace an unreachable or invalid baseline.

If the worktree contains unrelated changes, preserve them and do not mix them
into an implementation. A dirty worktree does not prevent a report-only
review, but its status must remain visible.

## Baseline Contract

Use a small root repository file named `upstream-review-baseline.md`:

```markdown
# Upstream Review Baseline

- Canonical upstream repository:
  `https://github.com/ctrl-alt-keith/ai-workflow-playbook.git`
- Last reviewed upstream commit: `[full commit SHA]`
- Review date: `[YYYY-MM-DD]`

This baseline means upstream was reviewed for local applicability through the
recorded commit. It does not mean every upstream change was adopted.
```

The baseline means **upstream reviewed through this commit**, not **all
upstream changes through this commit were adopted**. It is a review boundary,
not a synchronization cursor, release marker, adoption ledger, or approval.
Keep it as a normal reviewable file rather than a Git tag so it does not blur
local release history.

Advance the baseline only when the durable refresh report and selected
implementation changes become part of the same repository change. The
resulting baseline normally equals the upstream head reviewed, including when
some candidates were adapted, rejected as not applicable, or left for a human
decision. Unresolved decisions remain visible in the report; they do not turn
the baseline into an adoption claim.

## First Refresh

Use this path when the baseline file is absent, malformed, unreachable, copied
without trustworthy provenance, or otherwise unreliable.

1. Inspect current local content, local history, remotes, migration notes, and
   any provenance references that may identify the local playbook's starting
   point.
2. Inspect current upstream content and history relevant to the local
   playbook. Look for a defensible shared or source commit, but do not assume
   common Git ancestry exists.
3. If a trustworthy starting commit is found, record why it is trustworthy and
   use it as the initial comparison baseline.
4. If no trustworthy historical baseline exists, perform a snapshot review of
   current local and upstream content. Document the unknown historical starting
   point and the limits of the review. Do not imply every historical upstream
   commit was individually reviewed.
5. If the human chooses implementation, establish an explicit baseline at the
   upstream commit reviewed as part of the same repository change as the
   durable report and selected updates. Otherwise leave the baseline unchanged.

An implemented first refresh establishes a useful forward boundary; an
ephemeral review leaves the baseline unestablished. Neither path requires a
permanent audit of all upstream history. Never invent a commit or silently use
the current upstream head as though a review had already happened.

## Routine Refresh And Three Comparisons

For a trustworthy recorded baseline, keep these comparisons separate. Start
with summaries such as `--stat` or `--name-status`, then inspect the detailed
diffs needed for candidate decisions. The examples use a fetched local
`origin`; for an intentionally local-only repository, substitute the inspected
`refs/heads/[local-default-branch]` ref described in preflight.

1. **Upstream evolution:** recorded baseline to current upstream default
   branch.

   ```text
   git diff --stat [baseline-commit]..refs/remotes/upstream/[upstream-default-branch]
   git diff --name-status [baseline-commit]..refs/remotes/upstream/[upstream-default-branch]
   ```

2. **Local divergence:** recorded baseline to current local default branch.

   ```text
   git diff --stat [baseline-commit]..refs/remotes/origin/[local-default-branch]
   git diff --name-status [baseline-commit]..refs/remotes/origin/[local-default-branch]
   ```

3. **Candidate delta:** current local default branch compared with current
   upstream default branch.

   ```text
   git diff --stat refs/remotes/origin/[local-default-branch]..refs/remotes/upstream/[upstream-default-branch]
   git diff --name-status refs/remotes/origin/[local-default-branch]..refs/remotes/upstream/[upstream-default-branch]
   ```

A direct local-versus-upstream diff alone is insufficient. It mixes intentional
local adaptations accumulated over time with newly introduced upstream
changes. Upstream evolution identifies what is new since the last review;
local divergence preserves the context of local choices; the candidate delta
shows the current content gap. Use all three before deciding what is relevant.

Inspect relevant canonical upstream docs, especially:

- `docs/start-here.md`
- `docs/source-first-retrieval.md`
- `docs/repo-readiness.md`
- `docs/engineering-baseline.md`
- `docs/review-packet.md`

Review relevant merged upstream pull requests in the baseline-to-head range
when hosted PR evidence is available. Do not require tracking every upstream
change forever.

## Candidate Classification

Classify each candidate upstream change:

- **adopt now:** applicable as written and selected for local adoption
- **adapt with edits:** useful intent, but local context requires changes
- **not applicable:** reviewed and deliberately not selected for this local
  environment
- **human decision required:** evidence or authority is insufficient for the
  reviewer to decide

For each candidate, record:

- upstream intent and problem addressed
- source files, commits, or pull requests inspected
- existing local decisions and known deviations
- classification and rationale
- selected adaptation, if any
- unresolved evidence or human authority needed

Treat governance, enforcement, CI/CD, settings, branch protection,
`CODEOWNERS`, release automation, and automatic promotion as outside this
refresh contract unless the human separately authorizes that work.

## Durable Refresh Report

For the implementation outcome, create one lightweight report at:

`refresh-reports/YYYY-MM-DD-upstream-refresh.md`

If more than one refresh completes on the same date, add a short descriptive
suffix. Do not rewrite older reports or require a perpetual per-change ledger.

Use this report shape:

```markdown
# Upstream Refresh Report: YYYY-MM-DD

## Preflight

- Working-tree status:
- Configured remotes:
- Local default branch:
- Upstream default branch:
- Checked-out head:
- Local default-branch head:
- Upstream head:
- Recorded baseline:
- Baseline object available:
- Baseline reachable from upstream head:
- Local origin fetch result:
- Upstream fetch result:

## Review

- Upstream range reviewed: `[baseline]..[upstream head]`
- Upstream head commit:
- Local head commit:
- Candidate classifications and rationale:
- Selected adaptations:
- Known local deviations:
- Unresolved human decisions:
- Review limitations or first-refresh uncertainty:

## Result

- Files changed, if any:
- Validation run, if any:
- Resulting baseline:
```

The report records what was reviewed and decided in the implemented refresh. It
does not assert that every upstream change was adopted or require tracking
every upstream change forever. A review-report-only outcome does not create
this file.

## Implementation And Deliverables

For **review report only**, return the findings to the human and stop. Do not
create files, update the baseline, create a branch or pull request, or modify
the local playbook.

For **implement recommended updates**, after the human selects recommendations
and when tooling is available:

1. Create an isolated branch or worktree as required by the local repository.
2. Implement only candidates classified for adoption or adaptation.
3. Preserve known local deviations.
4. Run the local repository's canonical validation.
5. Complete the refresh report, then update the baseline to the reviewed
   upstream head.
6. Commit the selected local updates, report, and baseline together.
7. Open a reviewable pull request.

When finished, report:

- preflight state and fetch results
- upstream range and exact heads reviewed
- candidate classifications and rationale
- selected adaptations and known local deviations
- unresolved human decisions
- report and resulting baseline paths when implemented
- pull request, files changed, validation, and residual risks when implemented

## Boundaries

Do not introduce automatic synchronization or promotion. Do not overwrite local
decisions. Do not create enforcement behavior. Do not turn the baseline or
reports into a governance framework or synchronization ledger. Do not require
tracking every upstream change forever. Do not duplicate large amounts of
upstream doctrine.
