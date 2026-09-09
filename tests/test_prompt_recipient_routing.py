from __future__ import annotations

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
    "Route capability",
    "Selected delivery",
)


def parse_qualification_cases() -> dict[str, dict[str, str]]:
    lines = PROMPTS.read_text(encoding="utf-8").splitlines()
    section_start = lines.index(SECTION_HEADING)
    table_start = next(
        index
        for index in range(section_start + 1, len(lines))
        if lines[index].startswith("| Case |")
    )
    header = tuple(cell.strip() for cell in lines[table_start].strip("|").split("|"))
    if header != EXPECTED_COLUMNS:
        raise AssertionError(f"unexpected qualification columns: {header}")

    cases: dict[str, dict[str, str]] = {}
    for line in lines[table_start + 2 :]:
        if not line.startswith("|"):
            break
        values = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        row = dict(zip(EXPECTED_COLUMNS, values, strict=True))
        case_id = row.pop("Case")
        if case_id in cases:
            raise AssertionError(f"duplicate qualification case: {case_id}")
        cases[case_id] = row
    return cases


class PromptRecipientRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = parse_qualification_cases()

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
