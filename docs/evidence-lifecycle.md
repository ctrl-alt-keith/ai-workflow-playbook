# Evidence Lifecycle

## Purpose

Use this guidance when a workflow accepts, integrates, synthesizes, or reports
evidence. It defines a general evidence lifecycle and semantic-accounting
boundary; it is not a mandatory ceremony for routine repository work.

For domain-specific acquisition, provenance, licensing, and retention of
external material, use
[`knowledge-ingestion-patterns.md`](knowledge-ingestion-patterns.md). For
comparative agent convergence and divergence, use
[`multi-agent-synthesis.md`](multi-agent-synthesis.md). Those owners remain
authoritative for their narrower domains.

## Accepted Evidence And Freeze

Accepted evidence is the reviewed input set eligible for integration and
synthesis. Acceptance records eligibility under the current contract; it does
not make every claim true, resolve every conflict, or grant authority for a
downstream decision.

Before integration, synthesis, or decision production, freeze the accepted set
at exact reviewable identities or versions. Preserve what was accepted,
rejected, or unresolved and the decision that established the boundary. Later
corrections or additions create an explicit new acceptance decision and a new
evidence boundary rather than silently rewriting the frozen set.

A freeze protects the reviewed input boundary. It does not freeze later
interpretation, imply permanent retention, require a particular manifest or
storage system, or prevent a documented correction.

## Independent Evaluation Dimensions

Evaluate protocol conformance separately from substantive value. A conforming
execution can produce low-value findings, while a nonconforming execution can
surface useful material that still requires separate review before use.

Substantive value does not excuse unsafe or unauthorized execution, and a
protocol failure does not require useful evidence to disappear. Preserve the
failure and any potentially useful material when the applicable security,
privacy, licensing, and retention rules permit, while keeping its acceptance
status explicit.

## Information-Preserving Integration

Integration should preserve the information needed for later synthesis and
review. Keep source and contributor identity, relevant intent, provenance,
constraints, conflicts, uncertainty, unsuccessful searches, and unresolved
questions visible. Do not make the integrated result appear cleaner by
silently harmonizing disagreement or dropping negative outcomes.

Integration organizes accepted evidence; it does not decide what the evidence
means or convert contributor conclusions into shared findings without review.

## Synthesis And Semantic Classes

Synthesis consumes the frozen accepted-evidence set. When the distinctions
matter, keep these semantic classes explicit:

- Observation: what an accepted source or execution directly reports.
- Interpretation: what the observation means within the stated context.
- Inference: reasoning that extends beyond what the evidence directly states.
- Recommendation: a proposed action or decision supported by evidence and any
  named inference.
- Open question: an unresolved point that remains outside the supported
  conclusion.

Inference and implications are legitimate synthesis outputs when they are
identified as such. Do not restate them as observations or evidence, and do not
require or preserve private reasoning traces to make the distinction.

## Semantic Accounting And Traceability

Keep a reviewable path from each material recommendation to its motivating
evidence, relevant conflicts or constraints, and any inference that connects
them. Traceability should be proportionate: a link, citation, section reference,
or artifact identity is enough when it lets a reviewer reconstruct the basis
without a separate database.

When multiple sources or outputs agree, distinguish independent corroboration
from convergence caused by a shared source, dependency, or reasoning path.
Shared-source convergence is not independent corroboration. Apply
[`multi-agent-synthesis.md#reading-convergence-and-divergence`](multi-agent-synthesis.md#reading-convergence-and-divergence)
for the interpretation of convergence, divergence, and dependencies rather
than creating a second scoring or voting model here.

## Negative And Null Evidence

A completed-search receipt and an explicit negative outcome are evidence of the
scope searched and the result observed under that scope. They are not proof
that a fact, source, or alternative does not exist outside it.

Preserve enough bounded context to understand what was checked and what the
negative outcome means. Carry unsuccessful searches, constrained findings,
conflicts, and unresolved questions through integration and synthesis when they
affect the conclusion. Do not turn them into factual negatives or retain them
indefinitely without an applicable preservation decision.

## Validation Boundary

Deterministic validation can establish declared mechanical properties such as
artifact identity, required structure, internal traceability, and completion
against an explicit set. It cannot establish substantive truth, significance,
approval, or decision authority.

Use [`repo-readiness.md#validation`](repo-readiness.md#validation) as the owner
of the validation taxonomy and gate behavior. Evidence workflows should name
what a check establishes without forking that taxonomy or substituting checks
for semantic judgment.

## Reporting

When a report contains multiple output classes, distinguish factual findings,
operational observations, recommendations, and open questions. Preserve the
observation, interpretation, inference, recommendation, and open-question
distinctions above wherever collapsing them would obscure the evidentiary
boundary.

Simple reports do not need a fixed taxonomy or template. The requirement is to
keep materially different classes visible and retain access to the complete
supporting artifacts rather than hiding them behind a polished summary.
