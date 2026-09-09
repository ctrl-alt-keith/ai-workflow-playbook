from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest


PROMPTS = Path(__file__).resolve().parents[1] / "docs" / "prompts.md"


def inline_limit() -> int:
    matches = re.findall(
        r"inline_prompt_transport_byte_limit\s*=\s*(\d+)",
        PROMPTS.read_text(encoding="utf-8"),
    )
    if len(matches) != 1:
        raise AssertionError(f"expected one canonical inline limit, found {matches}")
    return int(matches[0])


def select_inline_or_airtable(
    payload: bytes, *, structurally_safe: bool, airtable_available: bool
) -> str:
    if len(payload) < inline_limit() and structurally_safe:
        return "inline-two-block"
    return "airtable" if airtable_available else "blocked"


def select_airtable_route(
    connector_result: str,
    *,
    fallback_probed_first: bool = False,
    fallback_identity_matches: bool = False,
) -> str:
    if connector_result == "available":
        return "invalid-order" if fallback_probed_first else "connector"
    if connector_result not in {"unavailable", "unsupported", "failed"}:
        raise ValueError(connector_result)
    return "fallback" if fallback_identity_matches else "blocked"


def producer_readback_matches(
    frozen_payload: bytes,
    returned_payload: str,
    *,
    stored_bytes: int,
    stored_sha256: str,
    final_newline_present: bool,
) -> bool:
    returned = returned_payload.encode("utf-8")
    return (
        returned == frozen_payload
        and returned.endswith(b"\n") is final_newline_present
        and len(returned) == stored_bytes
        and hashlib.sha256(returned).hexdigest() == stored_sha256
    )


class AirtableHandoffContractTests(unittest.TestCase):
    def test_safe_inline_threshold_and_structural_override(self) -> None:
        limit = inline_limit()
        self.assertEqual(limit, 4096)
        self.assertEqual(
            select_inline_or_airtable(
                b"x" * (limit - 1),
                structurally_safe=True,
                airtable_available=True,
            ),
            "inline-two-block",
        )
        self.assertEqual(
            select_inline_or_airtable(
                b"x" * limit,
                structurally_safe=True,
                airtable_available=True,
            ),
            "airtable",
        )
        self.assertEqual(
            select_inline_or_airtable(
                b"multiline\nprompt",
                structurally_safe=False,
                airtable_available=True,
            ),
            "airtable",
        )

    def test_connector_precedes_fallback_and_fallback_identity_is_required(self) -> None:
        self.assertEqual(select_airtable_route("available"), "connector")
        self.assertEqual(
            select_airtable_route("available", fallback_probed_first=True),
            "invalid-order",
        )
        for connector_result in ("unavailable", "unsupported", "failed"):
            with self.subTest(connector_result=connector_result):
                self.assertEqual(select_airtable_route(connector_result), "blocked")
                self.assertEqual(
                    select_airtable_route(
                        connector_result, fallback_identity_matches=True
                    ),
                    "fallback",
                )

    def test_terminal_lf_mismatch_fails_producer_readback(self) -> None:
        for returned_size in (5770, 13012):
            with self.subTest(returned_size=returned_size):
                returned = "x" * returned_size
                frozen = (returned + "\n").encode("utf-8")
                self.assertFalse(
                    producer_readback_matches(
                        frozen,
                        returned,
                        stored_bytes=len(frozen),
                        stored_sha256=hashlib.sha256(frozen).hexdigest(),
                        final_newline_present=True,
                    )
                )


if __name__ == "__main__":
    unittest.main()
