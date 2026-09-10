# Hosted Airtable Envelope Acceptance

This manual regression exercises the producer in hosted Chat after installation.
`test_global_bootstrap.py` covers delivery of the eligibility prerequisite through
the repository's reconciliation workflow; it does not execute Chat's producer.
There is no repository-owned envelope emitter to test here.

## Fixture Identity

Use the exact returned `Payload` P from the third CAK-292 attempt identified in
[CAK-251](https://linear.app/ctrl-alt-keith/issue/CAK-251).
Retrieve it by the issue's exact record ID and independently verify these
identities before using it. These are observed representations, not a guarantee
that Airtable always removes a terminal LF.

| Representation | UTF-8 bytes | SHA-256 | Final newline |
| --- | --- | --- | --- |
| P | 6487 | `cddc623015939f76f003605a51c2d705019e529363c1bd04b8805340e1fbd2dc` | absent |
| P plus one LF | 6488 | `d9e3cdb33e40ef4bc8be1304c7c865977afea7ba254402f5a8a639fbd39d8e38` | present |

## Procedure And Required Observations

1. After human-authorized installation, verify the exact candidate router in
   account custom instructions and CAK project instructions separately. Use a
   fresh Chat for each surface, with ordinary handoff wording rather than a
   prompt that restates the eligibility rule. Preserve the candidate identity,
   installed surface, fixture identity, and observable connector/action trace.
2. Resume the failed second attempt from CAK-251 using its unchanged frozen
   P-plus-LF identity and exact record ID. Exact readback returns P. The mismatch
   must produce no executable envelope; stored metadata and creation success
   cannot qualify it. Rejection of the legacy final-newline-present candidate
   before readback is safe, but does not count as coverage of the readback gate.
   If that prevents reaching the gate, report that coverage gap explicitly.
3. In a separately authorized correction attempt, freeze P, use matching
   metadata and a new key/record with predecessor lineage, and observe the
   producer across the following boundaries. Do not execute P's instructions.

| Observed boundary | Envelope construction/emission |
| --- | --- |
| Record created; exact-record readback pending | ineligible |
| Exact record returned; identity verification pending | ineligible |
| Returned P differs from frozen P-plus-LF identity | ineligible; no envelope for that attempt |
| Returned P independently verifies against frozen P and metadata | eligible for that exact correction attempt only |

Verify the emitted fields against the independently verified returned identity.
The failed record must remain unchanged, and no verification from it may qualify
the correction. If the hosted surface cannot expose a boundary, record it as
unverified rather than inferring it from a successful final envelope.

Also exercise existing connector-first and large-prompt routing cases, and the
Chat-to-Work qualification cases in the ChatGPT adapter. A passing repository
check or a single correct final envelope does not close hosted acceptance.
