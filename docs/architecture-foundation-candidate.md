# Candidate Architecture Foundation

> Status: candidate foundation — not doctrine
>
> Evidence basis: derived from the noncanonical
> [architecture research archive](https://github.com/ctrl-alt-keith/ai-workflow-incubator/tree/7ef03580cf9c7725b0e325c48ac74cb6a6d4a76f/archive/architecture-research-2026-07-23)
>
> Authority: non-authoritative; this draft does not supersede current Playbook
> guidance
>
> Promotion boundary: subject to adversarial review and explicit human
> doctrine promotion

## Purpose And Scope

This candidate defines the smallest reusable philosophy, vocabulary, and
promotion process needed before an enduring product architecture can be
codified. It is deliberately not a product catalog, repository design, runtime
topology, or implementation plan.

Architecture should be derived in this order:

```text
philosophy
  -> shared definitions
  -> promotion rules
  -> product model
  -> implementation and repository guidance
```

Each layer constrains the layers after it. A later layer may choose among
implementations that preserve the earlier semantics; it may not redefine an
earlier authority boundary merely because a current topology makes another
choice convenient.

This document keeps three statement classes distinct:

- **Proposed normative guidance** states what a future architecture foundation
  should require. It remains a candidate until explicit doctrine promotion.
- **Research observation** reports what the archived sources or current
  Playbook already say. It supplies evidence but is not authority by itself.
- **Deferred question** records a philosophical, definitional, policy, or
  identity-axis decision this candidate does not answer.

## Candidate Philosophy

The labels below distinguish principles inherited from current doctrine from
new candidate synthesis. Inherited principles remain canonically owned by
[`core-model.md`](core-model.md); they are restated here only to apply them to
product architecture.

### 1. Enduring identity and authority precede topology

**Candidate synthesis.** Architecture should follow customer outcomes and
authority boundaries that remain meaningful when current implementations are
replaced. A repository, package, deployable, service, or named component may
reveal evidence about an identity, but none creates that identity by existing.

### 2. Authority follows the bounded question

**Inherited application.** The
[`Authority Follows The Question`](core-model.md#authority-follows-the-question)
principle rejects a universal system of record. Product architecture should
first state the question precisely, then identify the person, source, or
product whose answer controls that kind of fact within that scope. When a
decision spans several questions, it should preserve the separate owners and
reconcile their answers without allowing one source to absorb another's
authority.

### 3. Consequential authority remains human-rooted

**Inherited application.** The core model's
[`Roles`](core-model.md#roles) and
[`Authority And Transitions`](core-model.md#authority-and-transitions) keep
intent, acceptance, and other consequential transitions human-rooted.
Products, tools, and automations may exercise explicitly delegated authority,
produce evidence, or prepare a decision. Capability, execution, validation,
and stored state do not create permission that was not granted.

### 4. Products do not self-accept their outputs

**Inherited application.** The core model separates
[`evidence production from decision production`](core-model.md#protocol-phases).
A producer must not treat its own valid artifact, finding, proposal, receipt,
or surface as approval of the downstream decision. Acceptance belongs to the
human or consuming authority that owns the next bounded question. This
separation remains necessary even when the producer and consumer share one
operator, repository, or runtime.

### 5. Contracts belong to semantic producers

**Candidate synthesis from current interface guidance.** The default owner of
shared contract meaning should be the identity responsible for producing the
artifact or behavior. The producer maintains emission semantics and compatible
evolution; each consumer owns accepted versions, consumer policy, and
real-path validation. Transport preserves the interchange but owns neither
side's meaning. When no single semantic producer exists, an explicit standards
authority may be needed rather than inferred from shared implementation. That
multi-producer case remains deferred.

### 6. Surfaces render state but do not own it

**Inherited application.** The core model's
[`Evidence Classification Invariant`](core-model.md#evidence-classification-invariant)
keeps derived artifacts distinct from authoritative state. A surface may
produce evidence that it rendered information, delivered an alert, or mediated
a decision. It must not become independent proof of the underlying state
merely by presenting it. A surface remains a replaceable projection unless an
explicitly promoted product boundary assigns it a distinct authoritative
question.

### 7. Implementation and repository topology are downstream

**Candidate synthesis.** Packages, deployables, runtime identities, storage,
source layout, and repositories should be chosen after the enduring outcome and
authority model is clear. Those choices may enforce visibility, security,
review, release, rollback, locality, or contamination boundaries. They must
not be used as shortcuts for deciding what the product is.

### 8. Doctrine is promoted from evidence

**Candidate synthesis consistent with current promotion guidance.** Reusable
doctrine should not be created by isolated insight, polished prose, model
agreement, or one successful run. Research may identify a candidate and
explain why it is conceptually necessary. Doctrine promotion requires
preserved evidence, adversarial review, and an explicit human authority
transition. Divergence and negative evidence remain part of the record.

If this foundation is eventually promoted, canonical ownership and any
duplicated wording must be reconciled so one rule does not drift across
multiple authoritative files.

## Product Identity Taxonomy

**Product identity** is the neutral genus for the architectural hypothesis
being evaluated. Qualification and promotion establish its current status:

```text
proposed product identity
  -> passes the conceptual test
product candidate
  -> passes the accepted operational-evidence standard
  -> receives explicit human product promotion
enduring product
```

The bare term **product** applies to a product candidate or enduring product;
it does not turn an unqualified brainstorm into a product. A rejected identity
or superseded identity is a historical disposition, not necessarily a current
product. The prior evidence and decision remain part of the record even when
the identity no longer qualifies.

## Shared Definitions

**Authority.** Legitimate power for an answer or decision to control within a
defined scope. Authority is distinct from authorization, capability, technical
access, responsibility, accountability, and execution. A
repository-governance authority may control what source is accepted without
authorizing a particular actor to merge a change.

**Authorization.** Permission for an actor to perform a particular action under
stated conditions. Authorization is narrower than authority and does not
assign ownership of the underlying decision. A valid token may authorize an
API call without making its holder authoritative for why the call should occur.

**Responsibility.** An obligation to perform work or maintain an outcome.
Responsibility does not by itself grant permission to act or make the
responsible party's answer controlling. A maintainer may be responsible for a
report while another role retains approval authority.

**Accountability.** An obligation to answer for a result, including explaining
the evidence, decisions, and consequences. Accountability may accompany
authority or responsibility but is not identical to either. A reviewer may be
accountable for a decision without being responsible for implementation.

**Authoritative question.** A bounded question whose controlling answer is
assigned to a defined authority within a stated scope and time. It is narrower
than a universal source of truth. A source repository may answer what code is
present while a planning owner answers why the work is prioritized.

**Execution.** Performance of an action. Execution may exercise capability
under authorization, but successful execution does not establish authority,
responsibility, accountability, or approval. A job completing successfully
does not make its output accepted.

**Customer.** The party that values or requests a product outcome. A customer
is distinct from a consumer, which accepts or uses an emitted artifact,
contract, evidence item, or behavior. The same identity may occupy both roles,
but the roles must not be equated silently.

**Customer outcome.** A result a customer recognizes as valuable independently
of the internal method or artifact that produced it. It is not every emitted
file or operational event. A debug log can support an outcome without being
the outcome.

**Operator.** An actor that runs, supervises, or responds to a process.
Operating a product does not automatically make the operator its customer,
consumer, authority, or beneficiary. Those roles must be assigned separately
when the distinction matters.

**Product identity.** An architectural hypothesis organized around a customer
outcome, one or more bounded authoritative questions, owned evidence or
contracts, stable non-goals, and a meaningful lifecycle. It is the neutral
genus for proposed, candidate, enduring, rejected, and superseded identities.
A repository, service, team, interface, or brainstorm does not establish that
the hypothesis has passed the conceptual test.

**Product.** A product identity that has passed the conceptual test: either a
product candidate or an enduring product. The bare term does not state whether
product promotion has occurred. A proposed product identity that has not
passed the test is not yet a product.

**Product candidate.** A product identity that passes the conceptual test but
has not received product promotion to enduring status. It has an independently
recognizable customer and outcome, distinct authoritative question or
questions, owned evidence, stable non-goals, and a replacement-resistant
identity. A memorable name or proposed control plane without independent
demand is not a product candidate.

**Enduring product.** A product candidate whose outcome and authority boundary
survive implementation replacement, have been shown by real operation to
remain load-bearing under the accepted promotion standard, and receive
explicit human product promotion. The definition does not select the disputed
one-use or two-use evidence threshold.

**Subsystem.** A cohesive internal component that contributes to a product
outcome without owning an independent customer outcome or final authoritative
question. A subsystem may be complex or independently deployed. A reducer does
not become a product merely because it runs as a separate service.

**Capability.** A named ability or behavior that can be implemented, requested,
offered, required, or denied. Capability describes what can be done, not who
may decide that it should be done. An exposed API operation is a capability;
its existence does not authorize a particular actor to invoke it.

**Contract.** Explicit semantic expectations at a boundary, including meaning,
ownership, compatibility, validation, and failure behavior as applicable. A
schema, shared type, or example may express part of a contract but is not
automatically the whole contract. Contract ownership does not create approval,
retention, transport, or downstream decision authority.

**Producer.** The identity responsible for emitting an artifact or behavior and
maintaining its shared emission semantics. Producer status does not create
approval, retention, transport, or downstream decision authority. A dashboard
that copies a receipt is not the producer of the domain state represented by
that receipt.

**Consumer.** The identity that accepts or uses a producer's output under its
own compatibility rules, policy, and lifecycle. Consumer status does not
create authority over the producer's shared semantics or a downstream
decision. A consumer-side validator cannot silently redefine a producer field.

**Trust boundary.** A point where crossing data or authority changes required
validation, identity, handling, authorization, or approval. A trust boundary is
not automatically a product or repository boundary, but it may support a
product identity when it also owns an independent customer outcome and
lifecycle; that identity question remains subject to the conceptual test.

**Runtime boundary.** A separation between independently executing processes,
jobs, services, devices, or environments. A runtime or network crossing is not
itself a trust boundary unless required validation, identity, handling,
authority, authorization, or approval changes across it. Runtime independence
also does not establish product identity.

**Repository.** A source-control, review, history, visibility, and governance
container. It may contain several products, part of one product, or
non-product evidence. One repository does not imply one product, and one
product does not imply one repository.

**Package.** A distributable or installable unit of code or data with a defined
consumption boundary. Packaging does not establish customer outcome,
authority, or runtime independence. Several packages may implement one
product, and one package may contain shared capabilities.

**Deployable.** A unit that can be independently executed, released, rolled
out, failed, scaled, credentialed, or rolled back. Deployment independence does
not establish product identity. A scheduled job remains a deployable even when
it implements only one subsystem.

**Surface.** A human or machine interaction view over state, evidence, or
capabilities. A surface may collect input, route a decision, and produce
evidence of its own rendering, delivery, or mediation. It does not own or
independently prove the represented domain state unless that authority is
explicitly assigned. A dashboard snapshot is not the source of truth for the
system it displays.

**Lifecycle.** The meaningful states, transitions, evidence, and authority
boundaries through which an identity persists. A lifecycle is not a cron
schedule, deployment pipeline, or repository workflow, though those may
implement it. Running nightly describes cadence, not lifecycle.

**Evidence.** Preserved observations or artifacts that support a claim within a
stated scope. Evidence may be direct, derived, negative, partial, or
conflicting; it does not itself grant authority, authorization, approval, or
universal truth. A passing test is evidence for what the test checked, not
proof of product acceptance.

**Promotion.** An explicit human-authorized transition changing the accepted
status of an identity or guidance within a named destination. Promotion is the
generic concept; its product and doctrine applications are distinct.

**Product promotion.** The explicit human-authorized transition from product
candidate to enduring product under the accepted promotion standard. A
successful run, contract, label, copied file, model consensus, or merge is not
product promotion unless it records that decision.

**Doctrine promotion.** The explicit human-authorized transition from candidate
guidance to accepted Playbook doctrine. A branch, pull request, copied file,
label, model consensus, or merge is not doctrine promotion unless it records
that decision.

**Doctrine.** The current accepted reusable normative guidance for how a class
of work should be understood or performed. Doctrine differs from research,
candidate guidance, descriptive documentation, local policy, and
implementation. A popular runbook is not shared doctrine unless the owning
authority promotes it.

**Implementation.** Replaceable mechanisms that realize product semantics,
contracts, and authority boundaries in code, configuration, operations, or
process. Implementation evidence can support architecture, but implementation
convenience cannot redefine it. A service layout is an implementation choice,
not an enduring identity.

## Candidate Promotion Standard

Conceptual identity and operational proof answer different questions:

- **Conceptual irreducibility** asks whether a distinct product boundary is
  necessary enough to name as a product candidate.
- **Operational evidence** asks whether real use has shown that the boundary is
  load-bearing enough to support product promotion to enduring status.

### Research provenance of this synthesis

Neither archived promotion report is canonical. This draft primarily uses the
Codex report's two-part structure:

- Codex supplies the separation between conceptual irreducibility and
  load-bearing repetition.
- Claude supplies the independent-customer deletion test, the alternative
  one-real-transaction threshold, and explicit recognition that some disputes
  cannot be settled by operational evidence alone.

The synthesis below proposes a conservative candidate rule while preserving
the threshold and identity-axis disagreements as explicit human decisions.

### Candidate test: conceptual irreducibility

A proposed product identity must satisfy all of the following to become a
product candidate:

1. **Independent customer and outcome:** name a customer who would still
   request the outcome if adjacent products and current implementations were
   removed.
2. **Owned authoritative question or questions:** the candidate owns the
   controlling answer within the defined scope. An adjacent product may
   exercise explicitly delegated authority, but must not absorb, override, or
   become the default owner of that question within the same scope.
3. **Owned durable evidence:** artifacts or contracts would be semantically
   misplaced under an adjacent product.
4. **Stable non-goal:** the identity includes a consequential boundary it must
   refuse to cross.
5. **Substitution:** replacing current repositories, tools, providers, and
   runtimes leaves the outcome and authority intact.

The candidate cannot pass by inventing an internal customer, declaring a
self-defined consumer, treating its own contract as proof of demand, or
staging cosmetically varied demonstrations. A contract may support semantic
ownership; it does not prove that an independent customer values the outcome.
Delegation permits bounded exercise without transferring authority ownership;
it does not grant unrelated authorization, make execution authoritative, or
replace consumer acceptance.

Passing this test establishes product-candidate status. It does not establish
an enduring product.

### Classify the unresolved question before counting evidence

First distinguish:

- **Missing operational evidence:** a named real observation could change the
  identity status under an already accepted criterion.
- **Deferred doctrine question:** available evidence cannot resolve the
  decision because the disagreement concerns a philosophical, definitional,
  policy, or identity-axis question requiring an explicit human ruling.

**Deferred** is an adjudication status, not a product identity or maturity
status. An identity may remain a proposed product identity or product candidate
while its adjudication is deferred. More ordinary operation does not resolve a
deferred question unless the human ruling first identifies a specific
observation that would matter.

### Evidence test: load-bearing operation

This draft proposes the following smallest conservative rule for product
promotion:

1. At least **two materially independent, non-synthetic real uses** exercise
   the boundary, differing along a material axis such as customer, consumer,
   task, domain, or mechanism. Repeating the same demonstration does not count.
2. At least one use contains a **consequential boundary event**: a refusal,
   fail-closed result, separate approval handoff, blocked action, independently
   consumed contract, or another observable result that would differ if the
   boundary did not exist.
3. The outcome, evidence, and lifecycle remain **attributable to the candidate**
   rather than to a repository name, one implementation, or an adjacent
   product.
4. When the boundary emits a contract, the semantic producer maintains it and
   a real consumer preserves separate acceptance and validation responsibility.
5. An authorized human reviews the evidence, unresolved disagreement,
   counterexamples, and stable non-goals, then explicitly promotes or rejects
   the candidate.

Implementation replacement, contract revision, multiple providers, and
incidents are strong corroboration, but this candidate standard does not make
each one a universal prerequisite.

### Preserved threshold disagreement

The archived promotion reports agree that conceptual coherence identifies a
candidate and real operation supports enduring status. They disagree on the
minimum operational threshold:

- Claude allows product promotion after one real, non-synthetic
  producer-to-consumer transaction when distinct authority, customer,
  contract, independent identity, and irreducibility are already established.
- Codex requires two materially independent real uses, including a
  consequential boundary event and attributable continuity.

This draft proposes two materially independent uses as the smallest
conservative candidate rule: one use establishes possibility, while a second
varied use supplies the minimum evidence of repetition. Whether one
transaction is sufficient, whether two uses are sufficient, and whether the
threshold varies by risk class remain explicit human doctrine decisions.

### Product identity dispositions

- **Proposed product identity:** an architectural hypothesis that has not yet
  passed the conceptual test.
- **Product candidate:** a product identity that passes the conceptual test but
  has not received product promotion.
- **Enduring product:** a product candidate that passes the accepted
  operational-evidence standard and receives explicit human product promotion.
- **Rejected identity:** fails the conceptual test, or real operation shows
  that its outcome and lifecycle belong naturally to another product.
- **Superseded identity:** a later identity or materially different boundary
  replaces its current architectural role.

Rejected and superseded identities are historical dispositions, not claims
that the identity remains a current product.

### Reverse product transitions

Later evidence may show that a previously promoted boundary is no longer
load-bearing or was carved incorrectly. An explicit human decision may:

- demote an enduring product to product candidate when the conceptual boundary
  remains plausible but the operational basis no longer supports enduring
  status;
- reject an enduring product when its independent outcome or authoritative
  question proves illusory or belongs to an adjacent product; or
- supersede an enduring product when another identity or materially revised
  boundary replaces it.

Every reverse transition must preserve the prior evidence and decision record,
record why current authority changed, and avoid rewriting the identity's
historical status.

## Incubator, Playbook, And Doctrine Promotion

The **Incubator** is the noncanonical exploration and evidence boundary. It
preserves experiments, research, competing hypotheses, negative results,
rejected ideas, superseded candidates, and promotion evidence without granting
them doctrine or implementation authority.

The **Playbook** is the current accepted reusable doctrine. Candidate guidance
becomes Playbook authority only through explicit human doctrine promotion under
the Playbook's review and validation boundary. A branch, draft pull request,
polished report, merge, or model consensus remains a proposal unless it records
that transition.

Doctrine promotion is:

- **an explicit human authority transition:** evidence supports the decision
  but does not make it;
- **additive:** the accepted reusable claim and its provenance are added to the
  Playbook without converting the research archive into canon; and
- **non-destructive:** source research, rejected ideas, negative evidence, and
  superseded candidates remain preserved under their historical status.

The normal path is:

```text
experiment
  -> research
  -> candidate guidance
  -> explicit doctrine promotion
  -> accepted Playbook doctrine
```

The equally valid alternate path is:

```text
experiment
  -> research
  -> rejected or superseded guidance
  -> retained as historical evidence
```

### Doctrine revision, demotion, and withdrawal

Later evidence may show that accepted guidance is too broad, no longer useful,
or based on a boundary that was carved incorrectly. An explicit human decision
may:

- **revise** doctrine by narrowing, extending, or replacing the currently
  authoritative guidance;
- **demote** doctrine to candidate guidance when further evidence or review is
  required; or
- **withdraw** doctrine when it should no longer guide current work.

Each transition changes what is authoritative now. It must preserve the prior
evidence and decision record, state why current authority changed, and avoid
rewriting the guidance's historical status.

## Bare Product Identity Entry

A future product-identity entry should contain only the identity and authority
needed to evaluate it before implementation:

```markdown
# [Product identity name]

Product identity status: [proposed | candidate | enduring | rejected | superseded]
Adjudication status: [active | deferred | resolved]

## Enduring Outcome
[Customer-recognized result that survives implementation replacement.]

## Authoritative Questions
[The primary bounded controlling question and any supporting questions this
identity would answer.]

## Authority Owned
[Decisions or transitions it may make, plus authority that remains elsewhere.]

## Customers And Consumers
[Who values or requests the outcome; who accepts or uses its contracts,
artifacts, evidence, or behavior. Keep the roles distinct.]

## Contracts And Evidence
[Producer-maintained contracts, owned evidence, consumer acceptance boundary,
and product-promotion evidence.]

## Stable Non-Goals
[Boundaries the product must refuse to cross.]

## Trust Boundaries
[Data or authority crossings that change validation, identity, handling,
authorization, or approval. State whether any boundary supports product
identity or is only an implementation or governance boundary.]

## Lifecycle
[Meaningful states, transitions, and human authority boundaries.]

## Promotion Status
[Conceptual-test result, operational evidence, preserved disagreements,
adversarial review, explicit human disposition, and any deferred ruling.]
```

The entry should not prescribe repositories, packages, deployables, runtime
topology, storage, migration, or implementation order. Those belong to later
guidance derived from the accepted product model.

## Deferred Human Decisions

This candidate supplies vocabulary and process for later decisions without
adjudicating the disputed AI Workflow product identities. The following remain
deferred:

- whether one real transaction or two materially independent uses are the
  minimum for product promotion;
- whether the operational-evidence threshold should vary by product or risk
  class;
- when interdiction authority establishes an independent product outcome and
  lifecycle rather than a privileged subsystem;
- whether horizontal read-only conformance evidence is a product or a
  capability owned elsewhere;
- whether credential or trust ceilings become products or remain governance
  functions;
- when a multi-producer contract requires a separately named standards
  authority; and
- which trust boundaries support independent product identities rather than
  implementation or governance boundaries.

These are doctrine or identity-axis questions, not merely missing usage data.
Ordinary additional operation does not settle them unless an explicit human
ruling identifies the observation that would change the decision.

The classification of any current AI Workflow product identity remains outside
this document. This foundation defines how a future product model is evaluated;
it does not populate that model.
