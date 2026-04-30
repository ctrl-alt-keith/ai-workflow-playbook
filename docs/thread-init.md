# Thread Initialization

## Purpose

Establish scope, authority, and working behavior at the start of an
AI-assisted thread.

Use this pattern to make the playbook the thread's reusable workflow authority,
name the current project boundary, and prevent unrelated context from shaping
the work.

## When To Use

- New threads
- Project handoffs
- Work where repo, branch, notes, or experiment isolation matters
- Follow-up threads that need a clean scope boundary before execution

## Relationship To Context Refresh

Thread initialization sets the working boundary and authority for a thread.
Use context refresh after initialization when prior state, repo drift, or
verified current context matters.

## Usage Instructions

- Paste the appropriate template at the start of a thread or handoff.
- Fill in the placeholders before sending.
- Use standard mode for ordinary scoped work.
- Use strict mode when context isolation matters more than speed.
- Update `Current goal` as the work evolves; keep the rest stable unless the
  scope changes.

## Standard Mode Template

```markdown
Use this playbook as the canonical source of patterns, workflow rules, and
decision defaults for this thread.

Thread rules:
- Do not pull context, conventions, or assumptions from unrelated projects,
  repos, branches, scratchpads, experiments, or prior threads unless I
  explicitly name them.
- Treat any non-playbook context outside the stated project scope as out of
  scope by default.
- Prefer existing project patterns and applicable playbook patterns before
  introducing a new process pattern.
- If project reality differs from the playbook, adapt the playbook pattern to
  fit the project. Do not copy blindly.
- If the playbook is silent, make the smallest reasonable assumption and state
  it.

Project description:
- [Describe the project, repo, or work area]

Current goal:
- [Describe the immediate task or outcome]

Constraints:
- [Optional: deadlines, tooling limits, compatibility requirements, non-goals]

Start by:
- Identify the relevant playbook pattern(s) for this task
- Confirm the working scope and what is explicitly out of scope
- Call out any missing information that blocks safe execution
- Then proceed with the work
```

## Strict Mode Template

```markdown
Use this playbook as the canonical source for this thread.

Strict mode rules:
- Do not import context from any unrelated project, repo, branch, scratchpad,
  experiment, or prior thread unless I explicitly authorize it by name.
- Do not invent a process pattern when an applicable playbook pattern already
  covers the case.
- Adapt playbook patterns to the current project and explain any necessary
  deviation.
- If context is ambiguous, stop and ask one focused clarification question
  before acting.
- Keep recommendations and edits tightly scoped to the stated project and
  current goal.

Project description:
- [Describe the project]

Current goal:
- [Describe the task]

Constraints:
- [Optional]

Start by:
- Name the playbook pattern(s) you are applying
- State assumptions
- State exclusions
- Then execute
```
