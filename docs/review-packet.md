# Review Packet

Before merge or release, prepare a standard review packet for the human reviewer.

Use this packet at the release point described in [`feature-lifecycle.md`](feature-lifecycle.md), and use [`alignment-checkpoints.md`](alignment-checkpoints.md) when deciding whether a pre-merge sanity check is needed.

## Packet Format

The packet should include:

- Objective: what this phase was meant to accomplish
- Scope: what changed and what intentionally did not
- Interaction mode: implementation, review/audit, or
  orchestration/prompt-authoring
- Source evidence: issue, PR, evidence note, docs, or review input that shaped
  the work
- Coordination links: GitHub issue IDs, planning ticket IDs such as Linear IDs,
  and expected PR linkage when relevant
- Validation: what was run and what the results were
- Risks: remaining concerns, edge cases, follow-up work, or any important gap between mocked or contract-level validation and real-world validation
- Recommendation: `ready to merge`, `needs decision`, or `blocked`

## What Codex Should Summarize

Codex should summarize:

- the objective
- the actual scope
- the validation evidence
- the main risks
- an explicit recommendation: `ready to merge`, `needs decision`, or `blocked`

The goal is not to restate the diff line by line. The goal is to make human review targeted and efficient.

When a decision depends on integrated or synthesized evidence, use
[`evidence-lifecycle.md`](evidence-lifecycle.md) for the accepted-evidence,
semantic-accounting, and reporting boundaries.

If the repo does not have a formal validation path yet, say that directly and summarize the lightweight validation that was used.

When relevant, say explicitly whether validation was mocked, contract-level, or exercised against real behavior, and treat that gap as a risk.

## Direct PR Inspection

Linked review artifacts are authoritative; pasted summaries and completion
reports are context.
The source-first ordering rule in
[`source-first-retrieval.md`](source-first-retrieval.md) applies before
continuity or summary-based reasoning whenever a PR, issue, branch, commit, or
repository trigger is present.

When the human references, links, names, or asks to review, check, assess,
approve, or comment on a GitHub PR or similar connector-backed review artifact,
the reviewer must inspect the artifact through the matching connector before
giving review feedback. For GitHub PRs, open the PR through the GitHub
connector.

Local checkouts, `git diff`, and `gh` commands may be used as supplemental
evidence for PR review, but they must not replace connector inspection.

Treat "open the PR" as read-only connector inspection. It does not mean opening
the PR in a browser, and it does not mean submitting a GitHub review.

User-provided PR summaries, completion reports, pasted titles, local path
snippets, and copied diff excerpts are useful navigation and context, but they
are not the review source of truth when a PR link, name, or number is
available. A PR review must be grounded in the actual PR surface from the
connector. The reviewer must inspect, where available:

- PR title and body
- changed files
- relevant diffs
- comments and unresolved review discussion
- CI and check status
- mergeability
- scope against the task, issue, or stated goal

Return review feedback in chat by default. The reviewer must not mutate the PR:
do not submit, approve, request changes, comment on, label, merge, close, or
otherwise change the PR unless the human explicitly asks for that GitHub action.

Treat "review this PR" as inspect the PR and provide feedback in chat. Do not
post the review to GitHub unless the human explicitly asks to post the review
to GitHub.

Do not claim a PR is safe to merge, ready to merge, or approved without direct
evidence from the PR itself through the connector.

Do not perform summary-only PR reviews when a PR link, name, or number is
available unless connector access fails or the human explicitly says not to use
the connector.

If connector access is unavailable, fails, is declined, or is explicitly
forbidden by the human, say so clearly. Do not provide a merge or readiness
recommendation from secondhand text. Provide only clearly caveated feedback
from information already present, or ask for connector access to be restored.

If the human corrects tool or connector usage in the thread, treat that
correction as a hard workflow constraint for subsequent similar review
requests.

## Single-Operator Review Posture

When a repository ecosystem fits the single-operator posture in
[`repo-readiness.md`](repo-readiness.md#single-operator-review-posture), review
feedback should distinguish:

- blocking issues that should stop merge
- non-blocking risks that are acceptable to test operationally
- implementation opportunities that would make the current change more
  cohesive
- practical follow-on improvements that are useful but not required before
  merge

Do not turn locally testable, reversible improvements into automatic deferrals
only because they are adjacent to the original request. Also do not soften
security-sensitive, destructive, irreversible, compatibility-sensitive, or
high-blast-radius findings into experiments.

## Optional Trust Or Evidence Context

When prior validation, repeated usage, or unresolved uncertainty affects review
risk, include brief trust or evidence context in the packet. Short prose is
enough. The point is to explain why reviewers can trust, question, or re-check
the change.

Use this only when it improves review quality. Do not add it for routine changes
where the objective, validation, and risks already give reviewers enough signal.

Example snippet:

```text
Trust context (optional):
- Prior validation: This pattern was used in knowledge-adapters PR #248 and
  passed `make chaos-all`.
- Confidence: medium; behavior is stable but not yet promoted to the playbook.
```

## Doctrine Provenance

When a change promotes reusable doctrine, the review packet should link the
reviewed evidence and decision that support the promotion. Identify the
observation, maturity, disposition, target, and exact implementation artifact
or commit so a reviewer can trace the rule without copying the complete
retrospective into the doctrine file.

State which material was frozen before implementation, which items remained
open questions or were otherwise not promoted, and whether the implementation
preserved the reviewed decision. Keep the evidence artifact and implementation
lifecycle distinct; neither a retrospective nor its summary grants approval to
merge the doctrine change.

## What The Human Should Focus On

The human reviewer should focus on:

- whether the phase objective was actually met
- whether the validation and acceptance criteria are correct, not just passing
- whether risks are understood and acceptable
- whether the change is appropriately scoped for the phase
- whether the work is ready to merge or release

Human review is for judgment, prioritization, and standards enforcement. It should not be wasted on reconstructing context that the review packet should have provided.

## Scope Verification

During review:

- confirm the PR matches its stated goal (issue, prompt, or task description)
- confirm no unrelated changes are included
- confirm the diff aligns with the intended arc
- confirm issue linkage (if present) is accurate
- confirm planning-ticket linkage (if present) is accurate and does not replace
  GitHub as the repository closure source of truth unless repo-local guidance
  says otherwise

Quick check:

- "If I remove part of this diff, does the PR still make sense?"
- if yes, that part likely does not belong

## Merge Checks

Before merge:

- the PR diff must contain only the intended arc
- issue-driven PRs must include `Closes #[issue number]`
- when a planning ticket such as Linear is linked, the PR should reference it
  for coordination, and post-merge notes should say whether planning status
  needs to remain open or can be marked complete after GitHub closure is
  confirmed
