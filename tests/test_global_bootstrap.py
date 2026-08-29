from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_global_bootstrap.py"
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"
ROUTER = PROJECTIONS / "bootstrap-router.md"
START_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


class GlobalBootstrapTests(unittest.TestCase):
    def marked(self, router: str) -> str:
        return f"{START_MARKER}\n{router}{END_MARKER}\n"

    def run_check(
        self, codex_file: Path, claude_file: Path, *, require_claude: bool = False
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(SCRIPT),
            "--codex-file",
            str(codex_file),
            "--claude-file",
            str(claude_file),
        ]
        if require_claude:
            command.append("--require-claude")
        return subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_one_router_encodes_persistent_material_change_boundary(self) -> None:
        exact_boundary = (
            "Before the first project action, and again only when the "
            "task/repository materially changes"
        )
        contents = ROUTER.read_text(encoding="utf-8")
        normalized = " ".join(contents.split())
        self.assertIn(exact_boundary, normalized)
        self.assertIn("reuse the still-current repository operating mode", normalized)
        self.assertIn("do not retrieve `start-here.md` again merely", normalized)
        self.assertIn(
            "When the first-action or material-change trigger applies, "
            "retrieving and applying `start-here.md` is the only permitted action:",
            normalized,
        )
        self.assertIn(
            "If it cannot be retrieved or read, the only permitted response is "
            "to say so plainly",
            normalized,
        )
        self.assertIn("do not proceed from memory", normalized)
        self.assertIn(
            "the only permitted action: Do not respond, reason about the task, "
            "or invoke another tool before applying it.",
            normalized,
        )
        for removed_copy in (
            "codex-AGENTS.md",
            "claude-CLAUDE.md",
            "chatgpt-custom-instructions.md",
        ):
            self.assertFalse((PROJECTIONS / removed_copy).exists())

    def test_distribution_names_each_hosted_provider_destination(self) -> None:
        readme = (PROJECTIONS / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        self.assertIn("immediate Codex desktop repair has exactly one", readme)
        self.assertIn("does not require a Codex project setting", readme)
        self.assertIn("ChatGPT account custom instructions", readme)
        self.assertIn("ChatGPT CAK project instructions", readme)
        self.assertIn("Claude profile instructions", readme)
        self.assertIn("Claude Cowork global instructions", readme)
        self.assertIn("distinct hosted configuration surfaces", readme)
        self.assertIn(
            "capability gap, not equivalent to the local byte check", normalized
        )
        self.assertIn("## Local Reconciliation", readme)
        self.assertIn(
            "python3 scripts/check_global_bootstrap.py --require-claude", readme
        )
        self.assertIn("Settings > Cowork > Global instructions", readme)

    def test_claude_adapter_preserves_scope_order_and_cowork_caveats(self) -> None:
        adapter = (ROOT / "docs" / "tool-adapters" / "claude.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(adapter.split())
        self.assertIn("managed policy, user instructions", normalized)
        self.assertIn("Project instructions appear in context after user", normalized)
        self.assertIn("./CLAUDE.md` or `./.claude/CLAUDE.md", normalized)
        self.assertIn("broader CAK-187 provider rollout", normalized)
        self.assertIn("--require-claude", normalized)
        self.assertIn("outside-working-directory imports", normalized)
        self.assertIn("desktop Cowork sessions", normalized)
        self.assertIn("symlink or hard link", normalized)
        self.assertIn("strips block-level HTML comments", normalized)

    def test_claude_adapter_routes_chat_cowork_and_code_surfaces(self) -> None:
        adapter = (ROOT / "docs" / "tool-adapters" / "claude.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(adapter.split())
        chat = adapter.split("### Claude Chat", 1)[1].split("### Claude Cowork", 1)[0]
        cowork = adapter.split("### Claude Cowork", 1)[1].split("### Claude Code", 1)[0]
        code = adapter.split("### Claude Code", 1)[1].split(
            "## Instruction Discovery And Precedence", 1
        )[0]
        for heading in (
            "## Surface And Invocation Routing",
            "### Claude Chat",
            "### Claude Cowork",
            "### Claude Code",
        ):
            self.assertIn(heading, adapter)
        self.assertIn("../core-model.md#surface-classes", adapter)
        self.assertIn("agentic-remote", normalized)
        self.assertIn("agentic-local", normalized)
        self.assertIn("Settings > Cowork > Global instructions", normalized)
        self.assertIn("#global-bootstrap-persistence", adapter)
        self.assertIn("#connector-availability-is-runtime-evidence", chat)
        self.assertIn("new turn or tool call", normalized)
        self.assertIn(
            "report the exact capability gap and stop", " ".join(chat.split())
        )
        self.assertIn(
            "task definition must name a qualified current-source route",
            " ".join(cowork.split()),
        )
        self.assertIn("duplicate transport is idempotent", " ".join(cowork.split()))
        self.assertIn(
            "does not substitute for either required source", " ".join(code.split())
        )
        self.assertIn("capability gap and stop", " ".join(code.split()))

    def test_validator_accepts_exact_blocks_with_unrelated_local_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex = self.marked(router)
            claude = self.marked(router)
            codex_file.write_text(
                f"Personal preface.\n\n{codex}\nPersonal suffix.\n", encoding="utf-8"
            )
            claude_file.write_text(
                f"Personal preface.\n\n{claude}\nPersonal suffix.\n", encoding="utf-8"
            )

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS Codex", result.stdout)
            self.assertIn("PASS Claude", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_validator_skips_absent_optional_claude_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "missing-CLAUDE.md"
            codex_file.write_text(
                self.marked(ROUTER.read_text(encoding="utf-8")), encoding="utf-8"
            )

            optional = self.run_check(codex_file, claude_file)
            required = self.run_check(
                codex_file, claude_file, require_claude=True
            )

            self.assertEqual(optional.returncode, 0, optional.stdout)
            self.assertIn("SKIP Claude: broader-rollout", optional.stdout)
            self.assertIn("PASS Codex", optional.stdout)
            self.assertEqual(required.returncode, 1)
            self.assertIn("FAIL Claude: missing local instruction file", required.stdout)

    def test_validator_normalizes_outer_newlines_symmetrically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8").rstrip("\n") + "\n\n"
            codex_file.write_text(self.marked(router), encoding="utf-8")
            claude_file.write_text(self.marked(router), encoding="utf-8")

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_reports_drift_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex = self.marked(router)
            claude = self.marked(router)
            codex_file.write_text(
                codex.replace("first project action", "every action"), encoding="utf-8"
            )
            claude_file.write_text(claude, encoding="utf-8")
            before = codex_file.read_bytes()

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL Codex: managed body differs", result.stdout)
            self.assertEqual(codex_file.read_bytes(), before)
            self.assertEqual(result.stderr, "")

    def test_validator_rejects_missing_or_duplicate_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            projection = self.marked(ROUTER.read_text(encoding="utf-8"))
            codex_file.write_text("unmanaged instructions only\n", encoding="utf-8")
            claude_file.write_text(projection + projection, encoding="utf-8")

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("expected exactly one", result.stdout)
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
