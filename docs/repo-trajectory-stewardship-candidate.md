# Repo Trajectory Stewardship Candidate

Status: staged candidate
Promotion: pre-pattern
Trust: weak

## Purpose

Describe a possible reusable workflow pattern for repository trajectory
stewardship without making it canonical guidance yet.

This note is intentionally staged. It captures a candidate shape that may later
be promoted if real repository work shows the pattern is reusable,
evidence-supported, and clear enough to guide action.

## Candidate Pattern

Compare four surfaces:

- declared repo purpose;
- historical repository behavior;
- current changes under review;
- likely trajectory implied by recent activity.

The useful question is not only "does this comply with the current rule?" It is
"does this repository still appear to be moving toward the purpose humans want
for it?"

## Compliance Checks Vs Stewardship Checks

Compliance checks ask whether a known rule is currently satisfied. They work
best for mechanical expectations such as validation commands, branch hygiene,
generated artifact drift, or documented execution contracts.

Stewardship or trajectory checks ask whether evidence over time suggests the
repo's purpose, behavior, and direction still fit together. They are more
interpretive and should remain advisory unless a separate canonical rule makes
one part mechanically checkable.

Useful stewardship questions:

- Does the README purpose still match what the repo repeatedly does?
- Do issues, pull requests, releases, and changed paths reinforce or expand the
  declared boundary?
- Does apparent drift look accidental, healthy, or unresolved?
- Is the next steering action to update docs, narrow scope, split work, accept a
  new direction, or gather more evidence?

## Candidate Output

A trajectory packet should be descriptive, evidence-backed, and modest. Possible
outcomes:

- stable: declared purpose, historical behavior, and current direction align;
- minor drift: differences are visible but low-risk or locally explainable;
- significant drift: observed behavior materially diverges from the declared
  purpose or expected boundary;
- unclear: evidence is insufficient, contradictory, or missing.

Each outcome should include:

- evidence inspected;
- tensions or counter-evidence;
- uncertainty and skipped sources;
- recommended human steering action.

The packet should not include a numeric score, automatic remediation list, or
merge gate.

## AI Role

In this pattern, AI is a continuity and stewardship aid rather than primarily a
coding tool. It helps humans keep long-running repository intent visible across
threads, branches, issues, PRs, docs, and generated context.

That role is useful when it reduces rediscovery and helps humans steer. It is
risky when it treats interpretation as enforcement or turns every mismatch into
a failure.

## Promotion Bar

Keep this as pre-pattern material until there is concrete evidence from real
repo work.

Promotion would need evidence that the workflow:

- helps more than one repository or workflow arc;
- produces reviewable outputs humans find useful;
- distinguishes healthy drift from harmful drift;
- preserves repo-local authority and playbook boundaries;
- does not duplicate mechanical compliance checks already owned elsewhere.
