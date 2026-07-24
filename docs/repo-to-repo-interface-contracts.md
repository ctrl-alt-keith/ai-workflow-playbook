# Repo-To-Repo Interface Contracts

## Purpose

Use a small, explicit contract when one repository produces an artifact or
behavior that another repository consumes. The contract should make ownership,
compatibility, validation, and failure behavior reviewable without creating a
central schema repository, shared library, or new approval gate.

Apply the subject and authority rules in the
[`Constitutional Vocabulary Guide`](constitutional-vocabulary-guide.md) when
naming Semantic Contract Producers, Runtime Producers, contract hosts,
consumers, human authority, and repository implementation. The
[`Human Constitutional Terminology Ratification Decision`](constitutional-terminology-ratification-decision.md)
records the accepted terminology status.

This is a documentation pattern, not a required file format. Use only the
sections that clarify the real interface. A short section in an existing design
document is enough for a simple integration; a dedicated contract document is
appropriate when the interface is versioned, security-sensitive, or consumed
by more than one workflow.

## Evidence Behind The Pattern

The strongest current example is the
[Trusted Network Registry schema contract](https://github.com/ctrl-alt-keith/trusted-network-registry/blob/main/docs/registry-schema.md)
and its
[`linode-image-lab` consumer contract](https://github.com/ctrl-alt-keith/linode-image-lab/blob/main/docs/trusted-registry-firewall-sync.md).
The registry's semantic contract producer defines the versioned schema. The
producer repository currently hosts the normative contract, implementation,
and public-safe fixture. Its runtime producer emits a contract instance. The
consumer declares the accepted version, carries a compatibility fixture through
its real validation and planning path, and fails closed on invalid or stale
input.

The
[`knowledge-adapters` Source Package Contract](https://github.com/ctrl-alt-keith/knowledge-adapters/blob/main/docs/source-package-contract.md)
adds proven patterns for semantic compatibility, required capabilities,
integrity verification, immutable handoffs, and distinct producer and consumer
responsibilities. Its
[`knowledge-vault` consumer contract](https://github.com/ctrl-alt-keith/knowledge-vault/blob/main/docs/source-package-consumer-contract.md)
keeps consumer policy local while linking back to the normative contract
currently hosted with the producer implementation. The bundle-to-destination
and image-lab-to-LKE boundaries are lighter: they rely primarily on documented
file or container/CLI behavior and local consumer validation. They do not yet
justify a shared library or centrally managed schema.

## Semantic Ownership And Placement

- Name the semantic contract producer that owns shared meaning, emission
  semantics, and compatible evolution.
- Name the runtime producer that emits the artifact or performs the behavior.
- Put the normative artifact shape and producer guarantees in an explicit
  normative contract host, normally the producer repository near the
  implementation, schema, fixture, or command that emits them.
- Put accepted versions, consumer-specific policy, and integration validation
  with each contract consumer, normally in its current implementation
  repository.
- Link both sides explicitly and name the Semantic Contract Producer that
  governs shared semantics.
- Keep transport or orchestration responsibility separate when an operator or
  a third repository moves the artifact between producer and consumer.
- Name the human authority when consequential approval, acceptance, retention,
  publication, or another decision boundary is involved.
- Put reusable guidance here in the playbook; do not move domain contracts into
  the playbook.

Semantic ownership of a contract means authority over its documented shared
meaning. It does not transfer the consumer's policy, infrastructure, runtime,
or downstream lifecycle. Hosting the normative contract or implementing either
side does not create Product authority or consequential human approval.

## Lightweight Contract Template

Copy or adapt this outline. Delete irrelevant prompts.

```markdown
# <Interface Name> Contract

Status: <draft, experimental, or stable>; version: <identifier if versioned>

## Purpose And Scope
What crosses the boundary, why it exists, and where the interface begins and
ends.

## Participants And Authority
- Semantic contract producer: <Product or other typed identity> owns <shared
  meaning, emission semantics, and compatible evolution>.
- Runtime producer: <component or process> emits <artifact or behavior>.
- Normative contract host: <repository-relative link or other explicit
  location>.
- Contract consumer: <Product or other typed identity> accepts <versions and
  use> under <consumer-local policy>.
- Consumer implementation: <repository, component, or process>.
- Operator/orchestrator/transport: <responsibility only when applicable>.
- Human authority: <consequential decision and authorized role, when
  applicable>.

## Inputs And Outputs
Required and optional inputs; emitted artifacts, API behavior, commands, or
receipts. State where credentials and destination-specific state belong.

## Shape And Examples
Link the schema, type, CLI contract, directory layout, media type, or concise
field table. Link a sanitized fixture or realistic example when one exists.

## Versioning And Compatibility
How versions are identified; what additive and incompatible change mean; which
versions or capabilities the consumer accepts; migration or overlap policy.

## Validation Responsibilities
What the producer validates before emission, what transport preserves, what the
consumer validates before use, and which fixtures or contract tests exercise
the boundary.

## Failure Behavior
Rejection, quarantine, retry, partial-success, stale-input, and fallback
semantics. Say whether the consumer fails closed or can safely degrade.

## Security And Durability
Trust classification, secrets and sensitive-data rules, integrity or
authenticity guarantees, retention, immutability, and cleanup expectations.

## Non-Goals
Responsibilities this interface deliberately does not acquire.
```

For a simple file handoff, purpose, typed authority roles, input/output shape,
validation, failure behavior, and non-goals may be the entire contract. Do not
add a version field merely to complete the template; version only when
compatibility needs to be negotiated or incompatible evolution must be
detectable.

## Compatibility And Change Guidance

- Prefer an explicit artifact or protocol version when a consumer cannot infer
  compatibility safely. Define whether it versions the envelope, schema,
  command, or whole interchange.
- Use required capability declarations when an additive feature cannot be
  safely ignored. Do not use capability flags as a substitute for a major
  version when existing semantics change incompatibly.
- Keep producer fixtures sanitized and realistic. Consumers may vendor a
  fixture when that creates a deterministic compatibility test; record its
  source and update it deliberately.
- Exercise the consumer path that gives the artifact meaning, not only JSON
  parsing or file existence. Keep tests proportional to interface risk.
- Reject unsupported or ambiguous input before mutation. Document any safe
  degraded mode explicitly; do not invent silent fallback behavior.
- Treat integrity, provenance, and authenticity as separate claims. A checksum
  can establish byte integrity without authenticating the producer or approving
  the content.
- Coordinate incompatible changes across repositories, but keep each
  implementation change in its current repository and PR. Land producer
  support before consumer opt-in when ordering matters; preserve an overlap
  window when practical.

## Recurring Convergence Is Not Compatibility

The autonomous maintenance layer can keep documentation, governance,
conventions, and bounded implementation patterns aligned across repositories.
That recurring convergence can reduce the maintenance cost of independent
implementations, but it does not establish semantic compatibility.

Use a formal producer/consumer contract when a repository consumes another
repository's artifact or behavior and must detect incompatible evolution.
Automation may inspect both sides, update fixtures, and propose coordinated
changes, but the interface still needs explicit ownership, compatibility rules,
and validation in the producer and consumer paths.

Repeated automated repair at an integration seam is evidence that the contract
may be missing or too weak. It is not a reason to accept permanent drift, and it
does not by itself justify extracting similar implementations into a shared
library.

## Review Questions

- Does the contract describe the interface that exists, with links to current
  evidence, rather than a hoped-for abstraction?
- Are the Semantic Contract Producer, Runtime Producer, normative contract
  host, consumer, transport, and any consequential human authority distinct?
- Can the consumer detect unsupported or stale input before unsafe use?
- Are security, durability, and failure claims no stronger than implementation
  and validation evidence?
- Are optional fields, capabilities, and version rules proportionate to the
  integration?
- Would a solo operator know which repository to change and which checks to
  run?

## Intentional Non-Automation

This pattern does not require a central registry of contracts, a shared schema
package, cross-repository test orchestration, synchronized releases, or a new
CI gate. Those mechanisms add coordination and failure surfaces. Introduce one
only after repeated interfaces demonstrate a concrete need that repository-
local schemas, fixtures, links, and validation cannot meet.
