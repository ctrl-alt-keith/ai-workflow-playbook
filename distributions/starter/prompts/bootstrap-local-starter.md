# Bootstrap Local Starter Prompt

Use this prompt with an LLM that can inspect the intended adoption destination.

## Prompt

You are helping adopt the AI Workflow Playbook in a workplace or team context.

Your task is to inspect the intended destination and create the correct starter
structure for that destination. The primary recommended destination is a
work-local AI Workflow Playbook repository hosted on GitHub or GitHub
Enterprise. Repo-local `.ai-workflow/` scaffolds are a secondary path for
project repositories, and local-only folders are a fallback for experimentation.

For a generated work-local playbook repository, local `docs/start-here.md`
becomes the canonical starting point for that environment. Upstream
`https://github.com/ctrl-alt-keith/ai-workflow-playbook` is the provenance and
refresh source, not the day-to-day authority. The local playbook and upstream
source may live on different repository hosts. Treat this starter output as
advisory adoption support, not an enforcement layer.

## Destination Selection

Before writing files, determine which adoption target is intended:

- existing GitHub or GitHub Enterprise playbook repository
- new GitHub or GitHub Enterprise playbook repository
- existing project repository requiring `.ai-workflow/` scaffolding
- local-only folder

If the destination is ambiguous, stop and ask which target to use.

## Protected Upstream Remote

For a Git-backed work-local playbook repository, when Git access to the
canonical upstream is available, configure or normalize a remote named
`upstream`. This remote is for provenance and review material only. It does not
change the authority of the local playbook.

Inspect before changing it:

```text
git remote -v
git remote get-url --all upstream
git remote get-url --push --all upstream
```

If `upstream` is absent, add it. If it exists, inspect and normalize it instead
of blindly adding another remote. The intended end state is exactly one fetch
URL for the canonical repository and a separate invalid push URL:

```text
git remote add upstream https://github.com/ctrl-alt-keith/ai-workflow-playbook.git
git remote set-url upstream https://github.com/ctrl-alt-keith/ai-workflow-playbook.git
git remote set-url --push upstream DISABLED
git fetch upstream --prune --tags
```

Use only the applicable add-or-set command. If inspection finds extra fetch or
push URLs, remove those explicitly with reviewed `git remote set-url --delete`
commands and re-inspect the result. Do not replace or rename the local
repository's `origin`. The invalid push URL is intentional: the remote name
alone is not read-only, so accidental upstream pushes should fail locally.

Do not require this remote for non-Git destinations or when Git access to the
canonical upstream is unavailable. Preserve the connector, hosted-source, or
fully qualified URL review path in those cases, and report the unavailable Git
path without weakening local authority.

## Destination Outcomes

Before writing to any repository, inspect contributor docs, READMEs, validation
commands, package metadata, Makefile/task runner, CI, review guidance, and
existing `AGENTS.md`. Establish the current validation, review, release, and
team-process owners from files and command output. Respect team/workplace
process; assume neither administrator rights nor solo-operator governance.

| Destination | Output and boundary |
| --- | --- |
| Existing work-local playbook repo | Create/update lightweight repository-level content directly; local `docs/start-here.md` is canonical. No top-level `.ai-workflow/`. |
| New work-local playbook repo | Create only when tooling, supplied repository details, and permissions allow; otherwise provide explicit creation instructions and stop. Use the same repository-level shape. |
| Existing project repo | Create/update only project-local workflow scaffolds under `.ai-workflow/`. Recommended: `repo-notes.md`, `review-packet-template.md`, and optional `AGENTS.template.md`. |
| Local-only folder | Resolve future-playbook versus project-scaffold intent before writing; ask if ambiguous. Use repository-level files for the former, `.ai-workflow/` for the latter, and report the path. |

For playbook repositories, use this lightweight shape, adapted to verified local
context rather than wholesale upstream copying:

- `README.md`: direct users/tools to local `docs/start-here.md`.
- `docs/start-here.md`: identify the local canonical entrypoint.
- `docs/source-first-retrieval.md`, `docs/repo-readiness.md`, and
  `docs/review-packet.md`: locally adapted guidance.
- `prompts/upstream-refresh.md`: periodic applicability review of
  `https://github.com/ctrl-alt-keith/ai-workflow-playbook` as source material,
  never blind synchronization.
- `upstream-review-baseline.md`: only after a trustworthy completed review.
- `refresh-reports/YYYY-MM-DD-upstream-refresh.md`: only for implemented selected
  refresh recommendations.
- `templates/AGENTS.template.md`: point to local `docs/start-here.md`.
- `templates/review-packet-template.md`.

Adjust the shape only for a better lightweight fit to local context. The
baseline records upstream review coverage, not adoption. Use a repository file,
not a Git tag, and never create/advance it before the corresponding review
completes. For a genuinely new playbook from the current starter, record the
exact upstream commit inspected after reviewing generated local content. For
an existing repo with uncertain origin, leave it unestablished and use the
first-refresh path in `prompts/upstream-refresh.md`; never invent a baseline.

```markdown
# Upstream Review Baseline

- Canonical upstream repository:
  `https://github.com/ctrl-alt-keith/ai-workflow-playbook.git`
- Last reviewed upstream commit: `[full commit SHA]`
- Review date: `[YYYY-MM-DD]`

This baseline means upstream was reviewed for local applicability through the
recorded commit. It does not mean every upstream change was adopted.
```

Project notes capture inspected purpose/technologies, discoverable canonical
setup/validation commands, documented review/contribution process, source-first
reminders, unknowns, and links to the local playbook's `docs/start-here.md`,
`docs/source-first-retrieval.md`, `docs/repo-readiness.md`, and
`docs/review-packet.md`.

The review template covers objective, scope/non-scope, inspected evidence,
validation/results, risks/unknowns/follow-up decisions, and human-review
recommendation. Optional `AGENTS.template.md` is a draft showing canonical
links and local commands; root installation requires a separate explicit user
instruction.

Hard boundaries:

- Do not create or modify root `AGENTS.md` unless the user explicitly requests
  it.
- Do not modify source code.
- Do not modify CI/CD.
- Do not modify GitHub settings.
- Do not modify branch protection.
- Do not modify `CODEOWNERS`.
- Do not modify release automation.
- Do not modify enforcement controls.
- Do not create new governance requirements.
- Do not make settings or process changes on behalf of the team.
- Do not introduce automatic synchronization or promotion.

Make every suggested workflow change advisory unless the user explicitly
requests implementation.

## Deliverable

For an existing repository destination, create a branch, commit changes, and
open a reviewable pull request when tooling is available. If PR creation is
unavailable, leave the changes in the working tree and report the exact files
changed.

For a new repository destination, create the repository when tooling,
user-provided repository details, and permissions allow. If creation is
unavailable, provide explicit repository creation instructions and stop before
making assumptions.

For a local-only destination, create files locally using the selected
playbook-repository or project-scaffold structure and report the path.

When finished, report:

- files created or updated
- source evidence inspected
- validation commands discovered
- protected upstream remote status, when applicable
- baseline status and exact recorded commit, when established
- any unknowns or assumptions
- confirmation that no source code, CI/CD, GitHub settings, branch protection,
  `CODEOWNERS`, release automation, enforcement controls, or root `AGENTS.md`
  were modified
