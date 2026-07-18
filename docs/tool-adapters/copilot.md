# Copilot Adapter

This document explains how GitHub Copilot maps onto the core playbook. It is adapter-specific guidance, not part of the core operating model.

## Context

- This guidance is based on observed usage alongside ChatGPT and Codex
- It describes where Copilot fits well and where prompts need reshaping
- It does not define tooling, automation, or alternate workflow paths

## Role in Workflow

- ChatGPT: planning, orchestration, prompt design, and shaping the next bounded task
- Codex: bounded execution, repo-level changes, validation, and PR creation
- Copilot: inline suggestion, completion, and editing during implementation
- Copilot is suggestion-based, not task-driven
- Copilot operates inside editor context, not as the workflow driver
- Copilot works best after the structure, intent, and boundaries are already decided

## What Works Well

- small, local code edits
- filling in obvious implementations
- iterative refinement of a function, test, query, or small block
- continuing an established pattern already present in the file
- drafting boilerplate inside an already-defined structure
- shortening repetitive editing once the target shape is clear

## What Does Not Translate

- full multi-step prompts that assume the tool will plan and execute a sequence
- repo-wide changes that require coordinated edits across many files
- PR lifecycle tasks such as validation, commit scoping, or PR creation
- orchestration-level instructions about phase, workflow, or review flow
- prompts that depend on broad repo context or rationale not visible in the editor
- instructions that ask the tool to decide scope, tradeoffs, or completion state

## Prompt Adaptation Guidance

- break large prompts into small, local instructions
- place the cursor or selection at the exact edit site before prompting
- rely on surrounding code context instead of restating full workflow context
- use Copilot for refinement, continuation, or transformation rather than direction
- keep intent clear but localized to one file, function, or block
- use ChatGPT or Codex when the work needs planning, coordination, or repo-level follow-through

## Prompt-Contract Capability Mapping

The shared semantics in [`prompt-contracts.md`](../prompt-contracts.md) remain
authoritative when a material task is considered for Copilot. Copilot may map
only requirements supported by its suggestion-based editor surface:

| Semantic requirement | Copilot mapping |
| --- | --- |
| Localized transformation or continuation in selected editor context | Supported when the selected file, range, intent, and constraints are already explicit. |
| Product-neutral `light` reasoning class | May be represented as a small local suggestion task; this is task-shape guidance, not a guaranteed product knob. |
| `medium` or `high` reasoning class | No testable equivalent mapping is claimed. If mandatory, use a supported executor or fail closed. |
| Repository-wide source hydration or exact source-manifest reconstruction | Unsupported as a mandatory Copilot capability; fail closed or route to Codex. |
| Deterministic rendering and exact executor-visible byte identity | Unsupported as a mandatory Copilot capability; editor suggestions are not claimed to be a deterministic renderer. |
| Append-only attempt receipts, replay-exact dependencies, or checkpoint lineage | Unsupported as a mandatory Copilot capability; an owning execution layer must provide them. |
| Canonical validation, commit, push, PR delivery, or ordered transport fallback | Unsupported as Copilot-owned workflow behavior; route to the repository executor. |
| Live authority re-read and acting-identity verification | Unsupported as Copilot-owned authorization behavior; the execution or adoption layer must enforce it. |

An advisory unsupported requirement may be omitted only when the semantic
contract explicitly allows that degradation and no guarantee is weakened. An
unsupported mandatory capability fails closed. Do not claim Codex/Copilot
parity without a testable mapping for the requirement being compared.

## Notes

- Copilot complements the workflow; it does not replace ChatGPT or Codex
- Treat Copilot as an implementation aid once direction is already set
- If a prompt starts describing steps, files, and validation, it likely belongs in ChatGPT or Codex instead
