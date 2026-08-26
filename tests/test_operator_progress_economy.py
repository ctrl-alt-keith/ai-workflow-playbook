from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def progress_fixture() -> dict:
    item_results = [
        {"item": f"file-{number:02d}", "status": "created"}
        for number in range(1, 65)
    ]
    return {
        "fixture_scope": "contract-only-not-runtime-or-ui-conformance",
        "attempt": "cak-149-fixture-attempt",
        "durable_item_results": item_results,
        "model_updates": [
            "Started bounded 64-item create with aggregate progress.",
            "32 of 64 items verified; no material blocker.",
            "64 of 64 items created and verified; complete results evidenced separately.",
        ],
        "material_blocker": {
            "visible_immediately": True,
            "kind": "authority mismatch",
        },
        "safety_boundaries": {
            boundary: "visible"
            for boundary in (
                "approval",
                "permission",
                "destructive",
                "collision",
                "overwrite",
                "drift",
                "privacy",
                "retention",
                "authority",
                "scope",
                "blocker",
                "validation",
            )
        },
        "create_without_preview": ["create", "raw-readback", "metadata"],
        "requested_visual_inspection": [
            "create",
            "raw-readback",
            "metadata",
            "preview",
        ],
        "client_forced_card": {
            "surface": "client-enforced-ui",
            "preview_invoked": False,
            "suppression_claimed": False,
        },
        "mid_run_preference": {
            "attempt_before": "cak-149-fixture-attempt",
            "attempt_after": "cak-149-fixture-attempt",
            "runtime_supports_change": True,
        },
    }


class OperatorProgressEconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = normalized(DOCS / "core-model.md")
        cls.evidence = normalized(DOCS / "evidence-lifecycle.md")
        cls.prompts = normalized(DOCS / "prompts.md")
        cls.chatgpt = normalized(DOCS / "tool-adapters" / "chatgpt.md")
        cls.codex = normalized(DOCS / "tool-adapters" / "codex.md")
        cls.claude = normalized(DOCS / "tool-adapters" / "claude.md")
        cls.fixture = progress_fixture()

    def test_core_owns_the_provider_neutral_invariant(self):
        for phrase in (
            "Routine successful item operations are not operator-observability events",
            "prefer aggregate milestones and a compact final result",
            "authority or scope mismatches",
            "drift, privacy or retention issues",
            "collision or overwrite risk",
            "validation failures",
            "permission, approval, destructive, or other safety boundaries",
            "Preserve complete item-level evidence outside the conversation",
            "when the active runtime supports it",
            "report client-forced output as a limitation",
        ):
            self.assertIn(phrase, self.core)

        for provider_name in ("ChatGPT", "Codex", "Claude", "Dropbox"):
            self.assertNotIn(provider_name, self.core)

    def test_existing_owners_receive_thin_projections(self):
        self.assertIn(
            "compact delivery does not require routine item-level success narration",
            self.evidence,
        )
        self.assertIn("Operator-Visible Progress Add-On", self.prompts)
        self.assertIn("without copying its material-event taxonomy", self.prompts)

        self.assertIn("Do not invoke preview", self.chatgpt)
        self.assertIn("client-enforced UI", self.chatgpt)
        self.assertIn("aggregate routine successful operations", self.codex)
        self.assertIn("without restarting", self.codex)
        self.assertIn("governed stream and attempt evidence", self.claude)
        self.assertIn("execution-context mismatch", self.claude)

    def test_64_item_success_fixture_is_aggregate_but_complete(self):
        self.assertEqual(
            "contract-only-not-runtime-or-ui-conformance",
            self.fixture["fixture_scope"],
        )
        item_results = self.fixture["durable_item_results"]
        updates = self.fixture["model_updates"]

        self.assertEqual(64, len(item_results))
        self.assertEqual(64, len({result["item"] for result in item_results}))
        self.assertLess(len(updates), len(item_results))
        for result in item_results:
            self.assertFalse(any(result["item"] in update for update in updates))

    def test_material_boundaries_remain_visible(self):
        self.assertTrue(self.fixture["material_blocker"]["visible_immediately"])
        self.assertEqual(
            {"visible"}, set(self.fixture["safety_boundaries"].values())
        )
        for boundary in (
            "approval",
            "permission",
            "destructive",
            "collision",
            "overwrite",
            "drift",
            "privacy",
            "retention",
            "authority",
            "scope",
            "blocker",
            "validation",
        ):
            self.assertIn(boundary, self.fixture["safety_boundaries"])

    def test_preview_and_client_forced_ui_are_separate(self):
        self.assertNotIn("preview", self.fixture["create_without_preview"])
        self.assertIn("preview", self.fixture["requested_visual_inspection"])
        forced_card = self.fixture["client_forced_card"]
        self.assertEqual("client-enforced-ui", forced_card["surface"])
        self.assertFalse(forced_card["preview_invoked"])
        self.assertFalse(forced_card["suppression_claimed"])

    def test_supported_mid_run_preference_keeps_the_attempt(self):
        preference = self.fixture["mid_run_preference"]
        self.assertTrue(preference["runtime_supports_change"])
        self.assertEqual(preference["attempt_before"], preference["attempt_after"])


if __name__ == "__main__":
    unittest.main()
