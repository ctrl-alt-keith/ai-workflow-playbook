# Candidate Architecture Foundation

> Status: candidate doctrine
>
> Evidence basis: derived from the noncanonical
> [architecture research archive](https://github.com/ctrl-alt-keith/ai-workflow-incubator/tree/7ef03580cf9c7725b0e325c48ac74cb6a6d4a76f/archive/architecture-research-2026-07-23)
>
> Authority: not authoritative; this draft does not supersede current Playbook
> guidance
>
> Promotion boundary: subject to adversarial review and explicit human
> promotion

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

## Candidate Philosophy

### 1. Enduring identity and authority precede topology

Architecture follows customer outcomes and authority boundaries that remain
meaningful when current implementations are replaced. A repository, package,
deployable, service, or named component may reveal evidence about an identity,
but none creates that identity by existing.

### 2. Authority follows the bounded question

There is no universal system of record. First state the question precisely,
then identify the person, source, or product whose answer controls that kind of
fact within that scope. When a decision spans several questions, preserve the
separate owners and reconcile their answers without allowing one source to
absorb another's authority.

### 3. Consequential authority remains human-rooted

Humans own intent, acceptance, promotion, and other consequential transitions.
Products, tools, and automations may exercise explicitly delegated authority,
produce evidence, or prepare a decision. Capability, execution, validation,
and stored state do not create permission that was not granted.

### 4. Products do not self-accept their outputs

A producer cannot treat its own valid artifact, finding, proposal, receipt, or
surface as approval of the downstream decision. Acceptance belongs to the
human or consuming authority that owns the next bounded question. This
separation remains necessary even when the producer and consumer share one
operator, repository, or runtime.

### 5. Contracts belong to semantic producers

The default owner of shared contract meaning is the product that produces the
artifact or behavior. The producer owns emission semantics and compatible
evolution; each consumer owns accepted versions, consumer policy, and
real-path validation. Transport preserves the interchange but owns neither
side's meaning. When no single semantic producer exists, an explicit standards
authority must be named rather than inferred from shared implementation.

### 6. Surfaces render state but do not own it

Dashboards, reports, digests, indexes, alerts, and other surfaces present or
route product-owned state. They remain replaceable projections unless an
explicitly promoted product boundary assigns them a distinct authoritative
question. A derived view must not become evidence for the authoritative state
it summarizes.

### 7. Implementation and repository topology are downstream

Packages, deployables, runtime identities, storage, source layout, and
repositories are chosen after the enduring outcome and authority model is
clear. Those choices may enforce visibility, security, review, release,
rollback, locality, or contamination boundaries. They must not be used as
shortcuts for deciding what the product is.

### 8. Doctrine is promoted from evidence

Reusable doctrine is not created by isolated insight, polished prose, model
agreement, or one successful run. Research may identify a candidate and
explain why it is conceptually necessary. Promotion requires preserved
operational evidence, adversarial review, and an explicit human authority
transition. Divergence and negative evidence remain part of the record.

## Shared Definitions

**Authority.** Legitimate responsibility and permission to answer a bounded
question or authorize a transition. Authority is not capability, influence, or
technical access. A tool that can delete a record is not thereby authorized to
delete it.

**Authoritative question.** The precise question for which a named authority's
answer controls within a stated scope and time. It is narrower than a universal
source of truth. A source repository may answer what code is present while a
planning owner answers why the work is prioritized.

**Customer outcome.** A result a customer recognizes as valuable independently
of the internal method or artifact that produced it. It is not every emitted
file or operational event. A debug log can support an outcome without being
the outcome.

**Product.** A durable arrangement around a customer outcome, one or more
bounded authoritative questions, owned evidence or contracts, stable
non-goals, and a meaningful lifecycle. A product is not defined by a
repository, service, team, or interface. A separately deployed worker is not a
product when its replacement leaves the same outcome and authority intact.

**Enduring product.** A product whose outcome and authoritative boundary
survive implementation replacement and whose separation has proved
load-bearing in repeated real work. It differs from a product candidate by
having operational evidence of durability. A plausible future service is not
enduring merely because its design is coherent.

**Product candidate.** A conceptually irreducible proposed product that has a
distinct outcome, authoritative question, owned evidence, stable non-goal, and
replacement-resistant identity, but lacks sufficient operational evidence for
enduring status. A memorable name or proposed control plane without an
independent outcome is not a candidate.

**Subsystem.** A cohesive internal component that contributes to a product
outcome without owning an independent customer outcome or final authoritative
question. A subsystem may be complex or independently deployed. A reducer does
not become a product merely because it runs as a separate service.

**Capability.** A named ability or behavior that can be implemented, requested,
offered, required, or denied. Capability describes what can be done, not who
may decide that it should be done. An API permission is capability, not
authorization for a particular use.

**Contract.** Explicit semantic expectations at a boundary, including meaning,
ownership, compatibility, validation, and failure behavior as applicable. A
schema, shared type, or example may express part of a contract but is not
automatically the whole contract. Contract ownership does not make the
contract an independent product.

**Producer.** The authority that emits an artifact or behavior and owns its
shared emission semantics. The producer need not transport, approve, retain, or
consume what it produces. A dashboard that copies a receipt is not the producer
of the domain state represented by that receipt.

**Consumer.** An authority that accepts and uses a producer's output under its
own compatibility rules, policy, and lifecycle. A consumer owns acceptance and
use, not the producer's shared semantics. A consumer-side validator cannot
silently redefine a producer field.

**Trust boundary.** A point where crossing data or authority changes the
required validation, handling, identity, or approval. A trust boundary is not
automatically a product or repository boundary. A network hop between
components with identical handling requirements may not be a meaningful trust
boundary.

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
capabilities. A surface may collect input or route a decision, but it does not
own the represented domain state unless that authority is explicitly assigned.
A dashboard snapshot is not the source of truth for the system it displays.

**Lifecycle.** The meaningful states, transitions, evidence, and authority
boundaries through which an identity persists. A lifecycle is not a cron
schedule, deployment pipeline, or repository workflow, though those may
implement it. Running nightly describes cadence, not lifecycle.

**Evidence.** Preserved observations or artifacts that support a claim within a
stated scope. Evidence may be direct, derived, negative, partial, or
conflicting; it does not itself grant authority, approval, or universal truth.
A passing test is evidence for what the test checked, not proof of product
acceptance.

**Promotion.** An explicit human-authorized transition that makes a candidate
the accepted current authority in a destination, based on reviewed evidence.
Copying a document, opening or merging a pull request, or changing a status
label is not sufficient unless it records the explicit promotion decision.

**Doctrine.** The current accepted reusable normative guidance for how a class
of work should be understood or performed. Doctrine differs from research,
descriptive documentation, local policy, and implementation. A popular
runbook is not shared doctrine unless the owning authority promotes it.

**Implementation.** Replaceable mechanisms that realize product semantics,
contracts, and authority boundaries in code, configuration, operations, or
process. Implementation evidence can support architecture, but implementation
convenience cannot redefine it. A service layout is an implementation choice,
not an enduring identity.

## Candidate Promotion Standard

Conceptual identity and operational proof answer different questions:

- **Conceptual irreducibility** asks whether a distinct product boundary is
  necessary enough to name as a candidate.
- **Operational evidence** asks whether real use has shown that the boundary is
  load-bearing enough to promote as enduring.

### Candidate test: conceptual irreducibility

A product candidate must satisfy all of the following:

1. **Independent outcome:** a customer recognizes the result apart from the
   mechanism that produces it.
2. **Exclusive authoritative question:** an adjacent product must not answer
   the bounded question on the candidate's behalf.
3. **Owned durable evidence:** artifacts or contracts would be semantically
   misplaced under an adjacent product.
4. **Stable non-goal:** the identity includes a consequential boundary it must
   refuse to cross.
5. **Substitution:** replacing current repositories, tools, providers, and
   runtimes leaves the outcome and authority intact.

Passing this test identifies a candidate. It does not establish an enduring
product.

### Evidence test: load-bearing operation

This draft proposes the following smallest conservative rule for promotion:

1. At least **two independent, non-synthetic real uses** exercise the boundary,
   differing along a material axis such as customer, consumer, task, domain, or
   mechanism. Repeating the same demonstration does not count.
2. At least one use contains a **consequential boundary event**: a refusal,
   fail-closed result, separate approval handoff, blocked action, independently
   consumed contract, or another observable result that would differ if the
   boundary did not exist.
3. The outcome, evidence, and lifecycle remain **attributable to the candidate**
   rather than to a repository name, one implementation, or an adjacent
   product.
4. When the boundary emits a contract, the semantic producer owns it and a
   real consumer preserves separate acceptance and validation authority.
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

- one report allows promotion after one real, non-synthetic producer-to-consumer
  transaction when distinct authority, customer, contract, identity, and
  irreducibility are already established;
- the other requires two independent real uses, including a consequential
  boundary event and attributable continuity.

This draft adopts two independent uses as the smallest conservative candidate
rule: one use establishes possibility, while a second varied use supplies the
minimum evidence of repetition. The archive does not establish that this
threshold is sufficient for every risk class. An adversarial reviewer may
require stronger evidence, and any future claim that one use is sufficient
remains an explicit human doctrine decision rather than a silent exception.

### Dispositions

- **Product candidate:** passes the conceptual test but not the evidence test.
- **Enduring product:** passes both tests and receives explicit human
  promotion.
- **Rejected identity:** fails the conceptual test or real operation shows that
  its outcome and lifecycle belong naturally to another product.
- **Superseded identity:** was once useful but later evidence supports a
  replacement or materially narrower boundary.

## Incubator, Playbook, And Promotion

The **Incubator** is the noncanonical exploration and evidence boundary. It
preserves experiments, research, competing hypotheses, negative results,
rejected ideas, superseded candidates, and promotion evidence without granting
them doctrine or implementation authority.

The **Playbook** is the current accepted reusable doctrine. Content becomes
Playbook authority only through explicit human promotion under the Playbook's
review and validation boundary. A branch, draft pull request, polished report,
or model consensus remains a proposal until that transition occurs.

Promotion is:

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
  -> candidate
  -> promoted doctrine
```

The equally valid alternate path is:

```text
experiment
  -> research
  -> rejected or superseded
  -> retained as historical evidence
```

Doctrine revision or demotion changes what guidance is authoritative now. It
does not rewrite the evidence, decisions, or doctrine versions that were
authoritative earlier. A later rule should preserve provenance to the prior
rule and the evidence that justified the change.

## Bare Product Entry

A future product entry should contain only the identity and authority needed to
evaluate it before implementation:

```markdown
# [Product name]

Status: [candidate | enduring | rejected | superseded]

## Enduring Outcome
[Customer-recognized result that survives implementation replacement.]

## Authoritative Question
[The bounded question this product, and no adjacent product, answers.]

## Authority Owned
[Decisions or transitions it may make, plus authority that remains elsewhere.]

## Customers And Consumers
[Who values the outcome; who consumes its contracts or evidence.]

## Contracts And Evidence
[Producer-owned contracts, owned evidence, consumer acceptance boundary, and
promotion evidence.]

## Stable Non-Goals
[Boundaries the product must refuse to cross.]

## Trust Boundaries
[Data or authority crossings that change validation, identity, handling, or
approval.]

## Lifecycle
[Meaningful states, transitions, and human authority boundaries.]

## Promotion Status
[Conceptual-test result, operational evidence, preserved disagreements,
adversarial review, and explicit human disposition.]
```

The entry should not prescribe repositories, packages, deployables, runtime
topology, storage, migration, or implementation order. Those belong to later
guidance derived from the accepted product model.

## Review Boundary

This candidate intentionally leaves these questions open for adversarial
review:

- whether two independent real uses are sufficient for every product and risk
  class;
- when a multi-producer contract requires a separate standards authority;
- how to distinguish a product-level authoritative question from a
  cross-cutting governance function or contract authority;
- which trust boundaries own customer outcomes and which remain implementation
  or governance boundaries; and
- whether any existing product candidate satisfies this standard.

The last question is explicitly outside this document. This foundation defines
how a future product model is evaluated; it does not populate that model.
