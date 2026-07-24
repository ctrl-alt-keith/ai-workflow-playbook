# Constitutional Vocabulary Guide

> Status: Playbook implementation guidance
>
> Source: derived from the accepted Constitutional Vocabulary Review
>
> Authority: subordinate to current Playbook doctrine
>
> Adoption boundary: inclusion in a reviewed Playbook change records adoption
> as implementation guidance only. It is not doctrine promotion, Product
> promotion, a new Product Model, an authority-boundary change, or automatic
> promotion of the
> [candidate Architecture Foundation](architecture-foundation-candidate.md)
> into doctrine.

## Purpose

This guide standardizes constitutional language across the ecosystem. It helps
documentation consistently distinguish:

- Product authority;
- human governance authority;
- repository implementation and accepted source state; and
- runtime execution.

The central rule is:

> A Product owns the bounded domain question and contract meaning.
> An authorized human makes consequential decisions.
> A Repository currently hosts, records, and implements accepted state.
> A Capability, Subsystem, or runtime component performs work.

Every authority statement should identify the bounded question being answered.
Avoid using a repository name as shorthand for Product authority, human
judgment, and implementation behavior simultaneously.

## Constitutional Grammar

### Product Or Product Candidate

A Product is an architectural identity with a bounded outcome and authoritative
question. A Product Candidate has passed the conceptual test but has not
received explicit human promotion to enduring status.

Use the precise status on first reference.

**Valid verbs:**

- owns a bounded authoritative question;
- defines an outcome or stable non-goal;
- owns shared contract meaning;
- establishes a lifecycle boundary;
- produces or preserves Product evidence; and
- consumes another Product's contract.

**Avoid:**

- implying that a Product Candidate is enduring;
- saying a Product self-approves or self-promotes;
- using the Product name for low-level execution when a component performs the
  action; and
- inferring Product identity from a repository, package, service, or
  deployment.

**Example:**

> Publication owns the authorized external-delivery transaction and
> publication-receipt semantics.

### Enduring Product

An Enduring Product is a Product Candidate that has satisfied the accepted
operational standard and received explicit human Product promotion.

It uses the same authority grammar as a Product Candidate. "Enduring" describes
accepted status, not greater execution capability.

**Valid verbs:**

- owns the same bounded authority established by its Product identity;
- has received explicit Product promotion; and
- preserves a replacement-resistant outcome and authority boundary.

**Avoid:**

- calling a Product enduring because it has code, users, contracts, tests,
  successful runs, or merged changes;
- treating widespread implementation as Product promotion; and
- omitting the promotion decision when asserting enduring status.

**Example:**

> This identity remains a Product Candidate; no explicit human promotion to
> Enduring Product has occurred.

### Human Governance Authority

Human governance authority is the root of consequential intent, approval,
acceptance, promotion, and reversal.

Name the role when the distinction matters: authorized human reviewer, planning
authority, repository merge authority, Product-promotion authority, or another
bounded decision role.

**Valid verbs:**

- decides;
- approves or rejects;
- authorizes;
- accepts;
- promotes;
- merges;
- delegates;
- prioritizes;
- reverses; and
- grants permission.

**Avoid:**

- assigning human judgment to a repository, tool, validator, or automation;
- assuming that an operator automatically has decision authority;
- treating successful execution or validation as approval; and
- saying that a Product accepts its own output.

**Example:**

> An authorized human reviewer decides whether candidate material is retained,
> rejected, restricted, or deferred.

### Repository

A Repository is a source-control, review, history, and implementation
container. It may implement one Product, multiple Products, part of a Product,
or supporting Capabilities that are not Products.

**Valid verbs:**

- currently hosts;
- contains;
- records;
- stores;
- implements;
- packages;
- exposes;
- validates;
- distributes;
- provides; and
- controls accepted repository source, review, validation, and merge facts.

**Avoid:**

- saying a Repository owns a domain merely because its implementation lives
  there;
- defining Product identity from repository topology;
- using "Repository authority" without naming the repository-specific
  question; and
- implying that the first or only implementation owns constitutional meaning.

**Example:**

> `ka-destinations` currently implements Publication destination drivers and
> records publication receipts.

### Semantic Contract Producer

The Semantic Contract Producer is the Product identity responsible for the
meaning of an emitted artifact or behavior.

**Valid verbs:**

- owns shared contract meaning;
- defines emission semantics;
- defines compatibility expectations;
- maintains compatible evolution; and
- establishes producer guarantees.

**Avoid:**

- identifying the semantic producer solely by repository location;
- transferring consumer policy or downstream approval authority to the
  producer;
- treating transport as ownership of either side's meaning; and
- treating an emitting component as the constitutional contract owner.

**Example:**

> Source Acquisition is the semantic producer of the Source Package contract.

### Runtime Producer

A Runtime Producer is the component, command, adapter, service, or process that
emits a contract instance.

**Valid verbs:**

- emits;
- serializes;
- validates before emission;
- normalizes;
- packages;
- records;
- returns; and
- performs the producer-side operation.

**Avoid:**

- saying it owns shared semantics unless it is explicitly also the semantic
  authority;
- saying its successful output approves a downstream decision;
- assigning editorial, retention, or publication authority to the component;
  and
- confusing provenance identity with authenticated authority.

**Example:**

> The source adapter emits a sealed Source Package conforming to Source
> Acquisition semantics.

### Contract Consumer

A Contract Consumer accepts or uses an emitted artifact or behavior under
consumer-local policy.

When necessary, distinguish the consuming Product from the component that
performs consumer validation.

**Valid verbs:**

- consumes;
- accepts declared versions;
- rejects unsupported versions;
- applies consumer-local policy;
- validates before use;
- interprets within the normative contract; and
- performs real-path integration validation.

**Avoid:**

- redefining producer-owned shared semantics;
- treating structural validity as approval;
- assuming that consumption grants authority over the producer; and
- confusing the consuming Product with the Repository hosting its
  implementation.

**Example:**

> Knowledge Record consumes the Source Package contract and owns its editorial
> acceptance policy. The consumer implementation currently hosted in
> `knowledge-vault` validates packages before review.

### Capability

A Capability is a named ability or behavior. It describes what can be done,
not who may decide that it should be done.

**Valid verbs:**

- enables;
- performs;
- supports;
- provides;
- validates;
- renders;
- acquires;
- publishes; and
- transports.

**Avoid:**

- owns authority;
- decides;
- approves;
- authorizes;
- governs a Product boundary; and
- becoming a Product merely because it is technically substantial.

**Example:**

> The publication Capability performs destination-specific rendering under an
> existing authorization.

### Subsystem

A Subsystem is a cohesive internal component that contributes to a Product
outcome without owning an independent customer outcome or final authoritative
question.

**Valid verbs:**

- implements;
- executes;
- transforms;
- validates;
- coordinates;
- renders;
- transports;
- emits; and
- records.

**Avoid:**

- assigning final Product authority to the Subsystem;
- inferring Product identity from independent deployment;
- saying the Subsystem approves its own output; and
- using deployment or complexity as evidence of authority.

**Example:**

> The destination driver Subsystem performs the external API operation and
> returns observed destination identity.

### Surface

A Surface is a human or machine view over state, evidence, or Capabilities.

**Valid verbs:**

- displays;
- renders;
- presents;
- collects;
- routes;
- mediates;
- links; and
- records evidence of delivery or presentation.

**Avoid:**

- owns the represented state;
- proves the underlying domain state;
- decides merely by presenting a control; and
- becomes authoritative because it is the primary user interface.

**Example:**

> The review Surface presents candidate material and records the reviewer's
> disposition; it does not make the editorial decision.

## Writing Rules

### 1. Use "Owns" Only For Bounded Authority

Before writing "owns," ask what exact question is controlled.

Valid:

> Knowledge Record owns the editorial-retention authority boundary.

Invalid:

> `knowledge-vault` owns everything related to reviewed knowledge.

Ownership must not be shorthand for implementation location, technical
Capability, maintenance responsibility, or historical association.

### 2. Repositories Host And Implement

Use Repository names for current topology and accepted Repository state:

- currently hosts;
- currently implements;
- contains;
- records;
- stores;
- validates; and
- distributes.

Prefer "currently" when the implementation location could change without
changing the Product identity.

### 3. Humans Decide

Consequential decisions must use a human-governance subject unless authority
has been explicitly delegated.

Use:

- "An authorized human reviewer decides...";
- "The Product-promotion authority promotes..."; and
- "Repository merge authority accepts the source change...".

Do not use a tool, Repository, policy document, validator, or Product as a
substitute for the human decision-maker.

A policy may be authoritative for criteria. A human remains authoritative for
applying those criteria to a consequential case.

### 4. Capabilities And Subsystems Perform

Use operational verbs for operational actors:

- an adapter acquires;
- a validator validates;
- a driver publishes;
- a renderer renders; and
- an orchestrator transports.

Execution does not create authority or approval.

### 5. Separate Semantic Producer From Runtime Producer

A Product owns shared contract meaning. A component emits a conforming
instance. A Repository hosts the contract and implementation.

Use all three subjects when the distinction is material:

> Source Acquisition owns Source Package semantics. `knowledge-adapters`
> currently hosts the normative contract. A source adapter emits a conforming
> package.

### 6. Separate Consumer Policy From Producer Semantics

The semantic producer defines the shared interchange. The consumer owns
accepted versions, consumer-local policy, and validation before use.

A consumer may summarize the producer contract but must not silently redefine
it.

### 7. Separate Repository Governance From Product Governance

Repository governance controls questions such as:

- which source is accepted;
- which validation is required;
- whether review requirements were met;
- whether a change may merge; and
- what current implementation exists.

Product governance controls the Product's bounded domain questions.

Repository acceptance is not Product promotion. A merged contract or
implementation does not make a Product Candidate enduring.

### 8. Preserve Product-Status Qualifiers

On first reference, use:

- Product Candidate;
- Enduring Product;
- proposed Product identity; or
- rejected or superseded identity;

as applicable.

Do not let the unqualified word "Product" obscure whether promotion has
occurred.

### 9. Do Not Rewrite History Silently

Historical records should remain accurate evidence of the language and
assumptions used when they were created.

When terminology evolves:

- preserve frozen artifacts and exact historical records;
- add an interpretation banner, companion note, or current terminology index;
- distinguish historical implementation allocation from current
  constitutional authority; and
- never make old evidence appear to have used vocabulary it did not use.

## Authority Questions

Every governance statement should answer a bounded question.

| Question | Constitutional authority | Implementation or evidence location |
| --- | --- | --- |
| What source or implementation is accepted in this Repository? | Repository governance and merge authority | Repository source, review, validation, and history |
| What candidate material is retained, rejected, restricted, or deferred? | Knowledge Record authority boundary, exercised by an authorized human reviewer | Current Knowledge Record implementation and retained decision records |
| What exact artifact is authorized for external delivery, and what happened? | Publication authority boundary plus human or delegated publication authorization | Publication implementation, destination driver, and receipt |
| What was requested, acquired, normalized, and packaged? | Source Acquisition authority boundary | Adapter execution evidence and Source Package |
| May this Repository change merge? | Repository merge authority | Review state, validation, branch, and pull-request evidence |
| What does a shared contract mean? | Semantic Contract Producer | Normative contract currently hosted near the producer implementation |
| Which contract versions and inputs may this consumer accept? | Consuming Product's local policy | Consumer contract, validator, fixtures, and integration tests |
| What did a command, adapter, validator, or driver do? | No new governance authority; this is an implementation-behavior question | Runtime logs, receipts, tests, and Repository implementation |

Avoid the universal question "Which Repository is the authority?" Ask instead:

> Authority for which fact, decision, transition, or contract meaning?

## Repository-First And Constitutional Examples

### Editorial Retention

Repository-first:

> `knowledge-vault` owns editorial review.

Constitutional:

> Knowledge Record owns the editorial-retention authority boundary. An
> authorized human reviewer makes consequential retention decisions.
> `knowledge-vault` currently hosts the implementation and records accepted
> editorial decisions.

### Acquisition

Repository-first:

> `knowledge-adapters` owns ingestion and normalization.

Constitutional:

> Source Acquisition owns the bounded acquisition transaction and Source
> Package semantics. `knowledge-adapters` currently implements acquisition
> adapters and hosts the normative contract.

### Publication

Repository-first:

> `ka-destinations` owns publication.

Constitutional:

> Publication owns the authorized external-delivery transaction and
> publication-receipt semantics. `ka-destinations` currently implements
> destination-specific publication behavior.

### Contract Ownership

Repository-first:

> The producer Repository owns the contract.

Constitutional:

> The Semantic Contract Producer owns shared contract meaning and compatible
> evolution. The producer Repository currently hosts the normative contract
> and producer implementation.

### Runtime Execution

Repository-first:

> The adapter owns acquisition.

Constitutional:

> Source Acquisition owns acquisition semantics. The adapter performs the
> acquisition and emits the resulting contract artifact.

### Human Review

Repository-first:

> The vault decides whether content should be retained.

Constitutional:

> An authorized human reviewer decides whether candidate material is retained
> under Knowledge Record policy. The consumer implementation records and
> validates that decision.

### Repository Authority

Overbroad:

> This Repository is authoritative.

Constitutional:

> This Repository's accepted source and hosted state are authoritative for its
> current files, implementation, validation, review, and merge facts.

### Multiple Products In One Repository

Repository-first:

> This Repository's Product is reviewed knowledge.

Constitutional:

> This Repository currently hosts the Knowledge Record implementation and an
> Evidence Synthesis reference workflow. Their authority boundaries remain
> distinct even though they share Repository topology.

## Repository Guidance

- A Repository may implement one Product, several Products, part of a Product,
  or supporting Capabilities that are not Products.
- Repository boundaries may enforce source control, review, security, release,
  history, or contamination boundaries without defining Product identity.
- The first, primary, or only implementation does not automatically own
  constitutional meaning.
- Moving an implementation does not move Product authority unless the
  governing authority boundary is explicitly changed.
- Shared Repository location does not merge Product authorities.
- Separate Repositories do not prove separate Product identities.
- Repository names should appear as implementation or evidence locations, not
  as substitutes for Products.
- Historical records should preserve their original vocabulary. Current
  guidance should explain how historical Repository-first language maps to the
  constitutional model.

## Terminology Reference

### Product Candidate Term

A Product identity that has passed the conceptual test but has not received
explicit human promotion to Enduring Product.

### Enduring Product Term

A Product Candidate whose outcome and authority boundary have satisfied the
accepted operational standard and received explicit human Product promotion.

### Governance Function Term

A proposed term for a human-rooted, non-Product function controlling intent,
policy, approval, promotion, prioritization, or permission within a bounded
scope without owning an independent customer outcome.

This definition still requires human ratification. Until then, prefer a
specific authority name such as "authorized human reviewer," "Repository merge
authority," or "Product-promotion authority."

### Semantic Producer Term

The Product identity responsible for shared contract meaning, emission
semantics, and compatible evolution.

### Runtime Producer Term

The component or process that performs producer-side behavior and emits a
contract instance.

### Repository Authority Term

Authority limited to a named Repository question, such as accepted source,
current implementation, validation, review, or merge state. It is not general
Product or domain authority.

### Human Decision Authority Term

The authorized human role whose answer controls a consequential decision or
transition within a defined scope.

## Relationship To Existing Doctrine

This guide operationalizes the accepted Constitutional Vocabulary Review and
its application of current doctrine and candidate constitutional guidance.
Apply it with the human-rooted, question-typed authority rules in
[`core-model.md`](core-model.md).

It does not:

- promote a Product Candidate;
- define a new Product;
- alter an authority boundary;
- redesign Repository topology;
- establish a new contract;
- replace current Playbook doctrine; or
- convert candidate constitutional guidance into doctrine by itself.

## Recommended Home And Use

This guide lives in the AI Workflow Playbook as reusable implementation
guidance, adjacent to the cross-repository glossary and interface-contract
guidance.

Link to it from:

- the cross-repository architecture glossary;
- the Repository-to-Repository contract guidance;
- ecosystem documentation; and
- contributor guidance for Repositories using constitutional terminology.

Repository-local documents should apply this guide, not fork or redefine it.

## Completion And Ratification Boundary

The guide is complete enough to drive a focused documentation-alignment pass
using consistent, mechanical language rules.

Before Repository-wide updates begin, explicit human ratification remains
required for:

1. the formal definition of **Governance Function**;
2. the required first-reference distinction between **Product Candidate** and
   **Enduring Product**;
3. the formal **Semantic Producer** versus **Runtime Producer** distinction;
4. the question-typed meaning of **Repository Authority**; and
5. adoption and any future status of this guide itself.

No Product promotion or architectural redesign follows from this guide.
