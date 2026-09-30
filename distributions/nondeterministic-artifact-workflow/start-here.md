# Start here: make and approve an artifact in ChatGPT Work

This guide is for someone making a product photo or another visual artifact
from their own files. You bring the originals and decide what is true to the
subject. ChatGPT Work helps make several options, saves each one, and handles
the file work. You choose what is worth finishing and approve one exact final
file. Nothing is published by this workflow.

## Set up once

1. Connect a durable place you are authorized to use to ChatGPT Work, such as
   your work Dropbox. Make sure Work can open the **original files** and save
   files there. Follow your organization's rules for private material and AI
   tools.
2. Create or choose one folder as your **workspace root**. It can be a new
   folder or an existing project folder. Keep the originals and results there
   so you can find them later. Work can help create the subfolders below.
3. Save copies of [task-contract.md](task-contract.md) and
   [work-launcher.md](work-launcher.md) where you can reach them from Work.
   The contract describes one job; the launcher tells Work how to run it.

This folder layout is suggested, not required. If you already have a useful
layout, write your actual folder names in the contract. Use the same job name
for its sources, contract, candidates, and review note.

```text
Your workspace root/
  01 Sources/<job>/         original files for this job
  02 Contracts/<job>.md     this job's filled-in contract
  03 Candidates/<job>/      saved options and finished versions
  04 Accepted Masters/     final files you have approved
  05 Review Notes/<job>.md  choices, feedback, and approval record
```

## For each new job

1. **Add the originals.** Put the source files in `01 Sources/<job>/` under
   your workspace root. Keep them untouched. A photo, background, detail shot,
   or other reference can each have a different role.
2. **Fill in a contract.** Copy `task-contract.md` to
   `02 Contracts/<job>.md`. Write what you want, which real details must
   remain accurate, what may change, what must never change, and how many
   options Work may make. Name the source files and their roles. You can use
   ordinary words: Work can look up file identities and fill in technical
   fields, but it must confirm the actual originals before generating anything.
   Include any output size or format you need, which tools Work may use, any
   privacy limits, and who can approve the result.
3. **Start Work.** Attach the completed contract and an unfilled copy of the
   [Work launcher](work-launcher.md), then use the first-run prompt below. Work
   uses the launcher as instructions and takes its bracketed details from your
   contract; you do not need to send it as a second prompt. If Work cannot
   reach an original file or the connected store, resolve that before
   proceeding. If you use the launcher as your prompt instead, fill in its
   brackets before sending it.
4. **Review the saved options.** Work should save each generated candidate as
   a separate file and show you the actual saved results. Compare them with
   the real subject and the contract. Tell Work what is right or wrong. You
   may choose a promising candidate, ask for another option within your stated
   limits, or stop. Choosing a candidate is not final approval.
5. **Finish the chosen file.** If it needs a mechanical change such as resizing
   or converting the format, tell Work exactly what to do. Work saves a new
   finished file and checks its size and format. If the subject itself needs to
   change, ask for a new candidate and review it again.
6. **Approve the exact master.** Open the finished file itself, check the
   subject and output requirements, and tell Work which **exact file** you
   approve and for what use. Work can then move that same verified file into
   `04 Accepted Masters/` without replacing anything already there. It should
   read the moved file back and record the result in `05 Review Notes/<job>.md`.
   If it cannot confirm the moved file is the approved one, hold it for your
   review.

If you do not approve the final file, it stays a candidate. Approval to keep
an exact master does not also approve publication.

## Feedback Work can use

- “The lighting is good, but the handle shape is wrong. Keep the handle as it
  appears in the original detail photo.”
- “Option 2 has the right product. Please make the background less busy while
  keeping the product unchanged.”
- “I choose option 3. Resize it to a 2050 × 2050 PNG, save a new file, and show
  me that finished file before I approve it.”
- “I approve the finished file named `rod-final-v1.png` that you just showed
  me for the product listing. Move that exact file to Accepted Masters.”

Be specific about the visible difference and, when possible, which original
shows the correct detail. You do not need special prompt wording.

## Keep in mind

- An image generator may ignore a requested size. Check the **saved** image's
  dimensions. Work can resize a selected candidate afterward if that is an
  allowed finishing step.
- A beautiful image is not acceptable if it misrepresents the physical product
  or breaks another protected detail. Compare the result with the real thing.
- Keep every candidate. Work should make a new file for each attempt and never
  overwrite an earlier option or an accepted master.
- A preview, thumbnail, or shared link may not be the original file. Work must
  use the actual source files from your connected store.

You should not have to calculate hashes, track file identities, or maintain
bookkeeping by hand. Work handles those checks and records, then tells you
plainly if it cannot verify a file or move. Your decisions are about the
subject, the chosen result, and approval of the final file.

## First-run prompt

Attach your filled-in contract and an unfilled copy of `work-launcher.md` to a
ChatGPT Work message, then copy this prompt. The contract names your connected
store and workspace root, so this prompt does not need a personal account path.

```text
Please help me run the one artifact job in the completed task contract attached
to this message. Use the connected store and workspace root named in that
contract. Follow the work-launcher.md workflow supplied with the contract.
Use the task name, store, workspace root, and run limits from my contract for
the launcher's bracketed details; the launcher is reference instructions, not
a second task.

First, confirm that you can read the original source files in my store and
save and read back files under that workspace root. Fill in any source file
identities or other technical record fields you can verify. If a required
original, permission, or detail is missing, stop and tell me what you need.

Then make only the candidate options allowed by my contract. Save each as a
separate file, show me the saved results, and stop for my review. Wait for me
to choose any finishing steps and, later, to approve one exact final file
before moving it into Accepted Masters. Do not publish anything.
```

## Share feedback

If this workflow is confusing, breaks, or gives you an idea others could use,
you can [open a GitHub issue](https://github.com/ctrl-alt-keith/ai-workflow-playbook/issues/new).
It helps to include what you were trying to do, where you got stuck or what
behaved unexpectedly, which step or file was involved, and any non-sensitive
screenshots or example text that would make the problem clearer. You do not
need to know how the Playbook works internally.
