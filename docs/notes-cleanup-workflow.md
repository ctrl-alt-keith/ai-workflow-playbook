# Notes Cleanup Workflow

Use this workflow to clean up a notes repository after reusable guidance has
already been promoted into the playbook.

The goal is to keep notes high-signal while preserving the playbook as the
canonical source for cross-repo workflow guidance.

## When To Run It

Run this workflow when:

- promotion work has already landed in the playbook and the notes set still
  contains overlapping material
- a notes repository has accumulated duplicate workflow guidance, outdated
  summaries, or stale capture artifacts
- a cleanup pass is needed before starting a new capture or promotion cycle
- a previous audit identified remove or trim candidates that still need to be
  resolved

Do not use this workflow to decide whether guidance should be promoted. Run it
after those promotion decisions are already complete.

## Expected Outcomes

By the end of the workflow:

- the notes repository keeps only staging-layer material that still belongs in
  notes
- duplicated or already-promoted guidance is removed or trimmed back
- remaining files point clearly at the canonical playbook locations that now own
  the guidance
- a follow-up audit confirms the notes set has converged on the playbook as the
  source of truth

## Cleanup Loop

Repeat `audit -> trim -> re-audit` until the notes converge on the Playbook as
the canonical source.

### 1. Audit

After promotion lands, stay inside the notes project root. Classify relevant
files as `remove`, `trim`, `keep`, or `defer`; identify the canonical Playbook
owner for every `remove` or `trim` recommendation. Keep findings file-specific,
prioritize useful cleanup, and do not reopen settled promotion decisions.

### 2. Trim

Apply a focused batch:

- remove fully superseded files
- trim redundant/promoted guidance while preserving valid staging context,
  local follow-up material, and nonconflicting notes
- leave `defer` items until their blocking local decision or dependency resolves
- consolidate overlapping survivors into one clear staging reference

### 3. Re-audit

After cleanup changes land, repeat the audit. Confirm earlier recommendations
were addressed, remaining notes serve a staging purpose, consolidation left no
duplicate guidance, and each deferred item still has a concrete blocker.
Repeat trim and audit when avoidable overlap remains.

## Practical Rule

Use the [cleanup loop](#cleanup-loop) through re-audit; deletion alone does not
complete this workflow.
