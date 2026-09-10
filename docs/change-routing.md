# Change Routing

Use this map to locate a workflow fix from an observed symptom or intended
change. It is navigation to existing owners, not another policy owner or an
exhaustive repository map.

**If the canonical doctrine is already correct, stop editing doctrine and
locate the enforcement, runtime, or presentation layer that actually produced
the behavior.** This applies the existing
[canonical-ownership rule](start-here.md#canonical-ownership).

| Symptom or intended change | Semantic seam | Canonical doctrine owner | Implementation / enforcement surface to inspect | Nearby wrong layer to avoid |
| --- | --- | --- | --- | --- |
| Chat → Work attempted without consent | Transition action qualification | [Core consent boundary](core-model.md#interactive-to-execution-transition-consent); [ChatGPT projection](tool-adapters/chatgpt.md#chat-to-work-projection) | The action qualifier and runtime routing/tool policy that attempted the transition, including instruction precedence | Adding consent prose when the rule is already correct; assuming every runtime defect belongs in Enforcement |
| Wrong prompt delivery route selected | Transport selection | [Delivery decision model](prompts.md#prompt-delivery-decision-model) | The concrete selector that resolves recipient, handoff boundary, and permitted route | Airtable record integrity checks or envelope formatting |
| Airtable payload identity or exact-record readback fails | Serialization and consumer verification | [Canonical-text handoff](prompts.md#airtable-canonical-text-handoff); [exact rendered bytes](prompt-contracts.md#exact-rendered-prompt-bytes) | Producer serialization/readback and consumer exact-record retrieval, re-encoding, and identity verification | External-envelope presentation |
| Airtable record verifies, but external handoff text is malformed | Envelope emission and presentation | [Cross-executor presentation](prompts.md#cross-executor-prompt-presentation); [external envelope](prompts.md#issue-owned-durable-prompt-delivery-envelope-add-on) for issue-owned material prompts | The envelope emitter or client/presentation projection that emitted/displayed the text; [terminal presentation boundary](prompts.md#current-terminal-presentation-boundary) | Changing stored payload bytes or weakening transport integrity |
| Repository bootstrap runs at the wrong time or misses sources | Startup activation and source routing | [Startup contract](start-here.md#startup-contract); [repository read order](start-here.md#repository-read-order) | The concrete bootstrap implementation and the installed/runtime instruction projection; [global-bootstrap distribution](../distributions/global-bootstrap/README.md) for its supported surfaces | Patching downstream task prompts |
| Codex selects the wrong model or launches a different selector | Executor configuration and runtime mapping | [Model routing](tool-adapters/codex.md#openai-model-and-reasoning-routing); [selector acceptance](tool-adapters/codex.md#codex-selector-routing-and-acceptance) | The concrete model selector, task-launch arguments, and runtime-reported mapping | Generic core doctrine; treating prerequisite preflight as selector qualification |
| PR merge attempted without the required human authorization | Merge action qualification | [PR readiness](repo-readiness.md#pr-readiness); [core authority](core-model.md#authority-and-transitions) | The action qualifier that makes the merge or auto-merge operation eligible | Reinterpreting GitHub capability or passing checks as permission |
| A mechanical check disagrees with accepted Playbook guidance | Doctrine-to-check conformance | [Enforcement relationship](repo-readiness.md#enforcement-relationship) | `ai-workflow-enforcement` for the selected doctrine it implements mechanically; locate the actual check through its current repository sources | Moving policy ownership into the checker or changing correct doctrine to fit drift |

The implementation column identifies an inspection surface, not a verified
file location or a claim that the surface is locally editable. Resolve exact
implementation placement through the owning repository's current `AGENTS.md`
and sources, or the responsible provider/runtime's current evidence, under
[source-first retrieval](source-first-retrieval.md#minimum-sufficient-retrieval).
An unresolved implementation owner stays unknown; a repository role in the
[ecosystem overview](ai-workflow-ecosystem.md#current-repository-implementation-roles)
does not identify every selector or renderer.

Navigation grants no mutation or transition authority; the existing
[interaction mode and authority boundary](repo-readiness.md#interaction-mode-preflight)
still controls the next action.
