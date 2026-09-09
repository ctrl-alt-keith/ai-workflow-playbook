from __future__ import annotations

import hashlib
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS = REPO_ROOT / "docs" / "prompts.md"
SECTION_HEADING = "### Recipient-routing qualification cases"
EXPECTED_COLUMNS = (
    "Case",
    "Produced artifact",
    "Operator/viewer",
    "Execution recipient",
    "Downstream execution surface",
    "Execution/handoff boundary",
    "Rendered UTF-8 bytes",
    "Inline representation",
    "Route capability",
    "Selected delivery",
)
AIRTABLE_SECTION_HEADING = "### Airtable qualification cases"
AIRTABLE_COLUMNS = (
    "Case",
    "Connector result",
    "Fallback prerequisite timing",
    "Fallback account identity",
    "Frozen final newline",
    "Frozen bytes",
    "Returned final newline",
    "Returned bytes",
    "Stored bytes",
    "Result",
)


def parse_qualification_cases() -> dict[str, dict[str, str]]:
    return parse_cases(SECTION_HEADING, EXPECTED_COLUMNS)


def parse_airtable_cases() -> dict[str, dict[str, str]]:
    return parse_cases(AIRTABLE_SECTION_HEADING, AIRTABLE_COLUMNS)


def parse_cases(
    section_heading: str, expected_columns: tuple[str, ...]
) -> dict[str, dict[str, str]]:
    lines = PROMPTS.read_text(encoding="utf-8").splitlines()
    section_start = lines.index(section_heading)
    table_start = next(
        index
        for index in range(section_start + 1, len(lines))
        if lines[index].startswith("| Case |")
    )
    header = tuple(cell.strip() for cell in lines[table_start].strip("|").split("|"))
    if header != expected_columns:
        raise AssertionError(f"unexpected qualification columns: {header}")

    cases: dict[str, dict[str, str]] = {}
    for line in lines[table_start + 2 :]:
        if not line.startswith("|"):
            break
        values = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        row = dict(zip(expected_columns, values, strict=True))
        case_id = row.pop("Case")
        if case_id in cases:
            raise AssertionError(f"duplicate qualification case: {case_id}")
        cases[case_id] = row
    return cases


class PromptRecipientRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = parse_qualification_cases()
        cls.airtable_cases = parse_airtable_cases()

    def test_prompt_me_manual_launch_keeps_codex_recipient(self) -> None:
        prompted = self.cases["cak-228-prompt-me-codex"]
        self.assertEqual(prompted["Operator/viewer"], "human")
        self.assertEqual(prompted["Execution recipient"], "codex")
        self.assertEqual(prompted["Downstream execution surface"], "codex")
        self.assertEqual(prompted["Execution/handoff boundary"], "fresh-execution")
        self.assertEqual(prompted["Selected delivery"], "airtable-thin-handoff")

    def test_in_run_steering_does_not_create_a_machine_handoff(self) -> None:
        for case in ("cak-242-codex-correction", "cak-241-codex-correction"):
            with self.subTest(case=case):
                correction = self.cases[case]
                self.assertEqual(correction["Produced artifact"], "complete")
                self.assertEqual(correction["Execution recipient"], "codex")
                self.assertEqual(correction["Downstream execution surface"], "codex")
                self.assertEqual(
                    correction["Execution/handoff boundary"], "in-run-steering"
                )

        steering = [
            row
            for row in self.cases.values()
            if row["Execution/handoff boundary"] == "in-run-steering"
        ]
        self.assertEqual(
            {row["Execution recipient"] for row in steering},
            {"codex", "claude", "chatgpt"},
        )
        self.assertEqual(
            {row["Route capability"] for row in steering},
            {"permitted", "unavailable", "not-inspected"},
        )
        self.assertEqual(
            {row["Selected delivery"] for row in steering}, {"inline-two-block"}
        )

    def test_inline_transport_limit_and_structural_override_route_before_failure(
        self,
    ) -> None:
        small = self.cases["cak-242-codex-correction"]
        oversized = self.cases["oversized-codex-steering"]
        fragile = self.cases["fragile-codex-steering"]
        unavailable = self.cases["oversized-route-unavailable"]

        self.assertEqual(int(small["Rendered UTF-8 bytes"]), 4095)
        self.assertEqual(small["Inline representation"], "safe")
        self.assertEqual(small["Selected delivery"], "inline-two-block")

        self.assertEqual(int(oversized["Rendered UTF-8 bytes"]), 4096)
        self.assertEqual(oversized["Execution/handoff boundary"], "transport-handoff")
        self.assertEqual(oversized["Selected delivery"], "airtable-thin-handoff")

        self.assertLess(int(fragile["Rendered UTF-8 bytes"]), 4096)
        self.assertEqual(fragile["Inline representation"], "fragile")
        self.assertEqual(fragile["Selected delivery"], "airtable-thin-handoff")
        self.assertEqual(unavailable["Selected delivery"], "blocked")

    def test_permitted_complete_machine_handoffs_use_airtable(self) -> None:
        qualifying = [
            row
            for row in self.cases.values()
            if row["Produced artifact"] == "complete"
            and row["Execution recipient"] not in {"human", "none"}
            and row["Execution/handoff boundary"]
            in {"fresh-execution", "revised-contract-review"}
            and row["Route capability"] == "permitted"
        ]
        self.assertEqual(
            {row["Execution/handoff boundary"] for row in qualifying},
            {"fresh-execution", "revised-contract-review"},
        )
        self.assertEqual(
            {row["Selected delivery"] for row in qualifying},
            {"airtable-thin-handoff"},
        )

    def test_machine_handoff_route_failure_never_falls_back_inline(self) -> None:
        failures = [
            row
            for row in self.cases.values()
            if row["Execution/handoff boundary"]
            in {"fresh-execution", "revised-contract-review"}
            and row["Route capability"]
            in {"unavailable", "identity-unresolved-after-inspection"}
        ]
        self.assertEqual(
            {row["Selected delivery"] for row in failures},
            {"blocked"},
        )

    def test_airtable_connector_precedes_fallback_capability_checks(self) -> None:
        connector = self.airtable_cases["connector-verified-payload"]
        invalid_order = self.airtable_cases[
            "codex-connector-supported-fallback-probed-first"
        ]
        identity_mismatch = self.airtable_cases[
            "codex-connector-failed-fallback-identity-mismatch"
        ]

        self.assertEqual(connector["Fallback prerequisite timing"], "not-inspected")
        self.assertEqual(connector["Result"], "emit-envelope")
        self.assertEqual(invalid_order["Fallback prerequisite timing"], "before-connector")
        self.assertEqual(invalid_order["Result"], "blocked-invalid-order")
        for result in ("absent", "unsupported", "failed"):
            with self.subTest(connector_result=result):
                fallback = self.airtable_cases[
                    f"codex-connector-{result}-fallback-verified"
                ]
                self.assertEqual(fallback["Connector result"], result)
                self.assertEqual(
                    fallback["Fallback prerequisite timing"], "after-connector"
                )
                self.assertEqual(
                    fallback["Fallback account identity"], "verified-for-base"
                )
                self.assertEqual(fallback["Result"], "fallback-eligible")
        self.assertEqual(identity_mismatch["Result"], "blocked")

    def test_final_newline_readback_mismatch_blocks_envelope(self) -> None:
        mismatch = self.airtable_cases["terminal-newline-mismatch"]
        self.assertEqual(mismatch["Frozen final newline"], "present")
        self.assertEqual(mismatch["Returned final newline"], "absent")
        self.assertEqual(int(mismatch["Frozen bytes"]), 5771)
        self.assertEqual(int(mismatch["Returned bytes"]), 5770)
        self.assertEqual(mismatch["Result"], "blocked")

        for payload_size in (5770, 13012):
            with self.subTest(payload_size=payload_size):
                returned_payload = b"x" * payload_size
                frozen_payload = returned_payload + b"\n"
                self.assertEqual(len(frozen_payload), len(returned_payload) + 1)
                self.assertNotEqual(
                    hashlib.sha256(frozen_payload).digest(),
                    hashlib.sha256(returned_payload).digest(),
                )

    def test_human_recipient_and_fragment_keep_lightweight_routes(self) -> None:
        human = self.cases["human-personal-use"]
        fragment = self.cases["conceptual-fragment"]
        self.assertEqual(human["Execution recipient"], "human")
        self.assertEqual(human["Selected delivery"], "inline-two-block")
        self.assertEqual(human["Route capability"], "not-required")
        self.assertEqual(fragment["Produced artifact"], "fragment")
        self.assertEqual(fragment["Selected delivery"], "lightweight")


if __name__ == "__main__":
    unittest.main()
