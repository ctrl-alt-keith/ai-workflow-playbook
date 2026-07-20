# Starter Distribution

## Purpose

This starter distribution helps a practitioner adopt the AI Workflow Playbook
for a workplace or team without introducing a new governance, enforcement, or
policy layer.

It is an adoption scaffold, not a fork of the playbook. Canonical workflow
guidance remains in [`../../docs/`](../../docs/), especially:

- [`../../docs/start-here.md`](../../docs/start-here.md)
- [`../../docs/source-first-retrieval.md`](../../docs/source-first-retrieval.md)
- [`../../docs/repo-readiness.md`](../../docs/repo-readiness.md)
- [`../../docs/engineering-baseline.md`](../../docs/engineering-baseline.md)
- [`../../docs/review-packet.md`](../../docs/review-packet.md)

## Intended Use

Use this package when the intended first step is a work-local AI Workflow
Playbook repository hosted on GitHub or GitHub Enterprise. That repository
becomes the canonical location referenced by workplace AI tools.

After creation, the work-local playbook is the daily authority for its
environment. Its local `docs/start-here.md` is the entrypoint for users and
tools. Upstream `https://github.com/ctrl-alt-keith/ai-workflow-playbook`
remains the provenance and refresh source.

Repo-local `.ai-workflow/` scaffolds remain useful when a project repository
needs local adoption notes. Local-only folders are a fallback for
experimentation before publishing anything.

These are intentionally different structures: a work-local playbook repository
gets repository-level `README.md`, `docs/`, `prompts/`, and `templates/`
content, while an existing project repository gets `.ai-workflow/` scaffolding.

The starter assumes ordinary contributor access, not administrator rights.

The starter is optimized for:

- source-first verification before claims about current repo state
- small, reviewable changes
- visible validation evidence
- human review and compatibility with existing team process
- hosted playbook adoption before repo-local scaffolds, governance, or
  automation
- periodic upstream review without blind synchronization

## Usage

### URL-First Preferred

1. Create or identify the destination repository, typically a personal GitHub
   Enterprise repository named `ai-workflow-playbook`.
2. Open Codex, Claude, ChatGPT, or another agent with access to that
   destination.
3. Copy the launcher prompt from
   [`prompts/use-this-starter.md`](prompts/use-this-starter.md).
4. Fill in the destination type and repository or folder.
5. Let the launcher point the agent at the canonical bootstrap prompt in this
   repository.

### Clone Or Download Fallback

If URL access is unavailable, clone or download this repository and provide the
agent with the local starter files. Use
[`prompts/use-this-starter.md`](prompts/use-this-starter.md) as the tiny
entrypoint and
[`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md) as
the full implementation prompt.

## Upstream Refresh

Work-local playbook repositories should retain a reference to
[`prompts/upstream-refresh.md`](prompts/upstream-refresh.md). Use it
periodically to review upstream changes from
`https://github.com/ctrl-alt-keith/ai-workflow-playbook` and decide whether to
adopt, adapt, skip, or escalate them.

The local work playbook may live on GitHub Enterprise, GitHub.com, or another
host. The upstream source may live on a different host. Use the fully qualified
upstream URL; do not infer upstream from the local repository host.

For Git-backed work-local playbook repositories with upstream Git access, keep
a remote named `upstream` with the canonical fetch URL and an invalid push URL:

```text
git remote set-url upstream https://github.com/ctrl-alt-keith/ai-workflow-playbook.git
git remote set-url --push upstream DISABLED
```

Bootstrap should add the remote when absent or normalize it when present, then
fetch it with pruning and tags. Inspect all existing fetch and push URLs before
changing them. The invalid push URL makes accidental pushes fail locally; the
name `upstream` by itself does not make a remote read-only. This setup is
optional for non-Git destinations or environments without upstream Git access,
which should continue to use connector, hosted-source, or URL review.

Durable implementation refreshes record review progress in a small repository
file named `upstream-review-baseline.md`. It preserves the canonical upstream
repository, the exact last reviewed upstream commit, and review date. The
baseline means "upstream reviewed through this commit," not "all upstream
changes through this commit were adopted." Keep refresh reports under
`refresh-reports/YYYY-MM-DD-upstream-refresh.md`; each report records the
reviewed range, candidate decisions, local deviations, and resulting baseline.
Review-report-only work remains conversational and creates neither file.

Routine refreshes compare three distinct surfaces:

1. upstream evolution from the recorded baseline to current upstream
2. local divergence from the baseline to the current local default branch
3. the candidate delta between the current local and upstream heads

A direct local-versus-upstream diff is not enough because it mixes intentional
local adaptations with upstream changes introduced since the last review. If
there is no trustworthy baseline, use the first-refresh path in the prompt:
inspect local history and content, establish an explicit starting point, and
record any uncertainty without requiring an exhaustive historical review.

This is not synchronization, enforcement, or automatic promotion. Local
ownership and workplace context control the final decision.

Model:

`upstream playbook -> refresh/adapt -> work-local playbook -> work/project repos`

## Contents

- [`onboarding.md`](onboarding.md): a short adoption path for teams
- [`manifest.md`](manifest.md): package contents, boundaries, and intended
  outputs
- [`prompts/use-this-starter.md`](prompts/use-this-starter.md): tiny
  copy/paste launcher prompt for URL-first adoption
- [`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md):
  prompt for selecting an adoption destination and creating starter scaffold
- [`prompts/upstream-refresh.md`](prompts/upstream-refresh.md): review-oriented
  prompt for evaluating upstream changes
- [`templates/AGENTS.template.md`](templates/AGENTS.template.md): optional
  repo-local instruction template
- [`templates/review-packet-template.md`](templates/review-packet-template.md):
  lightweight review packet template
- [`templates/repo-notes-template.md`](templates/repo-notes-template.md):
  repo discovery notes template

## Boundary

This distribution should not modify source code, CI/CD, GitHub settings, branch
protection, `CODEOWNERS`, release automation, or enforcement controls. It should
not create a parallel rulebook for the adopting repository.

Start with a reviewable hosted playbook repository when possible. Use
repo-local scaffolds second, and local-only folders only when experimentation is
the right first move. Capture what the team already does. Make suggested
workflow changes advisory unless the team explicitly requests implementation.
Do not create `.ai-workflow/` at the top level of a destination that is itself
meant to become a standalone playbook repository.
