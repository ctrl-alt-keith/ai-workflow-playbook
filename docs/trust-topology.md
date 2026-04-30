# Trust Topology

Use this optional model when a workflow pattern needs a lightweight way to
describe how much trust it has earned and what evidence supports that trust.

The goal is to make promotion and cleanup decisions easier without adding a new
required workflow step. If a pattern is already clearly validated, keep moving.
If confidence is unclear, use this model to name the current trust level and the
evidence behind it.

This document adapts trust topology ideas into a practical workflow model for
AI-assisted development systems.

## Purpose

Trust topology gives reusable guidance a simple shape:

- trust level: how settled the pattern is
- evidence: what proves the pattern works
- edges: how the pattern relates to other guidance or validation
- movement: how the pattern gains, loses, or keeps trust over time

Use it for playbook guidance, staging notes, prompt patterns, review workflows,
or tool-adapter behavior that may later become canonical.

Do not use it to create required metadata fields, a second tracking system, or a
reason to promote speculative ideas. The playbook remains reusable, validated,
and non-speculative.

## Trust Levels

### Weak

Use `weak` when a pattern is plausible but has little evidence.

Examples:

- a capture note from one delivery arc
- a review habit that helped once but has not been repeated
- a tool workaround that may only fit one repository

Weak patterns should stay in notes, prompts, or local project guidance until
they have evidence from real use.

### Emerging

Use `emerging` when a pattern has worked more than once, but the boundary is not
fully clear yet.

Examples:

- a checklist used across two related PRs
- a review packet shape that helped multiple reviewers
- a staging cleanup rule that seems useful but still needs sharper examples

Emerging patterns can be referenced, but they should still be treated as
adjustable. Keep the wording narrow and tied to the evidence.

### Strong

Use `strong` when a pattern has repeated evidence across repositories, phases,
or reviewers and has survived review without major correction.

Examples:

- a validation habit used across several repo changes
- a branch and PR rule that reduced review confusion in multiple arcs
- a prompt pattern that consistently produces useful review packets

Strong patterns are good candidates for playbook guidance when they are reusable
and not project-specific.

### Canonical

Use `canonical` when a pattern belongs in the playbook as settled guidance.

Examples:

- a lifecycle rule that defines what "done" means for repo changes
- a repo readiness expectation used before new project work starts
- a review packet format that acts as the standard release surface

Canonical guidance should be clear enough to apply without knowing the original
discussion. It should remain open to revision when new evidence shows the rule
is stale, too broad, or too narrow.

## Evidence

Evidence is the reason a pattern deserves its current trust level. Prefer direct
evidence over preference or memory.

Useful evidence includes:

- PRs that used the pattern successfully
- validation runs such as `make check`, tests, CI, or manual verification
- repeated usage across more than one repo, arc, reviewer, or delivery phase
- review feedback showing the pattern made inspection easier
- cleanup passes where the pattern helped remove or trim stale staging material

Weak evidence includes:

- a single anecdote without a merged result
- a pattern that sounds right but has not been tried
- copied guidance from another context that has not been validated locally
- broad claims without examples

Evidence does not need a formal schema. A short note, PR link, review packet, or
capture entry is enough when it lets a later reader understand why trust was
assigned.

## Edge Types

Edges describe relationships between patterns, evidence, and validation. They
are optional labels for reasoning, not required fields.

### Supports

Use `supports` when one pattern or piece of evidence strengthens another.

Examples:

- a merged PR supports a proposed branch rule
- repeated review packets support the standard packet format
- notes cleanup results support a staging-versus-canonical rule

### Depends On

Use `depends-on` when a pattern only makes sense if another rule or context is
true.

Examples:

- a PR completion rule depends on a repository having a GitHub remote
- a validation rule depends on the repo exposing a stable check command
- a tool-adapter rule depends on the core playbook model

When a dependency changes, revisit the dependent pattern before promoting it.

### Validated By

Use `validated-by` when a check, review, or real usage confirms that a pattern
worked in practice.

Examples:

- a docs change validated by `make check`
- a workflow rule validated by a ready-for-review PR using it end to end
- a prompt pattern validated by review feedback that found the output useful

Validation can be local, CI-based, manual, or reviewer-based. Be explicit about
which kind was used.

## Promotion Guidance

Promote a pattern when it has enough evidence for the trust level it claims and
belongs in the destination layer.

Use this progression as a guide:

1. Start as `weak` when the pattern is captured from one real event.
2. Move to `emerging` after repeated use shows the pattern is useful.
3. Move to `strong` after it works across boundaries such as repos, phases, or
   reviewers.
4. Move to `canonical` only when it is reusable, validated, non-speculative, and
   clear enough to guide action.

Promotion should be small and operational. When moving a pattern into the
playbook:

- keep only the reusable part
- include enough context to apply it
- remove project-specific detail
- avoid adding tracking requirements unless they already exist
- validate the docs change through the repo's normal check path

## Demotion Guidance

Demote or revise a pattern when evidence no longer supports its trust level.

Reasons to demote include:

- repeated exceptions show the rule is too broad
- reviewers find the guidance confusing or costly
- validation gaps were hidden by a too-confident summary
- the pattern only works in one repository or tool context
- newer canonical guidance makes the pattern redundant

Demotion does not have to mean deletion. A canonical rule may become strong
guidance with narrower wording. An emerging pattern may move back to notes while
more evidence is gathered. Weak patterns can be trimmed when they are no longer
useful.

## Examples

### Review Packet Format

A review packet starts as `weak` after one PR uses it successfully. It becomes
`emerging` when several PRs use the same shape and reviewers can inspect the
work faster. It becomes `strong` when the format works across release, docs, and
implementation PRs. It becomes `canonical` when the playbook defines it as the
standard pre-merge review surface.

Edges:

- review feedback `supports` the packet shape
- the packet format `depends-on` the feature lifecycle release phase
- successful PR reviews are `validated-by` human inspection and CI results

### Notes Cleanup Rule

A notes cleanup rule may start in staging after one cleanup pass. If it helps
separate promoted guidance from local follow-up across multiple notes
repositories, it can become `emerging` or `strong`. If it is only useful for one
folder structure, keep it local instead of promoting it.

Edges:

- cleanup PRs `support` the rule
- the rule `depends-on` the notes-versus-playbook boundary
- markdown checks and reviewer confirmation `validated-by` the cleanup result

### Tool Adapter Behavior

A tool-adapter habit should not become canonical just because it works once.
First confirm whether it is a core workflow rule or tool-specific behavior. If
the evidence only applies to one tool, keep it in that adapter. If the same
pattern works across tools, promote the reusable part into core guidance.

Edges:

- repeated adapter usage `supports` the pattern
- adapter guidance `depends-on` the core model
- successful task completion `validated-by` the repo's normal checks and review

## Background and Further Reading

This model is informed by broader ideas about trust as a networked property
rather than a binary state.

- Michael Roth, ["Trust Topology"](https://michael.roth.rocks/research/trust-topology/)
