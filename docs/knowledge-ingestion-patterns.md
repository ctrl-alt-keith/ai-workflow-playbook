# Knowledge Ingestion Patterns

## Purpose

Knowledge-ingestion systems collect external material, turn it into reviewed
understanding, and retain the parts that are useful later. This document
describes reusable workflow and architecture patterns for those systems.

It is not legal advice and should not replace repository-local policy,
licensing review, or organization-specific compliance requirements.

## Core Pattern

Separate ingestion, review, and retention.

1. Ingest external material into a quarantine or staging area.
2. Extract text, metadata, or structure without treating it as approved.
3. Review provenance, licensing, privacy, freshness, and usefulness.
4. Retain only approved notes, summaries, metadata, and artifacts.
5. Record rejected or restricted decisions without preserving material that
   should not be retained.

This separation keeps fast capture from becoming accidental publication or
long-term storage.

## Trust Boundary

Treat every external source as untrusted input. A source can be public,
interesting, and technically easy to fetch while still being inappropriate to
redistribute or retain.

Public accessibility does not imply redistribution permission. Workflows should
make licensing and reuse checks part of artifact review instead of assuming
that fetched content is retainable.

## Reviewed Versus Raw Artifacts

Use explicit lifecycle states:

- Raw fetched content is captured material that has not been reviewed.
- Extracted content is converted material, such as OCR output, reader-mode text,
  or PDF extraction, and remains unreviewed until checked.
- Reviewed notes are repository-authored summaries, synthesis, citations, and
  limited excerpts with provenance.
- Retained artifacts are committed or durable outputs that have passed review.

The review boundary applies to the artifact and source version that were
reviewed. A refreshed fetch, changed source, new comment thread, or updated PDF
should cross the boundary again before retention.

## Provenance-Aware Workflow

Retained knowledge should preserve enough provenance for a later reviewer to
understand source, freshness, allowed use, and review status.

Common metadata includes:

- source URL or stable source identifier
- source title and publisher or owner when relevant
- retrieval method and date when freshness matters
- license, terms, permission, or reuse rationale
- review status and retention decision
- output path or retained artifact identifier

Missing provenance should push a workflow toward rejection, limited notes, or a
follow-up review rather than full retention.

## Markdown-First Retention

Prefer markdown and simple structured metadata for retained knowledge. Plain
text makes provenance, citations, and review decisions easy to inspect in diffs,
search, local tools, and future migrations.

Avoid making opaque blob storage, proprietary exports, or vendor-only notebooks
the authoritative retained artifact. Binary files may still be useful as
supporting material, but the durable reviewed knowledge should remain portable
where practical.

## Summaries Before Redistribution

For publicly accessible but copyrighted material, prefer summaries, analysis,
and attributed notes over full or near-full source retention. Keep quotations
limited, clearly attributed, and necessary to the reviewed note.

Do not design ingestion workflows that quietly recreate books, reports,
articles, blog posts, PDFs, comments, forums, or other user-generated content
as repository artifacts unless the local policy and source terms support that
retention.

## Repository-Local Governance

Reusable playbook guidance should describe the pattern. Repository-local policy
should define enforcement details.

Keep retention policy close to the artifacts it governs. A repository that
stores retained knowledge should document its own prohibited content,
restricted content, acceptable retention classes, attribution expectations,
validation checks, and exception process.

The playbook should not duplicate those local policies. It should help future
repositories choose boundaries, lifecycle phases, and review mechanics.

## Architecture Guidance

Design ingestion systems so phase boundaries are visible:

- quarantine paths for fetched and converted material
- review queues for pending decisions
- retained-content paths for approved markdown and metadata
- rejection logs or decision records for material that should not be retained
- validation checks that catch structural, privacy, and policy drift

Automation should preserve the boundary between capture and retention. A fetch
job can collect material, but a review step should decide what becomes durable.

## Source-Shape Hardening Lifecycle

Mature each source type in its implementation repository before routine replay.
This applies to ingestion, extraction, ETL, scraping, OCR, export/import, and
normalization, where source formats, sites, document classes, or feeds can
introduce distinct failure shapes.

Use these maturity states:

- `experimental`: live exploration or early probes; not a stable replay input
  or retainable content source.
- `diagnostic`: important source shapes are reproducible; outputs support
  debugging, fixture design, and failure classification.
- `review-ready`: fixtures and diagnostics support predictable review of
  outputs, cleanup, provenance, and known limits.
- `promotion-capable`: replay economics, provenance, and retention boundaries
  support a bounded retain/no-retain decision.

The implementation repository owns live checks, sanitized fixtures,
failure-shape corpora, replay-quality metadata, no-op safety fixtures,
non-regression coverage, observability, and debugging. Replay/review repositories
own milestone validation, retention review, promotion/no-promotion decisions,
and durable provenance; do not make them the primary extraction-debugging
surface.

Apply [iteration economics](repo-readiness.md#solo-operator-iteration-economics).
Keep detection, fixture/metadata evidence, bounded correction, and live and
non-regression validation together when they share one source type, validation
story, and rollback boundary; split otherwise. Describe phases in the PR.
Exclude unrelated cleanup, new source families, crawler expansion, retention
decisions, and broad redesign.

Before broader replay, require:

- no surprising replay failures for the known source shape
- fixture fidelity established against real examples
- diagnostics for expected failure modes
- bounded replay economics, including expected review effort
- documented limitations and predictable cleanup and review boundaries

Predictable review, not perfect extraction, is the threshold. Use these
classifications in replay artifacts and decision records:

- `diagnostic-only`: implementation learning, not retention review
- `review-ready`: bounded human review with known cleanup limits
- `promotion-capable`: retain/no-retain decisions with provenance
- `unsafe-to-promote`: blocked by extraction risk, provenance gaps, policy,
  privacy, or uneconomic review effort

## Validation Role

Validation can check paths, metadata shape, review status values, obvious
privacy hazards, generated catalog drift, and forbidden repository-local
patterns. It cannot determine every licensing, attribution, privacy, or reuse
question.

Treat validation as guardrails around review, not as a replacement for review.

## Practical Defaults

Use these defaults when designing a retained-knowledge repository:

- keep raw and extracted material out of version control until reviewed
- commit reviewed markdown, reviewed metadata, and rejection notes
- require provenance and reuse notes before retention
- prefer summaries and citations over source reproduction
- record explicit review boundaries and refresh expectations
- keep policy in the repository that stores the retained artifacts
- avoid vendor lock-in by making retained knowledge inspectable as text
