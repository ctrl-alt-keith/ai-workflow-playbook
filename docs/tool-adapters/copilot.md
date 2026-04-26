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

## Notes

- Copilot complements the workflow; it does not replace ChatGPT or Codex
- Treat Copilot as an implementation aid once direction is already set
- If a prompt starts describing steps, files, and validation, it likely belongs in ChatGPT or Codex instead
