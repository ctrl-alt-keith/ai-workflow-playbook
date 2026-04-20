# Playbook Integrity Check

The integrity check is a lightweight periodic review to keep this repository a playbook instead of a dumping ground.

## Goal

Confirm that the repository still contains reusable guidance rather than drifting into notes, implementation, or tool sprawl.

## When To Run It

Run the check when:

- a new workflow family is proposed
- several docs were added in a short period
- a capture step produces more material than expected
- the repo starts feeling harder to navigate or easier to misuse
- a periodic maintenance pass is due

## What To Look For

Look for:

- scope drift toward project-specific implementation
- duplicated guidance that should be merged
- notebook behavior such as raw notes, scratch thinking, or incomplete fragments
- weak guidance that describes ideas without telling people how to act
- tool-specific material leaking into core docs instead of adapter docs

## Review Questions

Ask:

1. Is this content reusable across multiple projects?
2. Is it proven or necessary to explain the core model?
3. Is it specific enough to guide action?
4. Does it belong here, or in another repo?

If the answer is weak on multiple questions, the content probably does not belong in this repository in its current form.
