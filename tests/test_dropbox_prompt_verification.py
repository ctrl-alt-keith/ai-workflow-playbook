from dataclasses import dataclass, replace
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


@dataclass(frozen=True)
class DropboxUploadEvidence:
    created_file_id: str = "id:created"
    observed_file_id: str = "id:created"
    link_file_id: str = "id:created"
    local_byte_length: int = 7622
    stored_size: int = 7622
    local_dropbox_content_hash: str = "dropbox-content-hash"
    provider_dropbox_content_hash: str = "dropbox-content-hash"
    whole_file_sha256: str = "ordinary-whole-file-sha256"
    verification_content_downloads: int = 0
    delivery_link_calls: int = 1
    delivery_url_unconsumed: bool = True


def qualified_dropbox_upload(evidence):
    if len(
        {
            evidence.created_file_id,
            evidence.observed_file_id,
            evidence.link_file_id,
        }
    ) != 1:
        return False
    if evidence.stored_size != evidence.local_byte_length:
        return False
    if (
        evidence.provider_dropbox_content_hash
        != evidence.local_dropbox_content_hash
    ):
        return False
    if evidence.verification_content_downloads != 0:
        return False
    return evidence.delivery_link_calls == 1 and evidence.delivery_url_unconsumed


class DropboxPromptVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = (DOCS / "prompt-contracts.md").read_text(encoding="utf-8")
        cls.chatgpt = (
            DOCS / "tool-adapters" / "chatgpt.md"
        ).read_text(encoding="utf-8")
        cls.normalized_contract = " ".join(cls.contract.split())
        cls.normalized_chatgpt = " ".join(cls.chatgpt.split())

    def test_matching_local_size_and_dropbox_hash_qualify_without_readback(self):
        evidence = DropboxUploadEvidence()
        self.assertTrue(qualified_dropbox_upload(evidence))
        self.assertEqual(evidence.verification_content_downloads, 0)
        self.assertIn(
            "Raw post-write byte readback is not required after this qualified proof succeeds",
            self.normalized_contract,
        )

    def test_stored_size_mismatch_fails_closed(self):
        evidence = replace(DropboxUploadEvidence(), stored_size=7621)
        self.assertFalse(qualified_dropbox_upload(evidence))
        self.assertIn("stored-size mismatch", self.chatgpt)

    def test_dropbox_content_hash_mismatch_fails_closed(self):
        evidence = replace(
            DropboxUploadEvidence(), provider_dropbox_content_hash="mismatch"
        )
        self.assertFalse(qualified_dropbox_upload(evidence))
        self.assertIn("Dropbox content-hash mismatch", self.chatgpt)

    def test_provider_object_identity_mismatch_fails_closed(self):
        evidence = replace(DropboxUploadEvidence(), link_file_id="id:other")
        self.assertFalse(qualified_dropbox_upload(evidence))
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

    def test_controller_performs_no_verification_content_download(self):
        self.assertTrue(qualified_dropbox_upload(DropboxUploadEvidence()))
        self.assertIn("without a controller verification download", self.chatgpt)

    def test_one_unconsumed_delivery_link_call_can_supply_metadata_and_url(self):
        evidence = DropboxUploadEvidence()
        self.assertTrue(qualified_dropbox_upload(evidence))
        start = self.chatgpt.index("When `download_link` exposes")
        end = self.chatgpt.index("Overwrite, autorename", start)
        section = self.chatgpt[start:end]
        self.assertIn("one final call", section)
        self.assertIn("return that same unconsumed URL", section)
        for preflight in ("open", "preview", "unfurl", "scan", "`HEAD`", "range"):
            pattern = (
                rf"\b{re.escape(preflight)}\b"
                if preflight.isalpha()
                else re.escape(preflight)
            )
            self.assertRegex(section, pattern)

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
