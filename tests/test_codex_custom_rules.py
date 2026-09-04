from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".codex" / "rule-templates" / "custom.rules"


class CodexCustomRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.codex = shutil.which("codex")

    def check(self, *command: str) -> dict[str, object]:
        if self.codex is None:
            self.skipTest("codex CLI is required for execpolicy behavior checks")
        result = subprocess.run(
            [self.codex, "execpolicy", "check", "--rules", str(RULES), "--", *command],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def assert_falls_through(self, *command: str) -> None:
        result = self.check(*command)
        self.assertEqual(result.get("matchedRules"), [])
        self.assertNotIn("decision", result)

    def assert_prompts(self, *command: str) -> None:
        result = self.check(*command)
        self.assertEqual(result.get("decision"), "prompt")
        self.assertTrue(result.get("matchedRules"))

    def assert_forbidden(self, *command: str) -> None:
        result = self.check(*command)
        self.assertEqual(result.get("decision"), "forbidden")
        self.assertTrue(result.get("matchedRules"))

    def test_routine_local_development_falls_through_to_sandbox(self) -> None:
        commands = (
            ("git", "rebase", "origin/main"),
            ("git", "merge", "topic"),
            ("git", "cherry-pick", "abc123"),
            ("git", "revert", "abc123"),
            ("git", "worktree", "remove", "--", ".worktrees/topic"),
            ("cp", "source", "destination"),
            ("rsync", "-a", "source/", "destination/"),
            ("mkdir", "build"),
            ("mv", "source", "destination"),
            ("rm", "obsolete-file"),
            ("rmdir", "empty-directory"),
            ("gh", "search", "code", "needle", "--json", "textMatches"),
            ("gh", "pr", "view", "123"),
            ("gh", "repo", "view", "owner/repository"),
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_falls_through(*command)

    def test_meaningful_authority_boundaries_prompt(self) -> None:
        commands = (
            ("git", "reset", "--hard", "HEAD~1"),
            ("git", "worktree", "remove", "--force", ".worktrees/topic"),
            ("git", "push", "--force-with-lease", "origin", "HEAD"),
            ("gh", "pr", "merge", "123"),
            ("gh", "repo", "delete", "owner/repository"),
            ("gh", "release", "create", "v1.0.0"),
            ("gh", "auth", "token"),
            ("codex", "--dangerously-bypass-approvals-and-sandbox", "exec", "task"),
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_prompts(*command)

    def test_raw_github_api_routes_are_forbidden(self) -> None:
        commands = (
            ("gh", "api", "repos/owner/repository"),
            ("gh", "api", "graphql", "-f", "query={viewer{login}}"),
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_forbidden(*command)

    def test_shell_wrapped_contained_copy_falls_through_to_sandbox(self) -> None:
        self.assert_falls_through(
            "/bin/zsh",
            "-lc",
            "cp private-attempt-a/prompt.md private-attempt-b/prompt.md",
        )


if __name__ == "__main__":
    unittest.main()
