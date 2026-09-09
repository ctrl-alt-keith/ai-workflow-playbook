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

### Review output and finding disposition

Collect the reviewer's complete findings and verdict. When the review
materially affects a decision, preserve its evidence boundary and disposition
under
[`review-packet.md#independent-review-findings-and-re-review`](review-packet.md#independent-review-findings-and-re-review).
Apply governed-artifact capture only when the output independently meets the
candidate floor in
[`evidence-lifecycle.md#governed-artifact-capture`](evidence-lifecycle.md#governed-artifact-capture);
the review mode alone does not require a separate artifact or elaborate
receipt.

Keep failed attempts, completed reviews, findings, dispositions, and human
decisions distinct. Preservation records evidence only; it does not turn a
failed attempt into a verdict or any review into approval, merge authority, or
completion.

### Exact-candidate review contract

A governed review is a separate invocation of the selected reviewer against
one exact candidate. Supply the repository or artifact identity, exact commit
or immutable version, review question, relevant authoritative sources, and the
read-only access needed to inspect them. The reviewer must report sources
actually inspected, material capability gaps, findings with useful anchors,
and an explicit verdict.

Immediately before invoking a repository reviewer, verify that the selected
checkout resolves to the configured exact candidate commit. Include the
verified repository path and commit in the reviewer context. A mismatch stops
before review; it does not select a new candidate. Check the reviewed head
again before disposition or merge through the normal repository lifecycle.
This check binds the selected `HEAD`; it does not claim that every live
worktree byte equals committed content.

Use the narrowest provider tool set that can read the required sources. Disable
write tools, inherited connectors, session persistence, and unneeded startup
configuration when the provider supports those controls. If required source
access is unavailable, the reviewer reports the gap and limits its verdict
instead of receiving broader authority.

Read-only review constrains the reviewer's capabilities; it does not require
the repository, worktree registry, or shared Git administration to remain
still. Do not add source no-delta monitoring, worktree or object attribution,
live stabilization, process-controller state, or integrity receipts merely to
prove that the reviewer was read-only. Concurrent repository activity is not a
review failure when the configured candidate identity remains the one selected
for review.

Run the selected provider's bounded authentication preflight when its current
adapter requires one. Treat nonzero, empty, authentication, access, or other
provider failures explicitly and do not silently substitute another reviewer.
After a successful result, disposition findings and any need for re-review
under the review-packet contract. Reviewer output grants no implementation,
promotion, merge, release, or other consequential authority.

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
