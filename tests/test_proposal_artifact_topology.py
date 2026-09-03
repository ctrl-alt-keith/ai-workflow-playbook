from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def markdown_section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    tail = text[start + len(heading) :]
    next_heading = re.search(r"\n#{1,3} ", tail)
    end = start + len(heading) + (next_heading.start() if next_heading else len(tail))
    return text[start:end]


def normalized(text: str) -> str:
    return " ".join(text.split())


class ProposalArtifactTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owner = markdown_section(
            DOCS / "repo-readiness.md",
            "### Current-phase mutation authority and proposal surfaces",
        )
        cls.lifecycle = markdown_section(
            DOCS / "feature-lifecycle.md",
            "## Branch And PR Rules",
        )
        cls.prompts = markdown_section(
            DOCS / "prompts.md",
            "### Repository-topology authorization check",
        )
        cls.owner_normalized = normalized(cls.owner)
        cls.lifecycle_normalized = normalized(cls.lifecycle)
        cls.prompts_normalized = normalized(cls.prompts)

    def test_owner_keeps_phase_mutation_and_capture_as_separate_decisions(self):
        ordered_questions = (
            "What is the current semantic phase?",
            "Does current human intent or a narrower owning workflow authorize repository mutation in that phase?",
            "Does the produced material qualify for durable governed-artifact capture?",
        )
        positions = [self.owner_normalized.index(question) for question in ordered_questions]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "Proposal-first and design-first describe a semantic decision boundary, not a Git topology",
            self.owner_normalized,
        )

    def test_discussion_first_cases_select_non_git_surfaces(self):
        rows = [line for line in self.owner.splitlines() if line.startswith("|")]
        compact = next(row for row in rows if "Discussion-first, compact proposal" in row)
        substantial = next(
            row for row in rows if "Discussion-first, substantial proposal" in row
        )
        for row in (compact, substantial):
            self.assertIn("Not authorized", row)
            self.assertNotIn("worktree", row.lower())
            self.assertNotIn("pull request", row.lower())
        self.assertIn("Active interaction", compact)
        self.assertIn("Existing governed-artifact route", substantial)

    def test_explicit_repository_artifacts_and_implementation_remain_available(self):
        rows = [line for line in self.owner.splitlines() if line.startswith("|")]
        design_doc = next(row for row in rows if "Explicit repository design document" in row)
        proposal_pr = next(row for row in rows if "Explicit proposal pull request" in row)
        implementation = next(row for row in rows if "Direct implementation" in row)
        self.assertIn("named artifact only", design_doc)
        self.assertIn("proposal surface only", proposal_pr)
        self.assertIn("proposal pull request", proposal_pr)
        self.assertIn("Normal implementation", implementation)

    def test_material_review_does_not_select_git(self):
        self.assertIn(
            "independent-review or material-doctrine requirement may require an exact durable proposal identity, but it does not select Git",
            self.owner_normalized,
        )
        self.assertIn(
            "Materiality or an independent-review requirement does not itself choose the proposal PR",
            self.lifecycle_normalized,
        )

    def test_generated_handoffs_require_current_phase_mutation_authority(self):
        for action in (
            "implementation mode",
            "worktree",
            "branch",
            "repository edit",
            "commit",
            "push",
            "pull request",
        ):
            self.assertIn(action, self.prompts_normalized)
        self.assertIn(
            "identify the current human direction or narrower owning-workflow rule that authorizes repository mutation in the current phase",
            self.prompts_normalized,
        )
        self.assertIn("zero-repository-mutation stop boundary", self.prompts_normalized)

    def test_exact_proposal_identity_rejects_empty_commit_and_mutable_pr_body(self):
        combined = " ".join(
            (self.owner_normalized, self.lifecycle_normalized, self.prompts_normalized)
        )
        self.assertIn("empty commit", combined)
        self.assertIn("mutable pull-request description", combined)
        self.assertIn("natural durable owner", combined)

    def test_shared_owner_routes_provider_selection_to_storage_contract(self):
        self.assertIn(
            "Use the issue-owned provider destination only when the current project's owning storage contract selects and admits that route",
            self.owner_normalized,
        )
        self.assertIn(
            "The shared Playbook does not select Dropbox or another provider as a universal destination",
            self.owner_normalized,
        )


if __name__ == "__main__":
    unittest.main()
