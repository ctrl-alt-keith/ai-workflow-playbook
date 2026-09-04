# Review Packet

At each material human decision boundary, including before merge or release,
prepare a standard review packet for the human reviewer.

Use this packet at the semantic phase and release boundaries described in
[`feature-lifecycle.md`](feature-lifecycle.md), and use
[`alignment-checkpoints.md`](alignment-checkpoints.md) when deciding whether a
pre-merge sanity check is needed.

## Packet Format

Lead with the decision surface. The packet should include:

- Decision requested: the exact human judgment or approval needed
- Reviewed identity: the exact artifact, commit, or byte identity under review
- Objective: what this phase was meant to accomplish
- Scope: what changed and what intentionally did not
- Interaction mode: implementation, review/audit, or
  orchestration/prompt-authoring
- Source evidence: issue, PR, evidence note, docs, or review input that shaped
  the work
- Coordination links: GitHub issue IDs, planning ticket IDs such as Linear IDs,
  and expected PR linkage when relevant
- Invariants and guarantees: what must remain true if the decision is approved
- Exceptions: known deviations, exclusions, or unresolved cases
- Validation: what was run, its class under
  [`repo-readiness.md#validation`](repo-readiness.md#validation), and the result
- Authority consumed: the authority under which the reviewed work was prepared
- Authority granted: the authority the human decision actually grants; keep it
  pending until the authorized human records the decision
- Prohibited or unauthorized next stages: actions that remain outside the
  granted authority
- Next permitted action: the exact bounded action that may follow the decision
- Risks: remaining concerns, edge cases, follow-up work, or any important gap between mocked or contract-level validation and real-world validation
- Recommendation: `ready to merge`, `needs decision`, or `blocked`

The decision-first surface is an index into the complete artifacts, not a
replacement for them. Keep the full diff, evidence, validation output, and
review discussion accessible at the exact identities named by the packet.

## Approval Identity And Ownership

Approval applies to the exact reviewed artifact, commit, or bytes named in the
human-owned approval record. Link the human decision to that identity and state
the authority it grants and the next action it permits.

Execution systems may prepare a packet and identify the approval being
requested, but must not author, mutate, backfill, broaden, or infer the
human approval record. They may faithfully record unambiguous authority already
expressed by an explicit human instruction under the owning workflow; apply
[`feature-lifecycle.md#doctrine-promotion`](feature-lifecycle.md#doctrine-promotion)
for doctrine promotion and merge authorization.
Capability, successful execution, validation, status fields, receipts, or the
absence of objections cannot be interpreted as approval. The human role and
decision ownership remain defined in
[`core-model.md#human-role`](core-model.md#human-role).

## Approval Validity

Approval may remain valid after a non-semantic correction only when all of the
following are true:

- the change is limited to presentation, spelling, formatting, or equivalent
  correction and does not change reviewed meaning
- authority, guarantees, inputs, outputs, and execution meaning are unchanged
- the before-and-after identities and correction are recorded reviewably
- the human-owned approval record or governing review contract permits that
  bounded correction

Any change to authority, guarantees, inputs, outputs, or execution meaning
requires renewed approval. When the semantic effect is uncertain, treat the
prior approval as invalid rather than letting an execution system classify the
change on the human's behalf.

For versioned material prompts, apply the classification rules in
[`prompt-contracts.md#semantic-versioning`](prompt-contracts.md#semantic-versioning).
Any executor-visible imperative wording change is at least Minor. A parity
check is classification evidence only; changed approved bytes remain subject
to the owning reviewed-identity and approval-retention rules.

## Independent Review Findings And Re-Review

When independent review materially affects a decision, make its evidence
boundary visible in the review packet. Record:

- the exact artifact or commit the reviewer inspected;
- reviewer identity and role;
- material tools, access, and capability gaps;
- the sources the reviewer actually verified;
- any follow-up verification, attributed to the actor and source that performed
  it; and
- the preserved review output or durable review record.

Do not attribute a source claim to a reviewer that could not inspect it. A
capability declaration describes the evidence available to that review; it
does not grant authority or make the reviewer an oracle.

Connect every substantive finding to the exact reviewed artifact and give it an
explicit disposition:

- accepted;
- accepted with modification;
- reasoned decline;
- superseded; or
- verified externally.

Record the resolution and any remaining gap. Keep the taxonomy proportionate:
trivial nits can be handled inline, but substantive findings must not disappear
through silent edits. Review findings, dispositions, validation, and reviewer
verdicts remain evidence for the human decision. None grants implementation,
merge, release, or other transition authority.

After corrections, ask: **Is the original review still applicable to the
reviewed artifact?** Record one of three outcomes and the reason:

- no re-review when bounded corrections preserve the reviewed scope,
  ownership, claims, authority, acceptance criteria, omissions, and delivery
  topology;
- focused re-review when a material part of those surfaces changed but the
  artifact remains recognizably the same work; or
- a fresh artifact and full review when the corrected artifact is no longer
  meaningfully the same reviewed work.

Do not require another review merely because bytes changed, and do not skip one
merely because the filename or headline stayed the same. Continued
applicability is the governing question. The human-owned approval identity and
validity rules above still control after the review decision.

## What Codex Should Summarize

Codex should summarize:

- the decision requested and exact reviewed identity
- the objective
- the actual scope
- the invariants, exceptions, and authority boundary
- the validation evidence
- the main risks
- the exact next permitted action
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

### Connector-sufficient review latch

Once review/audit mode is selected and the available connector supplies the
exact PR head, changed files and relevant patches, checks, comments, reviews,
mergeability, and task context needed for the requested review, restrict the
eligible action set to those connector-backed reads and the chat response.
Source-first retrieval does not require independent local reproduction when
the authoritative review surface is already sufficient.

Clone, checkout, worktree creation, repository or local-filesystem mutation,
local test execution, temporary-repository setup, and cleanup commands are
ineligible unless the current human instruction explicitly requests
independent local reproduction. Selecting the connector-backed review path
invalidates any previously considered local-execution plan before another tool
call. If an out-of-scope action is attempted and fails, do not retry the same
forbidden action class with another command, syntax, wrapper, or cleanup plan.

When a concrete evidence gap remains after connector inspection, report the
exact missing evidence first. Propose local reproduction only as a separately
authorized next step; do not perform it from review/audit authority.

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

## Optional Review Effort Evidence

When it would help improve a repeated workflow, record lightweight evidence
about the human effort needed to reach the decision: what had to be inspected,
where context reconstruction was costly, or which part of the decision surface
reduced review burden. Keep it optional, proportionate, and tied to a specific
decision or irreversible boundary.

Review-effort evidence is workflow-learning context, not a required metric,
telemetry schema, performance score, approval substitute, or new gate.

## Doctrine Provenance

When a change promotes reusable doctrine, the review packet should link the
reviewed evidence and decision that support the promotion. Identify the
observation, maturity, disposition, target, and exact implementation artifact
or commit so a reviewer can trace the rule without copying the complete
retrospective into the doctrine file.

Identify the exact artifact reviewed for promotion, which items remained open
questions or were otherwise not promoted, and whether that artifact is the
implementation identity or an earlier reviewed decision. Keep evidence and
implementation state distinct even when they share one pull request; neither a
retrospective nor its summary grants approval to merge the doctrine change.

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
