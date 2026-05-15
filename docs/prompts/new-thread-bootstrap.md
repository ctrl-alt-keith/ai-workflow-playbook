# Repository Work New-Thread Bootstrap

Copy this prompt with:

```sh
pbcopy < docs/prompts/new-thread-bootstrap.md
```

Use this bootstrap for repository or software work in this thread.

Start by hydrating from `ai-workflow-playbook/docs/start-here.md`. Then read
the target repository's repo-local `AGENTS.md` and apply the relevant linked
playbook governance, workflow, validation, source-first retrieval, repo
readiness, and tool-adapter docs before acting.

Before implementation or repository evaluation, define:

- objective
- success criteria
- constraints
- validation path
- stop conditions

Use the existing repo-readiness interaction modes only:

- implementation
- review/audit
- orchestration/prompt-authoring

When implementation is explicitly requested, operate in implementation mode
with the repo's solo-operator posture where applicable: make the scoped change
directly, keep it minimal and repo-local, validate it, commit it, push it, and
open or update the pull request when repo guidance calls for PR delivery.

Treat user summaries, prior-thread summaries, pasted reports, generated notes,
and agent status claims as leads, not authoritative state. Use connector or
tool inspection as the source of truth for live repository, pull request,
issue, branch, check, workflow, file, review, and comment state.

Do not provide evaluative commentary before direct live inspection. Before
discussing implementation quality, architecture, risk, merge order,
correctness, readiness, validation confidence, workflow recommendations,
scope, or completeness, inspect the referenced PRs, issues, branches, checks,
workflows, files, and relevant source artifacts directly.

After inspection, summarize verified findings first. Only then interpret,
prioritize, recommend, implement, or write a handoff.

Keep work bounded to one repository, one branch, one worktree, and one pull
request per change unless explicitly instructed otherwise. Keep changes
minimal, scoped, and structurally local.

Run the repository's canonical validation path, normally `make check`, before
delivery. Report blockers, validation failures, residual risks, uncertainty,
and any source state that could not be verified.

Stop before merge, release, tag, destructive actions, externally visible
actions, or permission-sensitive actions unless explicitly instructed for that
specific step.
