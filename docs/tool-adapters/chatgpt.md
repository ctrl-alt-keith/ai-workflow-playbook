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
Playbook. After the CAK-108 project bootstrap has routed repository work to the
current [`start-here.md`](../start-here.md), apply this adapter with the
repository floor and the task-activated guidance.

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
verified sources. If the task materially changes interaction mode, artifact,
workflow, source need, execution locality, or authority boundary, re-run the
current activation route before responding, planning, drafting, or acting.
Retrieve newly activated owners without replaying unchanged doctrine or
hydrating unrelated documents. This is the persistent-context projection of
the [activation-sufficiency invariant](../start-here.md#required-repository-invariants);
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

### Interactive control-plane projection

Chat is the normal interactive control plane for human-led clarification,
scoping, authority decisions, decomposition, steering, review, and disposition.
Work is the preferred ChatGPT surface for a bounded general-purpose multi-step
outcome or non-repository deliverable. Codex is the preferred distinct
repository-oriented executor when completion materially depends on repository
locality, terminal commands, tests, Git, worktrees, commits, pull requests, or
code review. Hard reasoning may remain in Chat while the task is still
interactive; difficulty, model tier, or reasoning setting does not select Work
or Codex.

Use the shared routing, source-refresh, thin-envelope, and target-shaping rules
in
[`prompts.md`](../prompts.md#task-shape-surface-selection-and-thin-handoffs).
For a Work handoff, project the bounded outcome, permitted connected sources
and tools, output checks, and return-to-Chat boundary. For a Codex handoff, add
the exact repository locality, repository tools, canonical validation, PR
delivery, and stop-before-merge boundary. When either handoff points to a
governed package, verify its exact identity through the connected app before
relying on it; a mutable folder or conversation memory is not a substitute.

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

When the current Dropbox `create_folder` or `create_file` action contract, as
observed 2026-09-03, unconditionally requires the assistant to present the
exact mutation plan and obtain explicit confirmation in chat, that contract
owns the prerequisite for the attempt. The original `prompt me` request
remains sufficient task authorization under the Playbook, but it precedes the
required plan and therefore cannot satisfy that post-plan connector
confirmation. Apply the shared pilot's
existing `BLOCKED` and correction path until the prerequisite is satisfied;
do not reinterpret the interruption as missing task authority, add another
approval gate, or switch the machine recipient to inline prompt delivery.

### Recipient-Capability Prompt Presentation

Apply the complete shared
[`prompt delivery decision model`](../prompts.md#prompt-delivery-decision-model),
with the transport rules in
[`cross-executor prompt presentation`](../prompts.md#cross-executor-prompt-presentation).
Apply its shared
[`prompt freeze and transport-only latch`](../prompts.md#prompt-freeze-and-transport-only-latch)
without restating their state, evidence, or action mappings here. ChatGPT
consumes the frozen decision record and projects only its selected connector
actions and response surface.

For a machine execution recipient with qualified Dropbox retrieval and a
permitted destination, the model selects `file-backed` presentation. This
includes `qualified-with-known-limitation`: retain and report the diagnostic,
but do not reinterpret it as route disqualification. Use the authorized file
route, present the card produced by the write when available, and immediately
provide the target-shaped handoff. A separate preview or open action remains
optional under the connected-app rules above. Do not wait for prompt approval
or require the operator to open a preview. If the selected create action has
the post-plan confirmation contract described above, pause on that external
prerequisite and resume the shared transport path after it is satisfied;
confirmation authorizes only its file operation. File-card and preview behavior
is product-dependent runtime evidence, so recheck the relevant action.

For the explicitly activated CAK-209 normal-use Codex trial, ChatGPT applies the
shared
[`Issue-Owned File-Backed Handoff Prose-DAG Pilot`](../prompts.md#issue-owned-file-backed-handoff-prose-dag-pilot)
and presents its transition receipts as operator-visible metadata outside the
receiver's copyable handoff.

For a human execution recipient, or a machine execution recipient whose
inspected capability state permits inline fallback, the model selects `inline`
presentation and the existing
[two-block inline renderer](#prompt-presentation). If access is unknown,
inspect or attempt it before resolving the route. Material prompts also apply
the durable profile below; routine prompts do not inherit it from transport.

Route failure, bounded capability re-evaluation, fallback, and terminal
blocking remain owned by the canonical decision model. ChatGPT must preserve
the current record and owning failure reason rather than reinterpret a
diagnostic, repeat re-entry, or choose another renderer.

### Dropbox Preview And Minimal Executor Handoff

When optional operator preview is selected, complete the shared pre-link checks,
then call Dropbox `file_preview` with `file_paths` containing the exact
`file_id` returned by the write. Use the exact returned namespace path only
when no file ID is available; never strip its namespace prefix. Present the
tool-produced widget before the final `download_link` call.

The preview call and connector metadata are not a visibly rendered preview.
Do not substitute `open_in_dropbox_url`, copy or share links, thumbnail URLs,
or metadata for the widget, and claim visible rendering only when the operator
actually sees it. Preview remains optional and does not gate the handoff.

Keep the complete prompt in Dropbox. Outside the optional widget, emit only the
normal concise operator metadata and one compact retrieval, verification, and
execution bootstrap shown below; do not summarize or reproduce the prompt.

Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]

Recommended model: [model]

Recommended reasoning level: [level]

Reason:
[one concise task-specific explanation]

```text
Download: [fresh single-use raw-download URL]
Dropbox ID: [exact returned file ID]
Attempt directory basename: prompt-retrieval.XXXXXXXX
Local filename: prompt.md
Expected bytes: [byte count]
Expected SHA-256: [digest]
Execute: Download exactly once with a direct argv/process invocation into the qualified private attempt-local directory, verify the exact identity, byte count, and SHA-256, then execute the complete prompt file.
Stop: Fail closed on retrieval, identity, size, or SHA-256 mismatch. Do not reconstruct the prompt from chat.
```

### Issue-Owned Durable Prompt Capture And Handoff

Apply the shared
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile).
For Dropbox's qualified provider-checksum route, compute `content_hash` from
the frozen rendered bytes using Dropbox's documented algorithm. Apply the
owning storage contract's absent-create and collision rules; extracted
connector text is not exact-byte readback.

After the shared pre-link identity, path, containment, and revision checks,
optionally preview the file, then call `download_link` once. Its returned file
ID, path, stored size, and `content_hash` complete the provider-integrity
comparison. Report `PRESERVED` only after they match, leave the same non-empty
URL unconsumed for the executor, and otherwise use the shared raw-readback
fallback. The qualified checksum route performs no controller verification
content download.

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

Consume only the current frozen record from the shared
[prompt delivery decision model](../prompts.md#prompt-delivery-decision-model).
Its presentation and renderer selections are final inputs to this client
projection: `file-backed` uses the thin handoff, `blocked` renders no complete
prompt, and conceptual fragments remain lightweight.

For `inline` plus `canonical-inline-two-block`, emit the shared operator
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
