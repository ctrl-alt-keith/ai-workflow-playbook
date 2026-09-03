from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def section(path: Path, heading: str) -> str:
    contents = path.read_text(encoding="utf-8")
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        contents,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return " ".join(match.group("body").split())


class MinimumSufficientRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retrieval = section(
            DOCS / "source-first-retrieval.md", "Minimum-Sufficient Retrieval"
        )
        cls.readiness = section(
            DOCS / "repo-readiness.md", "Command Form And Intent Visibility"
        )
        cls.prompts = section(DOCS / "prompts.md", "Repository Implementation Task")

    def test_canonical_rule_binds_retrieval_to_the_decision(self):
        for pattern in (
            r"minimum sufficient authoritative evidence.*claim or decision",
            r"evidence boundary.*before retrieval",
            r"provider objects.*more authoritative",
            r"not necessary.*omit.*speculative inventory",
            r"materially necessary fact.*partial or blocked",
        ):
            self.assertRegex(self.retrieval, pattern)

    def test_raw_provider_reads_require_a_concrete_material_fact(self):
        for pattern in (
            r"repository-native `git`.*high-level provider CLI.*connected GitHub",
            r"absence of a high-level convenience command.*does not.*justify.*`gh api`",
            r"lower-level provider read only when.*fact is materially necessary",
            r"state the exact missing fact.*why it matters.*first-class surfaces",
            r"Specialized evidence-surface audits.*constrained low-level read path",
            r"provider API behavior.*itself the subject.*inspect that API directly",
        ):
            self.assertRegex(self.retrieval, pattern)

    def test_collision_risk_does_not_require_a_provider_inventory(self):
        for contents in (self.retrieval, self.prompts):
            for phrase in (
                "current `main`",
                "relevant pull requests",
                "target files",
                "specifically identified refs",
            ):
                self.assertIn(phrase, contents)
        self.assertIn(
            "Do not inventory every branch, ref, workflow, or provider object",
            self.prompts,
        )

    def test_prompt_and_command_guidance_route_to_the_canonical_rule(self):
        self.assertIn(
            "docs/source-first-retrieval.md#minimum-sufficient-retrieval",
            self.prompts,
        )
        self.assertIn(
            "source-first-retrieval.md#minimum-sufficient-retrieval",
            self.readiness,
        )
        self.assertRegex(
            self.readiness,
            r"materially necessary fact.*minimum-sufficient retrieval.*lower-level read",
        )


if __name__ == "__main__":
    unittest.main()
