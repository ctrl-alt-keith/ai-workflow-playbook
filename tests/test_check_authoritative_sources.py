from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_authoritative_sources.py"
SPEC = importlib.util.spec_from_file_location("check_authoritative_sources", SCRIPT_PATH)
assert SPEC is not None
scanner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(scanner)


class AuthoritativeSourceScannerTest(unittest.TestCase):
    exact_reference = "https://docs.example.test/reference/list/"

    def setUp(self) -> None:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.fixture_script = root / SCRIPT_PATH.name
        self.fixture_script.write_bytes(SCRIPT_PATH.read_bytes())
        self.fixture_policy = root / "authoritative_sources.json"
        self.fixture_policy.write_text(
            json.dumps(
                {
                    "exact_hosts": ["api.example.test"],
                    "exact_urls": [self.exact_reference],
                    "repository_host": "forge.example.test",
                    "repositories": ["provider/reference"],
                    "project_owners": ["project"],
                    "third_party_domain_suffixes": ["forum.example.test"],
                }
            ),
            encoding="utf-8",
        )
        self.policy = scanner.load_source_policy(self.fixture_policy)

    def run_scanner_cli(
        self,
        args: list[str],
        cwd: Path | None = None,
        official_domains: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        # The scanner also reads the live pull-request body from the CI event
        # payload; keep that out of the fixture so the test scans only its own inputs.
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"GITHUB_EVENT_PATH", "GITHUB_SHA"}
            and not key.startswith("AUTHORITATIVE_SOURCE_")
        }
        if official_domains is not None:
            environment["AUTHORITATIVE_SOURCE_OFFICIAL_DOMAINS"] = official_domains
        return subprocess.run(
            [sys.executable, str(self.fixture_script), *args],
            check=False,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )

    def test_flags_third_party_url_in_public_api_context(self) -> None:
        findings = scanner.scan_text(
            "PR body",
            "API pagination behavior source: https://forum.example.test/questions/1",
            self.policy,
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["domain"], "forum.example.test")
        self.assertEqual(findings[0]["reason"], "known third-party discussion or publishing domain")
        self.assertEqual(findings[0]["context"].lower(), "api")

    def test_ignores_non_api_context_url(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "Planning notes live at https://example.test/roadmap for reference.",
            self.policy,
        )

        self.assertEqual(findings, [])

    def test_source_origin_requires_an_exact_host_and_repository(self) -> None:
        official = (
            "https://api.example.test/rest",
            "https://forge.example.test/provider/reference/blob/main/rest.md",
            "https://forge.example.test/project/guide",
        )
        untrusted = (
            "https://sub.api.example.test/rest",
            "https://api.example.test.invalid/rest",
            "https://sub.forge.example.test/provider/reference",
            "https://forge.example.test/provider/reference-fork",
            "https://forge.example.test/another-owner/reference",
            "https://forge.example.test/project-alias/guide",
        )

        for url in official:
            with self.subTest(url=url):
                self.assertEqual(scanner.scan_text("PR body", f"REST API source: {url}", self.policy), [])
        for url in untrusted:
            with self.subTest(url=url):
                findings = scanner.scan_text("PR body", f"REST API source: {url}", self.policy)
                self.assertEqual([finding["url"] for finding in findings], [url])

    def test_cli_matches_only_the_configured_exact_url(self) -> None:
        official = self.exact_reference
        cases = (
            (official, False),
            ("https://docs.example.test/reference/", True),
            (f"{official}child/", True),
            (f"{official}?view=other", True),
            ("https://docs.example.test.invalid/reference/list/", True),
        )

        with tempfile.TemporaryDirectory() as tmp:
            body_path = Path(tmp) / "pr-body.md"
            for url, warns in cases:
                with self.subTest(url=url):
                    body_path.write_text(f"API reference: [source]({url})\n", encoding="utf-8")
                    result = self.run_scanner_cli(["--pr-body-file", str(body_path)])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if warns:
                        self.assertIn(f"::{url} detected.", result.stdout)
                    else:
                        self.assertIn("no non-authoritative source URLs found", result.stdout)

    def test_domain_overrides_only_suppress_matching_hosts_and_subdomains(self) -> None:
        allowed = (
            "https://docs.fixture.test/reference",
            "https://sdk.docs.fixture.test/reference",
            "https://another.fixture.test/reference",
        )
        unrelated = (
            "https://notdocs.fixture.test/reference",
            "https://docs.fixture.test.invalid/reference",
        )
        domains = "docs.fixture.test, another.fixture.test"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "example.md").write_text(
                "\n".join(f"API source: {url}" for url in (*allowed, *unrelated)),
                encoding="utf-8",
            )
            for flags, env in ((["--official-domain", domains], None), ([], domains)):
                with self.subTest(cli=bool(flags)):
                    result = self.run_scanner_cli(["--all-markdown", *flags], cwd=root, official_domains=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.count("::warning "), len(unrelated))
                    for url in allowed:
                        self.assertNotIn(url, result.stdout)
                    for url in unrelated:
                        self.assertIn(f"::{url} detected.", result.stdout)

    def test_domain_overrides_reject_urls_and_paths(self) -> None:
        for value in ("https://docs.fixture.test", "docs.fixture.test/reference"):
            for flags, env in ((["--official-domain", value], None), ([], value)):
                with self.subTest(value=value, cli=bool(flags)):
                    result = self.run_scanner_cli(flags, official_domains=env)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("invalid official domain override", result.stderr)

    def test_cli_refuses_to_scan_without_policy(self) -> None:
        self.fixture_policy.unlink()

        result = self.run_scanner_cli([])

        self.assertEqual(result.returncode, 2)
        self.assertIn(self.fixture_policy.name, result.stderr)

    def test_changed_markdown_files_parses_nul_delimited_git_output(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["git", "diff"],
            returncode=0,
            stdout="docs/guide.md\0README.md\0",
        )

        with mock.patch.object(scanner.subprocess, "run", return_value=completed):
            paths = scanner.changed_markdown_files("base", "head")

        self.assertEqual(paths, [Path("docs/guide.md"), Path("README.md")])

    def test_cli_scans_changed_markdown_with_newline_in_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            changed = docs_dir / "line\nbreak.md"
            changed.write_text("No API source yet.\n", encoding="utf-8")
            subprocess.run(["git", "add", "docs"], cwd=root, check=True)
            subprocess.run(
                [
                    "git", "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                    "-c", "user.email=test@example.com", "commit", "-qm", "base",
                ],
                cwd=root,
                check=True,
            )
            changed.write_text(
                "REST retry source: https://unrelated.test/changed\n", encoding="utf-8"
            )
            subprocess.run(["git", "add", "docs"], cwd=root, check=True)
            subprocess.run(
                [
                    "git", "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                    "-c", "user.email=test@example.com", "commit", "-qm", "change source",
                ],
                cwd=root,
                check=True,
            )

            result = self.run_scanner_cli(
                ["--base-ref", "HEAD~1", "--head-ref", "HEAD"], cwd=root
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("https://unrelated.test/changed", result.stdout)
        self.assertIn("::warning file=docs/line%0Abreak.md,line=1,", result.stdout)
        self.assertEqual(result.stdout.count("::warning "), 1)

    def test_changed_markdown_files_fails_closed_when_git_detection_fails(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["git", "diff"],
            returncode=1,
            stdout="docs/ignored.md\n",
        )

        with mock.patch.object(scanner.subprocess, "run", return_value=completed):
            with mock.patch("builtins.print") as print_mock:
                paths = scanner.changed_markdown_files("base", "head")

        self.assertEqual(paths, [])
        print_mock.assert_called_once_with(
            "authoritative-source-check: changed Markdown detection unavailable; scanning PR body only"
        )

    def test_cli_scans_changed_markdown_without_reporting_unchanged_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            changed = docs_dir / "changed.md"
            unchanged = docs_dir / "unchanged.md"
            changed.write_text("No API source yet.\n", encoding="utf-8")
            unchanged.write_text(
                "REST retry source: https://unchanged.test/reference\n", encoding="utf-8"
            )
            subprocess.run(["git", "add", "docs"], cwd=root, check=True)
            subprocess.run(
                [
                    "git", "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                    "-c", "user.email=test@example.com", "commit", "-qm", "base",
                ],
                cwd=root,
                check=True,
            )
            changed.write_text(
                "REST retry source: https://unrelated.test/changed\n", encoding="utf-8"
            )
            subprocess.run(["git", "add", "docs/changed.md"], cwd=root, check=True)
            subprocess.run(
                [
                    "git", "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                    "-c", "user.email=test@example.com", "commit", "-qm", "change source",
                ],
                cwd=root,
                check=True,
            )

            result = self.run_scanner_cli(
                ["--base-ref", "HEAD~1", "--head-ref", "HEAD"], cwd=root
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("https://unrelated.test/changed", result.stdout)
        self.assertIn("location: docs/changed.md:1", result.stdout)
        self.assertNotIn("https://unchanged.test/reference", result.stdout)

    def test_nearby_source_justification_suppresses_warning(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "\n".join(
                [
                    "Source justification: official docs unavailable for this API edge case.",
                    "Fallback context: https://unrelated.test/example/post",
                ]
            ),
            self.policy,
        )

        self.assertEqual(findings, [])

    def test_one_marker_does_not_suppress_multiple_nearby_sources(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "\n".join(
                [
                    "REST retry source: https://unrelated.test/example/first",
                    "Source justification: official docs unavailable for this API edge case.",
                    "SDK retry source: https://another.test/example/second",
                ]
            ),
            self.policy,
        )

        self.assertEqual(
            [finding["domain"] for finding in findings], ["unrelated.test", "another.test"]
        )

    def test_suppression_marker_without_reason_does_not_suppress_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "pr-body.md"
            url = "https://unrelated.test/example/post"
            body.write_text(f"Source justification: \nREST retry behavior source: {url}\n", encoding="utf-8")
            result = self.run_scanner_cli(["--pr-body-file", str(body)])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"::{url} detected.", result.stdout)

    def test_cli_pr_body_file_reports_advisory_warning_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body_path = Path(tmp) / "pr-body.md"
            body_path.write_text(
                "\n".join(
                    [
                        "REST retry behavior source: https://unrelated.test/example/post",
                        "API pagination source: https://unrelated.test/example/second",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_scanner_cli(["--pr-body-file", str(body_path)])

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("Authoritative source check: advisory warnings only", result.stdout)
        self.assertIn("::warning title=Non-authoritative public API source::", result.stdout)
        self.assertIn("2 URLs from this domain were detected", result.stdout)
        self.assertIn("- unrelated.test: https://unrelated.test/example/post", result.stdout)
        self.assertIn("location: PR body", result.stdout)

    def test_cli_all_markdown_reports_file_line_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (docs_dir / "example.md").write_text(
                "\n".join(
                    [
                        "# Example",
                        "REST retry behavior source: https://unrelated.test/example/post",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_scanner_cli(["--all-markdown"], cwd=root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn(
            "::warning file=docs/example.md,line=2,title=Non-authoritative public API source::",
            result.stdout,
        )
        self.assertIn("location: docs/example.md:2", result.stdout)

    def test_cli_all_markdown_ignores_worktree_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_dir = root / "docs"
            worktree_docs_dir = root / ".worktrees" / "feature" / "docs"
            docs_dir.mkdir()
            worktree_docs_dir.mkdir(parents=True)
            (docs_dir / "example.md").write_text(
                "REST retry behavior source: https://unrelated.test/source-doc",
                encoding="utf-8",
            )
            (worktree_docs_dir / "example.md").write_text(
                "REST retry behavior source: https://unrelated.test/worktree-doc",
                encoding="utf-8",
            )

            result = self.run_scanner_cli(["--all-markdown"], cwd=root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("https://unrelated.test/source-doc", result.stdout)
        self.assertNotIn("https://unrelated.test/worktree-doc", result.stdout)

    def test_markdown_sources_skip_symbolic_links_without_reading_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "machine-local-source"
            target.write_text(
                "REST retry behavior source: https://unrelated.test/private-source",
                encoding="utf-8",
            )
            link = root / "linked.md"
            link.symlink_to(target)

            sources = scanner.markdown_sources([link])

        self.assertEqual(sources, [])

    def test_markdown_sources_skip_unreadable_files_without_aborting_scan(self) -> None:
        unreadable = Path("docs/unreadable.md")
        readable = Path("docs/readable.md")

        with mock.patch.object(Path, "is_symlink", return_value=False), mock.patch.object(
            Path, "is_file", return_value=True
        ), mock.patch.object(
            Path,
            "read_text",
            side_effect=[PermissionError("denied"), "https://example.test/readable"],
        ):
            with mock.patch("builtins.print") as print_mock:
                sources = scanner.markdown_sources([unreadable, readable])

        self.assertEqual(sources, [("docs/readable.md", "https://example.test/readable")])
        print_mock.assert_called_once_with(
            "authoritative-source-check: skipped unreadable file docs/unreadable.md"
        )


if __name__ == "__main__":
    unittest.main()
