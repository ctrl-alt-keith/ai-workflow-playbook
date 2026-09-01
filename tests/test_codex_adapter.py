from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "docs" / "tool-adapters" / "codex.md"


class CodexAdapterTests(unittest.TestCase):
    def setUp(self):
        self.contents = " ".join(ADAPTER.read_text(encoding="utf-8").split())

    def test_goal_mode_routes_to_existing_contract_and_authority_owners(self):
        for phrase in (
            "## Goal Mode",
            "existing outcome-oriented task envelope",
            "core-model.md",
            "start-here.md",
            "source-first-retrieval.md",
            "prompts.md",
            "prompt-contracts.md",
            "does not create a second contract",
            "not human acceptance, approval, merge, release, publish, adoption, or downstream",
            "continuation authority",
            "Edit, replace, pause, or clear stale Goal state",
            "do not let it silently drive continuation under an obsolete task contract",
        ):
            self.assertIn(phrase, self.contents)

    def test_controller_owns_child_activation_and_source_sufficiency(self):
        for phrase in (
            "Before child dispatch, the controller resolves current startup activation",
            "establishes the repository floor",
            "every child-activated canonical owner or source",
            "bounded retrieval instructions",
            "retains ownership of the judgment that the context and source set is sufficient",
            "exact controller-selected sources",
            '"read whatever you need" into self-authorized broad hydration',
            "inherited full, partial, or no conversation history",
            "filesystem access, tool access, or successful retrieval",
        ):
            self.assertIn(phrase, self.contents)

    def test_child_activation_returns_control_to_controller(self):
        for phrase in (
            "newly activated owner or source",
            "The controller re-runs activation routing",
            "sends a bounded follow-up, reissues the task, handles the work directly, or stops the lane",
            "does not independently widen itself and declare the new set sufficient",
        ):
            self.assertIn(phrase, self.contents)

    def test_reconciliation_stays_with_shared_orchestration_owner(self):
        self.assertIn("Reconciliation remains controller-owned", self.contents)
        self.assertIn("orchestration-and-parallelism.md", self.contents)
        self.assertNotIn("Reconciliation And Merge Sequence", self.contents)

    def test_shell_only_transport_preserves_runtime_approval_boundary(self):
        for phrase in (
            "Shell-Only Execution Surfaces",
            "fixed non-login runner such as `zsh -c`",
            "does not authorize agent-authored shell wrappers",
            "runtime approval limitation",
            "broad `mkdir` or `mkdir -p` prefix allow rule",
            "containment for every operand or resolved path",
        ):
            self.assertIn(phrase, self.contents)

    def test_github_command_selection_inherits_the_shared_rule(self):
        self.assertIn(
            "repo-readiness.md#command-form-and-intent-visibility", self.contents
        )
        self.assertNotIn("`gh api`", self.contents)

    def test_pr_evidence_requires_current_connector_backed_state(self):
        for phrase in (
            "## GitHub And PR Evidence",
            "verify GitHub access instead of relying on cached context, summaries, or local branch state",
            "follow the connector-first rule",
            "Local checkout state, `git diff`, and `gh` output may supplement PR review",
            "but they do not replace it",
            "stop and report the access blocker instead of inferring remote state",
            "Do not claim mergeability, required checks, or branch-protection state without",
            "current PR or repository evidence",
        ):
            self.assertIn(phrase, self.contents)
