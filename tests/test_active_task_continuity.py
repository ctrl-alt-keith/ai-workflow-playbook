from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_MODEL = REPO_ROOT / "docs" / "core-model.md"
TABLE_MARKER = "<!-- qualification: active-bounded-task-continuity -->"
EXPECTED_COLUMNS = (
    "Case",
    "Relationship to active task",
    "Transition signal",
    "Outcome",
    "Unrelated durable mutation",
)


def parse_qualification_cases() -> dict[str, dict[str, str]]:
    lines = CORE_MODEL.read_text(encoding="utf-8").splitlines()
    marker_index = lines.index(TABLE_MARKER)
    table_start = next(
        index
        for index in range(marker_index + 1, len(lines))
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


class ActiveTaskContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = parse_qualification_cases()

    def test_related_follow_up_and_steering_continue(self) -> None:
        related = [
            row
            for row in self.cases.values()
            if row["Relationship to active task"] == "related"
        ]
        self.assertEqual(len(related), 2)
        self.assertEqual({row["Outcome"] for row in related}, {"continue"})
        self.assertEqual(
            {row["Unrelated durable mutation"] for row in related},
            {"not applicable"},
        )

    def test_explicit_or_confirmed_switch_re_routes_normally(self) -> None:
        switches = [
            row
            for row in self.cases.values()
            if row["Transition signal"] in {"explicit", "confirmed"}
        ]
        self.assertEqual(len(switches), 2)
        self.assertEqual(
            {row["Outcome"] for row in switches},
            {"switch and re-route"},
        )
        self.assertEqual(
            {row["Unrelated durable mutation"] for row in switches},
            {"only after normal current-task gates"},
        )

    def test_abrupt_unrelated_prompt_confirms_and_holds_mutation(self) -> None:
        held = self.cases["abrupt-unrelated-without-switch-signal"]
        self.assertEqual(held["Relationship to active task"], "unrelated")
        self.assertEqual(held["Transition signal"], "absent")
        self.assertEqual(held["Outcome"], "confirm and hold")
        self.assertEqual(
            held["Unrelated durable mutation"],
            "prohibited while unresolved",
        )


if __name__ == "__main__":
    unittest.main()
