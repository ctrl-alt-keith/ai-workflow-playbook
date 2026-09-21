# Copilot Adapter

This adapter covers GitHub Copilot used for a localized editor suggestion or
continuation. It does not select or define other Copilot products, agents, or
workflow paths. Shared rules remain owned by the Playbook.

Provider behavior was rechecked against official GitHub documentation on
2026-09-21; provider sources belong in reviewed PR evidence, not this
agent-read adapter.

## Eligible use

Use Copilot only after task direction, scope, and boundaries are decided, for a
small local transformation, continuation, refinement, or boilerplate edit in
an explicit file/range/editor context. Place the cursor or selection at the
edit site; state the local intent and constraints; rely on surrounding code
instead of restating repository workflow.

Do not route to this editor-suggestion surface a multi-step task, coordinated
repo-wide change, PR lifecycle work, broad-context/rationale-dependent prompt,
or a request that asks it to decide scope, tradeoffs, or completion. Route work
that needs planning, coordination, repository follow-through, canonical
validation, commit/push/PR delivery, or another execution contract to a
supported executor.

## Material prompt contract

[`prompt-contracts.md`](../prompt-contracts.md) remains authoritative. This
surface supports only a localized transformation/continuation when the selected
context, intent, and constraints are already explicit. A product-neutral
`light` reasoning class may be expressed as that small local task; it is not a
guaranteed product knob.

No testable mapping is claimed for a mandatory `medium` or `high` reasoning
class; repository-wide source hydration or exact source-manifest reconstruction;
deterministic rendering or exact executor-visible byte identity; append-only
attempt receipts, replay-exact dependencies, or checkpoint lineage; canonical
validation, commit, push, PR delivery, or transport fallback; or live authority
re-read and acting-identity verification. Route a mandatory requirement to a
supported owner or fail closed. Omit an unsupported advisory requirement only
when the semantic contract explicitly permits that degradation and no guarantee
is weakened. Do not claim Codex/Copilot parity without a testable mapping for
the compared requirement.
