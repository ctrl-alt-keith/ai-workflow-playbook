# Repo-To-Repo Interface Contracts

## Purpose

Use a small, explicit contract when one repository produces an artifact or
behavior that another repository consumes. The contract should make ownership,
compatibility, validation, and failure behavior reviewable without creating a
central schema repository, shared library, or new approval gate.

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
The producer owns a versioned schema and public-safe fixture. The consumer
declares the accepted version, carries a compatibility fixture through its real
validation and planning path, and fails closed on invalid or stale input.

The
[`knowledge-adapters` Source Package Contract](https://github.com/ctrl-alt-keith/knowledge-adapters/blob/main/docs/source-package-contract.md)
adds proven patterns for semantic compatibility, required capabilities,
integrity verification, immutable handoffs, and distinct producer and consumer
responsibilities. Its
[`knowledge-vault` consumer contract](https://github.com/ctrl-alt-keith/knowledge-vault/blob/main/docs/source-package-consumer-contract.md)
keeps consumer policy local while linking back to the producer-owned normative
contract. The bundle-to-destination and image-lab-to-LKE boundaries are lighter:
they rely primarily on documented file or container/CLI behavior and local
consumer validation. They do not yet justify a shared library or centrally
managed schema.

## Placement And Ownership

- Put the normative artifact shape and producer guarantees in the producer
  repository, near the implementation, schema, fixture, or command that emits
  them.
- Put accepted versions, consumer-specific policy, and integration validation
  in each consumer repository.
- Link both sides explicitly and name which side governs shared semantics.
- Keep transport or orchestration ownership separate when an operator or a
  third repository moves the artifact between producer and consumer.
- Put reusable guidance here in the playbook; do not move domain contracts into
  the playbook.

Ownership of a contract means responsibility for its documented semantics. It
does not transfer ownership of the consumer's policy, infrastructure, runtime,
or downstream lifecycle.

## Lightweight Contract Template

Copy or adapt this outline. Delete irrelevant prompts.

```markdown
# <Interface Name> Contract

Status: <draft, experimental, or stable>; version: <identifier if versioned>

## Purpose And Scope
What crosses the boundary, why it exists, and where the interface begins and
ends.

## Participants And Ownership
- Producer: <repository/component> owns <emission semantics>.
- Consumer: <repository/component> owns <acceptance and use>.
- Operator/orchestrator/transport: <only when applicable>.
- Normative contract home: <producer-owned link or other explicit authority>.

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

For a simple file handoff, purpose, owners, input/output shape, validation,
failure behavior, and non-goals may be the entire contract. Do not add a
version field merely to complete the template; version only when compatibility
needs to be negotiated or incompatible evolution must be detectable.

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
- Coordinate incompatible changes across repositories, but keep each change in
  its owning repository and PR. Land producer support before consumer opt-in
  when ordering matters; preserve an overlap window when practical.

## Review Questions

- Does the contract describe the interface that exists, with links to current
  evidence, rather than a hoped-for abstraction?
- Are producer, consumer, and transport responsibilities distinct?
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
