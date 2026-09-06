from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CHATGPT_ADAPTER = REPO_ROOT / "docs" / "tool-adapters" / "chatgpt.md"
SECTION_HEADING = "#### Chat-to-Work action qualification cases"
EXPECTED_COLUMNS = (
    "Case",
    "Task authority",
    "Execution capability or locality",
    "Work dependency or fit",
    "Work transition consent",
    "Eligible action",
)


def parse_qualification_cases() -> dict[str, dict[str, str]]:
    lines = CHATGPT_ADAPTER.read_text(encoding="utf-8").splitlines()
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


class ChatGPTSurfaceTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = parse_qualification_cases()

    def test_task_authority_does_not_grant_surface_transition_authority(self) -> None:
        expected_actions = {
            "cak-242-chat-local-operation": "execute-in-chat",
            "cak-243-start-work": "remain-in-chat-use-authorized-executor",
        }
        for case, expected_action in expected_actions.items():
            with self.subTest(case=case):
                row = self.cases[case]
                self.assertEqual(row["Task authority"], "authorized")
                self.assertEqual(row["Work transition consent"], "absent")
                self.assertEqual(row["Eligible action"], expected_action)

    def test_chat_local_capability_keeps_authorized_action_in_chat(self) -> None:
        row = self.cases["cak-242-chat-local-operation"]
        self.assertEqual(
            row["Execution capability or locality"], "chat-local-sufficient"
        )
        self.assertEqual(row["Eligible action"], "execute-in-chat")

    def test_work_only_dependency_is_offered_without_automatic_transition(self) -> None:
        work_only_without_consent = [
            row
            for row in self.cases.values()
            if row["Execution capability or locality"] == "work-only"
            and row["Work transition consent"] == "absent"
        ]
        self.assertEqual(len(work_only_without_consent), 1)
        self.assertEqual(
            {row["Work dependency or fit"] for row in work_only_without_consent},
            {"required"},
        )
        self.assertEqual(
            {row["Eligible action"] for row in work_only_without_consent},
            {"offer-work-remain-in-chat"},
        )

    def test_only_explicit_work_consent_qualifies_transition(self) -> None:
        transitions = [
            row
            for row in self.cases.values()
            if row["Eligible action"] == "transition-to-work"
        ]
        self.assertEqual(
            {row["Work transition consent"] for row in transitions},
            {"explicit-request", "explicit-acceptance"},
        )
        self.assertEqual(
            {case for case, row in self.cases.items() if row in transitions},
            {"explicit-work-request", "accepted-work-offer"},
        )
        requested = self.cases["explicit-work-request"]
        self.assertEqual(
            requested["Execution capability or locality"], "not-evaluated"
        )
        self.assertEqual(requested["Eligible action"], "transition-to-work")


if __name__ == "__main__":
    unittest.main()
