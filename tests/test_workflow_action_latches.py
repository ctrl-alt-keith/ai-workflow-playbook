from dataclasses import dataclass, replace
import hashlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CORE_MODEL = DOCS / "core-model.md"
REPO_READINESS = DOCS / "repo-readiness.md"
PROMPTS = DOCS / "prompts.md"
REVIEW_PACKET = DOCS / "review-packet.md"
CHATGPT_ADAPTER = DOCS / "tool-adapters" / "chatgpt.md"
CODEX_ADAPTER = DOCS / "tool-adapters" / "codex.md"
CLAUDE_ADAPTER = DOCS / "tool-adapters" / "claude.md"


@dataclass(frozen=True)
class AirtableHandoffEvidence:
    envelope_base_id: str
    observed_base_id: str
    envelope_table_id: str
    observed_table_id: str
    envelope_record_id: str
    observed_record_id: str
    envelope_key: str
    stored_key: str
    envelope_bytes: int
    stored_bytes: int
    envelope_sha256: str
    stored_sha256: str
    payload: str
    result_count: int = 1
    observed_fields: frozenset[str] = frozenset(
        {"Handoff Key", "Payload", "Payload Bytes", "SHA-256", "Producer"}
    )

    def verify(self):
        required_fields = {
            "Handoff Key",
            "Payload",
            "Payload Bytes",
            "SHA-256",
            "Producer",
        }
        if self.result_count != 1:
            raise ValueError("exact record retrieval did not return one record")
        for expected, observed, label in (
            (self.envelope_base_id, self.observed_base_id, "base ID"),
            (self.envelope_table_id, self.observed_table_id, "table ID"),
            (self.envelope_record_id, self.observed_record_id, "record ID"),
            (self.envelope_key, self.stored_key, "handoff key"),
        ):
            if expected != observed:
                raise ValueError(f"{label} mismatch")
        if self.observed_fields != required_fields:
            raise ValueError("field set mismatch")

        payload_bytes = self.payload.encode("utf-8")
        recomputed_bytes = len(payload_bytes)
        recomputed_sha256 = hashlib.sha256(payload_bytes).hexdigest()
        if not (
            recomputed_bytes == self.stored_bytes == self.envelope_bytes
        ):
            raise ValueError("payload byte length mismatch")
        if not (
            recomputed_sha256 == self.stored_sha256 == self.envelope_sha256
        ):
            raise ValueError("payload digest mismatch")
        return self.payload


class WorkflowActionLatchTests(unittest.TestCase):
    def test_each_shared_rule_has_one_canonical_heading_owner(self):
        expected_owners = {
            "## Interactive And Execution Surfaces": CORE_MODEL,
            "### Interaction-mode action eligibility latch": REPO_READINESS,
            "### Airtable canonical-text handoff": PROMPTS,
            "### Connector-sufficient review latch": REVIEW_PACKET,
        }
        markdown = {
            path: path.read_text(encoding="utf-8") for path in DOCS.rglob("*.md")
        }
        for heading, expected_owner in expected_owners.items():
            owners = {path for path, contents in markdown.items() if heading in contents}
            self.assertEqual(owners, {expected_owner}, heading)

        airtable_anchor = "prompts.md#airtable-canonical-text-handoff"
        for projection in (CHATGPT_ADAPTER, CODEX_ADAPTER, CLAUDE_ADAPTER):
            with self.subTest(projection=projection.name):
                self.assertIn(
                    airtable_anchor,
                    projection.read_text(encoding="utf-8").lower(),
                )

    def test_exact_record_and_independent_digest_verification(self):
        payload = "Implement the bounded task.\n"
        payload_bytes = payload.encode("utf-8")
        digest = hashlib.sha256(payload_bytes).hexdigest()
        evidence = AirtableHandoffEvidence(
            envelope_base_id="appExample",
            observed_base_id="appExample",
            envelope_table_id="tblExample",
            observed_table_id="tblExample",
            envelope_record_id="recAttempt1",
            observed_record_id="recAttempt1",
            envelope_key="CAK-220/chatgpt/attempt-1",
            stored_key="CAK-220/chatgpt/attempt-1",
            envelope_bytes=len(payload_bytes),
            stored_bytes=len(payload_bytes),
            envelope_sha256=digest,
            stored_sha256=digest,
            payload=payload,
        )
        self.assertEqual(evidence.verify(), payload)

        failures = (
            (replace(evidence, result_count=0), "one record"),
            (replace(evidence, result_count=2), "one record"),
            (replace(evidence, observed_record_id="recOther"), "record ID"),
            (replace(evidence, stored_key="other"), "handoff key"),
            (
                replace(evidence, observed_fields=frozenset({"Payload"})),
                "field set",
            ),
            (replace(evidence, stored_bytes=len(payload_bytes) - 1), "byte length"),
            (replace(evidence, envelope_sha256="0" * 64), "digest"),
            (replace(evidence, payload=payload.rstrip("\n")), "byte length"),
        )
        for invalid, message in failures:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    invalid.verify()

    def test_normal_route_excludes_obsolete_file_actions(self):
        contract = PROMPTS.read_text(encoding="utf-8").lower()
        shared = contract[
            contract.index("### airtable canonical-text handoff") :
            contract.index("## cross-executor prompt presentation")
        ]
        for obsolete in (
            "download link",
            "prompt preview",
            "attempt-local download",
            "confirmation workaround",
        ):
            self.assertNotIn(obsolete, shared)


if __name__ == "__main__":
    unittest.main()
