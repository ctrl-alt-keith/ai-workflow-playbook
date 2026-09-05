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
    "Downstream surface",
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

    def test_required_regression_cases_have_expected_semantics(self) -> None:
        expected = {
            "human-personal-use": (
                "complete",
                "human",
                "human",
                "human",
                "not-required",
                "inline-two-block",
            ),
            "cak-228-prompt-me-codex": (
                "complete",
                "human",
                "codex",
                "codex-fresh-thread",
                "permitted",
                "airtable-thin-handoff",
            ),
            "claude-executes": (
                "complete",
                "human",
                "claude",
                "claude-execution",
                "permitted",
                "airtable-thin-handoff",
            ),
            "chatgpt-executes": (
                "complete",
                "human",
                "chatgpt",
                "chatgpt-execution",
                "permitted",
                "airtable-thin-handoff",
            ),
            "manual-codex-launch": (
                "complete",
                "human",
                "codex",
                "codex-manual-fresh-thread",
                "permitted",
                "airtable-thin-handoff",
            ),
            "machine-route-unavailable": (
                "complete",
                "human",
                "codex",
                "codex-fresh-thread",
                "unavailable",
                "blocked",
            ),
            "machine-route-unresolved": (
                "complete",
                "human",
                "codex",
                "codex-fresh-thread",
                "unresolved",
                "blocked",
            ),
            "human-reads-complete-prompt": (
                "complete",
                "human",
                "human",
                "human",
                "not-required",
                "inline-two-block",
            ),
            "conceptual-fragment": (
                "fragment",
                "human",
                "none",
                "none",
                "not-applicable",
                "lightweight",
            ),
        }
        columns = EXPECTED_COLUMNS[1:]
        observed = {
            case_id: tuple(row[column] for column in columns)
            for case_id, row in self.cases.items()
        }
        self.assertEqual(expected, observed)

    def test_human_viewer_does_not_determine_execution_recipient(self) -> None:
        human_viewer_cases = [
            row for row in self.cases.values() if row["Operator/viewer"] == "human"
        ]
        self.assertEqual(
            {row["Execution recipient"] for row in human_viewer_cases},
            {"human", "codex", "claude", "chatgpt", "none"},
        )
        self.assertIn(
            "airtable-thin-handoff",
            {row["Selected delivery"] for row in human_viewer_cases},
        )

    def test_permitted_complete_machine_routes_use_airtable(self) -> None:
        qualifying = [
            row
            for row in self.cases.values()
            if row["Produced artifact"] == "complete"
            and row["Execution recipient"] not in {"human", "none"}
            and row["Route capability"] == "permitted"
        ]
        self.assertTrue(qualifying)
        self.assertEqual(
            {row["Selected delivery"] for row in qualifying},
            {"airtable-thin-handoff"},
        )

    def test_machine_route_failure_never_falls_back_inline(self) -> None:
        failures = [
            row
            for row in self.cases.values()
            if row["Route capability"] in {"unavailable", "unresolved"}
        ]
        self.assertEqual(
            {row["Selected delivery"] for row in failures},
            {"blocked"},
        )

    def test_manual_launch_does_not_change_machine_recipient(self) -> None:
        prompted = self.cases["cak-228-prompt-me-codex"]
        manual = self.cases["manual-codex-launch"]
        self.assertEqual(prompted["Execution recipient"], "codex")
        self.assertEqual(manual["Execution recipient"], "codex")
        self.assertEqual(
            prompted["Selected delivery"],
            manual["Selected delivery"],
        )


if __name__ == "__main__":
    unittest.main()
