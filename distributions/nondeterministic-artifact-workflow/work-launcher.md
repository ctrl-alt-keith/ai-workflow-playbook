# Work launcher — copy with a completed task contract

Use this with a tool-capable ChatGPT Work session that has access to your
authorized connected durable store. Replace the bracketed values and attach or
point to the completed contract. The human's current instruction and local storage
policy control what the session may do.

```text
Help me run one bounded artifact task using my completed task contract:
[attach contract or give its exact path/identity].

Connected store: [my authorized store]
Workspace root in that store: [my root folder]
Task name: [name]
This run's authorization and limits: [specific permitted work, providers,
candidate count, and any privacy/retention limits].

Read the current contract and resolve every named source to its original
binary in the connected store. Confirm source identities/versions and stage
those exact bytes in your execution context. Do not use a preview, thumbnail,
link target, inferred file, or conversational copy in place of the source.
If exact access, authority, or a required provider capability is missing,
stop and tell me what is missing. Do not guess or switch accounts/providers.

Generate only the authorized candidate attempts. Treat generation as
nondeterministic. Save each output as a new file in the contract's Candidates
folder for this task; never overwrite a prior attempt or an existing master.
Record each candidate's
source/contract reference, unique file identity, and digest when verifiable.
Read back each saved result where the store permits, report what was actually
verified, and keep uncertain writes on hold rather than blindly retrying.

Show me the saved candidates and a short comparison against protected truth,
prohibited changes, and allowed variation. Stop for my semantic review. Do
not infer approval from generation success, validation, or my preference for
one candidate.

After I select a candidate and authorize named finishing steps, apply only
deterministic finishing to that exact candidate. Save a new derivative without
overwriting the candidate; verify its specified mechanical properties and
record its lineage and exact identity. If a semantic change is needed, create
a new candidate and return to review.

Stop again for my approval of the exact final derivative or candidate and its
intended use. Only after that approval, move that same verified file to
the contract's Accepted Masters folder without replacing an existing file.
Read it back, confirm byte continuity or report that continuity is unverified,
and update
the contract's Review Notes file for this task with the approval, old and new
locators/identities, and any unresolved status. Do not publish or infer
publication permission.
```
