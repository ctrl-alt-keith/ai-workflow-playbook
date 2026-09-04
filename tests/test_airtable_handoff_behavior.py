from dataclasses import dataclass, replace
import hashlib
import unittest


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
    shared_airtable_user: str
    envelope_executor_identity: str
    final_newline_expected: bool
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
        if not self.envelope_executor_identity:
            raise ValueError("external executor identity missing")
        if self.payload.startswith("\ufeff") or "\r" in self.payload:
            raise ValueError("payload text format mismatch")
        if self.payload.endswith("\n") is not self.final_newline_expected:
            raise ValueError("payload final newline mismatch")

        payload_bytes = self.payload.encode("utf-8")
        recomputed_bytes = len(payload_bytes)
        recomputed_sha256 = hashlib.sha256(payload_bytes).hexdigest()
        if not (recomputed_bytes == self.stored_bytes == self.envelope_bytes):
            raise ValueError("payload byte length mismatch")
        if not (recomputed_sha256 == self.stored_sha256 == self.envelope_sha256):
            raise ValueError("payload digest mismatch")
        return self.payload


@dataclass(frozen=True)
class FrozenHandoffRecord:
    record_id: str
    handoff_key: str
    attempt_identity: str
    predecessor_record_id: str | None = None

    def correction(self, *, record_id, handoff_key, attempt_identity):
        if record_id == self.record_id:
            raise ValueError("correction must create a new record")
        if handoff_key == self.handoff_key:
            raise ValueError("correction must create a new handoff key")
        if attempt_identity == self.attempt_identity:
            raise ValueError("correction must create a new attempt")
        return FrozenHandoffRecord(
            record_id=record_id,
            handoff_key=handoff_key,
            attempt_identity=attempt_identity,
            predecessor_record_id=self.record_id,
        )


class AirtableHandoffBehaviorTests(unittest.TestCase):

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
            shared_airtable_user="shared-airtable-account",
            envelope_executor_identity="chatgpt/attempt-1",
            final_newline_expected=True,
        )
        self.assertEqual(evidence.verify(), payload)
        self.assertEqual(evidence.envelope_executor_identity, "chatgpt/attempt-1")
        self.assertNotEqual(
            evidence.envelope_executor_identity,
            evidence.shared_airtable_user,
        )

        failures = (
            (replace(evidence, result_count=0), "one record"),
            (replace(evidence, result_count=2), "one record"),
            (replace(evidence, observed_base_id="appOther"), "base ID"),
            (replace(evidence, observed_table_id="tblOther"), "table ID"),
            (replace(evidence, observed_record_id="recOther"), "record ID"),
            (replace(evidence, stored_key="other"), "handoff key"),
            (
                replace(evidence, observed_fields=frozenset({"Payload"})),
                "field set",
            ),
            (replace(evidence, stored_bytes=len(payload_bytes) - 1), "byte length"),
            (
                replace(evidence, envelope_bytes=len(payload_bytes) - 1),
                "byte length",
            ),
            (replace(evidence, stored_sha256="0" * 64), "digest"),
            (replace(evidence, envelope_sha256="0" * 64), "digest"),
            (replace(evidence, payload=payload.rstrip("\n")), "final newline"),
            (replace(evidence, payload="\ufeff" + payload), "text format"),
            (replace(evidence, payload=payload.replace("\n", "\r\n")), "text format"),
            (replace(evidence, final_newline_expected=False), "final newline"),
            (replace(evidence, envelope_executor_identity=""), "executor identity"),
        )
        for invalid, message in failures:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    invalid.verify()

    def test_correction_is_append_only_and_creates_a_new_attempt(self):
        original = FrozenHandoffRecord(
            record_id="recAttempt1",
            handoff_key="CAK-220/chatgpt/attempt-1",
            attempt_identity="chatgpt/attempt-1",
        )
        corrected = original.correction(
            record_id="recAttempt2",
            handoff_key="CAK-220/chatgpt/attempt-2",
            attempt_identity="chatgpt/attempt-2",
        )

        self.assertEqual(corrected.predecessor_record_id, original.record_id)
        self.assertNotEqual(corrected.record_id, original.record_id)
        self.assertNotEqual(corrected.handoff_key, original.handoff_key)
        self.assertNotEqual(corrected.attempt_identity, original.attempt_identity)

        invalid_corrections = (
            (
                {
                    "record_id": original.record_id,
                    "handoff_key": "CAK-220/chatgpt/attempt-2",
                    "attempt_identity": "chatgpt/attempt-2",
                },
                "new record",
            ),
            (
                {
                    "record_id": "recAttempt2",
                    "handoff_key": original.handoff_key,
                    "attempt_identity": "chatgpt/attempt-2",
                },
                "new handoff key",
            ),
            (
                {
                    "record_id": "recAttempt2",
                    "handoff_key": "CAK-220/chatgpt/attempt-2",
                    "attempt_identity": original.attempt_identity,
                },
                "new attempt",
            ),
        )
        for arguments, message in invalid_corrections:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    original.correction(**arguments)


if __name__ == "__main__":
    unittest.main()
