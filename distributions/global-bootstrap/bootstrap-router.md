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

After successful bootstrap, before qualifying an action that would instantiate
or transition to another execution surface, apply the current
`docs/core-model.md` interactive-to-execution transition-consent boundary and
the matching tool adapter. Explicit operator request for that surface, or
explicit acceptance of an offered transition, is a hard eligibility
prerequisite.

When consent is absent, remove the transition action from the eligible action
set before task-shape, capability, locality, or preferred-fit ranking. Use a
sufficient capability on the current surface, or offer the required surface
and remain on the current surface. Task authority, repository or file work,
mutation, browser use, coding, complexity, capability fit, and the availability
of a transition action never supply transition consent.
