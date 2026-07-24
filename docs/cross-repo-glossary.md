# Cross-Repo Architecture Glossary

## Purpose

Use these qualifiers when reasoning across repositories. The goal is not one
universal definition for every domain. It is to prevent humans and AI agents
from silently treating similar words as identical concepts.

Apply the subject, verb, and question-typed authority rules in the
[`Constitutional Vocabulary Guide`](constitutional-vocabulary-guide.md).
Repository-local sources control current repository-specific contract text and
execution behavior. When local usage is narrower or intentionally different,
name the qualified meaning and link its source.

## Terms

### Trust

Trust is justified reliance within a stated scope; it is not a single
ecosystem-wide approval bit.

- **Network trust**: permission for a network identity or CIDR to reach a
  narrowly managed endpoint or rule. It does not establish content or workflow
  trust.
- **Workflow trust**: confidence that a bounded process followed its declared
  inputs, validation, mutation, and cleanup rules. A successful run receipt is
  evidence for this claim, not proof that its source content is true.
- **Provenance trust**: confidence in custody and origin claims. Hashes support
  integrity; they do not by themselves authenticate a producer.
- **Editorial trust**: reviewed judgment that material is suitable for a
  retained purpose. A valid source package is candidate material, not editorial
  approval.

Prefer a qualifier. Avoid saying an artifact is simply “trusted” when the claim
is only valid, authenticated, reviewed, allowlisted, or retained.

### Trust Boundary

A trust boundary is the point where data or authority changes validation or
handling requirements.

- **Input trust boundary**: external or cross-repo input is treated as
  untrusted until the receiving repository validates it.
- **Mutation trust boundary**: dry-run or planning becomes an explicitly
  authorized external change.
- **Editorial trust boundary**: acquired candidate material becomes retained
  knowledge only after consumer-owned review.
- **Publication trust boundary**: reviewed or caller-supplied material is sent
  to an external destination; publication does not transfer editorial or
  lifecycle ownership to the publisher.

Name the data and authority crossing the boundary, the validator, and what a
successful crossing does—and does not—authorize.

### Manifest

A manifest is structured metadata describing intended or observed work. Name
its role because current repositories use several variants.

- **Artifact/package manifest**: authoritative inventory and metadata for a
  package or artifact set, such as `package.json` in a source package.
- **Plan manifest**: dry-run description of intended actions.
- **Run manifest**: structured result and evidence from an executed workflow;
  some repositories also call this a run receipt.
- **Deployment manifest**: declarative Kubernetes or GitOps resource document.

Do not assume every manifest is immutable, authoritative for file bytes, a
receipt, or a deployment declaration.

### Schema Version

A schema version identifies the compatibility rules for a specific serialized
shape. Name the object it versions: registry schema version, config schema
version, manifest schema version, or contract version.

A schema version is not automatically the producer release, adapter version,
API version, or whole interchange contract version. Document incompatible
change rules and consumer acceptance explicitly. Omit versioning when a simple
unversioned interface can evolve safely and compatibility is not negotiated.

### Bundle

A bundle is a grouped set of artifacts prepared for a bounded downstream use.

- **Knowledge bundle**: deterministic markdown assembled from normalized
  adapter output for review, analysis, or publication.
- **Evidence bundle**: provenance-bearing analytical evidence and related
  artifacts in `trusted-ai-environment`.
- **Source package**: the normative term for the sealed acquisition handoff
  from `knowledge-adapters` to consumers; do not casually rename it a bundle
  when package integrity and lifecycle semantics matter.

State whether the bundle is sealed, mutable, reviewed, publication-ready, or
merely candidate material; “bundle” alone promises none of those properties.

### Receipt

A receipt is durable evidence that a bounded operation was planned or
performed and how it ended.

- **Run/operational receipt**: redacted evidence of requested intent,
  validation, optional mutation, outcomes, and cleanup.
- **Publication receipt**: destination-specific evidence of an explicit
  publication event, such as its status and resulting document URL.
- **Lane stop receipt**: a worker's completion report used for orchestration;
  it is navigation and reconciliation evidence, not repository or CI truth.

A receipt is not necessarily a manifest, approval, audit log, retained
knowledge object, or proof of external truth. State its durability and source
of truth.

### Contract

A contract is an explicit set of expectations at a boundary.

- **Interchange contract**: shared producer/consumer semantics, artifact shape,
  compatibility, and failure rules.
- **Consumer contract**: accepted versions plus consumer-local validation and
  policy; it must not silently redefine producer-owned semantics.
- **Execution contract**: repository-local command, validation, or workflow
  behavior, such as `make check`.
- **Governance contract**: documented human or agent responsibilities and stop
  conditions.

Name whether a statement is normative, derived, experimental, or descriptive.
An example or current implementation is evidence for a contract but is not
automatically the whole contract.

### Adapter

An adapter translates one interface while preserving the governing semantic
boundary.

- **Source adapter**: acquires and normalizes external source material into
  provider-neutral candidate artifacts.
- **Tool/executor adapter**: maps shared playbook guidance to executor-specific
  behavior without redefining the core workflow.
- **Knowledge adapter repository/component**: use this only for the source-side
  product role; a downstream publisher is a destination, not a source adapter.

Qualify the term with source, provider, or executor. An adapter does not imply a
generic plugin system or ownership of both sides of the interface.

### Product

A Product is an architectural identity with a bounded customer outcome and
authoritative question. Repository topology does not establish Product
identity.

The status terms below are implementation vocabulary. They do not classify a
current identity, promote a Product Candidate, or promote the candidate
Architecture Foundation into doctrine.

- **Product Candidate**: a Product identity that has passed the conceptual test
  but has not received explicit human promotion to Enduring Product. The
  required first-reference status distinction remains subject to the
  ratification boundary recorded in the Constitutional Vocabulary Guide.
- **Enduring Product**: a Product Candidate whose outcome and authority
  boundary have satisfied the accepted operational standard and received
  explicit human Product promotion.
- **Repository implementation**: the replaceable code, configuration,
  operations, process, contracts, or evidence currently hosted by a
  repository. A repository may host several Products, part of one Product, or
  non-Product evidence.
- **Product object**: the durable or reviewable outcome, such as an operational
  receipt or publication event.
- **External provider product**: a third-party service or API; qualify it as a
  provider product to avoid assigning its lifecycle to an implementing
  repository.

Infrastructure used during a workflow is not automatically the product or
repository-owned state.

### Semantic Producer

A Semantic Producer is the Product or other typed identity responsible for
shared contract meaning, emission semantics, and compatible evolution.

The normative contract may currently live in the producer implementation
repository, but that location does not make the repository the constitutional
owner of the contract's meaning. This distinction remains subject to the
ratification boundary recorded in the Constitutional Vocabulary Guide.

### Runtime Producer

A Runtime Producer is the component, command, adapter, service, or process that
emits a contract instance. It performs producer-side behavior under the
contract; successful emission does not create approval, retention, publication,
or downstream decision authority.

Do not infer semantic ownership merely because the runtime producer is the
first or only implementation.

### Repository Authority

Repository Authority is always question-typed. A repository and its hosted
state control current files, implementation, review, validation, and merge
facts. That authority does not become general Product or domain authority.

The formal question-typed terminology remains subject to the ratification
boundary recorded in the Constitutional Vocabulary Guide.

### Capability

A capability is a named behavior that may affect eligibility, compatibility,
or execution.

- **Contract capability**: a declared feature of an interchange that a
  consumer may require or reject, such as collection progress.
- **Provider capability**: behavior or availability reported or documented by
  an external provider, such as a region supporting Object Storage.
- **Repository/tool capability**: behavior implemented by a repository or
  command.
- **Agent capability**: an available tool or execution ability; availability
  is not authorization to use it.

State who declares the capability, how it is verified, and whether it is
required, optional, or merely observed. A capability flag must not hide an
incompatible semantic change.

### Autonomous Maintenance Layer

The **autonomous maintenance layer** is the ecosystem capability that performs
recurring, bounded inspection, maintenance, and improvement across independently
governed repositories.

It may produce findings, review-ready proposals, or bounded hygiene under
mechanically verifiable safety predicates. Bounded hygiene may include cleanup
that is not literally reversible and therefore needs recovery evidence or a
documented recovery path where practical. The layer does not own canonical
doctrine, repository-local policy, producer/consumer semantics, merge decisions,
or consequential transitions. Its scheduler and enabled automation inventory
are local configuration; its authority boundaries and evidence contract are
architectural doctrine.

Use this governed term for the layer. Use “automation” or “job” only for a
specific implementation within it. Do not use “autonomous” to imply unrestricted
mutation authority.

## Usage Guidance

- Prefer qualified phrases in cross-repo docs, issues, prompts, and PRs.
- Preserve established public names, schema fields, and repository names; add
  a qualifier or link instead of renaming them in prose-only cleanup.
- When two repositories use the same word differently, document both meanings
  and the boundary between them rather than forcing a false universal meaning.
- Treat this glossary as navigation. Verify current repository contracts and
  implementation before making ownership, compatibility, or security claims.
