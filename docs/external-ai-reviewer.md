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

### Review output preservation and discussion routing

Apply the governed-artifact candidate and storage-admission contract in
[`evidence-lifecycle.md`](evidence-lifecycle.md#governed-artifact-capture) to
complete governed review output. A substantial governed review qualifies only
when the shared floor holds: another thread, reviewer, disposition step, or
human decision needs the exact output and reconstruction from a summary would
weaken that dependency.

When the candidate and storage contract pass, preserve the complete review at
the durable destination selected by the owning storage contract, which for a
governed review is the declared evidence destination bound by the launch
contract. Keep pull-request, planning, and chat discussion to the concise
verdict, material finding disposition, and an immutable pointer or identity for
the complete artifact. Do not paste the complete review into an incidental
discussion surface as the normal successful path. When qualified durable
capture is unavailable, apply the
[`mandatory governed-artifact capture failure boundary`](evidence-lifecycle.md#mandatory-governed-artifact-capture-failure-boundary)
rather than using that surface as storage.

Apply the same rule to failed and non-verdict attempts when their complete
output or failure evidence has authorized downstream value and retention is
permitted. Keep the attempt, complete output, terminal receipt, verdict,
finding disposition, and human decision as distinct identities and states.
Preservation records evidence only; it does not turn a failed attempt into a
review verdict or any review into approval, merge authority, or completion.

### Governed reviewer launch and completion

A governed review begins with a controller-owned launch contract, not with a
provider command assembled ad hoc. The contract must bind the exact prompt and
configuration identities, candidate worktree and commit, complete source graph,
logical launch root, additional readable directories, guarded roots, exact observational
commands, evidence destination, attempt count and any explicit retry policy, and
cancellation policy. Choose a
logical launch root that commonly owns the source graph when practical; otherwise
declare every additional directory explicitly. A narrow package-directory
launch that cannot reach the candidate is a contract failure, not a partially
qualified review. A provider may run from fresh attempt-local scratch to contain
its own startup mechanics only when the launcher exposes every logical source
root explicitly and verifies the effective runtime directory during initialization.

Bind an exact immutable stream and terminal-receipt path for every explicitly
authorized attempt and a distinct exact path for successful final reviewer output. Keep
mutable live-process mechanics in private controller-owned
attempt-local scratch and expose their exact locator while the controller is
live; do not turn a replace-in-place state file into a durable artifact. Only
the configured no-overwrite artifacts enter the governed evidence destination.

Before accepting substantive review, the controller must:

- read a representative object from every declared source location;
- execute every exact observational command with the review environment and
  reject hidden wrappers, interpreters, shell operators, hooks, pagers, external
  diffs, text-conversion drivers, and other command effects that exceed the
  grant;
- verify that the evidence destination is writable and disjoint from guarded
  sources;
- record the requested logical launch root, actual provider runtime directory,
  additional directories, tools, commands, and permission posture; and
- inspect provider initialization evidence and stop if the effective tools,
  connectors, startup capabilities, or source reachability differ from the
  contract.

Treat each observational command as an exact argv grammar, not a generic
executable plus token scan. Retain only the subcommand forms the review needs.
For Git, require one exact `git -C` declared root, classify every token as an
admitted option or exact revision/object expression, and reject unresolved
tokens rather than allowing Git to reinterpret them as paths. Explicit and
implicit `diff --no-index`, path traversal, outside absolute paths, mixed
inside/outside operands, unadmitted pathspec magic, and missing path boundaries
are contract failures before provider launch. If a retained Git form accepts
paths, require its exact path boundary and resolve every operand inside one
declared source root.

Controller-side command preflight does not prove that the same command can run
inside the provider process. Require a successful in-provider result from one
exact granted command canary, reject any sandbox-bypass request, and fail closed
when the canary is missing or fails. This qualifies the command transport; it
does not replace controller-side execution of every configured command form.

Treat provider permission flags as one control, not the whole read-only proof.
Use the narrowest available tool set, command grammar, provider hooks, sandbox
or filesystem restrictions, disabled connector surface, safe environment, and
controller-side preflight together. Preserve the exact preflight result in an
exclusive, no-overwrite receipt at the admitted evidence destination; do not
create and delete a write probe in a durable artifact namespace. Preserve any
material qualification gap even when the preflight receipt cannot be produced.

Read-only completion requires a positive whole-source no-delta postflight. The
baseline must accept deliberately dirty, staged, untracked, and ignored source
state without cleaning or normalizing it, then detect content creation,
modification, removal, mode or symlink changes, Git-index changes, and writes
to the candidate-specific and shared Git administration directories—including
lock-file creation, removal, replacement, mode, symlink, and content changes—and
writes that escape the candidate into another guarded source. Treat the
candidate worktree Git directory separately from the shared common Git
directory. Model the primary worktree explicitly alongside every linked
worktree, including each worktree's exact `HEAD`, `index`, `logs/HEAD`,
`COMMIT_EDITMSG`, and `ORIG_HEAD` administration paths. A change to one of
those paths is attributable to another worktree only when its observed HEAD
transition and, when symbolic, exact branch-ref transition agree. Any other
path beneath a known worktree Git directory, or any unknown common-root path,
remains blocking. Positively protect the candidate index, HEAD and symbolic identity,
selected commit, candidate branch ref and reflog, exact object revisions used by
an admitted review command, command-semantic configuration and administration,
and the resolution and reachable-object closure of those protected revisions.
Treat `origin/main` as a moving comparison base only in the explicitly supported
candidate comparisons `origin/main...HEAD` and `origin/main..HEAD`, rather than
as part of the frozen candidate identity. After candidate selection, its ref or
reflog may advance without invalidating evidence about that exact candidate,
including when the new main overlaps it semantically. A standalone
`origin/main` revision remains protected review input.
Record the exact before and after ref targets and classify the change explicitly;
freshness and mergeability against current main remain separate post-attempt
questions. Candidate identity and exact object revisions remain protected.
Apply equivalent index and administration coverage to another guarded source
that is itself a repository. Repository status alone is insufficient. Reviewer
output and receipts belong only in the declared, disjoint evidence destination
after its retention and visibility rules admit those bytes.

A changed common-Git object is not automatically candidate contamination, but
it is never ignored. Tolerate it only when current linked-worktree and ref
evidence identifies the change as other-worktree administration, a moving
comparison base, an unrelated ref or reflog, or shared object-storage activity; every protected ref,
revision, HEAD, and reachable object still resolves to the exact baseline
identity; and the changed object has an ordinary file or directory identity
with no lock, symlink, special-object, vanished-path, or mode ambiguity. Object
additions, packing, and storage-layout changes use this same positive
resolution-and-reachability proof. Candidate administration, protected refs or
reflogs, replacement refs, alternates, shallow or graft state, attributes,
configuration, packed-ref ambiguity, unknown shared administration, and any
inconsistent observation remain blocking. This worktree-aware proof permits
unrelated commits and pushes without requiring a clone or serialization while
remaining fail-closed when attribution is ambiguous.

Bind every attempt to the configured candidate commit again immediately before
capturing its attempt baseline and immediately before creating the reviewer
process. Apply both checks to each explicitly authorized attempt, and record the
observed commit and symbolic-ref identity. Drift at either boundary stops before
that attempt can start; it never becomes a new governed baseline.

During live monitoring, an object-only shared-Git change or a change to one of
the exact other-worktree administration paths can appear just before the
HEAD/ref transition that proves its owner. Admit only a bounded stabilization
interval for that provisional state. If the proof does not arrive, or any
candidate, protected-ref, lock, unknown administration, or other change
accompanies it, apply the blocking classification and emergency stop. Terminal
postflight does not admit provisional attribution.

Do not broadly exclude `.lock` paths from the decisive baseline-to-terminal
comparison. An unchanged pre-existing lock may remain when its exact identity
matches. A new, removed, or changed lock is reviewer side-effect contamination:
produce no qualifying verdict, do not reset it automatically, and stop until it
is corrected and dispositioned. Any live-monitor exception must identify one
controller-owned transient lock by exact path, actor, and lifetime and must not
apply to terminal postflight.

Keep raw observation separate from candidate-integrity disposition. Preflight,
live monitoring, emergency-stop decisions, terminal postflight,
successor-attempt eligibility, and receipts must use the same classification semantics. Record
each changed Git-administration object by normalized path relative to its owning
Git directory, owner scope, change type, before and after identities,
classification evidence, and blocking or tolerated disposition. A review may
pass with proven-unrelated raw changes, but its receipt must retain those raw
and tolerated paths rather than claim that no change occurred. Only blocking or
ambiguous changes qualify as unauthorized mutation for emergency stopping.

An attempt is complete only after the exact reviewer process group is terminal,
all output collectors reach end-of-stream, its output is captured, its terminal
receipt is durable, and no-delta
postflight passes. The Claude review controller authorizes exactly one provider
attempt; any later review is a new explicit controller invocation with its own
contract and evidence. Another adapter may own a bounded fresh exact-input
repeat only when its current contract explicitly declares that responsibility,
the prior attempt is fully terminal, and the terminal provider class is
documented as eligible. Authentication, billing, access, capability, command,
mutation, cancellation, and unknown failures are not automatically retryable.
Provider-internal retry events remain evidence inside one attempt.

Apply the shared live-process rules in
[`orchestration-and-parallelism.md#live-process-lifecycle`](orchestration-and-parallelism.md#live-process-lifecycle).
Silence, partial output, elapsed time, or a soft liveness threshold never proves
termination and never authorizes a replacement attempt.

Use [`review-packet.md#independent-review-findings-and-re-review`](review-packet.md#independent-review-findings-and-re-review)
for finding disposition and the decision between no re-review, focused
re-review, and a fresh artifact with full review. Do not duplicate those
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
