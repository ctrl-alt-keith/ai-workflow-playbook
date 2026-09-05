# Support triage guide

Experimental shadow preview. Existing Playbook prose controls.
Incomplete executor contract; no live use or adoption.

Input commit: `35241049177c16619761195d393913707dedb5e0`.

Source status: frozen mapped baseline.

Exact producing identities: `77f018ecc65b98acd671c196b8afcd423c9bd4310c8960e655bdf4c30a855550` (see provenance.json).

## Navigation

- Work began without startup context: [view clause](#pbstartup-floor)
- Unsure which guidance applies: [view clause](#pbconditional-activation)
- Follow-up appears to repeat or skip startup: [view clause](#pbmode-persistence)
- A summary is being treated as current state: [view clause](#pbretrieval-triggers)
- A readiness answer has missing evidence: [view clause](#pbclaim-verification)
- A source lookup was rejected or never performed: [view clause](#pbretrieval-recovery)

## Symptom routing

These entry points are navigation. Applicability and authority remain unresolved where the clauses say so.

### Work began without startup context

Applicability: conditional.

Escalation question: What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

[Failure and permitted recovery](#pbstartup-floorfailure) · [Required action](#pbstartup-flooreffect)

### Unsure which guidance applies

Applicability: conditional.

Escalation question: What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

[Failure and permitted recovery](#pbconditional-activationfailure) · [Required action](#pbconditional-activationeffect)

### Follow-up appears to repeat or skip startup

Applicability: conditional.

Escalation question: What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

[Failure and permitted recovery](#pbmode-persistencefailure) · [Required action](#pbmode-persistenceeffect)

### A summary is being treated as current state

Applicability: conditional.

Escalation question: What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

[Failure and permitted recovery](#pbretrieval-triggersfailure) · [Required action](#pbretrieval-triggerseffect)

### A readiness answer has missing evidence

Applicability: conditional.

Escalation question: What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

[Failure and permitted recovery](#pbclaim-verificationfailure) · [Required action](#pbclaim-verificationeffect)

### A source lookup was rejected or never performed

Applicability: conditional.

Escalation question: What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

[Failure and permitted recovery](#pbretrieval-recoveryfailure) · [Required action](#pbretrieval-recoveryeffect)


## pb.claim-verification

Applicability: conditional.
Selection: conditional; pb.retrieval-triggers:activates.

### pb.claim-verification/when

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/when -->
is:

- fact.mandatory_trigger
- true
<!-- end:pb.claim-verification/when -->

### pb.claim-verification/authority_ref

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/authority_ref -->
source:

source.readiness

question:

What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

check at:

immediately-before-action
<!-- end:pb.claim-verification/authority_ref -->

### pb.claim-verification/failure

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/failure -->
when:

is:

- fact.verification_complete
- false

action:

action.claim-verification-failure

alternatives:

(explicitly empty)

scope:

Readiness, mergeability, approval, closure or implementation-completeness claims
<!-- end:pb.claim-verification/failure -->

### pb.claim-verification/effect

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/effect -->
actor:

controller

modality:

must

action:

action.claim-verification

parameters:

operation:

current-operation
<!-- end:pb.claim-verification/effect -->

### pb.claim-verification/completion

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/completion -->
evidence:

evidence.claim-verification

boundary:

boundary.claim-verification

question:

Were the unit and all required external owners applied sufficiently? This remains controller judgment.
<!-- end:pb.claim-verification/completion -->

### pb.claim-verification/lifetime

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/lifetime -->
starts:

When a mandatory retrieval trigger is present

persists within:

Claim-specific verified/partial/blocked evidence boundary

ends when:

any:

- is:
  
  - fact.leaves_repository_work
  - true
- is:
  
  - fact.repository_changed
  - true
<!-- end:pb.claim-verification/lifetime -->

### pb.claim-verification/before

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/before -->
- boundary.claim-verification
<!-- end:pb.claim-verification/before -->

### pb.claim-verification/activates

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/activates -->
(explicitly empty)
<!-- end:pb.claim-verification/activates -->

### pb.claim-verification/overrides

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/overrides -->
(explicitly empty)
<!-- end:pb.claim-verification/overrides -->

### pb.claim-verification/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/owner -->
source.retrieval
<!-- end:pb.claim-verification/owner -->

### pb.claim-verification/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/references -->
(explicitly empty)
<!-- end:pb.claim-verification/references -->

### pb.claim-verification/requires

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/requires -->
- source.retrieval
- source.core
- source.review
<!-- end:pb.claim-verification/requires -->

### pb.claim-verification/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/status -->
active
<!-- end:pb.claim-verification/status -->

### pb.claim-verification/unit

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.claim-verification/unit -->
pb.claim-verification
<!-- end:pb.claim-verification/unit -->


## pb.conditional-activation

Applicability: conditional.
Selection: conditional; pb.mode-persistence:requires.

### pb.conditional-activation/when

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/when -->
is:

- fact.repository_work
- true
<!-- end:pb.conditional-activation/when -->

### pb.conditional-activation/authority_ref

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/authority_ref -->
source:

source.readiness

question:

What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

check at:

immediately-before-action
<!-- end:pb.conditional-activation/authority_ref -->

### pb.conditional-activation/failure

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/failure -->
when:

is:

- fact.source_available
- false

action:

action.conditional-activation-failure

alternatives:

(explicitly empty)

scope:

Affected analysis or artifact
<!-- end:pb.conditional-activation/failure -->

### pb.conditional-activation/effect

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/effect -->
actor:

controller

modality:

must

action:

action.conditional-activation

parameters:

operation:

current-operation
<!-- end:pb.conditional-activation/effect -->

### pb.conditional-activation/completion

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/completion -->
evidence:

evidence.conditional-activation

boundary:

boundary.conditional-activation

question:

Were the unit and all required external owners applied sufficiently? This remains controller judgment.
<!-- end:pb.conditional-activation/completion -->

### pb.conditional-activation/lifetime

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/lifetime -->
starts:

At startup and material changes

persists within:

Still-current floor plus newly activated owners

ends when:

any:

- is:
  
  - fact.leaves_repository_work
  - true
- is:
  
  - fact.repository_changed
  - true
<!-- end:pb.conditional-activation/lifetime -->

### pb.conditional-activation/before

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/before -->
- boundary.conditional-activation
<!-- end:pb.conditional-activation/before -->

### pb.conditional-activation/activates

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/activates -->
- target:
  
  source.maintenance
  
  when:
  
  is:
  
  - fact.maintenance_scope
  - true
- target:
  
  source.lifecycle
  
  when:
  
  is:
  
  - fact.feature_delivery_current
  - true
- target:
  
  source.ecosystem
  
  when:
  
  is:
  
  - fact.cross_repository_scope
  - true
- target:
  
  source.interfaces
  
  when:
  
  is:
  
  - fact.cross_repository_scope
  - true
- target:
  
  source.glossary
  
  when:
  
  is:
  
  - fact.cross_repository_scope
  - true
<!-- end:pb.conditional-activation/activates -->

### pb.conditional-activation/overrides

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/overrides -->
(explicitly empty)
<!-- end:pb.conditional-activation/overrides -->

### pb.conditional-activation/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/owner -->
source.start
<!-- end:pb.conditional-activation/owner -->

### pb.conditional-activation/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/references -->
(explicitly empty)
<!-- end:pb.conditional-activation/references -->

### pb.conditional-activation/requires

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/requires -->
- source.start
<!-- end:pb.conditional-activation/requires -->

### pb.conditional-activation/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/status -->
active
<!-- end:pb.conditional-activation/status -->

### pb.conditional-activation/unit

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.conditional-activation/unit -->
pb.conditional-activation
<!-- end:pb.conditional-activation/unit -->


## pb.mode-persistence

Applicability: conditional.
Selection: conditional.

### pb.mode-persistence/when

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/when -->
is:

- fact.startup_succeeded
- true
<!-- end:pb.mode-persistence/when -->

### pb.mode-persistence/authority_ref

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/authority_ref -->
source:

source.readiness

question:

What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

check at:

immediately-before-action
<!-- end:pb.mode-persistence/authority_ref -->

### pb.mode-persistence/failure

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/failure -->
when:

is:

- fact.source_available
- false

action:

action.mode-persistence-failure

alternatives:

(explicitly empty)

scope:

Affected conclusion or artifact after activation changes
<!-- end:pb.mode-persistence/failure -->

### pb.mode-persistence/effect

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/effect -->
actor:

controller

modality:

must

action:

action.mode-persistence

parameters:

operation:

current-operation
<!-- end:pb.mode-persistence/effect -->

### pb.mode-persistence/completion

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/completion -->
evidence:

evidence.mode-persistence

boundary:

boundary.mode-persistence

question:

Were the unit and all required external owners applied sufficiently? This remains controller judgment.
<!-- end:pb.mode-persistence/completion -->

### pb.mode-persistence/lifetime

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/lifetime -->
starts:

Successful complete repository startup

persists within:

Repository conventions; never frozen mutable facts or activated source set

ends when:

any:

- any:
  
  - is:
    
    - fact.leaves_repository_work
    - true
  - is:
    
    - fact.repository_changed
    - true
- is:
  
  - fact.human_style_override
  - true
<!-- end:pb.mode-persistence/lifetime -->

### pb.mode-persistence/before

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/before -->
- boundary.mode-persistence
<!-- end:pb.mode-persistence/before -->

### pb.mode-persistence/activates

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/activates -->
(explicitly empty)
<!-- end:pb.mode-persistence/activates -->

### pb.mode-persistence/overrides

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/overrides -->
(explicitly empty)
<!-- end:pb.mode-persistence/overrides -->

### pb.mode-persistence/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/owner -->
source.start
<!-- end:pb.mode-persistence/owner -->

### pb.mode-persistence/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/references -->
(explicitly empty)
<!-- end:pb.mode-persistence/references -->

### pb.mode-persistence/requires

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/requires -->
- pb.startup-floor
- pb.conditional-activation
<!-- end:pb.mode-persistence/requires -->

### pb.mode-persistence/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/status -->
active
<!-- end:pb.mode-persistence/status -->

### pb.mode-persistence/unit

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.mode-persistence/unit -->
pb.mode-persistence
<!-- end:pb.mode-persistence/unit -->


## pb.retrieval-recovery

Applicability: conditional.
Selection: conditional.

### pb.retrieval-recovery/when

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/when -->
is:

- fact.retrieval_missed
- true
<!-- end:pb.retrieval-recovery/when -->

### pb.retrieval-recovery/authority_ref

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/authority_ref -->
source:

source.readiness

question:

What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

check at:

immediately-before-action
<!-- end:pb.retrieval-recovery/authority_ref -->

### pb.retrieval-recovery/failure

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/failure -->
when:

is:

- fact.source_available
- false

action:

action.retrieval-recovery-failure

alternatives:

(explicitly empty)

scope:

Recovery-dependent conclusion
<!-- end:pb.retrieval-recovery/failure -->

### pb.retrieval-recovery/effect

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/effect -->
actor:

controller

modality:

must

action:

action.retrieval-recovery

parameters:

operation:

current-operation
<!-- end:pb.retrieval-recovery/effect -->

### pb.retrieval-recovery/completion

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/completion -->
evidence:

evidence.retrieval-recovery

boundary:

boundary.retrieval-recovery

question:

Were the unit and all required external owners applied sufficiently? This remains controller judgment.
<!-- end:pb.retrieval-recovery/completion -->

### pb.retrieval-recovery/lifetime

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/lifetime -->
starts:

Missed mandatory source-first ordering

persists within:

Recovery obligation until retrieval and correction are complete

ends when:

all:

- is:
  
  - fact.retrieval_missed
  - false
- is:
  
  - fact.verification_complete
  - true
<!-- end:pb.retrieval-recovery/lifetime -->

### pb.retrieval-recovery/before

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/before -->
- boundary.retrieval-recovery
<!-- end:pb.retrieval-recovery/before -->

### pb.retrieval-recovery/activates

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/activates -->
(explicitly empty)
<!-- end:pb.retrieval-recovery/activates -->

### pb.retrieval-recovery/overrides

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/overrides -->
(explicitly empty)
<!-- end:pb.retrieval-recovery/overrides -->

### pb.retrieval-recovery/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/owner -->
source.retrieval
<!-- end:pb.retrieval-recovery/owner -->

### pb.retrieval-recovery/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/references -->
- pb.claim-verification
<!-- end:pb.retrieval-recovery/references -->

### pb.retrieval-recovery/requires

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/requires -->
- source.retrieval
- source.start
- source.codex
<!-- end:pb.retrieval-recovery/requires -->

### pb.retrieval-recovery/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/status -->
active
<!-- end:pb.retrieval-recovery/status -->

### pb.retrieval-recovery/unit

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-recovery/unit -->
pb.retrieval-recovery
<!-- end:pb.retrieval-recovery/unit -->


## pb.retrieval-triggers

Applicability: conditional.
Selection: conditional.

### pb.retrieval-triggers/when

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/when -->
is:

- fact.repository_work
- true
<!-- end:pb.retrieval-triggers/when -->

### pb.retrieval-triggers/authority_ref

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/authority_ref -->
source:

source.readiness

question:

What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

check at:

immediately-before-action
<!-- end:pb.retrieval-triggers/authority_ref -->

### pb.retrieval-triggers/failure

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/failure -->
when:

is:

- fact.source_available
- false

action:

action.retrieval-triggers-failure

alternatives:

(explicitly empty)

scope:

Stateful reasoning
<!-- end:pb.retrieval-triggers/failure -->

### pb.retrieval-triggers/effect

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/effect -->
actor:

controller

modality:

must

action:

action.retrieval-triggers

parameters:

operation:

current-operation
<!-- end:pb.retrieval-triggers/effect -->

### pb.retrieval-triggers/completion

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/completion -->
evidence:

evidence.retrieval-triggers

boundary:

boundary.retrieval-triggers

question:

Were the unit and all required external owners applied sufficiently? This remains controller judgment.
<!-- end:pb.retrieval-triggers/completion -->

### pb.retrieval-triggers/lifetime

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/lifetime -->
starts:

Before continuity reasoning about current repository facts

persists within:

Source ownership and mandatory retrieval checks for the current claim

ends when:

any:

- is:
  
  - fact.leaves_repository_work
  - true
- is:
  
  - fact.repository_changed
  - true
<!-- end:pb.retrieval-triggers/lifetime -->

### pb.retrieval-triggers/before

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/before -->
- boundary.retrieval-triggers
<!-- end:pb.retrieval-triggers/before -->

### pb.retrieval-triggers/activates

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/activates -->
- target:
  
  pb.claim-verification
  
  when:
  
  is:
  
  - fact.mandatory_trigger
  - true
<!-- end:pb.retrieval-triggers/activates -->

### pb.retrieval-triggers/overrides

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/overrides -->
(explicitly empty)
<!-- end:pb.retrieval-triggers/overrides -->

### pb.retrieval-triggers/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/owner -->
source.retrieval
<!-- end:pb.retrieval-triggers/owner -->

### pb.retrieval-triggers/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/references -->
(explicitly empty)
<!-- end:pb.retrieval-triggers/references -->

### pb.retrieval-triggers/requires

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/requires -->
- source.retrieval
<!-- end:pb.retrieval-triggers/requires -->

### pb.retrieval-triggers/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/status -->
active
<!-- end:pb.retrieval-triggers/status -->

### pb.retrieval-triggers/unit

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:pb.retrieval-triggers/unit -->
pb.retrieval-triggers
<!-- end:pb.retrieval-triggers/unit -->


## pb.startup-floor

Applicability: conditional.
Selection: conditional; pb.mode-persistence:requires.

### pb.startup-floor/when

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/when -->
is:

- fact.repository_work
- true
<!-- end:pb.startup-floor/when -->

### pb.startup-floor/authority_ref

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/authority_ref -->
source:

source.readiness

question:

What does current human direction authorize for operation=current-operation? Resolve external interaction-mode and action-latch, plus source-specific restrictions.

check at:

immediately-before-action
<!-- end:pb.startup-floor/authority_ref -->

### pb.startup-floor/failure

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/failure -->
when:

is:

- fact.startup_ready
- false

action:

action.startup-floor-failure

alternatives:

(explicitly empty)

scope:

Repository-scoped action
<!-- end:pb.startup-floor/failure -->

### pb.startup-floor/effect

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/effect -->
actor:

controller

modality:

must

action:

action.startup-floor

parameters:

operation:

current-operation
<!-- end:pb.startup-floor/effect -->

### pb.startup-floor/completion

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/completion -->
evidence:

evidence.startup-floor

boundary:

boundary.startup-floor

question:

Were the unit and all required external owners applied sufficiently? This remains controller judgment.

when:

is:

- fact.startup_succeeded
- true
<!-- end:pb.startup-floor/completion -->

### pb.startup-floor/lifetime

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/lifetime -->
starts:

Entry before repository-scoped action

persists within:

Complete target-specific startup floor and task-activated owners

ends when:

any:

- is:
  
  - fact.leaves_repository_work
  - true
- is:
  
  - fact.repository_changed
  - true
<!-- end:pb.startup-floor/lifetime -->

### pb.startup-floor/before

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/before -->
- boundary.startup-floor
<!-- end:pb.startup-floor/before -->

### pb.startup-floor/activates

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/activates -->
(explicitly empty)
<!-- end:pb.startup-floor/activates -->

### pb.startup-floor/overrides

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/overrides -->
(explicitly empty)
<!-- end:pb.startup-floor/overrides -->

### pb.startup-floor/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/owner -->
source.start
<!-- end:pb.startup-floor/owner -->

### pb.startup-floor/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/references -->
(explicitly empty)
<!-- end:pb.startup-floor/references -->

### pb.startup-floor/requires

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/requires -->
- source.start
- source.core
- source.baseline
- source.agents
- source.readiness
- source.retrieval
- source.codex
- source.claude
- source.chatgpt
<!-- end:pb.startup-floor/requires -->

### pb.startup-floor/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/status -->
active
<!-- end:pb.startup-floor/status -->

### pb.startup-floor/unit

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:pb.startup-floor/unit -->
pb.startup-floor
<!-- end:pb.startup-floor/unit -->

## Owned vocabulary

### action.claim-verification/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/action_kind -->
behavior
<!-- end:action.claim-verification/action_kind -->

### action.claim-verification/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/does -->
Use this gate whenever a mandatory trigger is present:

- Trigger: name the artifact or request that activated retrieval.

- Source: name the authoritative source used for current state.

- Checks: list the state checks required by the task.

- Result: mark the gate `verified`, `partial`, or `blocked`.

- Unknowns: state anything required for the task that remains unverified.

If direct verification did not happen, say exactly:
`unknown → referenced repo state was not verified`.

Acceptable authoritative sources depend on the claim:

- Repository files, local `git` state, and checked-out refs are authoritative
  for the inspected local worktree only.

- GitHub PRs, issues, review threads, CI, mergeability, and branch metadata are
  authoritative for current remote PR and issue state.

- CI systems and validation command output are authoritative for the checks
  they actually ran.

- Official provider documentation, schemas, SDK docs, CLI docs, changelogs, or
  release notes are authoritative for external public API behavior.

For pull requests and issues, do not infer implementation quality, scope, risk,
merge readiness, or correctness from titles, summaries, commit messages,
reported check status, or conversational descriptions. Inspect changed files,
validation or check state, scope boundaries, and overlap or conflict risk
directly.

If the required source is unavailable, blocked, or access is declined, stop the
stateful workflow and report the blocker. Do not provide readiness,
mergeability, approval, closure, or implementation-completeness conclusions
from secondhand context.

If only part of the source can be verified, return a partial result. Separate
verified facts from unknowns, avoid recommendations that depend on missing
state, and say what retrieval would complete the gate.

If local and remote state disagree, state which source supports each fact and
which one controls the decision. For repository completion, GitHub PR and issue
state usually controls remote readiness, while local `git` state controls only
the current checkout.

<!-- end:action.claim-verification/does -->

### action.claim-verification/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/does_not_establish -->
- Operational adoption
- Permission for the dependent operation
- Complete executor contract
<!-- end:action.claim-verification/does_not_establish -->

### action.claim-verification/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/owner -->
source.retrieval
<!-- end:action.claim-verification/owner -->

### action.claim-verification/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.claim-verification/parameters -->

### action.claim-verification/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/references -->
- source.core
- source.retrieval
- source.review
<!-- end:action.claim-verification/references -->

### action.claim-verification/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification/status -->
active
<!-- end:action.claim-verification/status -->

### action.claim-verification-failure/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/action_kind -->
behavior
<!-- end:action.claim-verification-failure/action_kind -->

### action.claim-verification-failure/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/does -->
Report verified facts separately from unknowns. Stop the stateful workflow if a materially required source remains unavailable through permitted routes; no summary-based recommendation.
<!-- end:action.claim-verification-failure/does -->

### action.claim-verification-failure/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/does_not_establish -->
- New source-access permission
- Authority from failure or fallback
<!-- end:action.claim-verification-failure/does_not_establish -->

### action.claim-verification-failure/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/owner -->
source.retrieval
<!-- end:action.claim-verification-failure/owner -->

### action.claim-verification-failure/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.claim-verification-failure/parameters -->

### action.claim-verification-failure/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/references -->
- source.retrieval
<!-- end:action.claim-verification-failure/references -->

### action.claim-verification-failure/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.claim-verification-failure/status -->
active
<!-- end:action.claim-verification-failure/status -->

### action.conditional-activation/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/action_kind -->
behavior
<!-- end:action.conditional-activation/action_kind -->

### action.conditional-activation/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/does -->
Read `docs/maintenance-automations.md` only when repository work touches
recurring automation design or review, execution-locality classification,
automation prompt authoring, fleet-wide maintenance, governance or drift
automation, scheduled inspection or correction, autonomous-maintenance
architecture, or automation authority, evidence, scope, and safety contracts.

Read `docs/feature-lifecycle.md` when the current authorized action first enters
feature-delivery planning or execution; use its activation boundary to
distinguish intent, prerequisite workflow ownership, and implementation
eligibility.

Read `docs/ai-workflow-ecosystem.md`,
`docs/repo-to-repo-interface-contracts.md`, and
`docs/cross-repo-glossary.md` only when the work involves multiple
repositories, cross-repository interfaces, or architectural terminology.

Ordinary repository implementation, review, issue triage, and "what changed?"
work do not require those specialized documents unless their triggers also
apply.

<!-- end:action.conditional-activation/does -->

### action.conditional-activation/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/does_not_establish -->
- Operational adoption
- Permission for the dependent operation
- Complete executor contract
<!-- end:action.conditional-activation/does_not_establish -->

### action.conditional-activation/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/owner -->
source.start
<!-- end:action.conditional-activation/owner -->

### action.conditional-activation/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.conditional-activation/parameters -->

### action.conditional-activation/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/references -->
- source.ecosystem
- source.glossary
- source.interfaces
- source.lifecycle
- source.maintenance
- source.start
<!-- end:action.conditional-activation/references -->

### action.conditional-activation/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation/status -->
active
<!-- end:action.conditional-activation/status -->

### action.conditional-activation-failure/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/action_kind -->
behavior
<!-- end:action.conditional-activation-failure/action_kind -->

### action.conditional-activation-failure/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/does -->
Retain unknown activations and required context; inspect canonical routing before relying on selection. Stop affected work if a required owner remains unavailable.
<!-- end:action.conditional-activation-failure/does -->

### action.conditional-activation-failure/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/does_not_establish -->
- New source-access permission
- Authority from failure or fallback
<!-- end:action.conditional-activation-failure/does_not_establish -->

### action.conditional-activation-failure/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/owner -->
source.start
<!-- end:action.conditional-activation-failure/owner -->

### action.conditional-activation-failure/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.conditional-activation-failure/parameters -->

### action.conditional-activation-failure/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/references -->
- source.start
<!-- end:action.conditional-activation-failure/references -->

### action.conditional-activation-failure/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.conditional-activation-failure/status -->
active
<!-- end:action.conditional-activation-failure/status -->

### action.mode-persistence/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/action_kind -->
behavior
<!-- end:action.mode-persistence/action_kind -->

### action.mode-persistence/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/does -->
- Successful repository hydration is a mode transition, not only an
  information-retrieval event. After the required repository startup contract
  succeeds, repository operating mode remains active for the rest of the
  repository work. Plans, reviews, implementation prompts, validation
  summaries, completion reports, and other artifacts must continue to use the
  repository-native conventions established by the governing repository
  sources without requiring the human to restate them. This invariant does not
  freeze a specific template or layout; the canonical artifact conventions may
  evolve. Repository operating mode ends only when the interaction clearly
  leaves repository work or the human explicitly requests a different artifact
  style. Moving to another repository requires applying that repository's
  startup contract before assuming its native conventions.

- Repository operating-mode persistence does not freeze the task-specific
  activated source set. When a task materially changes interaction mode,
  artifact type, workflow, authoritative-source requirements, execution
  locality, target executor, or authority boundary, re-evaluate activation
  routing and compare the changed task's required-source set with the currently
  activated set. Reuse the still-current repository floor and owners, retrieve
  only newly required owners before answering, planning, drafting, or acting,
  and do not blanket-rehydrate ordinary follow-ups. If a newly required owner
  cannot be retrieved, fail closed for the affected conclusion or artifact;
  memory, summaries, and convenient examples are not substitutes.

<!-- end:action.mode-persistence/does -->

### action.mode-persistence/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/does_not_establish -->
- Operational adoption
- Permission for the dependent operation
- Complete executor contract
<!-- end:action.mode-persistence/does_not_establish -->

### action.mode-persistence/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/owner -->
source.start
<!-- end:action.mode-persistence/owner -->

### action.mode-persistence/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.mode-persistence/parameters -->

### action.mode-persistence/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/references -->
- source.start
<!-- end:action.mode-persistence/references -->

### action.mode-persistence/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence/status -->
active
<!-- end:action.mode-persistence/status -->

### action.mode-persistence-failure/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/action_kind -->
behavior
<!-- end:action.mode-persistence-failure/action_kind -->

### action.mode-persistence-failure/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/does -->
Fail closed if a newly required owner cannot be retrieved; preserve its failure/fallback/presentation contract. Memory, summaries and convenient examples are not substitutes.
<!-- end:action.mode-persistence-failure/does -->

### action.mode-persistence-failure/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/does_not_establish -->
- New source-access permission
- Authority from failure or fallback
<!-- end:action.mode-persistence-failure/does_not_establish -->

### action.mode-persistence-failure/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/owner -->
source.start
<!-- end:action.mode-persistence-failure/owner -->

### action.mode-persistence-failure/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.mode-persistence-failure/parameters -->

### action.mode-persistence-failure/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/references -->
- source.start
<!-- end:action.mode-persistence-failure/references -->

### action.mode-persistence-failure/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.mode-persistence-failure/status -->
active
<!-- end:action.mode-persistence-failure/status -->

### action.retrieval-recovery/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/action_kind -->
behavior
<!-- end:action.retrieval-recovery/action_kind -->

### action.retrieval-recovery/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/does -->
Recovery is required when source-first ordering has already been missed. This
includes:

- the assistant answered before opening the referenced PR, issue, repository,
  branch, commit, path, or provider source

- conversational continuity outran verification

- inferred state was used before retrieval

- a human explicitly calls out missing source inspection

- conversational context conflicts with authoritative state

When retrieval remains available, recovery restores verified state before
conversational repair:

1. Halt continuity reasoning.

2. Identify every unresolved mandatory trigger.

3. Retrieve the authoritative source state for those triggers.

4. Discard, correct, or mark unverified any assumptions made before retrieval.

5. Resume from the restored verified state and stated unknowns.

Acknowledgment alone is not recovery. Explaining the violation is not
remediation. Recovery must perform the missing retrieval or inspection when it
is available, then explain only remaining blockers, uncertainty, or corrections
that still matter after inspection.

<!-- end:action.retrieval-recovery/does -->

### action.retrieval-recovery/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/does_not_establish -->
- Operational adoption
- Permission for the dependent operation
- Complete executor contract
<!-- end:action.retrieval-recovery/does_not_establish -->

### action.retrieval-recovery/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/owner -->
source.retrieval
<!-- end:action.retrieval-recovery/owner -->

### action.retrieval-recovery/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.retrieval-recovery/parameters -->

### action.retrieval-recovery/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/references -->
- source.codex
- source.retrieval
- source.start
<!-- end:action.retrieval-recovery/references -->

### action.retrieval-recovery/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery/status -->
active
<!-- end:action.retrieval-recovery/status -->

### action.retrieval-recovery-failure/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/action_kind -->
behavior
<!-- end:action.retrieval-recovery-failure/action_kind -->

### action.retrieval-recovery-failure/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/does -->
If no permitted qualified authoritative route remains, stop affected stateful conclusions and name the gap. A disallowed raw API transport with an available approved connector requires connector recovery, not premature failure.
<!-- end:action.retrieval-recovery-failure/does -->

### action.retrieval-recovery-failure/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/does_not_establish -->
- New source-access permission
- Authority from failure or fallback
<!-- end:action.retrieval-recovery-failure/does_not_establish -->

### action.retrieval-recovery-failure/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/owner -->
source.retrieval
<!-- end:action.retrieval-recovery-failure/owner -->

### action.retrieval-recovery-failure/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.retrieval-recovery-failure/parameters -->

### action.retrieval-recovery-failure/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/references -->
- source.codex
- source.retrieval
- source.start
<!-- end:action.retrieval-recovery-failure/references -->

### action.retrieval-recovery-failure/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-recovery-failure/status -->
active
<!-- end:action.retrieval-recovery-failure/status -->

### action.retrieval-triggers/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/action_kind -->
behavior
<!-- end:action.retrieval-triggers/action_kind -->

### action.retrieval-triggers/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/does -->
Classify triggers before using prior conversation, summaries, memory, or pasted
descriptions to reason about repository state.

Mandatory source-first triggers require authoritative retrieval before
stateful reasoning or recommendations:

- GitHub pull request URLs, pull request numbers, or requests such as "review
  this PR", "review directly", "take a look", "check this PR", "continue this
  PR", or "is this ready?"

- GitHub issue URLs, issue numbers, or requests such as "continue from this
  issue", "implement this issue", or "what is left on this issue?"

- repository identifiers, repository URLs, or local repository paths

- repo-aware advisory or evaluation requests where a repository is explicitly
  named and the answer depends on that repository's actual state

- branch names, refs, tags, commit SHAs, comparison ranges, or release refs

- requests to assess mergeability, CI status, review state, changed files,
  issue closure, validation status, or current implementation scope

- requests involving PRs, issues, branches, workflows, checks, validation
  state, merge sequencing, or implementation quality; treat these as mandatory
  source-first triggers and select the appropriate repo-readiness interaction
  mode rather than defaulting to conversational analysis

- claims or requested changes that depend on current external provider,
  public API, SDK, CLI, package, or hosted-platform behavior

Optional triggers may guide retrieval when the next action depends on current
state, but they do not require source inspection for purely conversational
answers:

- pasted summaries, completion reports, copied diffs, screenshots, or release
  notes without a live artifact identifier

- references to earlier conversation, prior work, a remembered plan, previous
  operational synthesis, or broad repository names without a state-dependent
  action

- conceptual questions about workflow patterns, review posture, or tradeoffs

Ambiguous cases must be resolved before stateful conclusions. If "continue",
"the branch", "the PR", or similar wording points to a clear source, inspect
that source. If the target is unclear, ask a narrow clarifying question or
report the missing identifier. Do not fill the gap with conversational
inference.

<!-- end:action.retrieval-triggers/does -->

### action.retrieval-triggers/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/does_not_establish -->
- Operational adoption
- Permission for the dependent operation
- Complete executor contract
<!-- end:action.retrieval-triggers/does_not_establish -->

### action.retrieval-triggers/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/owner -->
source.retrieval
<!-- end:action.retrieval-triggers/owner -->

### action.retrieval-triggers/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.retrieval-triggers/parameters -->

### action.retrieval-triggers/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/references -->
- source.retrieval
<!-- end:action.retrieval-triggers/references -->

### action.retrieval-triggers/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers/status -->
active
<!-- end:action.retrieval-triggers/status -->

### action.retrieval-triggers-failure/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/action_kind -->
behavior
<!-- end:action.retrieval-triggers-failure/action_kind -->

### action.retrieval-triggers-failure/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/does -->
Report missing identifiers or unavailable mandatory source and stop dependent conclusions. Do not substitute conversational inference; use another permitted qualified route where available.
<!-- end:action.retrieval-triggers-failure/does -->

### action.retrieval-triggers-failure/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/does_not_establish -->
- New source-access permission
- Authority from failure or fallback
<!-- end:action.retrieval-triggers-failure/does_not_establish -->

### action.retrieval-triggers-failure/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/owner -->
source.retrieval
<!-- end:action.retrieval-triggers-failure/owner -->

### action.retrieval-triggers-failure/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.retrieval-triggers-failure/parameters -->

### action.retrieval-triggers-failure/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/references -->
- source.codex
- source.retrieval
<!-- end:action.retrieval-triggers-failure/references -->

### action.retrieval-triggers-failure/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:action.retrieval-triggers-failure/status -->
active
<!-- end:action.retrieval-triggers-failure/status -->

### action.startup-floor/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/action_kind -->
behavior
<!-- end:action.startup-floor/action_kind -->

### action.startup-floor/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/does -->
Before repository-scoped code, documentation, research, planning, leadership,
read-only review, audit, advice, architecture/workflow analysis, PR or issue
recommendations, and "what changed?" or "what next?" requests:

1. Read this page, `docs/core-model.md`, and
   `docs/engineering-baseline.md`.

2. Read the target repository's repo-local `AGENTS.md`.

3. Apply the matching executor adapter. Codex runs must apply
   `docs/tool-adapters/codex.md`; Claude runs must apply
   `docs/tool-adapters/claude.md`; repository-scoped ChatGPT runs must apply
   `docs/tool-adapters/chatgpt.md`.

4. Identify the repository or workspace's primary purpose.

5. Select the interaction mode from `docs/repo-readiness.md`: implementation,
   review/audit, or orchestration/prompt-authoring.

6. Identify the canonical source for the rule, behavior, or state being used.

7. Apply `docs/source-first-retrieval.md` before stateful repository reasoning.
   When connector capability matters, apply
   [Connector availability is runtime evidence](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/da7a7dcb056239ac4193d1d44500c606488621f2/docs/#connector-availability-is-runtime-evidence)
   without changing repository hydration or instruction discovery.

8. For policy-sensitive changes, apply the repo-family alignment check in
   `docs/repo-readiness.md`.

9. Confirm command form and execution settings for planned commands.

10. Identify the canonical validation, review, or inspection path.

11. Act only after these checks are clear, or report the blocker, uncertainty,
    capability gap, or missing context.

Controller-owned context sufficiency is determined from canonical routing for
the current task. The controller or other workflow owner must establish that
the repository floor and every activated document are present; a child or
delegated worker's own selection or belief that it has enough context cannot
establish sufficiency.

<!-- end:action.startup-floor/does -->

### action.startup-floor/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/does_not_establish -->
- Operational adoption
- Permission for the dependent operation
- Complete executor contract
<!-- end:action.startup-floor/does_not_establish -->

### action.startup-floor/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/owner -->
source.start
<!-- end:action.startup-floor/owner -->

### action.startup-floor/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.startup-floor/parameters -->

### action.startup-floor/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/references -->
- source.agents
- source.baseline
- source.chatgpt
- source.claude
- source.codex
- source.core
- source.readiness
- source.retrieval
- source.start
<!-- end:action.startup-floor/references -->

### action.startup-floor/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor/status -->
active
<!-- end:action.startup-floor/status -->

### action.startup-floor-failure/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/action_kind -->
behavior
<!-- end:action.startup-floor-failure/action_kind -->

### action.startup-floor-failure/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/does -->
Report the exact unresolved prerequisite, source or authority gap and stop affected action; successful retrieval alone does not establish application.
<!-- end:action.startup-floor-failure/does -->

### action.startup-floor-failure/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/does_not_establish -->
- New source-access permission
- Authority from failure or fallback
<!-- end:action.startup-floor-failure/does_not_establish -->

### action.startup-floor-failure/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/owner -->
source.start
<!-- end:action.startup-floor-failure/owner -->

### action.startup-floor-failure/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:action.startup-floor-failure/parameters -->

### action.startup-floor-failure/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/references -->
- source.retrieval
- source.start
<!-- end:action.startup-floor-failure/references -->

### action.startup-floor-failure/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:action.startup-floor-failure/status -->
active
<!-- end:action.startup-floor-failure/status -->

### boundary.claim-verification/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/action_kind -->
boundary
<!-- end:boundary.claim-verification/action_kind -->

### boundary.claim-verification/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/does -->
The specific dependent Readiness, mergeability, approval, closure or implementation-completeness claims for operation=current-operation. Check current outside authority immediately before it.
<!-- end:boundary.claim-verification/does -->

### boundary.claim-verification/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/does_not_establish -->
- Eligibility to perform the operation
<!-- end:boundary.claim-verification/does_not_establish -->

### boundary.claim-verification/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/owner -->
source.retrieval
<!-- end:boundary.claim-verification/owner -->

### boundary.claim-verification/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:boundary.claim-verification/parameters -->

### boundary.claim-verification/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/references -->
(explicitly empty)
<!-- end:boundary.claim-verification/references -->

### boundary.claim-verification/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.claim-verification/status -->
active
<!-- end:boundary.claim-verification/status -->

### boundary.conditional-activation/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/action_kind -->
boundary
<!-- end:boundary.conditional-activation/action_kind -->

### boundary.conditional-activation/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/does -->
The specific dependent Affected analysis or artifact for operation=current-operation. Check current outside authority immediately before it.
<!-- end:boundary.conditional-activation/does -->

### boundary.conditional-activation/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/does_not_establish -->
- Eligibility to perform the operation
<!-- end:boundary.conditional-activation/does_not_establish -->

### boundary.conditional-activation/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/owner -->
source.start
<!-- end:boundary.conditional-activation/owner -->

### boundary.conditional-activation/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:boundary.conditional-activation/parameters -->

### boundary.conditional-activation/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/references -->
(explicitly empty)
<!-- end:boundary.conditional-activation/references -->

### boundary.conditional-activation/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.conditional-activation/status -->
active
<!-- end:boundary.conditional-activation/status -->

### boundary.mode-persistence/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/action_kind -->
boundary
<!-- end:boundary.mode-persistence/action_kind -->

### boundary.mode-persistence/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/does -->
The specific dependent Affected conclusion or artifact after activation changes for operation=current-operation. Check current outside authority immediately before it.
<!-- end:boundary.mode-persistence/does -->

### boundary.mode-persistence/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/does_not_establish -->
- Eligibility to perform the operation
<!-- end:boundary.mode-persistence/does_not_establish -->

### boundary.mode-persistence/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/owner -->
source.start
<!-- end:boundary.mode-persistence/owner -->

### boundary.mode-persistence/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:boundary.mode-persistence/parameters -->

### boundary.mode-persistence/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/references -->
(explicitly empty)
<!-- end:boundary.mode-persistence/references -->

### boundary.mode-persistence/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.mode-persistence/status -->
active
<!-- end:boundary.mode-persistence/status -->

### boundary.retrieval-recovery/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/action_kind -->
boundary
<!-- end:boundary.retrieval-recovery/action_kind -->

### boundary.retrieval-recovery/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/does -->
The specific dependent Recovery-dependent conclusion for operation=current-operation. Check current outside authority immediately before it.
<!-- end:boundary.retrieval-recovery/does -->

### boundary.retrieval-recovery/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/does_not_establish -->
- Eligibility to perform the operation
<!-- end:boundary.retrieval-recovery/does_not_establish -->

### boundary.retrieval-recovery/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/owner -->
source.retrieval
<!-- end:boundary.retrieval-recovery/owner -->

### boundary.retrieval-recovery/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:boundary.retrieval-recovery/parameters -->

### boundary.retrieval-recovery/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/references -->
(explicitly empty)
<!-- end:boundary.retrieval-recovery/references -->

### boundary.retrieval-recovery/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-recovery/status -->
active
<!-- end:boundary.retrieval-recovery/status -->

### boundary.retrieval-triggers/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/action_kind -->
boundary
<!-- end:boundary.retrieval-triggers/action_kind -->

### boundary.retrieval-triggers/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/does -->
The specific dependent Stateful reasoning for operation=current-operation. Check current outside authority immediately before it.
<!-- end:boundary.retrieval-triggers/does -->

### boundary.retrieval-triggers/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/does_not_establish -->
- Eligibility to perform the operation
<!-- end:boundary.retrieval-triggers/does_not_establish -->

### boundary.retrieval-triggers/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/owner -->
source.retrieval
<!-- end:boundary.retrieval-triggers/owner -->

### boundary.retrieval-triggers/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:boundary.retrieval-triggers/parameters -->

### boundary.retrieval-triggers/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/references -->
(explicitly empty)
<!-- end:boundary.retrieval-triggers/references -->

### boundary.retrieval-triggers/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:boundary.retrieval-triggers/status -->
active
<!-- end:boundary.retrieval-triggers/status -->

### boundary.startup-floor/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/action_kind -->
boundary
<!-- end:boundary.startup-floor/action_kind -->

### boundary.startup-floor/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/does -->
The specific dependent Repository-scoped action for operation=current-operation. Check current outside authority immediately before it.
<!-- end:boundary.startup-floor/does -->

### boundary.startup-floor/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/does_not_establish -->
- Eligibility to perform the operation
<!-- end:boundary.startup-floor/does_not_establish -->

### boundary.startup-floor/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/owner -->
source.start
<!-- end:boundary.startup-floor/owner -->

### boundary.startup-floor/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:boundary.startup-floor/parameters -->

### boundary.startup-floor/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/references -->
(explicitly empty)
<!-- end:boundary.startup-floor/references -->

### boundary.startup-floor/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:boundary.startup-floor/status -->
active
<!-- end:boundary.startup-floor/status -->

### evidence.claim-verification/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/action_kind -->
evidence
<!-- end:evidence.claim-verification/action_kind -->

### evidence.claim-verification/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/does -->
Record source-specific checks, unresolved questions and evidence of applying this unit to operation=current-operation. Retrieval alone does not prove adequacy or compliance.
<!-- end:evidence.claim-verification/does -->

### evidence.claim-verification/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/does_not_establish -->
- Permission
- Discharge of external judgment
<!-- end:evidence.claim-verification/does_not_establish -->

### evidence.claim-verification/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/owner -->
source.retrieval
<!-- end:evidence.claim-verification/owner -->

### evidence.claim-verification/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:evidence.claim-verification/parameters -->

### evidence.claim-verification/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/references -->
(explicitly empty)
<!-- end:evidence.claim-verification/references -->

### evidence.claim-verification/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.claim-verification/status -->
active
<!-- end:evidence.claim-verification/status -->

### evidence.conditional-activation/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/action_kind -->
evidence
<!-- end:evidence.conditional-activation/action_kind -->

### evidence.conditional-activation/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/does -->
Record source-specific checks, unresolved questions and evidence of applying this unit to operation=current-operation. Retrieval alone does not prove adequacy or compliance.
<!-- end:evidence.conditional-activation/does -->

### evidence.conditional-activation/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/does_not_establish -->
- Permission
- Discharge of external judgment
<!-- end:evidence.conditional-activation/does_not_establish -->

### evidence.conditional-activation/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/owner -->
source.start
<!-- end:evidence.conditional-activation/owner -->

### evidence.conditional-activation/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:evidence.conditional-activation/parameters -->

### evidence.conditional-activation/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/references -->
(explicitly empty)
<!-- end:evidence.conditional-activation/references -->

### evidence.conditional-activation/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.conditional-activation/status -->
active
<!-- end:evidence.conditional-activation/status -->

### evidence.mode-persistence/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/action_kind -->
evidence
<!-- end:evidence.mode-persistence/action_kind -->

### evidence.mode-persistence/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/does -->
Record source-specific checks, unresolved questions and evidence of applying this unit to operation=current-operation. Retrieval alone does not prove adequacy or compliance.
<!-- end:evidence.mode-persistence/does -->

### evidence.mode-persistence/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/does_not_establish -->
- Permission
- Discharge of external judgment
<!-- end:evidence.mode-persistence/does_not_establish -->

### evidence.mode-persistence/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/owner -->
source.start
<!-- end:evidence.mode-persistence/owner -->

### evidence.mode-persistence/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:evidence.mode-persistence/parameters -->

### evidence.mode-persistence/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/references -->
(explicitly empty)
<!-- end:evidence.mode-persistence/references -->

### evidence.mode-persistence/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.mode-persistence/status -->
active
<!-- end:evidence.mode-persistence/status -->

### evidence.retrieval-recovery/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/action_kind -->
evidence
<!-- end:evidence.retrieval-recovery/action_kind -->

### evidence.retrieval-recovery/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/does -->
Record source-specific checks, unresolved questions and evidence of applying this unit to operation=current-operation. Retrieval alone does not prove adequacy or compliance.
<!-- end:evidence.retrieval-recovery/does -->

### evidence.retrieval-recovery/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/does_not_establish -->
- Permission
- Discharge of external judgment
<!-- end:evidence.retrieval-recovery/does_not_establish -->

### evidence.retrieval-recovery/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/owner -->
source.retrieval
<!-- end:evidence.retrieval-recovery/owner -->

### evidence.retrieval-recovery/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:evidence.retrieval-recovery/parameters -->

### evidence.retrieval-recovery/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/references -->
(explicitly empty)
<!-- end:evidence.retrieval-recovery/references -->

### evidence.retrieval-recovery/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-recovery/status -->
active
<!-- end:evidence.retrieval-recovery/status -->

### evidence.retrieval-triggers/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/action_kind -->
evidence
<!-- end:evidence.retrieval-triggers/action_kind -->

### evidence.retrieval-triggers/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/does -->
Record source-specific checks, unresolved questions and evidence of applying this unit to operation=current-operation. Retrieval alone does not prove adequacy or compliance.
<!-- end:evidence.retrieval-triggers/does -->

### evidence.retrieval-triggers/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/does_not_establish -->
- Permission
- Discharge of external judgment
<!-- end:evidence.retrieval-triggers/does_not_establish -->

### evidence.retrieval-triggers/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/owner -->
source.retrieval
<!-- end:evidence.retrieval-triggers/owner -->

### evidence.retrieval-triggers/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:evidence.retrieval-triggers/parameters -->

### evidence.retrieval-triggers/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/references -->
(explicitly empty)
<!-- end:evidence.retrieval-triggers/references -->

### evidence.retrieval-triggers/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/source-retrieval.yaml)

<!-- begin:evidence.retrieval-triggers/status -->
active
<!-- end:evidence.retrieval-triggers/status -->

### evidence.startup-floor/action_kind

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/action_kind -->
evidence
<!-- end:evidence.startup-floor/action_kind -->

### evidence.startup-floor/does

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/does -->
Record source-specific checks, unresolved questions and evidence of applying this unit to operation=current-operation. Retrieval alone does not prove adequacy or compliance.
<!-- end:evidence.startup-floor/does -->

### evidence.startup-floor/does_not_establish

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/does_not_establish -->
- Permission
- Discharge of external judgment
<!-- end:evidence.startup-floor/does_not_establish -->

### evidence.startup-floor/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/owner -->
source.start
<!-- end:evidence.startup-floor/owner -->

### evidence.startup-floor/parameters

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/parameters -->
- name:
  
  operation
  
  type:
  
  term.operation
  
  required:
  
  true
<!-- end:evidence.startup-floor/parameters -->

### evidence.startup-floor/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/references -->
(explicitly empty)
<!-- end:evidence.startup-floor/references -->

### evidence.startup-floor/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:evidence.startup-floor/status -->
active
<!-- end:evidence.startup-floor/status -->

### fact.cross_repository_scope/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/evaluators -->
- controller
<!-- end:fact.cross_repository_scope/evaluators -->

### fact.cross_repository_scope/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/freshness -->
mode:

context
<!-- end:fact.cross_repository_scope/freshness -->

### fact.cross_repository_scope/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/owner -->
source.start
<!-- end:fact.cross_repository_scope/owner -->

### fact.cross_repository_scope/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/question -->
Work involves multiple repositories, cross-repository interfaces or architectural terminology.
<!-- end:fact.cross_repository_scope/question -->

### fact.cross_repository_scope/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/references -->
(explicitly empty)
<!-- end:fact.cross_repository_scope/references -->

### fact.cross_repository_scope/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/resolution_class -->
external_judgment
<!-- end:fact.cross_repository_scope/resolution_class -->

### fact.cross_repository_scope/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/sources -->
- source.start
<!-- end:fact.cross_repository_scope/sources -->

### fact.cross_repository_scope/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/status -->
active
<!-- end:fact.cross_repository_scope/status -->

### fact.cross_repository_scope/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/type -->
boolean
<!-- end:fact.cross_repository_scope/type -->

### fact.cross_repository_scope/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.cross_repository_scope/values -->
- false
- true
<!-- end:fact.cross_repository_scope/values -->

### fact.feature_delivery_current/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/evaluators -->
- controller
<!-- end:fact.feature_delivery_current/evaluators -->

### fact.feature_delivery_current/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/freshness -->
mode:

context
<!-- end:fact.feature_delivery_current/freshness -->

### fact.feature_delivery_current/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/owner -->
source.start
<!-- end:fact.feature_delivery_current/owner -->

### fact.feature_delivery_current/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/question -->
Current authorized action enters feature-delivery planning or execution, after the prerequisite workflow's boundary.
<!-- end:fact.feature_delivery_current/question -->

### fact.feature_delivery_current/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/references -->
(explicitly empty)
<!-- end:fact.feature_delivery_current/references -->

### fact.feature_delivery_current/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/resolution_class -->
external_judgment
<!-- end:fact.feature_delivery_current/resolution_class -->

### fact.feature_delivery_current/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/sources -->
- source.lifecycle
<!-- end:fact.feature_delivery_current/sources -->

### fact.feature_delivery_current/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/status -->
active
<!-- end:fact.feature_delivery_current/status -->

### fact.feature_delivery_current/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/type -->
boolean
<!-- end:fact.feature_delivery_current/type -->

### fact.feature_delivery_current/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.feature_delivery_current/values -->
- false
- true
<!-- end:fact.feature_delivery_current/values -->

### fact.human_style_override/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/evaluators -->
- controller
<!-- end:fact.human_style_override/evaluators -->

### fact.human_style_override/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/freshness -->
mode:

context
<!-- end:fact.human_style_override/freshness -->

### fact.human_style_override/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/owner -->
source.start
<!-- end:fact.human_style_override/owner -->

### fact.human_style_override/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/question -->
Human explicitly requested another artifact style; does not waive required sources.
<!-- end:fact.human_style_override/question -->

### fact.human_style_override/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/references -->
(explicitly empty)
<!-- end:fact.human_style_override/references -->

### fact.human_style_override/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/resolution_class -->
external_judgment
<!-- end:fact.human_style_override/resolution_class -->

### fact.human_style_override/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/sources -->
- source.start
<!-- end:fact.human_style_override/sources -->

### fact.human_style_override/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/status -->
active
<!-- end:fact.human_style_override/status -->

### fact.human_style_override/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/type -->
boolean
<!-- end:fact.human_style_override/type -->

### fact.human_style_override/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.human_style_override/values -->
- false
- true
<!-- end:fact.human_style_override/values -->

### fact.leaves_repository_work/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/evaluators -->
- controller
<!-- end:fact.leaves_repository_work/evaluators -->

### fact.leaves_repository_work/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/freshness -->
mode:

context
<!-- end:fact.leaves_repository_work/freshness -->

### fact.leaves_repository_work/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/owner -->
source.start
<!-- end:fact.leaves_repository_work/owner -->

### fact.leaves_repository_work/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/question -->
Interaction clearly leaves repository work.
<!-- end:fact.leaves_repository_work/question -->

### fact.leaves_repository_work/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/references -->
(explicitly empty)
<!-- end:fact.leaves_repository_work/references -->

### fact.leaves_repository_work/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/resolution_class -->
external_judgment
<!-- end:fact.leaves_repository_work/resolution_class -->

### fact.leaves_repository_work/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/sources -->
- source.start
<!-- end:fact.leaves_repository_work/sources -->

### fact.leaves_repository_work/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/status -->
active
<!-- end:fact.leaves_repository_work/status -->

### fact.leaves_repository_work/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/type -->
boolean
<!-- end:fact.leaves_repository_work/type -->

### fact.leaves_repository_work/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.leaves_repository_work/values -->
- false
- true
<!-- end:fact.leaves_repository_work/values -->

### fact.maintenance_scope/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/evaluators -->
- controller
<!-- end:fact.maintenance_scope/evaluators -->

### fact.maintenance_scope/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/freshness -->
mode:

context
<!-- end:fact.maintenance_scope/freshness -->

### fact.maintenance_scope/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/owner -->
source.start
<!-- end:fact.maintenance_scope/owner -->

### fact.maintenance_scope/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/question -->
An actual maintenance-automation trigger in Conditional Repository Guidance applies.
<!-- end:fact.maintenance_scope/question -->

### fact.maintenance_scope/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/references -->
(explicitly empty)
<!-- end:fact.maintenance_scope/references -->

### fact.maintenance_scope/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/resolution_class -->
external_judgment
<!-- end:fact.maintenance_scope/resolution_class -->

### fact.maintenance_scope/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/sources -->
- source.start
<!-- end:fact.maintenance_scope/sources -->

### fact.maintenance_scope/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/status -->
active
<!-- end:fact.maintenance_scope/status -->

### fact.maintenance_scope/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/type -->
boolean
<!-- end:fact.maintenance_scope/type -->

### fact.maintenance_scope/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.maintenance_scope/values -->
- false
- true
<!-- end:fact.maintenance_scope/values -->

### fact.mandatory_trigger/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/evaluators -->
- controller
<!-- end:fact.mandatory_trigger/evaluators -->

### fact.mandatory_trigger/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/freshness -->
mode:

context
<!-- end:fact.mandatory_trigger/freshness -->

### fact.mandatory_trigger/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/owner -->
source.start
<!-- end:fact.mandatory_trigger/owner -->

### fact.mandatory_trigger/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/question -->
At least one mandatory trigger applies after classifying references and state-dependent questions against the complete Triggers section.
<!-- end:fact.mandatory_trigger/question -->

### fact.mandatory_trigger/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/references -->
(explicitly empty)
<!-- end:fact.mandatory_trigger/references -->

### fact.mandatory_trigger/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/resolution_class -->
external_judgment
<!-- end:fact.mandatory_trigger/resolution_class -->

### fact.mandatory_trigger/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/sources -->
- source.retrieval
<!-- end:fact.mandatory_trigger/sources -->

### fact.mandatory_trigger/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/status -->
active
<!-- end:fact.mandatory_trigger/status -->

### fact.mandatory_trigger/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/type -->
boolean
<!-- end:fact.mandatory_trigger/type -->

### fact.mandatory_trigger/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.mandatory_trigger/values -->
- false
- true
<!-- end:fact.mandatory_trigger/values -->

### fact.repository_changed/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/evaluators -->
- controller
<!-- end:fact.repository_changed/evaluators -->

### fact.repository_changed/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/freshness -->
mode:

context
<!-- end:fact.repository_changed/freshness -->

### fact.repository_changed/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/owner -->
source.start
<!-- end:fact.repository_changed/owner -->

### fact.repository_changed/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/question -->
Current target differs from the repository whose startup completed.
<!-- end:fact.repository_changed/question -->

### fact.repository_changed/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/references -->
(explicitly empty)
<!-- end:fact.repository_changed/references -->

### fact.repository_changed/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/resolution_class -->
external_judgment
<!-- end:fact.repository_changed/resolution_class -->

### fact.repository_changed/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/sources -->
- source.start
<!-- end:fact.repository_changed/sources -->

### fact.repository_changed/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/status -->
active
<!-- end:fact.repository_changed/status -->

### fact.repository_changed/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/type -->
boolean
<!-- end:fact.repository_changed/type -->

### fact.repository_changed/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_changed/values -->
- false
- true
<!-- end:fact.repository_changed/values -->

### fact.repository_work/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/evaluators -->
- controller
<!-- end:fact.repository_work/evaluators -->

### fact.repository_work/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/freshness -->
mode:

context
<!-- end:fact.repository_work/freshness -->

### fact.repository_work/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/owner -->
source.start
<!-- end:fact.repository_work/owner -->

### fact.repository_work/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/question -->
Current bounded action depends on repository state; classify from current human instruction, not keywords alone.
<!-- end:fact.repository_work/question -->

### fact.repository_work/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/references -->
(explicitly empty)
<!-- end:fact.repository_work/references -->

### fact.repository_work/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/resolution_class -->
external_judgment
<!-- end:fact.repository_work/resolution_class -->

### fact.repository_work/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/sources -->
- source.start
<!-- end:fact.repository_work/sources -->

### fact.repository_work/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/status -->
active
<!-- end:fact.repository_work/status -->

### fact.repository_work/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/type -->
boolean
<!-- end:fact.repository_work/type -->

### fact.repository_work/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.repository_work/values -->
- false
- true
<!-- end:fact.repository_work/values -->

### fact.retrieval_missed/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/evaluators -->
- controller
<!-- end:fact.retrieval_missed/evaluators -->

### fact.retrieval_missed/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/freshness -->
mode:

context
<!-- end:fact.retrieval_missed/freshness -->

### fact.retrieval_missed/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/owner -->
source.start
<!-- end:fact.retrieval_missed/owner -->

### fact.retrieval_missed/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/question -->
Mandatory retrieval ordering was missed, assumptions preceded inspection, or a listed recovery trigger applies.
<!-- end:fact.retrieval_missed/question -->

### fact.retrieval_missed/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/references -->
(explicitly empty)
<!-- end:fact.retrieval_missed/references -->

### fact.retrieval_missed/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/resolution_class -->
external_judgment
<!-- end:fact.retrieval_missed/resolution_class -->

### fact.retrieval_missed/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/sources -->
- source.retrieval
<!-- end:fact.retrieval_missed/sources -->

### fact.retrieval_missed/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/status -->
active
<!-- end:fact.retrieval_missed/status -->

### fact.retrieval_missed/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/type -->
boolean
<!-- end:fact.retrieval_missed/type -->

### fact.retrieval_missed/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.retrieval_missed/values -->
- false
- true
<!-- end:fact.retrieval_missed/values -->

### fact.source_available/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/evaluators -->
- controller
<!-- end:fact.source_available/evaluators -->

### fact.source_available/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/freshness -->
mode:

context
<!-- end:fact.source_available/freshness -->

### fact.source_available/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/owner -->
source.start
<!-- end:fact.source_available/owner -->

### fact.source_available/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/question -->
At least one currently permitted qualified authoritative route supplies the required source; one failed transport is insufficient to set false.
<!-- end:fact.source_available/question -->

### fact.source_available/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/references -->
(explicitly empty)
<!-- end:fact.source_available/references -->

### fact.source_available/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/resolution_class -->
external_judgment
<!-- end:fact.source_available/resolution_class -->

### fact.source_available/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/sources -->
- source.retrieval
<!-- end:fact.source_available/sources -->

### fact.source_available/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/status -->
active
<!-- end:fact.source_available/status -->

### fact.source_available/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/type -->
boolean
<!-- end:fact.source_available/type -->

### fact.source_available/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.source_available/values -->
- false
- true
<!-- end:fact.source_available/values -->

### fact.startup_ready/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/evaluators -->
- controller
<!-- end:fact.startup_ready/evaluators -->

### fact.startup_ready/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/freshness -->
mode:

context
<!-- end:fact.startup_ready/freshness -->

### fact.startup_ready/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/owner -->
source.start
<!-- end:fact.startup_ready/owner -->

### fact.startup_ready/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/question -->
All startup checks and task-specific prerequisites are clear under their owners.
<!-- end:fact.startup_ready/question -->

### fact.startup_ready/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/references -->
(explicitly empty)
<!-- end:fact.startup_ready/references -->

### fact.startup_ready/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/resolution_class -->
external_judgment
<!-- end:fact.startup_ready/resolution_class -->

### fact.startup_ready/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/sources -->
- source.start
<!-- end:fact.startup_ready/sources -->

### fact.startup_ready/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/status -->
active
<!-- end:fact.startup_ready/status -->

### fact.startup_ready/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/type -->
boolean
<!-- end:fact.startup_ready/type -->

### fact.startup_ready/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_ready/values -->
- false
- true
<!-- end:fact.startup_ready/values -->

### fact.startup_succeeded/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/evaluators -->
- controller
<!-- end:fact.startup_succeeded/evaluators -->

### fact.startup_succeeded/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/freshness -->
mode:

context
<!-- end:fact.startup_succeeded/freshness -->

### fact.startup_succeeded/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/owner -->
source.start
<!-- end:fact.startup_succeeded/owner -->

### fact.startup_succeeded/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/question -->
Controller verified and applied the complete repository floor and activated owners, not merely retrieved them.
<!-- end:fact.startup_succeeded/question -->

### fact.startup_succeeded/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/references -->
(explicitly empty)
<!-- end:fact.startup_succeeded/references -->

### fact.startup_succeeded/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/resolution_class -->
external_judgment
<!-- end:fact.startup_succeeded/resolution_class -->

### fact.startup_succeeded/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/sources -->
- source.start
<!-- end:fact.startup_succeeded/sources -->

### fact.startup_succeeded/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/status -->
active
<!-- end:fact.startup_succeeded/status -->

### fact.startup_succeeded/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/type -->
boolean
<!-- end:fact.startup_succeeded/type -->

### fact.startup_succeeded/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.startup_succeeded/values -->
- false
- true
<!-- end:fact.startup_succeeded/values -->

### fact.verification_complete/evaluators

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/evaluators -->
- controller
<!-- end:fact.verification_complete/evaluators -->

### fact.verification_complete/freshness

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/freshness -->
mode:

context
<!-- end:fact.verification_complete/freshness -->

### fact.verification_complete/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/owner -->
source.start
<!-- end:fact.verification_complete/owner -->

### fact.verification_complete/question

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/question -->
Claim-specific checks have verified every materially necessary source fact; partial verification is not complete.
<!-- end:fact.verification_complete/question -->

### fact.verification_complete/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/references -->
(explicitly empty)
<!-- end:fact.verification_complete/references -->

### fact.verification_complete/resolution_class

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/resolution_class -->
external_judgment
<!-- end:fact.verification_complete/resolution_class -->

### fact.verification_complete/sources

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/sources -->
- source.retrieval
<!-- end:fact.verification_complete/sources -->

### fact.verification_complete/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/status -->
active
<!-- end:fact.verification_complete/status -->

### fact.verification_complete/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/type -->
boolean
<!-- end:fact.verification_complete/type -->

### fact.verification_complete/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:fact.verification_complete/values -->
- false
- true
<!-- end:fact.verification_complete/values -->

### source.agents/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.agents/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.agents/definition -->

### source.agents/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.agents/owner -->
source.start
<!-- end:source.agents/owner -->

### source.agents/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.agents/path -->
AGENTS.md
<!-- end:source.agents/path -->

### source.agents/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.agents/references -->
(explicitly empty)
<!-- end:source.agents/references -->

### source.agents/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.agents/status -->
active
<!-- end:source.agents/status -->

### source.baseline/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.baseline/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.baseline/definition -->

### source.baseline/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.baseline/owner -->
source.start
<!-- end:source.baseline/owner -->

### source.baseline/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.baseline/path -->
docs/engineering-baseline.md
<!-- end:source.baseline/path -->

### source.baseline/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.baseline/references -->
(explicitly empty)
<!-- end:source.baseline/references -->

### source.baseline/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.baseline/status -->
active
<!-- end:source.baseline/status -->

### source.chatgpt/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.chatgpt/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. Applicability is unresolved; all adapters remain visible until qualified selection. 
<!-- end:source.chatgpt/definition -->

### source.chatgpt/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.chatgpt/owner -->
source.start
<!-- end:source.chatgpt/owner -->

### source.chatgpt/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.chatgpt/path -->
docs/tool-adapters/chatgpt.md
<!-- end:source.chatgpt/path -->

### source.chatgpt/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.chatgpt/references -->
(explicitly empty)
<!-- end:source.chatgpt/references -->

### source.chatgpt/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.chatgpt/status -->
active
<!-- end:source.chatgpt/status -->

### source.claude/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.claude/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. Applicability is unresolved; all adapters remain visible until qualified selection. 
<!-- end:source.claude/definition -->

### source.claude/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.claude/owner -->
source.start
<!-- end:source.claude/owner -->

### source.claude/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.claude/path -->
docs/tool-adapters/claude.md
<!-- end:source.claude/path -->

### source.claude/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.claude/references -->
(explicitly empty)
<!-- end:source.claude/references -->

### source.claude/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.claude/status -->
active
<!-- end:source.claude/status -->

### source.codex/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.codex/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. Applicability is unresolved; all adapters remain visible until qualified selection. 
<!-- end:source.codex/definition -->

### source.codex/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.codex/owner -->
source.start
<!-- end:source.codex/owner -->

### source.codex/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.codex/path -->
docs/tool-adapters/codex.md
<!-- end:source.codex/path -->

### source.codex/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.codex/references -->
(explicitly empty)
<!-- end:source.codex/references -->

### source.codex/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.codex/status -->
active
<!-- end:source.codex/status -->

### source.core/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.core/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.core/definition -->

### source.core/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.core/owner -->
source.start
<!-- end:source.core/owner -->

### source.core/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.core/path -->
docs/core-model.md
<!-- end:source.core/path -->

### source.core/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.core/references -->
(explicitly empty)
<!-- end:source.core/references -->

### source.core/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.core/status -->
active
<!-- end:source.core/status -->

### source.ecosystem/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.ecosystem/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.ecosystem/definition -->

### source.ecosystem/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.ecosystem/owner -->
source.start
<!-- end:source.ecosystem/owner -->

### source.ecosystem/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.ecosystem/path -->
docs/ai-workflow-ecosystem.md
<!-- end:source.ecosystem/path -->

### source.ecosystem/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.ecosystem/references -->
(explicitly empty)
<!-- end:source.ecosystem/references -->

### source.ecosystem/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.ecosystem/status -->
active
<!-- end:source.ecosystem/status -->

### source.glossary/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.glossary/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.glossary/definition -->

### source.glossary/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.glossary/owner -->
source.start
<!-- end:source.glossary/owner -->

### source.glossary/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.glossary/path -->
docs/cross-repo-glossary.md
<!-- end:source.glossary/path -->

### source.glossary/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.glossary/references -->
(explicitly empty)
<!-- end:source.glossary/references -->

### source.glossary/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.glossary/status -->
active
<!-- end:source.glossary/status -->

### source.interfaces/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.interfaces/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.interfaces/definition -->

### source.interfaces/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.interfaces/owner -->
source.start
<!-- end:source.interfaces/owner -->

### source.interfaces/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.interfaces/path -->
docs/repo-to-repo-interface-contracts.md
<!-- end:source.interfaces/path -->

### source.interfaces/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.interfaces/references -->
(explicitly empty)
<!-- end:source.interfaces/references -->

### source.interfaces/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.interfaces/status -->
active
<!-- end:source.interfaces/status -->

### source.lifecycle/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.lifecycle/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.lifecycle/definition -->

### source.lifecycle/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.lifecycle/owner -->
source.start
<!-- end:source.lifecycle/owner -->

### source.lifecycle/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.lifecycle/path -->
docs/feature-lifecycle.md
<!-- end:source.lifecycle/path -->

### source.lifecycle/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.lifecycle/references -->
(explicitly empty)
<!-- end:source.lifecycle/references -->

### source.lifecycle/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.lifecycle/status -->
active
<!-- end:source.lifecycle/status -->

### source.maintenance/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.maintenance/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.maintenance/definition -->

### source.maintenance/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.maintenance/owner -->
source.start
<!-- end:source.maintenance/owner -->

### source.maintenance/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.maintenance/path -->
docs/maintenance-automations.md
<!-- end:source.maintenance/path -->

### source.maintenance/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.maintenance/references -->
(explicitly empty)
<!-- end:source.maintenance/references -->

### source.maintenance/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.maintenance/status -->
active
<!-- end:source.maintenance/status -->

### source.readiness/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.readiness/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. Interaction-mode and action-latch remain external; no rules from either unit are included. 
<!-- end:source.readiness/definition -->

### source.readiness/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.readiness/owner -->
source.start
<!-- end:source.readiness/owner -->

### source.readiness/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.readiness/path -->
docs/repo-readiness.md
<!-- end:source.readiness/path -->

### source.readiness/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.readiness/references -->
(explicitly empty)
<!-- end:source.readiness/references -->

### source.readiness/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.readiness/status -->
active
<!-- end:source.readiness/status -->

### source.retrieval/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.retrieval/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.retrieval/definition -->

### source.retrieval/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.retrieval/owner -->
source.start
<!-- end:source.retrieval/owner -->

### source.retrieval/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.retrieval/path -->
docs/source-first-retrieval.md
<!-- end:source.retrieval/path -->

### source.retrieval/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.retrieval/references -->
(explicitly empty)
<!-- end:source.retrieval/references -->

### source.retrieval/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.retrieval/status -->
active
<!-- end:source.retrieval/status -->

### source.review/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.review/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.review/definition -->

### source.review/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.review/owner -->
source.start
<!-- end:source.review/owner -->

### source.review/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.review/path -->
docs/review-packet.md
<!-- end:source.review/path -->

### source.review/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.review/references -->
(explicitly empty)
<!-- end:source.review/references -->

### source.review/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.review/status -->
active
<!-- end:source.review/status -->

### source.start/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.start/definition -->
External canonical read. Resolve the claim from this source; missing content blocks the dependent conclusion. 
<!-- end:source.start/definition -->

### source.start/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.start/owner -->
source.start
<!-- end:source.start/owner -->

### source.start/path

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.start/path -->
docs/start-here.md
<!-- end:source.start/path -->

### source.start/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.start/references -->
(explicitly empty)
<!-- end:source.start/references -->

### source.start/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:source.start/status -->
active
<!-- end:source.start/status -->

### term.operation/definition

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:term.operation/definition -->
Identity of the one concrete operation under review in the synthetic pilot context. It does not denote all repository work or authorize dispatch.
<!-- end:term.operation/definition -->

### term.operation/owner

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:term.operation/owner -->
source.start
<!-- end:term.operation/owner -->

### term.operation/references

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:term.operation/references -->
(explicitly empty)
<!-- end:term.operation/references -->

### term.operation/status

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:term.operation/status -->
active
<!-- end:term.operation/status -->

### term.operation/type

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:term.operation/type -->
enum
<!-- end:term.operation/type -->

### term.operation/values

[Edit semantic source](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/35241049177c16619761195d393913707dedb5e0/experiments/code-first-playbook/semantics/startup.yaml)

<!-- begin:term.operation/values -->
- current-operation
<!-- end:term.operation/values -->

## Unresolved questions and external reads

```json
{
  "diagnostics": [],
  "exclusions": {},
  "external_rule_boundaries": [],
  "external_sources": [
    "source.agents",
    "source.baseline",
    "source.chatgpt",
    "source.claude",
    "source.codex",
    "source.core",
    "source.ecosystem",
    "source.glossary",
    "source.interfaces",
    "source.lifecycle",
    "source.maintenance",
    "source.readiness",
    "source.retrieval",
    "source.review",
    "source.start"
  ],
  "facts": {
    "fact.cross_repository_scope": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Work involves multiple repositories, cross-repository interfaces or architectural terminology.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.feature_delivery_current": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Current authorized action enters feature-delivery planning or execution, after the prerequisite workflow's boundary.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.human_style_override": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Human explicitly requested another artifact style; does not waive required sources.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.leaves_repository_work": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Interaction clearly leaves repository work.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.maintenance_scope": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "An actual maintenance-automation trigger in Conditional Repository Guidance applies.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.mandatory_trigger": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "At least one mandatory trigger applies after classifying references and state-dependent questions against the complete Triggers section.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.repository_changed": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Current target differs from the repository whose startup completed.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.repository_work": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Current bounded action depends on repository state; classify from current human instruction, not keywords alone.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.retrieval_missed": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Mandatory retrieval ordering was missed, assumptions preceded inspection, or a listed recovery trigger applies.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.source_available": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "At least one currently permitted qualified authoritative route supplies the required source; one failed transport is insufficient to set false.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.startup_ready": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "All startup checks and task-specific prerequisites are clear under their owners.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.startup_succeeded": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Controller verified and applied the complete repository floor and activated owners, not merely retrieved them.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    },
    "fact.verification_complete": {
      "observations": [],
      "owner": "source.start",
      "pruning_qualified": false,
      "question": "Claim-specific checks have verified every materially necessary source fact; partial verification is not complete.",
      "resolution_class": "external_judgment",
      "state": "unknown"
    }
  },
  "permission": "not_evaluated"
}
```

## Supporting context (non-normative)

The required unverified-state literal and all claim-dependent inspection details stay in the exact canonical read; rendering is not proof those checks ran.
Task Routing, Repository Read Order and narrower activation rules remain explicit canonical reads; no claim of startup closure.
Only the two persistence/activation-refresh bullets are projected. Other invariants in this section are inventoried as unprojected canonical reads. Style override ends artifact-convention persistence, not source obligations.
Bootstrap transport recovery combines this unit with unprojected Minimum-Sufficient Retrieval and Codex raw-API policy. No new transport permission or fallback ladder is introduced.
Trigger classification is an externally supplied judgment anchored to the full Triggers section. The pilot does not infer it from a phrase classifier.
All numbered startup requirements are represented as one obligation with explicit full canonical reads; adapter selection and repo-family conditions remain unprojected judgments.
