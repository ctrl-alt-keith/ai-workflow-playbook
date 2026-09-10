# AI Workflow Playbook Bootstrap

When a conversation already has an active bounded task, apply the current
active bounded-task continuity guard before treating a strongly unrelated
instruction as a material task or repository change.

Before the first project action, and again only when the task/repository
materially changes, retrieve the current `docs/start-here.md` from
`ctrl-alt-keith/ai-workflow-playbook` and follow its routing and startup
instructions. Treat this as mandatory bootstrap, not background guidance.
After successful bootstrap, reuse the still-current repository operating mode
and verified sources across subsequent turns; do not retrieve `start-here.md`
again merely because the conversation continues or another tool is invoked.
When the first-action or material-change trigger applies, retrieving and applying
`start-here.md` is the only permitted action: Do not respond, reason about the
task, or invoke another tool before applying it. If it cannot be retrieved or
read, the only permitted response is to say so plainly and stop; do not proceed
from memory.

## Execution-Surface Transition Eligibility

After successful bootstrap, apply the `docs/core-model.md`
interactive-to-execution transition-consent boundary and any narrower matching
adapter before qualifying a transition to another execution surface. Require
an explicit operator request for that surface or explicit acceptance of an
offered transition; without it, the transition action is ineligible.

## Airtable Envelope Eligibility

When Airtable handoff transport is selected, before selecting presentation or
constructing an external envelope, apply the `docs/prompts.md`
Airtable canonical-text handoff contract. Envelope construction and emission
remain ineligible until exact-record readback and independent identity
verification succeed for that producer attempt; record creation alone does not
qualify them.
