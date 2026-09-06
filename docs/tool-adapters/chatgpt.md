# ChatGPT Adapter

This adapter projects the Playbook onto repository-scoped ChatGPT use. Chat
and Work are nested task-shape or capability modes under that one ChatGPT
adapter, not separate durable executor identities or adapters. It begins after
repository work has been activated; ordinary conceptual Chat remains outside
repository startup. Shared operating rules remain owned by
[`start-here.md`](../start-here.md) and [`core-model.md`](../core-model.md).

Current [OpenAI Help Center guidance](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)
places Chat and Work under ChatGPT and identifies Codex as a distinct view with
history separate from ChatGPT history. [ChatGPT Work guidance](https://learn.chatgpt.com/docs/get-started-with-work)
describes Work as delegated work to ChatGPT and an alternative to Codex for
non-coding tasks. The Playbook uses that documented persistence boundary for
adapter selection.

## Repository-bootstrap boundary

Project instructions are bootstrap and routing input, not a second copy of the
Playbook. After project bootstrap routes repository work to current
[`start-here.md`](../start-here.md), apply this adapter with the repository
floor and task-activated guidance.

Use the one copy-ready
[`global bootstrap router`](../../distributions/global-bootstrap/bootstrap-router.md)
for both hosted ChatGPT destinations: account custom instructions and CAK
project instructions. Treat them as separately installed and manually verified
surfaces, not one ambiguous configuration. The router applies the shared
[`global bootstrap persistence`](../start-here.md#global-bootstrap-persistence)
timing invariant across repositories. Do not reinterpret the router as a
per-turn retrieval requirement.

## Project and conversation context

Project instructions, project or uploaded files, conversation history, memory,
and prior hydration can help route or continue work, but do not establish the
current source boundary. Generated artifacts and Work state are derived
outputs; connected-app availability is runtime capability evidence; a
connector result is evidence only for its observed operation. Classify and use
each surface through [`core-model.md`](../core-model.md#authority-follows-the-question),
[`source-first-retrieval.md`](../source-first-retrieval.md), and, for material
prompts, [`prompt-contracts.md`](../prompt-contracts.md).

## Persistent-context activation

Repository mode may continue across Chat and Work turns. For an ordinary
repository follow-up whose task shape remains sufficient, reuse still-current
verified sources. Before adopting a strongly unrelated instruction as a task
change, apply the core model's
[`active bounded-task continuity`](../core-model.md#active-bounded-task-continuity)
guard across both Chat and Work. If the task materially changes interaction
mode, artifact, workflow, source need, execution locality, or authority
boundary, re-run the current activation route before responding, planning,
drafting, or acting. Retrieve newly activated owners without replaying
unchanged doctrine or hydrating unrelated documents. This is the
persistent-context projection of the
[activation-sufficiency invariant](../start-here.md#required-repository-invariants);
[`repo-readiness.md`](../repo-readiness.md) owns interaction-mode selection.

## Chat, Work, and execution locality

Chat and Work are task-shape and capability surfaces under this one adapter,
not separate authority contracts. A transition between them preserves
repository mode unless the task's source or boundary needs change. When Work
moves between local and cloud execution, revalidate the required sources,
working location, tools, credentials, acting identity, and mutation surface
that materially changed. Use [`repo-readiness.md`](../repo-readiness.md) for
repository execution posture and
[`maintenance-automations.md`](../maintenance-automations.md) when locality or
unattended-work guidance is activated.

### Chat-to-Work projection

Apply the shared
[`interactive-to-execution consent boundary`](../core-model.md#interactive-to-execution-transition-consent):
in this adapter, it governs Chat-to-Work transitions. Codex remains the distinct
repository executor selected through explicit delegation; authoring or
presenting a Codex prompt does not select Work.

At the action boundary, resolve these decisions in order and keep their
authority separate:

1. whether the requested task or implementation is authorized;
2. which available capability and locality can perform it, including
   Chat-local tools, a Work-only capability, or a separately delegated
   executor route; and
3. whether the operator explicitly requested Work or explicitly accepted an
   offered transition.

The first two decisions never satisfy the third. Before invoking any action
that instantiates or transitions to Work, require the third decision to supply
explicit consent. If consent is absent, invalidate the Work action even when
the task is authorized or Work is required, preferred, or a better capability
fit. Apply the shared boundary's eligible outcomes without replacing a
separately authorized executor route.

#### Chat-to-Work action qualification cases

These representative cases illustrate the action boundary above.

| Case | Task authority | Execution capability or locality | Work dependency or fit | Work transition consent | Eligible action |
| --- | --- | --- | --- | --- | --- |
| `cak-242-chat-local-operation` | `authorized` | `chat-local-sufficient` | `optional-fit` | `absent` | `execute-in-chat` |
| `cak-243-start-work` | `authorized` | `separate-executor-route` | `preferred-fit` | `absent` | `remain-in-chat-use-authorized-executor` |
| `work-only-no-consent` | `authorized` | `work-only` | `required` | `absent` | `offer-work-remain-in-chat` |
| `explicit-work-request` | `authorized` | `not-evaluated` | `selected` | `explicit-request` | `transition-to-work` |
| `accepted-work-offer` | `authorized` | `work-only` | `required` | `explicit-acceptance` | `transition-to-work` |

### Surface-role projection

Under the core
[`surface roles`](../core-model.md#interactive-and-execution-surfaces), Chat is
interactive and Work is an execution surface for bounded general-purpose
outcomes. A Codex task combines an interactive thread with a repository
execution workspace. Work returns consequential results to Chat for review and
disposition by default; Codex returns them to its interactive thread unless
another owning workflow places that authority elsewhere.

Use the shared routing, source-refresh, thin-envelope, and target-shaping rules
in
[`prompts.md`](../prompts.md#task-shape-surface-selection-and-thin-handoffs).
Work handoffs name the bounded outcome, permitted sources and tools, output
checks, and return boundary. Codex handoffs add repository locality, validation,
PR delivery, and stop-before-merge. Verify any governed package identity before
relying on it.

## Connected apps, approvals, and consequential actions

An installed or authenticated app, available action, or product approval
setting describes capability or permission behavior; it does not expand the
human-authorized task. Keep consequential writes within the authorized scope
and re-observe their result before reporting the intended effect. The shared
authority, decision-boundary, and re-observation rules remain in
[`core-model.md`](../core-model.md), while connector availability is governed
by [`start-here.md`](../start-here.md#connector-availability-is-runtime-evidence).

For routine connected-app create or write operations, invoke only the write
and the minimum verification required by the owning evidence contract. Do not
invoke preview, thumbnail, open-in-provider, or share-link actions merely to
confirm success. Preview remains appropriate when the operator explicitly
requests visual inspection, rendered correctness requires it, or a narrower
owning workflow requires it. If the client renders a card from the write action
itself, classify that as client-enforced UI, avoid redundant preview calls or
model narration, and report the limitation when material rather than claiming
the card was suppressed. Current
[OpenAI Apps guidance](https://help.openai.com/en/articles/11487775), checked
2026-09-03, documents that permission options may include `Allow all actions`
for an eligible app or account, while availability is app- and account-specific
and some safety or workspace protections still apply. Treat the effective
setting and the exact action contract as runtime evidence; this repository
cannot configure either one or infer that a general permission setting waives
a more specific action requirement.

### Recipient-Capability Prompt Presentation

Apply the shared
[`prompt delivery decision model`](../prompts.md#prompt-delivery-decision-model),
with the transport rules in
[`cross-executor prompt presentation`](../prompts.md#cross-executor-prompt-presentation).
For a qualifying small canonical-text prompt whose resolved machine recipient
is eligible under the shared model and has a permitted Airtable route, use the
shared
[`Airtable canonical-text handoff`](../prompts.md#airtable-canonical-text-handoff)
and emit its compact external envelope. Do not add file preview,
download-link, or attempt-local retrieval steps.

For a human execution recipient, use the existing
[two-block inline renderer](#prompt-presentation). If Airtable capability for a
machine recipient is unknown, inspect or attempt it before resolving the route.
Material prompts also apply the durable profile below; routine prompts do not
inherit it from transport.

Route failure and terminal blocking remain owned by the canonical decision
model. ChatGPT must preserve the owning failure reason rather than choose
another renderer.

### Airtable Connector Projection

Resolve the permitted base, table, and required field IDs through current
Airtable actions. When ChatGPT is the producer, create one record with the five
shared fields and capture the returned record ID and creation time. Use the
frozen payload length and digest in both the record and the external envelope;
never update the record after handoff.

When ChatGPT is the consumer, call the table record-list action with the exact
`recordIds` constraint from the envelope. Require exactly one returned record,
then apply the shared field, canonical-text, byte-length, and SHA-256 checks.
Do not use `search_records`, key search, or an update/upsert action for normal
retrieval.

### Issue-Owned Durable Prompt Capture And Handoff

Apply the shared
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile).
Use the same exact Airtable record and external envelope as the normal route;
the profile adds material-prompt identity and evidence requirements, not a
second storage object or delivery ceremony.

## Workspace Agents

Workspace Agents are a ChatGPT execution surface, not a second adapter.

### Trigger initiation and durable run authority

API/event and scheduled Workspace Agent runs may begin without an interactive
user turn. A published agent or channel, API token, trigger payload, schedule
instructions, prior conversation or memory, and run status are capability,
input, continuity, or execution evidence; they do not create approval or widen
task authority. Trigger data is event/run input and evidence, not automatically
authoritative source state for another system. Each run must resolve its
durable bounded authority envelope and current required sources. If a required
source, identity, connection, or authority is missing, stale, conflicting, or
mismatched, fail closed or return an explicit non-authorizing partial or
blocked result. Use [`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md), and
[`maintenance-automations.md`](../maintenance-automations.md) for the shared
authority, retrieval, and recurring-execution rules. Workspace Agents are
hosted execution when the required facts, connections, identities, and outputs
are actually provisioned there.

### Acting connection identity

Workspace Agents can use end-user connections or agent-owned/shared
connections. Keep the invoker/end user, API caller/token principal, Workspace
Agent/configuration, and downstream connected-system acting account distinct.
Tie reads, writes, source scope, attribution, and re-observation to the actual
connection identity; do not attribute an agent-owned connection action to its
invoker. Connection permissions expose or constrain capability, but do not
widen human task authority. Stop when the expected acting identity does not
match the available connection rather than silently substituting one.

### Draft, publication, and channels

Draft/Preview is candidate or test state, not proof of a published operational
agent. Publication, sharing/channel enablement, or equivalent activation is a
material operational transition requiring applicable explicit authority and
re-observation of the resulting provider state. It can make a selected
configuration callable, but does not make sources current, grant arbitrary
downstream authority, convert capability into approval, or make generated
outputs canonical. If a schedule, trigger, or channel change materially alters
future initiation, audience, source scope, identity, instructions, or possible
effects, preserve that material-transition boundary without assuming universal
republish or version mechanics. Run logs/status, memory, conversation keys,
generated artifacts, and prior results remain continuity, history, or evidence
surfaces; a completed run does not replace post-write re-observation of the
connected-system object.

## Prompt and downstream-context projection

When the task becomes prompt authoring, activate the current prompt and
orchestration owners rather than reproducing their doctrine here. Project or
controller context does not prove a downstream prompt has the same sources or
evidence. Use [`prompts.md`](../prompts.md),
[`prompt-contracts.md`](../prompt-contracts.md), and
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md) for
the applicable prompt and downstream-context contract.

### Prompt presentation

Consume the current selection from the shared
[prompt delivery decision model](../prompts.md#prompt-delivery-decision-model).
Its presentation is final input to this client projection: an Airtable route
uses the thin handoff, a blocked route renders no complete prompt, and
conceptual fragments remain lightweight.

For the canonical inline two-block presentation, emit the shared operator
metadata and complete executable prompt as two consecutive fenced blocks with
no assistant prose before, between, or after them. Keep the executable block
independently usable and represent embedded examples without nested fences.
ChatGPT-targeted prompts resolve the shared thread-name placeholder to nothing;
only a downstream adapter that explicitly supports naming may add it.

## Generated artifacts

Creating a ChatGPT artifact in Chat or Work does not make it current
authoritative state or grant publication, sharing, overwrite, or adoption
authority. Apply the derived-artifact and consequential-action boundaries in
[`core-model.md`](../core-model.md) and the material-artifact contract in
[`prompt-contracts.md`](../prompt-contracts.md) when activated.

## Scheduled and unattended execution

Scheduled or unattended ChatGPT execution must project the current automation,
source, and locality rules for each run. A standalone run cannot assume an
originating conversation; an in-chat run may use conversation as context but
not as proof of current canonical or provider state. Do not depend on an
interactive approval or unavailable local state. The governing owner is
[`maintenance-automations.md`](../maintenance-automations.md), with current
retrieval in [`source-first-retrieval.md`](../source-first-retrieval.md).

## Recovery after activation drift

If persistent context proves under-hydrated, stop continuity-based drafting or
action and re-enter current canonical routing. Retrieve the missing activated
owners, revalidate mutable sources, and replace or correct the affected
artifact as a whole before resuming. This is a ChatGPT projection of
[`source-first-retrieval.md`](../source-first-retrieval.md) and, for prompts,
[`prompts.md`](../prompts.md); it is not symptom-by-symptom repair from
conversation memory.

## Evidence and provider-reference boundary

This adapter defines Playbook behavior, not a provider guarantee about how
ChatGPT context, memory, permissions, or Work execution operates. The current
sources above establish only their documented selector, mode, and history
behavior; other client details remain runtime evidence. Re-check provider
behavior through authoritative current evidence when a task depends on it.
