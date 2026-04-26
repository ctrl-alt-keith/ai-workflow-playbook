# Using Claude as a Lightweight PR Reviewer

Claude can be useful as a second set of eyes during development, but it should
stay lightweight.

Use it as an optional reviewer, not as part of the execution loop. Its role is
advisory only and never blocking. Treat it as an impartial observer that may
spot edge cases, completeness gaps, or risky assumptions before merge.

## When To Use Claude

Use Claude when:

- a PR touches multiple files, layers, or concerns
- a change has cross-repo implications
- the change feels slightly off or confidence is lower than usual
- a pattern may be promoted into the playbook and deserves a quick sanity check

## When Not To Use Claude

Do not use Claude when:

- the change is small or mechanical
- confidence is already high
- tests and CI already cover the meaningful risk
- it would become a habitual or automatic step

## Workflow Integration

Keep the default loop simple:

```text
Codex -> PR -> human skim -> merge
```

Use Claude only when a targeted review would add signal:

```text
Codex -> PR -> Claude (targeted review) -> human skim -> merge
```

Claude is optional and situational. It is never required for merge.

## Input Guidelines

Give Claude only the context needed to review well:

- a short statement of goal or intent
- the PR description or a brief summary
- only the relevant diffs, not the full repo

Optionally include one specific concern if you want Claude to look for a known
risk.

## Output Constraints

Keep the output narrow:

- 2-4 observations maximum
- focus on edge cases
- focus on incomplete behavior
- focus on risky assumptions
- focus on inconsistencies

Do not use it for:

- scope expansion
- architectural redesign
- stylistic nitpicks

## Reusable Prompt: PR Review

```text
Review this PR as a lightweight second set of eyes.

Goal:
<short goal or intent>

PR summary:
<summary>

Relevant diff:
<paste only the relevant diff or files>

Optional concern:
<specific concern, if any>

Constraints:
- Do not propose redesigns.
- Do not expand scope.
- Return 2-4 high-signal observations max.
- Focus only on edge cases, incomplete behavior, risky assumptions, or
  inconsistencies.
- Ignore style nits and minor preference comments.
- If nothing stands out, say: LGTM
```

## Reusable Prompt: System / Pattern Sanity Check

Use this for playbook guidance or cross-repo patterns where the main question is
whether the pattern is clear and safe to reuse.

```text
Review this proposed pattern as a lightweight sanity check.

Intent:
<short statement of the pattern and why it exists>

Material:
<paste the relevant guidance, summary, or diff>

Constraints:
- Return at most 3 issues.
- Focus on clarity problems, hidden assumptions, or misuse risk.
- Do not redesign the pattern.
- Do not expand scope.
- If nothing stands out, say: LGTM
```

## Failure Modes

Watch for these failure modes:

- over-auditing simple changes
- suggestion overload that creates churn without reducing risk
- architectural drift from letting review comments reshape the task
- slowing the loop with an extra step that adds little signal

## Guiding Principle

Use Claude when something feels slightly off, not as a default step.
