# Accepted v2 Architecture Foundation

> Status: accepted initial v2 architecture under the authorized human decision recorded on 2026-09-12
>
> Provenance: [CAK-301 architecture promotion decision](doctrine-promotion-decisions/cak-301-v2-architecture-foundation-001.md)
>
> Scope: semantic foundation; implementation and operational qualification remain separate

This foundation selects one bounded operation with an owning controller and a
qualified route. These are responsibilities, not separate services or Product
identities. It accepts five useful **current bounded semantic obligations**.
Their partition is a design choice supported by bounded failure witnesses, not
an experimentally irreducible or permanently minimal set. A later design may
combine responsibilities while preserving the required semantics. No universal
correctness owner is created.

## Semantic obligations

### I1 — Scoped source and owner validity

Resolve the controlling source and owner for each consequential fact or decision
reference by subject, question and validity scope. Exact immutable content may
come from a verified retained copy; refresh material mutable source facts from
their current owner before dependent use. Missing, ambiguous or conflicting
source/owner resolution blocks that dependent use rather than selecting a
convenient substitute.

I1 owns source/owner resolution and source validity only; it does not decide
permission, effect recovery, candidate applicability or route capability.

### I2 — Current bounded action authority

Before an effect request crosses the last admission boundary the selected
profile can actually enforce, the acting identity, exact action/candidate,
destination and material conditions must remain covered by current bounded
authority, including its original validity limits. An attempt restart, route
change, status update or successful check cannot renew or enlarge that
authority.

I2 owns permission for this action at admission. A request validly submitted
may commit after later revocation outside the enforceable boundary; local
termination cannot cancel an already admitted remote request.

### I3 — Effect identity and conservative recovery

For effects whose repetition, loss or uncertain completion matters, replacing
an attempt must preserve or recover enough owner-backed identity and effect
truth to choose a safe next action. Distinguish logical operation/effect from
attempt and payload identity; distinguish known presence, qualified absence,
conflict/duplicates and unknown. Unknown is a hold, not replay permission.
Missing receipts do not erase effects. Preserve recovery references to original
authority/validity and any required exact result; use I2 to determine current
permission and I4 for candidate/result checks.

I3 owns uncertain-effect knowledge, correlation and recovery, not admission or
acceptance. The first remote slice needs a conservative possible-submission
fact unless an equally authoritative owner supplies it. No automatic ambiguous
retry, remote exactly-once, or provider-side stale-writer fence is claimed.

### I4 — Exact candidate, property and contract applicability

Conformance, evaluation and acceptance decisions must apply to the actual
candidate identity, the scoped property/use question and the governing
contract, from the decision owner resolved under I1. Verify required mechanical
postconditions on the actual resulting artifact. Equal inputs, predecessor
lineage, upstream validation or a favorable result on another question do not
establish applicability. Reuse evidence only under the applicable
property/use-preservation contract; recover accepted exact bytes rather than
regenerate a supposed equivalent.

Decision applicability requires an exact per-record contract reference or an
exact, **exclusively bound** enclosing collection/context. A decision from an
unrelated contract cannot satisfy a required decision, including a C0 verdict
transplanted into C1 for the same candidate/property/owner. Missing or
ambiguous binding blocks dependent use; conflict or supersession stays with
the named decision owner. This binding is a necessary implementation acceptance
obligation, not a result exercised by corrected E4. Applicable acceptance is
not action or publication authority; I2 owns permission.

### I5 — Route capability and claim ceiling

Determine whether the selected route/profile can support the operation's
required capabilities and hard route constraints before ranking eligible
routes by preferences. Bound route-related execution and completion claims to
the observation or enforcement boundary and material assumptions actually
supported. An unsupported or unknown required route capability blocks that
route or selects an explicitly permitted narrower profile; local or partial
route evidence must not be extended into unobserved provider, recipient or
lifecycle guarantees.

I5 owns route capability sufficiency and route claim ceilings, not substantive
truth, permission, recovery, source ownership or candidate decisions. A
replacement route needs its own applicable evidence; provider substitutability
is not assumed.

## First profile and responsibility boundary

The initial profile retains supplied exact text or binary bytes at one unique
authorized target, verifies the actual retained object, and recovers
conservatively when an attempt disappears. Authority is guaranteed through the
last actually enforceable admission boundary before submission. If the remote
outcome becomes uncertain, hold for reconciliation rather than automatically
replaying or transferring execution. This profile does not promise opaque
remote-commit revocation, provider fencing, automatic ambiguous takeover,
remote exactly-once execution, or universal provider substitution. The real
implementation must name its actual admission boundary.

The owning controller handles scope, evidence eligibility, reconciliation and
synthesis under human direction. A cohesive artifact operation resolves
references, admits authority, retains recovery facts, submits and observes,
verifies exact output and applies required decisions. A qualified route maps
that operation to actual provider/runtime capabilities and returns facts and
unknowns. Existing fact and decision owners retain their authority. A worker's
completion or pass claim is contributed evidence until the owning
controller/reviewer checks controlling sources and accepts it for the stated
purpose. Neither worker success nor operation completion grants human
acceptance or promotion authority.

## NOT BUILDING / NOT REQUIRED YET

The foundation does not require a workflow engine, central policy service,
universal event store, capability registry, evaluator service, permanent agent
fleet or service per obligation. These are not permanently forbidden; a later
concrete need may justify one. The first profile does not build a photo
platform, general transform catalog, publication flow or recipient execution.
It also does not require cross-provider transactions, a universal checkpoint
journal, duplicate status database, guaranteed receipt on every failure,
giant copied handoffs, fixed model hierarchy, a new repository per obligation,
or adoption of CAK-299 reference code. Status queries and byte-preserving
copies do not universally require fresh human approval or semantic review.

Contract-scoped decision applicability, real authority integration at the
named admission boundary, persistence and recovery through the selected host,
and the direct route's create/no-overwrite, collision, correlation and exact
readback behavior require implementation qualification before operational use.
Historical E3 retained a generic error and unchanged-object/readback evidence;
its producing controller's collision report did not independently demonstrate
collision behavior. Corrected E4 exercised a single-contract synthetic
decision model, not decision-to-contract binding. Local process-crash results
do not establish power-loss durability or remote guarantees. Preserve these
claim ceilings when assessing an implementation.

This decision does not promote the separate
[Candidate Architecture Foundation](architecture-foundation-candidate.md),
change any [Product status](product-status.md), accept PR #454's implementation,
or replace the current v1/default bootstrap. Those boundaries need separate
decisions and validation.
