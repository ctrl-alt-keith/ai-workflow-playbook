# Core Model

The operating model is simple: humans own intent, standards, and decisions; AI accelerates drafting, execution, synthesis, and iteration inside clear boundaries.

Repository tasks translate those role boundaries into the interaction modes in
[`repo-readiness.md`](repo-readiness.md#interaction-mode-preflight):
implementation, review/audit, and orchestration/prompt-authoring. Select the
mode before acting so the AI role matches the human's intended delegation.

## Playbook Philosophy

The Playbook exists to make AI-assisted work more reliable, proportional, and
understandable without making ordinary work harder. Add workflow only when it
prevents a demonstrated failure or preserves an important authority, evidence,
execution, or safety boundary. Prefer the smallest reusable rule with one
canonical owner, and remove duplication, obsolete ceremony, and explanatory
machinery when they no longer improve behavior.

Use one maintenance test: does the change reduce ambiguity or protect a real
boundary enough to justify its complexity? A change should leave the Playbook
easier to apply correctly, not merely more completely specified. Incidents are
evidence for improving an underlying rule, not permanent doctrine or an archive
of every failure and fix.

## Operating Principles

These principles apply to AI-assisted work whose evidence, authority, review,
or completion boundaries materially affect the outcome. They do not make
ordinary chat, brainstorming, or conceptual discussion procedural.

- **Establish relevant reality before acting.** Inspect the current sources
  that control the task when they are available. Treat conversation, memory,
  and summaries as navigation rather than authority. Repository source
  triggers and retrieval mechanics remain owned by
  [`source-first-retrieval.md`](source-first-retrieval.md).
- **Keep evidence, authority, and capability distinct.** Evidence can support
  a decision without approving it, and the ability to perform an action does
  not grant permission to perform it.
- **Preserve material boundaries.** Keep scope, ownership, authority, and
  evidence status visible. When the distinction affects a decision, say what
  is verified, inferred, partial, unknown, or blocked; use
  [`evidence-lifecycle.md`](evidence-lifecycle.md) when evidence is accepted,
  integrated, or synthesized.
- **Make uncertainty and capability gaps explicit.** Name unavailable sources,
  unsupported claims, and tool or access limits instead of inferring through
  them or flattening them into a generic disclaimer.
- **Use a proportional decision boundary before consequential execution.**
  Increase design, review, or approval separation with ambiguity, risk,
  authority sensitivity, and irreversibility. Small, obvious, reversible work
  should not inherit unnecessary ceremony. Repository lifecycle and delivery
  mechanics remain owned by [`feature-lifecycle.md`](feature-lifecycle.md).
- **Validate or verify before relying on consequential conclusions.** Choose
  checks that match the claim and risk. Passing validation is evidence about
  what was checked; it is not acceptance, approval, or broader authority.
- **Re-observe resulting reality after consequential change.** Retrieve the
  actual outcome instead of assuming the planned effect occurred, then
  reconcile separately owned systems only when their workflows require it.

## Evidence Classification Invariant

Before a material conclusion, identify its authoritative source and classify
relied-on inputs by their relationship to it; use the evidence classes the
question needs, not a fixed taxonomy.

Derived reports, dashboards, receipts, summaries, and caches may evidence their
own production or history. Verify them against the owner before concluding
anything about the authoritative state they summarize. A derived artifact must
never become evidence for the authoritative state it summarizes. This is an
execution invariant; [source-first-retrieval.md](source-first-retrieval.md) owns repository
triggers, ordering, verification, and recovery.

## Operator Observability

Surface operational transitions when they materially change human review,
workflow authority, or subsequent execution. State the entered mode, contract,
evidence boundary, validation/readiness state, or blocker and its consequence.
Do not expose or request private reasoning or impose a fixed phase list or
template.

For bounded bulk or connector-heavy work, report aggregate milestones and
retain complete item evidence outside conversation. Report material blockers,
authority/scope mismatch, drift, privacy/retention issues, collisions,
overwrite risk, validation failure, and permission/approval/destructive
boundaries promptly. Honor supported mid-run presentation preferences; report
client-forced output as a limitation. Routine item successes need no update.

### Successful completion projection

For ordinary successful repository work, use roughly 2–4 short sentences:
outcome, exact review surface and status, useful canonical-validation summary,
and current stop boundary. Add facts only when they change operator review,
decision, or action. Detailed evidence belongs in the PR, issue, and durable
artifacts.

Omit routine transport verification, hashes, counts, receipts, source/preflight
inventories, scratch/cleanup mechanics, command history, raw test counts,
unchanged authority reminders, and details already in the artifact. Keep
runtime/model evidence, adjacent dispositions, findings, and unresolved claims
there unless material to operator action.

Expand for failure/partial success, identity or integrity mismatch, consequential
retry, validation/review failure, capability/authentication limits, unexpected
state, unresolved risk/blocker, required human decision, or cleanup residue.
Report the exception and consequence, not the full forensic history. This
projection does not weaken evidence collection or retrievability, required
progress updates, or specialized handoff identity/verification requirements.

## Authority Follows The Question

Do not select one universal system of record for a workflow. Classify the
question first, then retrieve the source that owns that kind of fact:

- Current human direction controls delegated intent and authority; the owning
  task or planning surface controls recorded intent, priority, sequencing, and
  acceptance context.
- The owning repository and its hosted repository state control current files,
  implementation, review, validation, and merge facts.
- Canonical shared documentation controls reusable doctrine; repo-local
  sources control repository-specific contracts and execution behavior.
- The owning provider or runtime controls current external operational state.
- Durable artifacts, receipts, reports, and logs answer historical execution
  questions only within the claims and evidence they preserve; they do not
  become proof of current mutable state or authority.

Some questions cross these boundaries. Retrieve each applicable owner, keep
the claims distinct, and reconcile them by owning scope and the applicable
instruction hierarchy. Recorded planning intent does not override current
human direction, and one source must not override facts owned by another.
Availability, convenience, discoverability, integration quality, duplication,
or durability does not transfer authority. For recovery, reconstruct the
applicable contract and next action from the durable sources named by the
owning workflow, then revalidate mutable facts.

## Protocol Invariants

Reviewed semantic invariants define a protocol: meaning, scope, authority,
evidence identity, isolation, and validation. Tools, workers, prompts, branches,
and orchestration topology may change only while preserving them. Successful
execution does not establish a reusable invariant or authorize semantic change.

## Roles

### Human role

- Define the goal, scope, and quality bar
- Set or approve the execution plan
- Review meaningful deltas, risks, and tradeoffs
- Decide when work is complete
- Decide what is worth capturing into the playbook

### AI role

- Turn direction into concrete next steps
- Execute bounded work quickly and consistently
- Surface ambiguity, risk, and missing information
- Summarize changes, evidence, and open questions
- Help capture reusable patterns after delivery

## Interactive And Execution Surfaces

Interactive and execution surfaces are semantic roles, not product identities
or authority classes. Interactive surfaces support conversation, intent,
steering, judgment, review, disposition, and final human-controlled closure.
Execution surfaces perform bounded tool-backed work, mutation, validation, and
evidence production under an explicit execution contract.

A product may expose either or both roles. Route by task shape and current
capability, not vendor, product, difficulty, or model choice. Consequential
completion decisions normally return to the interactive surface unless an
owning workflow explicitly places that authority elsewhere. The interactive
surface is not canonical or a required intermediary; human direction and each
fact or decision's owning source retain authority.

A semantic handoff declares the current bounded action, the existing human
authority and its owning reference, the sources and constraints that apply,
and the completion boundary. It may point to exact durable recoverable state
instead of reproducing that state in conversation. The handoff, its pointer,
the recovered payload, a recorded next action, validation, and successful
retrieval create zero authority. The receiving actor must verify its identity
and current authority, refresh mutable facts from their owning sources, and
fail closed where the applicable contract or exact recoverable state cannot be
resolved.

### Interactive-to-execution transition consent

An interactive surface may recommend a different execution surface, but it
must not instantiate or transition into that surface without explicit operator
consent. Consent is either a direct operator request for that execution surface
or explicit acceptance of an offered transition.

Task complexity, multi-step work, repository work, browser, file, or artifact
work, coding, and a judgment that the execution surface is a better fit do not
create transition authority. When a required capability exists only on that
surface, report the limitation and offer the transition; continue using tools
available on the interactive surface when they are sufficient.

### Independent Review As A Third Role

Independent review is likewise scoped to a run rather than to a product,
vendor, model, effort setting, or thread. A reviewer produces evidence about
work it did not itself produce.

This section establishes only that the role exists alongside interactive and
execution surfaces.
[`external-ai-reviewer.md`](external-ai-reviewer.md) remains the canonical
owner of what independence requires, how a reviewer is selected, and how
reviewer failure or substitution is handled. Do not restate those requirements
here or in an executor adapter.

### Surface Classes

A surface class describes what an execution surface can structurally do,
independent of vendor or product. It states repository locality only. It does
not state who started the run.

- **Conversational** — no filesystem and no repository locality. Context
  arrives per thread, and any startup contract that depends on reading
  repository files is best-effort rather than guaranteed.
- **Agentic-local** — filesystem and repository locality. A startup contract
  that reads repository and repo-local instruction files genuinely runs.
- **Agentic-remote** — agentic execution without guaranteed local repository
  locality. Sources are reached through a connector or another retrieval
  route rather than through the filesystem.

Initiation is a separate property rather than a fourth class. A run is either
human-initiated or unattended, and either may occur on any class. An
unattended run on an agentic-local surface remains agentic-local; what
changes is that no human is present to resolve an ambiguity, which the owning
workflow handles rather than the class.

Surface class does not assign a role and does not rank surfaces. Any actor may
occupy any role its surface class can structurally support.

Executor adapters own the mapping from their concrete products onto these
classes; this document enumerates no products. Until an adapter declares the
class for a surface, that surface has no class under this vocabulary and this
section places no obligation on it. Where an adapter has declared a class and
a required contract depends on a capability that class lacks, fail closed and
report the capability gap rather than substituting a weaker route.

## Kickoff Mutation Boundaries

Kickoff is neither a universally read-only phase nor permission to begin every
later phase. A controller or generated prompt must state the task-appropriate
mutation boundary explicitly and keep these three classes distinct:

1. **Task-owned orchestration and evidence mutations may be permitted.** When
   current authority and prerequisites support them, a controller may update
   the governing task, append concise task-owned progress or source
   assessments, produce and preserve a decision package or exact downstream
   prompt and its receipt, verify read-back, and record exact identities. The
   applicable planning, evidence, and storage owners still decide whether and
   how each write is admitted.
2. **Delegated substantive execution is not implied.** Kickoff bookkeeping or
   evidence capture does not authorize repository mutation, implementation,
   migration, destructive cleanup, production execution, provider
   reconfiguration, or other task substance assigned to a later executor or
   phase. That work requires its own bounded authority and satisfied
   prerequisites. In particular, producing prompt or handoff evidence does not
   authorize repository implementation, remote-repository mutation, or
   unrelated planning-system mutation.
3. **Human-gated transitions remain separately human-gated.** Architecture or
   operational adoption, destructive approval, merge, release, publication,
   scientific adoption, and any task-specific human decision gate require the
   authorized human decision against the exact reviewed identity.

The existence of a thread does not establish readiness. If authority or a
prerequisite fails, the controller must not mark the governing work in progress
merely because kickoff occurred. It may record the exact blocker only when that
task-owned write is useful and authorized. Unrelated planning items,
repositories, providers, and execution state remain untouched.

A genuinely read-only kickoff remains valid when the owning workflow requires
it. State why the restriction is needed and scope it to the applicable actor,
phase, and mutation surfaces instead of relying on a vague blanket phrase.

Controller-owned orchestration is distinct from prompt-contract machinery.
Hydrators, representation adapters, renderers, validators, receipts, and
checkpoints remain evidence-only under
[`prompt-contracts.md`](prompt-contracts.md#ownership-and-live-authority) and
must not drive lifecycle state or orchestration.

A prompt, digest, receipt, artifact, planning status, successful call, storage
object, comment, validation result, retrieval, review verdict, branch, commit,
or pull request creates zero authority. These records may exercise or evidence
authority that already exists; they cannot authorize a later phase or cross a
human gate.

## Authority And Transitions

Authority is permission to make a decision or cross a workflow boundary. It is
distinct from capability: a person, agent, tool, or automation may be able to
perform an action without being authorized to perform it.

Material transitions should make explicit the authority they consume and any
authority an authorized human grants for the next bounded action. Execution,
successful completion, validation, receipts, stored state, prompts, replay,
topology, and automation can record or exercise existing authority; none can
create approval authority. When authority is absent, ambiguous, expired, or
outside the current contract, the transition remains fail-closed.

## Protocol Phases

When a workflow includes both, separate evidence production (acquisition,
production, review, integration, validation under the operational contract) from
decision production (interpretation of accepted evidence, recommendation,
approval, disposition). Crossing requires an explicit review and authority boundary;
completed evidence does not approve downstream decisions. These are semantic
roles, not required stages or Git topology. When accepting, integrating, or
synthesizing evidence, apply [evidence-lifecycle.md](evidence-lifecycle.md) before
crossing into decision production.

## Active Bounded-Task Continuity

When a conversation already has an active bounded task, preserve that task
across related follow-ups, corrections, steering, questions, and task-local
tangents. Clear human direction to start a new task, switch topics, ask an
unrelated question, or make an equivalent transition adopts the new task
without another confirmation.

When a new instruction is strongly unrelated and has no clear transition
signal, treat the discontinuity as a plausible wrong-thread prompt. Preserve
the active task, briefly ask whether to switch this conversation to the new
task or continue the active task, and make no task-owned planning,
repository, execution, or other durable mutation for the unrelated request
while intent is unresolved.

After a clear or confirmed switch, adopt the new task and apply the normal
task-change, activation-routing, interaction-mode, execution-surface, and
source-refresh rules before acting.

Use this guard only for a strong discontinuity from an active bounded task. It
does not create a general intent taxonomy, confidence score, classifier, or
confirmation framework.

### Active-task continuity qualification cases

These cases protect the semantic boundary rather than classifying natural
language.

| Case | Relationship to active task | Transition signal | Outcome | Unrelated durable mutation |
| --- | --- | --- | --- | --- |
| `related-implementation-follow-up` | related | none required | continue | not applicable |
| `correction-steering-or-task-local-tangent` | related | none required | continue | not applicable |
| `explicit-unrelated-topic-switch` | unrelated | explicit | switch and re-route | only after normal current-task gates |
| `abrupt-unrelated-without-switch-signal` | unrelated | absent | confirm and hold | prohibited while unresolved |
| `confirmed-switch-after-hold` | unrelated | confirmed | switch and re-route | only after normal current-task gates |

## Durable Continuity

Durable project artifacts are the recoverable continuity substrate for a
workflow. Depending on the task, those artifacts can include the current
operational contract, authoritative repository and issue state, exact evidence
and artifact identities, human approval records, stage and attempt receipts,
validation results, and the next permitted action. Their authority remains
specific to the role assigned by the owning source; durability alone does not
make an artifact canonical or grant permission.

Conversation is useful for intent, navigation, and explanation, but it is
non-authoritative context. Recovery must be possible from durable sources by
reconstructing the applicable contract, current authority, accepted inputs,
completed work, and next permitted action, then revalidating any mutable source
state. If that contract cannot be reconstructed or no longer applies, stored
history cannot silently authorize continuation.
