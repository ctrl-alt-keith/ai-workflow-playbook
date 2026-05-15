# ai-workflow Ecosystem Overview

The `ai-workflow-*` ecosystem is an emerging set of small, composable
repositories for reproducible model-assisted operational workflows and
provenance-aware retained knowledge.

This document is a conceptual overview. It is not a product pitch, a legal
policy, a vendor commitment, or a finalized architecture specification. It
describes the intended shape of the system so repository work can stay aligned
while the details continue to evolve.

## Purpose

The ecosystem exists to make model-assisted operations inspectable,
repeatable, and reviewable. Its center of gravity is durable workflow and
knowledge capture rather than opaque memory or one-off automation.

The core purpose is to support:

- reproducible operational workflows
- provenance-aware retained knowledge
- reviewable ingestion and retention
- markdown-first portability
- git-native change history
- pull-request-reviewed model-assisted operations
- clear separation between guidance, enforcement, ingestion, and retained
  state

The system should make it possible to ask where knowledge came from, how it was
processed, who reviewed it, where the retained version lives, and which
workflow rule governs the next action.

## Repository Roles

The repositories are intentionally small and role-specific. Their boundaries
may sharpen over time, but the current conceptual split is:

| Repository | Conceptual role |
| --- | --- |
| `ai-workflow-playbook` | Canonical home for reusable workflow patterns, operating philosophy, interaction modes, review expectations, and promotion guidance. It explains how to work. |
| `ai-workflow-enforcement` | Mechanical policy and drift enforcement. It should encode checkable workflow rules without becoming the place where the philosophy is invented. |
| `ai-workflow-incubator` | Exploration and staging for emerging patterns before they are promoted into durable playbook guidance or split into their own repository. |
| `knowledge-vault` | Reviewed retained knowledge. The vault stores the durable notes, summaries, and retained artifacts that have passed through human review. |
| `knowledge-adapters` | Acquisition and normalization of external sources. Adapters treat incoming material as untrusted input and prepare it for review without declaring it retained knowledge by default. |
| `ka-destinations` | Publishing, export, and rendering paths for reviewed knowledge. Destinations adapt retained material for use elsewhere without becoming the source of truth. |

In short: adapters acquire and normalize, the vault retains reviewed knowledge,
destinations publish or render, the playbook captures reusable patterns,
enforcement checks mechanical policy, and the incubator gives unsettled ideas a
place to mature before promotion.

## State Boundaries

Retained knowledge should move through distinguishable states instead of
collapsing capture, extraction, review, and memory into one opaque step.

Useful states include:

- `raw`: source material as acquired or referenced
- `extracted`: selected or normalized material prepared for inspection
- `reviewed`: human-inspected notes, summaries, or decisions
- `retained`: durable knowledge accepted into the vault or another owning
  repository

The exact file layout and metadata may evolve. The architectural requirement is
that the workflow keeps those states conceptually separate so later reviewers
can understand what has merely been collected, what has been processed, what
has been reviewed, and what is now treated as retained knowledge.

External sources remain untrusted until review establishes what should be kept.
The preferred retained form is usually a summary, reviewed note, attribution
record, or bounded excerpt rather than indiscriminate scraping. Retention should
preserve enough provenance to audit the source without turning the vault into a
mirror of everything encountered.

## Design Principles

### Provenance First

Source identity, attribution, transformation history, and review status are
first-class concerns. A retained note should not pretend to be self-originating
when it was derived from an external source, generated draft, human review, or
prior repository artifact.

Provenance is not only about citation. It is also about operational trust: what
was seen, what was summarized, what was discarded, what was reviewed, and why
the retained result deserves to be reused.

### Markdown-First And Git-Native

Markdown and git are the default durability layer because they are portable,
diffable, inspectable, and friendly to pull-request review. Structured metadata
can help when it earns its keep, but the system should not require a proprietary
memory service to understand its retained knowledge.

The goal is durable, reviewable files first. Tools should improve acquisition,
checking, rendering, and reuse without making the underlying knowledge opaque.

### Human-In-The-Loop Governance

Automation can acquire, normalize, summarize, compare, and suggest. Humans
still own retention decisions, promotion decisions, and governance boundaries.

Pull requests are the normal review surface for durable changes. That keeps
model-assisted operations visible in diffs, validation output, review notes,
and repository history.

### Small, Composable Repositories

Each repository should own one major responsibility. Small repositories make it
easier to reason about authority:

- guidance belongs in the playbook
- mechanical checking belongs in enforcement
- provisional discovery belongs in incubation
- reviewed retained knowledge belongs in the vault
- source acquisition belongs in adapters
- publication and rendering belong in destinations

This separation reduces accidental coupling and makes it easier to change one
part of the system without silently changing the meaning of retained knowledge.

### Reviewable Automation Over Opaque Memory

The ecosystem should avoid opaque model-memory systems where retained context
is hard to inspect, export, diff, or govern. Durable memory should be visible as
reviewed files with provenance and repository history.

Model assistance is valuable when it accelerates bounded work while preserving
reviewability. It becomes risky when it silently absorbs source material,
forgets attribution, or makes retained state dependent on a platform that users
cannot inspect.

### Portability Over Vendor Lock-In

The system should prefer ordinary files, documented workflows, portable
formats, and replaceable tools. Individual tools may be useful, but knowledge
should not become trapped inside a single vendor, hosted feature, or assistant
runtime.

Portability also applies to people. A future reviewer should be able to clone a
repository, read the markdown, inspect the history, and understand the workflow
without needing private model state.

### Iterative Discovery Before Schema Commitment

The ecosystem is still learning. It should preserve room for discovery instead
of forcing premature schemas, final taxonomies, or rigid implementation detail.

The preferred path is:

1. capture a real workflow need
2. test it in a bounded repository change
3. review the evidence
4. promote the reusable lesson
5. tighten mechanical enforcement only after the rule is stable enough to check

Schemas and automation should follow durable patterns, not lead them before the
workflow is understood.

### Solo Operator Scaling Direction

As AI-assisted work scales, the limiting factor becomes decomposition,
verification, and review compression rather than raw implementation speed.
Prefer small, repo-local, independently verifiable changes with clear
validation and stop rules.

The preferred scaling model is one top-level orchestration prompt for the run,
with safe parallel work delegated to self-contained subagents or workers. The
top-level prompt owns decomposition, lane boundaries, reconciliation, and
reporting. Workers own only their assigned task envelope and should not depend
on full conversation history, implicit role inheritance, or shared hidden state.

Worker envelopes should make the repository, goal, scope, constraints,
validation path, stop conditions, and reporting expectations explicit. Parallel
workers should operate independently on separate worktrees and branches, or on
clearly non-overlapping file, behavior, or risk surfaces when a branch split is
not the right unit. If overlap appears, reconciliation belongs to the
orchestrator or human reviewer, not to unsupervised worker coordination.

Repo-local sovereignty remains the default. Discovery should be report-only
before mutation, and cross-repo changes should be decomposed into separately
reviewable repository PRs rather than bundled into mega-changes. Avoid standing
centralized control planes, unbounded autonomy, and premature standardization.

Promote new workflow abstractions only after repeated evidence from real repo
work shows that they reduce review or coordination burden without becoming
ceremony. Noncanonical exploration may be staged in
[`ai-workflow-incubator`](https://github.com/ctrl-alt-keith/ai-workflow-incubator/blob/main/architecture/solo-operator-operational-architecture-2026-05-14.md),
but incubator notes do not create playbook policy.

## Public And Non-Work Boundary

Current retained-knowledge workflows are intentionally focused on public and
non-work material.

That boundary avoids unnecessary ambiguity around:

- employer intellectual-property ownership
- confidential data handling
- private operational leakage
- policy and legal complexity

This boundary is a practical operating constraint, not legal advice. If a
workflow needs to handle work, confidential, or employer-controlled material,
that should be treated as a separate design problem with explicit policy,
approval, retention, and access-control requirements before ingestion begins.

## Architectural Direction

The ecosystem is evolving toward reproducible operational memory for
model-assisted work:

- workflow-aware retained knowledge
- policy-aware ingestion
- provenance-preserving acquisition and review
- markdown-first retained state
- automation that remains inspectable and pull-request-reviewed
- human-governed promotion from raw input to retained knowledge

The intended mature shape is not a monolith. It is a set of cooperating
repositories where each part knows its authority boundary and where durable
knowledge remains portable, inspectable, attributable, and reviewable.
