# Starter Distribution

## Purpose

This starter distribution helps an existing workplace or team repository adopt
the AI Workflow Playbook locally without introducing a new governance,
enforcement, or policy layer.

It is an adoption scaffold, not a fork of the playbook. Canonical workflow
guidance remains in [`../../docs/`](../../docs/), especially:

- [`../../docs/start-here.md`](../../docs/start-here.md)
- [`../../docs/source-first-retrieval.md`](../../docs/source-first-retrieval.md)
- [`../../docs/repo-readiness.md`](../../docs/repo-readiness.md)
- [`../../docs/engineering-baseline.md`](../../docs/engineering-baseline.md)
- [`../../docs/review-packet.md`](../../docs/review-packet.md)

## Intended Use

Use this package when a team wants a lightweight local starting point before
considering governance changes, automation, or repository settings changes.
It assumes ordinary contributor access, not administrator rights.

The starter is optimized for:

- source-first verification before claims about current repo state
- small, reviewable changes
- visible validation evidence
- human review and compatibility with existing team process
- local adoption before governance or automation

## Contents

- [`onboarding.md`](onboarding.md): a short adoption path for teams
- [`manifest.md`](manifest.md): package contents, boundaries, and intended
  outputs
- [`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md):
  prompt for creating local `.ai-workflow/` scaffolding in an adopter repo
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

Start locally. Capture what the team already does. Make suggested workflow
changes advisory unless the team explicitly requests implementation.
