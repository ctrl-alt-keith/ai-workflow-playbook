# Using an External AI Reviewer

An external AI reviewer can provide independent evidence at two different
scales: a lightweight targeted sanity check during delivery, or a governed
independent artifact review before a material transition. Keep the selected
mode explicit and proportional to the work.

This pattern is provider-agnostic. It can apply to Claude, Gemini, ChatGPT, or
another reviewer model when a targeted review would add signal.

A reviewer verdict is evidence, not execution authority. It does not grant
implementation, approval, merge, release, or another transition. Human and
repo-local authority boundaries continue to control.

External-review independence is a role boundary, not a model, vendor, effort,
or thread property. A child task spawned by the reviewed party does not satisfy
the external-review role, even when it uses a different provider or isolated
context. A qualifying external reviewer is separately invoked under the review
contract and does not inherit the reviewed party's execution context or
authority. This rule does not make child work generally invalid; it only limits
what can satisfy the external-review prerequisite.

## Review Modes

### Lightweight targeted review

Use this optional, non-blocking mode as a second set of eyes on an implementation
or pull request. The reviewer may spot edge cases, completeness gaps, or risky
assumptions before merge. Keep the input and output narrow.

### Governed independent artifact review

Use this mode when the human or task explicitly requires independent review, or
when a selected high-risk workflow contract makes review a proportionate
transition prerequisite. Suitable work may involve material policy, authority,
cross-repository ownership, irreversible consequences, or costly ambiguity
that should be challenged before implementation.

Governed review must identify the exact artifact, reviewer, declared tools and
capabilities, read-only access boundary, sources actually retrieved, material
gaps, and preserved output. The reviewer should independently inspect available
authoritative sources and stop or qualify findings when required evidence is
unavailable. Attribute every verification claim to the actor and source that
performed it; route inaccessible sources to another authorized actor or tool
instead of implying that the reviewer verified them.

### Reviewer selection and failure

The selected reviewer identity and provider are part of the governed-review
contract. When a human, task, or review plan names a specific reviewer or
provider, only a review performed by that selection satisfies the prerequisite.
For example, a task that names Claude requires a Claude review; output from
Codex, Gemini, ChatGPT, or another substitute may be preserved as supplemental
evidence, but it does not complete the named review.

If the selected reviewer cannot authenticate, retrieve required evidence, or
complete the review, preserve that failed attempt and its capability gap in the
review record. Stop at the selected review boundary until the named reviewer
can complete the review or the human authority explicitly approves a revised
review plan. Do not silently substitute another provider, relabel substitute
output as the selected review, or omit the failure from provenance.

Before an expensive Claude review, run its bounded effective-user auth
preflight. A successful preflight only establishes authentication for that
process context; it is not evidence about candidate quality or a guarantee for
the later review. On a preflight or review failure, preserve candidate and
review state unchanged, record only non-secret diagnostics, stop automated
retries, and do not infer `REJECT`, alter auth/session files, or try another
identity-context guess after the validated context is in effect.

When provider output reliably identifies `AUTH_OAUTH_TOKEN_EXPIRED_401` or
`AUTH_SAVED_LOGIN_REFRESH_REJECTED`, stop at `REVIEWER INFRASTRUCTURE FAILURE
— OPERATOR REAUTHENTICATION REQUIRED` and require interactive reauthentication
before rerunning the unchanged preflight and review. Preserve documented
revoked/invalid-credential classes separately; unknown auth-shaped output must
fail closed without a conjectured provider cause. Neither kind of failure is
candidate evidence or grounds to substitute another reviewer.

### Governed reviewer launch and completion

A governed review begins with a controller-owned launch contract, not with a
provider command assembled ad hoc. The contract must bind the exact prompt and
configuration identities, candidate worktree, complete source graph, launch
root, additional readable directories, guarded roots, exact observational
commands, evidence destination, retry bound, and cancellation policy. Choose a
launch root that commonly owns the source graph when practical; otherwise
declare every additional directory explicitly. A narrow package-directory
launch that cannot reach the candidate is a contract failure, not a partially
qualified review.

Before accepting substantive review, the controller must:

- read a representative object from every declared source location;
- execute every exact observational command with the review environment and
  reject hidden wrappers, interpreters, shell operators, hooks, pagers, external
  diffs, text-conversion drivers, and other command effects that exceed the
  grant;
- verify that the evidence destination is writable and disjoint from guarded
  sources;
- record the requested launch root, additional directories, tools, commands,
  and permission posture; and
- inspect provider initialization evidence and stop if the effective tools,
  connectors, startup capabilities, or source reachability differ from the
  contract.

Treat provider permission flags as one control, not the whole read-only proof.
Use the narrowest available tool set, command grammar, provider hooks, sandbox
or filesystem restrictions, disabled connector surface, safe environment, and
controller-side preflight together. Preserve the exact preflight result and
any material qualification gap.

Read-only completion requires a positive whole-source no-delta postflight. The
baseline must accept deliberately dirty, staged, untracked, and ignored source
state without cleaning or normalizing it, then detect content creation,
modification, removal, mode or symlink changes, Git-index changes, and writes
that escape the candidate into another guarded source. Repository status alone
is insufficient. Reviewer output and receipts belong only in the declared,
disjoint evidence destination after its retention and visibility rules admit
those bytes.

An attempt is complete only after the exact reviewer process group is terminal,
its output is captured, its terminal receipt is durable, and no-delta
postflight passes. A fresh attempt may repeat the exact inputs only for an
explicitly documented transient provider class, after the prior attempt is
fully terminal, under the same controller and contract identity, and within a
small declared cap. This is a fresh execution with an exact-input repeat, not a
historical replay. Authentication, billing, access, capability, command,
mutation, cancellation, and unknown failures are not automatically retryable.
Provider-internal retry events are evidence inside one attempt unless the
outer contract explicitly classifies the terminal result as eligible for a new
attempt.

Apply the shared live-process rules in
[`orchestration-and-parallelism.md#live-process-lifecycle`](orchestration-and-parallelism.md#live-process-lifecycle).
Silence, partial output, elapsed time, or a soft liveness threshold never proves
termination and never authorizes a replacement attempt.

Use [`review-packet.md#independent-review-findings-and-re-review`](review-packet.md#independent-review-findings-and-re-review)
for finding disposition and the decision between no re-review, focused
re-review, and a fresh proposal with full review. Do not duplicate those
semantics in a provider adapter or reviewer prompt.

## When To Use an External AI Reviewer

Use an external AI reviewer when:

- a PR touches multiple files, layers, or concerns
- a change has cross-repo implications or consistency risk
- the change feels slightly off or confidence is lower than usual
- a docs or playbook change deserves a quick sanity check for clarity or
  completeness
- a human, task, or proportional high-risk workflow contract selects governed
  independent review before implementation

## When Not To Use an External AI Reviewer

Do not use an external AI reviewer when:

- the change is small or mechanical
- confidence is already high
- tests and CI already cover the meaningful risk
- review would be habitual ceremony rather than useful independent evidence

## Workflow Integration

Keep the default loop simple:

```text
Codex -> PR -> human skim -> merge
```

Use an external AI reviewer only when a targeted review would add signal:

```text
Codex -> PR -> external AI reviewer (targeted review) -> human skim -> merge
```

This lightweight path is optional and never required for merge. Governed review
is a distinct pre-transition mode: when explicitly selected, completing it and
dispositioning its findings may be a prerequisite to implementation or another
named boundary. The review verdict itself still grants no authority.

## Input Guidelines

For lightweight review, give the reviewer only the context needed to review
well:

- a short statement of goal or intent
- the PR description or a brief summary
- only the relevant diffs, not the full repo

Optionally include one specific concern if you want the reviewer to look for a
known risk.

For governed review, provide or authorize read-only retrieval of:

- the exact artifact identity and owning repository;
- the goal, scope, exclusions, risks, and acceptance criteria;
- the governing issue, proposal, contract, or authority record;
- the relevant repository and external source graph; and
- the requested review dimensions and stop conditions.

Require the reviewer to report its identity, sources inspected, capability
gaps, source attribution, findings with exact anchors and severity, and an
explicit verdict. Preserve the output at a reviewable identity. Do not ask for
broad redesign or allow review to widen the approved scope silently.

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
You are acting as an external AI reviewer providing a lightweight second set of
eyes on this PR.

Goal:
<short goal or intent>

Success criteria:
- Return only high-signal review observations that could affect correctness,
  completeness, or safe reuse.
- Do not turn the review into implementation, redesign, or broad process advice.

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

Stop rules:
- If the provided diff or summary is insufficient for a useful review, say what
  evidence is missing instead of guessing.
```

## Reusable Prompt: System / Pattern Sanity Check

Use this for playbook guidance or cross-repo patterns where the main question is
whether the pattern is clear and safe to reuse.

```text
You are acting as an external AI reviewer providing a lightweight sanity check
on this proposed pattern.

Intent:
<short statement of the pattern and why it exists>

Success criteria:
- Identify only issues that materially affect clarity, safety, or reuse.
- Preserve the pattern's intended scope.

Material:
<paste the relevant guidance, summary, or diff>

Constraints:
- Return at most 3 issues.
- Focus on clarity problems, hidden assumptions, or misuse risk.
- Do not redesign the pattern.
- Do not expand scope.
- If nothing stands out, say: LGTM

Stop rules:
- If the material is too incomplete to judge, say what is missing instead of
  inventing context.
```

## Reusable Prompt: Governed Independent Artifact Review

```text
You are acting as an independent, read-only reviewer of an exact artifact.

Artifact and identity:
<repository, path or commit, and exact identity>

Decision boundary:
<the human decision or workflow transition this review informs>

Goal, scope, and exclusions:
<bounded review context>

Authoritative sources:
<sources to inspect directly with the available read-only access>

Review dimensions:
- correctness and completeness against the stated scope;
- ownership, authority, and phase-boundary integrity;
- unsupported claims, hidden assumptions, or over-generalization;
- smallest adequate change and prohibited scope expansion.

Required output:
- reviewer identity and role;
- tools, access, sources actually inspected, and material capability gaps;
- findings with severity and exact artifact anchors;
- source attribution for each verification claim;
- explicit verdict: ACCEPT, ACCEPT WITH CHANGES, or REJECT.

Constraints:
- Perform no mutation.
- Do not infer unavailable source state or treat a capability as authority.
- Do not redesign or widen the artifact beyond reporting a finding.
- If required evidence is unavailable, identify the gap and limit the verdict
  instead of guessing.
```

## Failure Modes

Watch for these failure modes:

- over-auditing simple changes
- suggestion overload that creates churn without reducing risk
- architectural drift from letting review comments reshape the task
- slowing the loop with an extra step that adds little signal
- unsupported verification claims when the reviewer lacked source access
- silent reviewer substitution after a named reviewer fails or is unavailable
- treating an ACCEPT verdict as approval or transition authority
- repeating a full review without deciding whether the original review remains
  applicable

## Guiding Principle

Use lightweight review when targeted second-opinion signal is worth its cost.
Use governed independent review only when explicit authority or proportional
risk selects it. In either mode, preserve provider neutrality, evidence limits,
and human decision ownership.
