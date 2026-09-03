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


def successful_completion_fixture() -> dict:
    return {
        "fixture_scope": "contract-only-not-runtime-or-ui-conformance",
        "operator_report": {
            "outcome": "Implemented CAK-185",
            "result": "PR #384 is open and review-ready",
            "validation_review": "canonical validation passed; independent review accepted",
            "head": "reviewed-head-sentinel",
            "stop_boundary": "stopped before merge",
        },
        "durable_forensic_evidence": {
            "retrieval_attempts": "forensic-only-three-preflight-attempts",
            "payload_bytes": "forensic-only-10193-byte-payload",
            "payload_sha256": "forensic-only-payload-sha256",
            "provider_file_id": "forensic-only-provider-file-id",
            "provider_path": "/forensic-only/cak-185-prompt.md",
            "provider_revision": "forensic-only-provider-revision",
            "provider_content_hash": "forensic-only-provider-content-hash",
            "review_artifact_identities": [
                "forensic-only-review-v1",
                "forensic-only-review-v2",
            ],
            "scratch_cleanup": "forensic-only-scratch-cleanup-verified",
            "deletion_authority_reminder": "forensic-only-deletion-confirmation",
        },
        "exception_report": {
            "result": "handoff blocked",
            "material_exception": "payload integrity mismatch",
            "consequence": "operator action is required before execution",
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
        cls.completion = successful_completion_fixture()

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
            "A successful completion report is an operator review surface, not a replay of the durable receipt",
            "the reviewable repository result and its current status",
            "the canonical validation and review outcome at a useful summary level",
            "the current stop boundary",
            "not a required sentence template or layout",
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
        self.assertIn("Successful completion projection", self.codex)
        self.assertIn("Successful completion projection", self.claude)
        self.assertEqual(
            2, self.prompts.count("successful-completion-projection")
        )
        self.assertIn(
            "Report the canonical outcome and any material validation exception",
            self.prompts,
        )
        self.assertIn(
            "report to the coordinating orchestrator",
            self.prompts,
        )
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

    def test_successful_completion_projects_operator_result_not_forensic_replay(self):
        self.assertEqual(
            "contract-only-not-runtime-or-ui-conformance",
            self.completion["fixture_scope"],
        )
        report = " ".join(self.completion["operator_report"].values())
        forensic = self.completion["durable_forensic_evidence"]

        for expected in (
            "Implemented CAK-185",
            "PR #384",
            "validation passed",
            "review accepted",
            "reviewed-head-sentinel",
            "stopped before merge",
        ):
            self.assertIn(expected, report)

        for value in forensic.values():
            values = value if isinstance(value, list) else [value]
            for item in values:
                self.assertNotIn(str(item), report)

        for phrase in (
            "byte counts and digests",
            "provider object metadata",
            "temporary-scratch and cleanup mechanics",
            "retained evidence identities",
            "command history, and raw test counts",
            "does not weaken evidence collection, verification, identity, retention, or retrievability",
        ):
            self.assertIn(phrase, self.core)

    def test_material_exception_surfaces_without_replaying_complete_receipt(self):
        exception = " ".join(self.completion["exception_report"].values())
        self.assertIn("integrity mismatch", exception)
        self.assertIn("operator action is required", exception)
        self.assertIn(
            "Report the material exception and its consequence rather than the complete forensic history",
            self.core,
        )

    def test_completion_projection_preserves_transition_receipts(self):
        self.assertIn(
            "does not suppress progress updates or mandatory transition-time receipts",
            self.core,
        )
        self.assertIn(
            "must still be emitted at their transition boundaries",
            self.core,
        )
        self.assertIn(
            "Issue-Owned File-Backed Handoff Prose-DAG Pilot",
            self.prompts,
        )


if __name__ == "__main__":
    unittest.main()
