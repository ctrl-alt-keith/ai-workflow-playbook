from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class AttemptLocalScratchSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readiness_text = (DOCS / "repo-readiness.md").read_text(encoding="utf-8")
        cls.readiness = normalized(DOCS / "repo-readiness.md")
        cls.codex = normalized(DOCS / "tool-adapters" / "codex.md")
        cls.engineering = normalized(DOCS / "engineering-baseline.md")
        cls.evidence = normalized(DOCS / "evidence-lifecycle.md")
        cls.claude = normalized(DOCS / "tool-adapters" / "claude.md")
        cls.agents = normalized(ROOT / "AGENTS.md")

    def test_readiness_owns_the_lifecycle_taxonomy(self):
        for phrase in (
            "`scratch` is a lifecycle and storage class, not an assumed persistent workspace pathname",
            "Durable state",
            "Repository-owned working state",
            "Attempt-local disposable scratch",
            "Crash residue",
            "Legacy workspace scratch",
            "attempt-local scratch",
            "Generic persistent `scratch/` is prohibited by default for disposable mechanics",
        ):
            self.assertIn(phrase, self.readiness)

    def test_authority_promotion_cleanup_and_fallback_fail_closed(self):
        for phrase in (
            "no required durable state may exist solely in scratch",
            "not authority",
            "Promotion precedes cleanup",
            "exact-verify it",
            "Copying bytes elsewhere does not transfer ownership, authority, evidence acceptance, or recovery status",
            "after the attempt no longer depends on scratch",
            "all dependency-bearing output has been promoted and exact-verified",
            "required evidence has been preserved",
            "the executor attempts cleanup",
            "Only the owning executor, or an operator explicitly authorized",
            "Cleanup is best-effort, not a crash or reboot deletion guarantee",
            "Never silently fall back",
            "Fail closed on unexpected members",
            "Crash residue is not normal-completion cleanup",
            "Never reuse it",
        ):
            self.assertIn(phrase, self.readiness)

    def test_repo_locality_does_not_create_a_junk_drawer_default(self):
        self.assertNotIn(
            "Keep temporary workflow artifacts scoped to that repository whenever practical",
            self.readiness,
        )
        for phrase in (
            "Classify workflow material by natural owner and lifecycle",
            "repository-owned working state stays in the repository",
            "tool-owned working state stays under its tool's contract",
            "durable review, evidence, recovery, replay, planning, and execution-identity material belongs with its natural durable owner",
            "generated artifacts or manifests do not become repository-owned merely because they are local",
            "Locality does not transfer ownership or make evidence disposable",
        ):
            self.assertIn(phrase, self.readiness)

    def test_first_normative_use_and_repository_working_state_are_distinct(self):
        taxonomy_definition = self.readiness_text.index("- **Attempt-local disposable scratch**")
        short_form = self.readiness_text.index("**attempt-local scratch**", taxonomy_definition)
        self.assertGreater(short_form, taxonomy_definition)
        self.assertIn("Use **attempt-local scratch** after this definition", self.readiness)
        self.assertIn(".venv", self.readiness)
        self.assertIn("compiler/dependency caches", self.readiness)
        self.assertIn("worktrees, and tool state are not automatically scratch", self.readiness)
        self.assertNotIn("~/src/ctrl-alt-keith/scratch/", self.readiness)
        self.assertIn("Each material attempt that needs disposable local mechanics receives fresh", self.readiness)
        self.assertIn("Do not adopt or reuse it across attempts", self.readiness)
        self.assertIn("do not give it a planning, authority, evidence, recovery, replay, or sole-durable", self.readiness)

    def test_taxonomy_and_cleanup_projections_delegate_to_the_canonical_owner(self):
        section = self.readiness_text.split("## Repo-Local Workflow State", 1)[1].split(
            "## Command Form And Intent Visibility", 1
        )[0]
        for label in (
            "**Durable state**",
            "**Repository-owned working state**",
            "**Tool-owned working state**",
            "**Attempt-local disposable scratch**",
            "**Crash residue**",
            "**Legacy workspace scratch**",
        ):
            self.assertIn(label, section)
        self.assertIn("workflow-state ownership and lifecycle classification", self.readiness)
        self.assertIn("tool-owned working state under its tool's contract", self.agents)
        for projection in (
            self.codex,
            self.claude,
            normalized(DOCS / "prompt-contracts.md"),
            normalized(DOCS / "prompts.md"),
        ):
            self.assertIn("Revalidate containment and identity", projection)
            self.assertIn("repo-readiness.md#repo-local-workflow-state", projection)
        self.assertIn(
            "repo-readiness.md#repo-local-workflow-state",
            normalized(DOCS / "evidence-lifecycle.md"),
        )

    def test_darwin_and_linux_have_bounded_platform_projections(self):
        self.assertIn("/usr/bin/getconf DARWIN_USER_TEMP_DIR", self.readiness)
        self.assertIn("bounded Linux design from CAK-155", self.readiness)
        self.assertIn("pending first Linux-host execution evidence", self.readiness)
        self.assertIn("exact sticky shared-temporary mode `01777`", self.readiness)
        self.assertIn("Windows and other mappings remain unqualified", self.readiness)

    def test_nearby_guidance_does_not_restore_a_persistent_default(self):
        self.assertNotIn("Keep temporary workflow state repo-local", self.agents)
        self.assertIn("attempt-local disposable scratch", self.agents)
        self.assertIn("attempt-local scratch", self.engineering)
        self.assertIn("allocated only through its platform's qualified route", self.engineering)
        self.assertIn("helper API or environment variable selects allocation mechanics", self.codex)
        self.assertNotIn("Use repo-local scratch paths for workflow artifacts", self.codex)
        self.assertNotIn("Ordinary repo-local scratch", self.evidence)
        self.assertIn("attempt-local scratch is not a substitute", self.evidence)
        self.assertIn("use attempt-local scratch only", self.claude)


if __name__ == "__main__":
    unittest.main()
