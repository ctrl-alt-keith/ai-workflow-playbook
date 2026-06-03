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

Repo-local `.ai-workflow/` scaffolds remain useful when a project repository
needs local adoption notes. Local-only folders are a fallback for
experimentation before publishing anything.

The starter assumes ordinary contributor access, not administrator rights.

The starter is optimized for:

- source-first verification before claims about current repo state
- small, reviewable changes
- visible validation evidence
- human review and compatibility with existing team process
- hosted playbook adoption before repo-local scaffolds, governance, or
  automation

## Contents

- [`onboarding.md`](onboarding.md): a short adoption path for teams
- [`manifest.md`](manifest.md): package contents, boundaries, and intended
  outputs
- [`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md):
  prompt for selecting an adoption destination and creating starter scaffold
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
