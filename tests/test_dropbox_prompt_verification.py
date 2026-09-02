from dataclasses import dataclass, replace
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DROPBOX_HASH = "a" * 64
WHOLE_FILE_SHA256 = "b" * 64
DROPBOX_PATH = "ns:14959974083//issues/CAK-194/prompt.md"


@dataclass(frozen=True)
class DropboxUploadEvidence:
    created_file_id: str | None = "id:created"
    observed_file_id: str | None = "id:created"
    link_file_id: str | None = "id:created"
    created_path: str | None = DROPBOX_PATH
    observed_path: str | None = DROPBOX_PATH
    link_path: str | None = DROPBOX_PATH
    local_byte_length: int | None = 7622
    stored_size: int | None = 7622
    link_stored_size: int | None = 7622
    local_dropbox_content_hash: str | None = DROPBOX_HASH
    provider_dropbox_content_hash: str | None = DROPBOX_HASH
    link_dropbox_content_hash: str | None = DROPBOX_HASH
    whole_file_sha256: str | None = WHOLE_FILE_SHA256
    verification_content_downloads: int = 0
    delivery_link_calls: int = 1
    delivery_url: str | None = "https://download.example/opaque-receiver-url"
    delivery_url_unconsumed: bool = True
    delivery_url_expired: bool = False
    delivery_url_ambiguous: bool = False
    containment_verified: bool = True
    receiver_content_transfers: int = 1
    receiver_observed_byte_length: int | None = 7622
    receiver_observed_sha256: str | None = WHOLE_FILE_SHA256


def present_text(value):
    return isinstance(value, str) and bool(value.strip())


def valid_file_id(value):
    return isinstance(value, str) and re.fullmatch(
        r"id:[A-Za-z0-9_-]+", value
    ) is not None


def valid_size(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def valid_sha256(value):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    )


def qualified_dropbox_delivery_attempt(evidence):
    file_ids = (
        evidence.created_file_id,
        evidence.observed_file_id,
        evidence.link_file_id,
    )
    if not all(valid_file_id(value) for value in file_ids):
        return False
    if len(set(file_ids)) != 1:
        return False

    paths = (evidence.created_path, evidence.observed_path, evidence.link_path)
    if not all(present_text(value) for value in paths):
        return False
    if len(set(paths)) != 1:
        return False
    if not evidence.containment_verified:
        return False

    sizes = (
        evidence.local_byte_length,
        evidence.stored_size,
        evidence.link_stored_size,
    )
    if not all(valid_size(value) for value in sizes):
        return False
    if len(set(sizes)) != 1:
        return False

    dropbox_hashes = (
        evidence.local_dropbox_content_hash,
        evidence.provider_dropbox_content_hash,
        evidence.link_dropbox_content_hash,
    )
    if not all(valid_sha256(value) for value in dropbox_hashes):
        return False
    if len(set(dropbox_hashes)) != 1:
        return False
    if not valid_sha256(evidence.whole_file_sha256):
        return False

    if evidence.verification_content_downloads != 0:
        return False
    if evidence.delivery_link_calls != 1:
        return False
    if not present_text(evidence.delivery_url):
        return False
    if not evidence.delivery_url_unconsumed:
        return False
    if evidence.delivery_url_expired or evidence.delivery_url_ambiguous:
        return False
    if evidence.receiver_content_transfers != 1:
        return False
    if not valid_size(evidence.receiver_observed_byte_length):
        return False
    if evidence.receiver_observed_byte_length != evidence.local_byte_length:
        return False
    if not valid_sha256(evidence.receiver_observed_sha256):
        return False
    return evidence.receiver_observed_sha256 == evidence.whole_file_sha256


class DropboxPromptVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = (DOCS / "prompt-contracts.md").read_text(encoding="utf-8")
        cls.chatgpt = (
            DOCS / "tool-adapters" / "chatgpt.md"
        ).read_text(encoding="utf-8")
        cls.normalized_contract = " ".join(cls.contract.split())
        cls.normalized_chatgpt = " ".join(cls.chatgpt.split())

    def test_complete_attempt_evidence_qualifies_without_controller_readback(self):
        evidence = DropboxUploadEvidence()
        self.assertTrue(qualified_dropbox_delivery_attempt(evidence))
        self.assertEqual(evidence.verification_content_downloads, 0)
        self.assertEqual(evidence.delivery_link_calls, 1)
        self.assertEqual(evidence.receiver_content_transfers, 1)
        self.assertEqual(
            evidence.receiver_observed_byte_length,
            evidence.local_byte_length,
        )
        self.assertEqual(
            evidence.receiver_observed_sha256,
            evidence.whole_file_sha256,
        )
        self.assertIn(
            "Raw post-write byte readback is not required after this qualified proof succeeds",
            self.normalized_contract,
        )

    def test_stored_size_mismatch_fails_closed(self):
        evidence = replace(DropboxUploadEvidence(), stored_size=7621)
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))
        self.assertIn("stored-size mismatch", self.chatgpt)

    def test_dropbox_content_hash_mismatch_fails_closed(self):
        evidence = replace(
            DropboxUploadEvidence(), provider_dropbox_content_hash="c" * 64
        )
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))
        self.assertIn("Dropbox content-hash mismatch", self.chatgpt)

    def test_provider_object_identity_mismatch_fails_closed(self):
        evidence = replace(DropboxUploadEvidence(), link_file_id="id:other")
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))
        self.assertIn("object-identity mismatch", self.chatgpt)

    def test_whole_file_sha_and_dropbox_hash_are_distinct(self):
        evidence = DropboxUploadEvidence()
        self.assertNotEqual(
            evidence.whole_file_sha256,
            evidence.local_dropbox_content_hash,
        )
        for phrase in (
            "it is not ordinary whole-file SHA-256",
            "never be compared directly or described as equivalent",
            "Do not reconstruct the prompt from chat or compare ordinary SHA-256 directly with Dropbox content_hash",
        ):
            self.assertIn(
                phrase,
                " ".join((self.normalized_contract, self.normalized_chatgpt)),
            )

    def test_missing_file_id_evidence_cannot_qualify_vacuously(self):
        for value in (None, ""):
            with self.subTest(value=value):
                evidence = replace(
                    DropboxUploadEvidence(),
                    created_file_id=value,
                    observed_file_id=value,
                    link_file_id=value,
                )
                self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_malformed_file_id_evidence_fails_closed(self):
        for field in ("created_file_id", "observed_file_id", "link_file_id"):
            for value in ("created", "id:", "id:bad value"):
                with self.subTest(field=field, value=value):
                    evidence = replace(DropboxUploadEvidence(), **{field: value})
                    self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_missing_or_empty_paths_fail_closed(self):
        for field in ("created_path", "observed_path", "link_path"):
            for value in (None, "", "   "):
                with self.subTest(field=field, value=value):
                    evidence = replace(DropboxUploadEvidence(), **{field: value})
                    self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_missing_or_empty_dropbox_hashes_fail_closed(self):
        for field in (
            "local_dropbox_content_hash",
            "provider_dropbox_content_hash",
            "link_dropbox_content_hash",
        ):
            for value in (None, ""):
                with self.subTest(field=field, value=value):
                    evidence = replace(DropboxUploadEvidence(), **{field: value})
                    self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_malformed_dropbox_hashes_fail_closed(self):
        malformed = ("a" * 63, "A" * 64, "g" * 64)
        for field in (
            "local_dropbox_content_hash",
            "provider_dropbox_content_hash",
            "link_dropbox_content_hash",
        ):
            for value in malformed:
                with self.subTest(field=field, value=value):
                    evidence = replace(DropboxUploadEvidence(), **{field: value})
                    self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_missing_sizes_fail_closed(self):
        for field in ("local_byte_length", "stored_size", "link_stored_size"):
            with self.subTest(field=field):
                evidence = replace(DropboxUploadEvidence(), **{field: None})
                self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_invalid_numeric_sizes_fail_closed(self):
        for field in ("local_byte_length", "stored_size", "link_stored_size"):
            for value in ("7622", True, 0, -1):
                with self.subTest(field=field, value=value):
                    evidence = replace(DropboxUploadEvidence(), **{field: value})
                    self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_missing_or_empty_delivery_url_fails_closed(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                evidence = replace(DropboxUploadEvidence(), delivery_url=value)
                self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_link_path_or_file_id_mismatch_fails_closed(self):
        for changes in (
            {"link_path": "ns:14959974083//issues/CAK-194/other.md"},
            {"link_file_id": "id:other"},
            {"link_stored_size": 7621},
            {"link_dropbox_content_hash": "c" * 64},
        ):
            with self.subTest(changes=changes):
                evidence = replace(DropboxUploadEvidence(), **changes)
                self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_unverified_containment_does_not_qualify(self):
        evidence = replace(DropboxUploadEvidence(), containment_verified=False)
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_second_download_link_call_does_not_qualify(self):
        evidence = replace(DropboxUploadEvidence(), delivery_link_calls=2)
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_consumed_url_does_not_qualify(self):
        evidence = replace(DropboxUploadEvidence(), delivery_url_unconsumed=False)
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_controller_verification_content_download_does_not_qualify(self):
        evidence = replace(
            DropboxUploadEvidence(), verification_content_downloads=1
        )
        self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_expired_or_ambiguous_url_does_not_qualify(self):
        for changes in (
            {"delivery_url_expired": True},
            {"delivery_url_ambiguous": True},
        ):
            with self.subTest(changes=changes):
                evidence = replace(DropboxUploadEvidence(), **changes)
                self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_receiver_transfer_and_verification_are_required(self):
        invalid = (
            {"receiver_content_transfers": 0},
            {"receiver_content_transfers": 2},
            {"receiver_observed_byte_length": None},
            {"receiver_observed_byte_length": 7621},
            {"receiver_observed_sha256": None},
            {"receiver_observed_sha256": "c" * 64},
        )
        for changes in invalid:
            with self.subTest(changes=changes):
                evidence = replace(DropboxUploadEvidence(), **changes)
                self.assertFalse(qualified_dropbox_delivery_attempt(evidence))

    def test_attempt_scoped_transfer_invariant_is_documented(self):
        self.assertIn(
            "exactly one final metadata-bearing `download_link` call",
            self.normalized_chatgpt,
        )
        self.assertIn(
            "exactly one receiver content transfer",
            self.normalized_chatgpt,
        )
        self.assertIn(
            "new distinct delivery attempt",
            self.normalized_chatgpt,
        )

    def test_transformed_or_manual_substitutes_remain_prohibited(self):
        for substitute in (
            "Extracted text",
            "preview content",
            "reconstructed chat text",
            "synchronized Dropbox files",
            "manual operator download/hash steps",
        ):
            self.assertIn(substitute, self.normalized_chatgpt)

    def test_executor_still_verifies_length_and_whole_file_sha_before_execution(self):
        start = self.chatgpt.index("```text\nDownload:")
        end = self.chatgpt.index("```", start + 3) + 3
        section = self.chatgpt[start:end]
        self.assertIn("Expected bytes:", section)
        self.assertIn("Expected SHA-256:", section)
        self.assertIn(
            "Download once, verify the exact identity, byte count, and SHA-256, then execute",
            section,
        )


if __name__ == "__main__":
    unittest.main()
