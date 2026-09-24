# Codex Adapter

Codex maps the shared Playbook to a bounded repository execution surface. Apply
the repository floor and the task-activated canonical owners; this adapter
contains only Codex-specific controls.

Provider provenance: OpenAI Codex model and instruction-discovery guidance
checked 2026-09-23. Official sources belong in reviewed change evidence.

## OpenAI Model And Reasoning Routing

Apply [model routing](../model-routing.md). Select model and reasoning effort
separately for the bounded responsibility, and record requested and
runtime-effective values separately. A runtime value that is not exposed is
`unobservable`; requested configuration is not proof of the effective value.
Start with GPT-6 Sol at Medium unless the bounded responsibility meets a
different route below.

| Task class | Default model | Reasoning class |
| --- | --- | --- |
| Mechanical retrieval, checks, formatting, or evidence packaging | GPT-6 Luna | Light |
| Deterministic edits and routine PR delivery with clear acceptance criteria and independent validation | GPT-6 Luna | Medium |
| Normal implementation, CI diagnosis, or bounded evidence interpretation | GPT-6 Sol | Medium |
| Bounded synthesis, difficult local debugging, or moderate reconciliation | GPT-6 Sol | High |
| Architecture, authority, protocol, or adversarial-review work | GPT-6 Astra | High; consider higher only for observed need |

These defaults are routing hypotheses, not capability guarantees. Escalate on
unresolved ambiguity, conflicting evidence, unexplained invariants, repeated
failure, or material error consequences. Use GPT-6 Astra for the unresolved
bounded question when the Sol route no longer suffices; use GPT-6 Luna when
deterministic work is independently checkable. Delegate established
deterministic work only with its inputs, validation, and authority boundary
intact.

For a model comparison, preserve the prior effective effort as the baseline,
change independently evaluable variables separately, and record any required
configuration difference as a limitation. Leave optional execution features out
of the baseline until the workload and measured results justify them.

### Codex Selector Routing And Acceptance

For a `FRESH THREAD` or `CHILD TASK`, record the requested model, exact
selector, requested effort, runtime-effective model/effort (or
`unobservable`), and any allowed substitution before work starts. Exact-model
requirements fail closed: reject aliases, near matches, guessed IDs, and
unapproved fallback.

| Requested model | Exact selector |
| --- | --- |
| GPT-6 Astra | `gpt-6-astra` |
| GPT-6 Sol | `gpt-6-sol` |
| GPT-6 Luna | `gpt-6-luna` |

Pass the accepted exact selector to the actual launch. Local preflight checks
only independent prerequisites; they do not launch Codex or qualify a selector.

For `SAME THREAD`, preserve the parent configuration. When work crosses a
capability boundary, use an explicitly authorized fresh thread or child rather
than silently changing it. Apply the shared routing vocabulary and material
prompt requirements in [prompts](../prompts.md) and
[prompt contracts](../prompt-contracts.md).

When providing a complete Codex prompt, place its operator metadata before the
copyable prompt body and keep it outside that body:

```text
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <model or preserve/resolve-at-launch state>
Recommended reasoning level: <Light | Medium | High or preserve/resolve-at-launch state>
Reason: <concise task-specific reason>
```

This metadata is advisory and does not grant task authority. Resolve unknown
launch controls with the operator; do not report them as unavailable without
runtime evidence. Preserve mandatory capabilities, reasoning class, allowed
degradation, and non-weakenable guarantees when mapping a material prompt to
Codex. In Markdown, render metadata and the prompt body in consecutive code
blocks with no intervening prose.

For qualifying Airtable canonical-text handoff, apply the shared verification
and fail-closed contract in [prompts](../prompts.md#airtable-canonical-text-handoff).

### Visible Thread Names

Apply [executor-applied visible thread names](../prompts.md#executor-applied-visible-thread-names).
For a Codex `FRESH THREAD`, or an eligible separately visible `CHILD TASK`,
apply the computed name before substantive work when the surface exposes the
control. For an ordinary `SAME THREAD`, omit naming unless an explicit rename
is in scope. If the control is unavailable, continue and report that
non-blocking limitation; do not ask the operator to perform it.

## Repository Execution

Before repository work, apply [start here](../start-here.md), the repository
floor, and task-activated owners. Confirm the Codex project, execution
container, current directory, Git state, repository, and worktree match the
task before mutation. Stop on a required source, authority, repository, or
worktree mismatch.

Codex loads applicable global and project guidance in precedence order; use the
guidance actually available to the run. Ambiguous repository work is review or
orchestration unless the human explicitly authorizes implementation, commit,
push, or PR delivery.

Before repository automation or worker fan-out, run
[`scripts/repository-preflight`](../../scripts/repository-preflight) from the
Playbook checkout and stop on a non-zero exit. This establishes only the
[shared repository prerequisites](../repository-preflight.md); Codex launch and
model qualification remain separate.

### Worktrees

Use the repository's one-repository, one-branch, one-dedicated-worktree, one-PR
rule. For same-repository parallel work, separate lanes by file, behavior, or
risk surface and pause for coordination on overlap. Use the repository's
canonical validation and PR-readiness paths; PR readiness never authorizes a
merge, release, or other human decision.

Place repo-changing worktrees under `<repo>/.worktrees/`. Before creating or
reusing one, inspect `git worktree list` and select a path that clearly belongs
to the task; create it with direct `git worktree add`, not a separate `mkdir`.
Reuse only a clean, intelligible worktree for the same active task. When cleanup
is in scope, remove only task worktrees and report any blocked or deferred
cleanup rather than concealing it.

Use direct repository and provider commands where the execution surface supports
them. Do not add shell wrappers for convenience; use one only when necessary
shell semantics cannot be expressed directly, and keep it narrow. Do not bypass
runtime approval or sandbox boundaries; surface an approval limitation early.
Use the portable [user-layer rule template](../../.codex/rule-templates/custom.rules)
only as a template: it grants no authority or allow rule and does not install
itself. Do not use raw `gh api` when a high-level command or approved connector
is required.

When a child CLI's authentication or runtime behavior depends on login identity,
verify the effective operating-system identity and inherited environment
separately. Normalize only the relevant identity-sensitive variables for that
bounded invocation; do not hard-code an operator identity or infer that one
matching variable makes the child safe.

## Review, Evidence, And Runtime Boundaries

For GitHub-dependent work, verify current access and inspect the owning source
before relying on cached context or local state. For a requested PR review,
apply [direct PR inspection](../review-packet.md#direct-pr-inspection). Do not
claim mergeability, required checks, or branch protection without current
evidence.

For independent review, apply [external reviewer](../external-ai-reviewer.md)
and [finding disposition](../review-packet.md#independent-review-findings-and-re-review).
Bind the review to its exact candidate, sources, decision boundary, prohibited
mutations, and stop condition. A reviewer verdict is evidence, never approval;
keep any reviewer source-access gap visible until an authorized actor verifies
it.

When launching a local `claude-review` or `codex-review`, use the active
checkout's repository-owned launcher with its exact candidate commit and
required preflight; apply [launcher outcome handling](../../scripts/review-launchers.md).
A launch mismatch stops before review; failed launch or review is not a verdict
and does not authorize substitution. Treat diagnostics as evidence only when
the terminal record says they were written or a qualified post-execution
readback under [`review-launchers.md`](../../scripts/review-launchers.md)
verifies them.

Goal state, successful validation, a receipt, checkpoint, or delivered prompt
is execution evidence, not acceptance, approval, merge, release, publication,
or continuation authority. Re-evaluate activation, source refresh, and
authority when scope, source requirements, locality, or completion boundary
materially changes.

Use [official-source requirements](../engineering-baseline.md#public-api-baselines)
for external behavior claims. Report material phase, source, validation,
artifact, blocker, and stop changes under [operator observability](../core-model.md#operator-observability)
without exposing hidden reasoning.

Continue autonomously only while scope, repository context, required sources,
validation, and the next authority boundary are clear. Do not widen scope or
take ownership of a merge, release, tag, uncertain deletion, security-sensitive
action, permission decision, or policy interpretation.
