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

Use the cleanup loop in this order:

1. Audit
2. Trim
3. Re-audit

### 1. Audit

Run the
[`Notes vs Playbook Alignment Audit`](prompts.md#notes-vs-playbook-alignment-audit)
against the notes project after promotion work has landed.

During the audit:

- stay inside the notes project root
- classify relevant files as `remove`, `trim`, `keep`, or `defer`
- point each `remove` or `trim` recommendation at the canonical playbook
  location that now owns the guidance
- keep the audit operational and file-specific

The audit output should identify the highest-leverage cleanup work without
reopening already-settled promotion decisions.

### 2. Trim

Apply the audit recommendations in a focused batch.

During trim:

- remove files that are fully superseded by the playbook
- trim files that still belong in notes but contain redundant or promoted
  material
- preserve valid staging-layer context, local follow-up material, and notes that
  do not conflict with the playbook
- leave `defer` items alone until the blocking local decision or dependency is
  resolved

If multiple files overlap the same promoted rule, consolidate the surviving
notes so one clear staging reference remains instead of several partial copies.

### 3. Re-audit

Run the same audit again after cleanup changes land in the notes project.

Use the re-audit to confirm that:

- earlier `remove` and `trim` items were addressed cleanly
- remaining notes still serve a valid staging purpose
- no duplicate guidance was left behind during consolidation
- any `defer` items are still deferred for a concrete reason rather than because
  cleanup stalled

If the re-audit still finds avoidable overlap, repeat the trim step and rerun
the audit until the notes set converges.

## Practical Rule

Treat this workflow as `audit -> trim -> re-audit`, not as a one-pass deletion
exercise. The audit identifies cleanup targets, the trim step reduces the notes
set, and the re-audit verifies that the repository now reflects the playbook as
the canonical source.
