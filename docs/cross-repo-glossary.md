# Cross-Repo Architecture Glossary

## Purpose

Use these qualifiers when reasoning across repositories. The goal is not one
universal definition for every domain. It is to prevent humans and AI agents
from silently treating similar words as identical concepts.

Repository-local contracts remain authoritative. When local usage is narrower
or intentionally different, name the qualified meaning and link its source.

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

An adapter translates one interface while preserving an owning boundary.

- **Source adapter**: acquires and normalizes external source material into
  provider-neutral candidate artifacts.
- **Tool/executor adapter**: maps shared playbook guidance to executor-specific
  behavior without redefining the core workflow.
- **Knowledge adapter repository/component**: use this only for the source-side
  product role; a downstream publisher is a destination, not a source adapter.

Qualify the term with source, provider, or executor. An adapter does not imply a
generic plugin system or ownership of both sides of the interface.

### Product

A product is the bounded outcome a repository exists to provide, not every
resource it touches.

- **Repository product boundary**: owned responsibilities, primary product
  object, decision filter, and non-goals.
- **Product object**: the durable or reviewable outcome, such as an operational
  receipt or publication event.
- **External provider product**: a third-party service or API; qualify it as a
  provider product to avoid assigning its lifecycle to the repository.

Infrastructure used during a workflow is not automatically the product or
repository-owned state.

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

## Usage Guidance

- Prefer qualified phrases in cross-repo docs, issues, prompts, and PRs.
- Preserve established public names, schema fields, and repository names; add
  a qualifier or link instead of renaming them in prose-only cleanup.
- When two repositories use the same word differently, document both meanings
  and the boundary between them rather than forcing a false universal meaning.
- Treat this glossary as navigation. Verify current repository contracts and
  implementation before making ownership, compatibility, or security claims.
