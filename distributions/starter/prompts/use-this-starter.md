# Use This Starter

Copy this launcher prompt into Codex, Claude, ChatGPT, or another agent that
has access to the intended destination.

```text
You are helping me apply the AI Workflow Playbook starter.

First, retrieve and read the canonical bootstrap prompt from:
https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/main/distributions/starter/prompts/bootstrap-local-starter.md

Use that bootstrap prompt as the controlling instructions for this task. Do not
continue from memory if the URL cannot be retrieved; ask me to paste the
bootstrap prompt instead.

Destination:
- Type: [existing GitHub/GitHub Enterprise playbook repository | new GitHub/GitHub Enterprise playbook repository | existing project repository requiring .ai-workflow/ scaffolding | local-only folder]
- Repository or folder: [URL, owner/name, or path]
- Constraints: [team process, local-only future playbook repo, local-only project scaffold, unavailable PR tooling, or none]

If the destination is ambiguous, stop and ask which target to use.
```
