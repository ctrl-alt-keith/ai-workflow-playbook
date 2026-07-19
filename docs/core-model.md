# Core Model

The operating model is simple: humans own intent, standards, and decisions; AI accelerates drafting, execution, synthesis, and iteration inside clear boundaries.

Repository tasks translate those role boundaries into the interaction modes in
[`repo-readiness.md`](repo-readiness.md#interaction-mode-preflight):
implementation, review/audit, and orchestration/prompt-authoring. Select the
mode before acting so the AI role matches the human's intended delegation.

## Operating Principles

These principles apply to meaningful AI collaboration when work depends on
current sources, a consequential action, or a bounded workflow. They do not
make ordinary chat, brainstorming, or conceptual discussion procedural.

- **Establish relevant reality before acting.** Inspect the current sources
  that control the task when they are available. Treat conversation, memory,
  and summaries as navigation rather than authority. Repository source
  triggers and retrieval mechanics remain owned by
  [`source-first-retrieval.md`](source-first-retrieval.md).
- **Keep evidence, authority, and capability distinct.** Evidence can support
  a decision without approving it, and the ability to perform an action does
  not grant permission to perform it.
- **Preserve material boundaries.** Keep scope, ownership, authority, and
  evidence status visible. When the distinction affects a decision, say what
  is verified, inferred, partial, unknown, or blocked; use
  [`evidence-lifecycle.md`](evidence-lifecycle.md) when evidence is accepted,
  integrated, or synthesized.
- **Make uncertainty and capability gaps explicit.** Name unavailable sources,
  unsupported claims, and tool or access limits instead of inferring through
  them or flattening them into a generic disclaimer.
- **Use a proportional decision boundary before consequential execution.**
  Increase design, review, or approval separation with ambiguity, risk,
  authority sensitivity, and irreversibility. Small, obvious, reversible work
  should not inherit unnecessary ceremony. Repository proposal-first delivery
  remains owned by [`feature-lifecycle.md`](feature-lifecycle.md).
- **Make the phase and next permitted action legible when they matter.** Report
  observable decisions, artifacts, unmet criteria, and transition boundaries
  instead of narrating internal activity. Do not impose a universal phase
  machine on simple work.
- **Validate or verify before relying on consequential conclusions.** Choose
  checks that match the claim and risk. Passing validation is evidence about
  what was checked; it is not acceptance, approval, or broader authority.
- **Re-observe resulting reality after consequential change.** Retrieve the
  actual outcome instead of assuming the planned effect occurred, then
  reconcile separately owned systems only when their workflows require it.
- **Keep mechanisms with their narrowest canonical owner.** A general principle
  should route to specialized workflow or domain guidance rather than copy its
  trigger lists, taxonomies, schemas, or execution procedures. Do not
  generalize domain mechanics merely because an analogy exists elsewhere.

## Protocol Invariants

A reusable workflow protocol is defined by its reviewed semantic invariants,
not by one implementation topology. The stable contract names the intended
meaning, scope, authority boundaries, evidence identity, isolation guarantees,
and validation expectations that must survive changes in tools, workers,
prompts, branches, or orchestration shape.

Topology and execution mechanics may evolve when those approved invariants are
preserved. A successful run or convenient implementation is evidence about one
execution; it does not silently establish a reusable invariant or authorize a
semantic change.

## Roles

### Human role

- Define the goal, scope, and quality bar
- Set or approve the execution plan
- Review meaningful deltas, risks, and tradeoffs
- Decide when work is complete
- Decide what is worth capturing into the playbook

### AI role

- Turn direction into concrete next steps
- Execute bounded work quickly and consistently
- Surface ambiguity, risk, and missing information
- Summarize changes, evidence, and open questions
- Help capture reusable patterns after delivery

## Authority And Transitions

Authority is permission to make a decision or cross a workflow boundary. It is
distinct from capability: a person, agent, tool, or automation may be able to
perform an action without being authorized to perform it.

Material transitions should make explicit the authority they consume and any
authority an authorized human grants for the next bounded action. Execution,
successful completion, validation, receipts, stored state, prompts, replay,
topology, and automation can record or exercise existing authority; none can
create approval authority. When authority is absent, ambiguous, expired, or
outside the current contract, the transition remains fail-closed.

## Protocol Phases

Separate evidence production from decision production when a workflow includes
both:

- Evidence-production phases acquire, produce, review, integrate, or validate
  material under the current operational contract.
- Decision-production phases interpret the accepted evidence and produce
  recommendations, approvals, dispositions, or other consequential choices.

The boundary is semantic, not a required stage list, branch topology, or pull
request count. Crossing it requires an explicit review and authority boundary,
and completed evidence production does not imply approval of a downstream
decision.

When a workflow accepts, integrates, or synthesizes evidence, apply the
[`evidence lifecycle`](evidence-lifecycle.md) before crossing into decision
production.

## Durable Continuity

Durable project artifacts are the recoverable continuity substrate for a
workflow. Depending on the task, those artifacts can include the current
operational contract, authoritative repository and issue state, exact evidence
and artifact identities, human approval records, stage and attempt receipts,
validation results, and the next permitted action. Their authority remains
specific to the role assigned by the owning source; durability alone does not
make an artifact canonical or grant permission.

Conversation is useful for intent, navigation, and explanation, but it is
non-authoritative context. Recovery must be possible from durable sources by
reconstructing the applicable contract, current authority, accepted inputs,
completed work, and next permitted action, then revalidating any mutable source
state. If that contract cannot be reconstructed or no longer applies, stored
history cannot silently authorize continuation.

## Workflow

The default loop is:

1. Align on the goal and the current phase.
2. Let AI execute the next bounded unit of work.
3. Validate outputs against the contract, tests, or review criteria.
4. Tighten based on feedback.
5. Capture reusable learning before the next arc begins.

## Feedback Loops

Reliable AI-assisted work depends on short feedback loops:

- Execution loop: produce a change, then validate it quickly
- Review loop: summarize what changed so a human can inspect the right things
- Capture loop: turn proven practice into reusable guidance before context fades

Use [`trust-topology.md`](trust-topology.md) as an optional vocabulary when the
confidence level, validation evidence, or promotion path for a reusable pattern
is unclear.

## Discipline

Speed is only useful when paired with disciplined execution. This model assumes:

- Clear scope boundaries
- Frequent validation
- Explicit pauses when uncertainty increases
- Written capture of reusable lessons

Without those controls, AI work tends to drift, overproduce, or hide weak reasoning behind fluent output.
