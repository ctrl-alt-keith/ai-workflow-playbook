# AI Workflow Playbook Bootstrap

When a conversation already has an active bounded task, do not treat a
strongly unrelated instruction without a clear transition signal as a material
task or repository change. Preserve the active task, ask whether to switch or
continue, and make no task-owned or durable mutation for the unrelated request
until the operator's intent is resolved. Ordinary task-local steering and
clear task switches proceed normally.

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
