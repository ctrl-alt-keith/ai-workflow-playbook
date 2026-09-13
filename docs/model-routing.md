# Model And Reasoning Routing

Use this page when choosing an executor's model and reasoning configuration for
a bounded task or worker lane. Executor adapters own the available models,
effort controls, exact selectors, runtime acceptance, fallbacks, and
qualification evidence; this page does not compare providers or claim quality
parity.

## Select The Bounded Responsibility First

Choose the responsibility before its configuration. When work has been split
into lanes, first bound each lane's concern, invariant, inputs, exclusions, and
validation path; then choose the lowest-cost available model and reasoning
configuration sufficient for that responsibility. A stronger configuration for
one lane does not make every lane strong, and worker count does not itself
justify escalation.

Start proportionally rather than trying to predict an optimal configuration.
A reasonable executor-specific default is a starting posture, not a quality
claim. Adapt as the work supplies evidence: ambiguity, consequence of error,
novelty, reversibility, context breadth, reconciliation difficulty, conflicting
evidence, and weak independent validation can justify more capability or
effort. Deterministic, independently checkable work with clear acceptance
criteria can justify less.

## Escalate And Delegate On Evidence

Use task characteristics rather than duration or apparent size. Escalate after
a bounded investigation leaves material ambiguity, conflicting authorities or
evidence, an unexplained invariant, repeated failed attempts, an architecture
or authority decision, or error consequences that weak validation cannot
contain. Prefer escalating the unresolved bounded question over restarting the
whole workflow at a stronger setting when the topology supports it.

Delegate established, deterministic, independently checkable work downward
when it is worthwhile. Preserve its bounded inputs, validation, execution
identity, result, and authority boundary where the governing workflow requires
them. Model capability does not create authority, and a child of the reviewed
party is not an independent reviewer.

Requested configuration and runtime-effective configuration are separate
facts. Where the runtime exposes effective configuration, record any
substitution or fallback needed for qualification or evidence. Where it does
not, say so; a requested setting alone does not prove what served the work.
Thread-continuity semantics remain owned by
[`prompts.md`](prompts.md#thread-routing-and-configuration-continuity).
