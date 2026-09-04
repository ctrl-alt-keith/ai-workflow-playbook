from __future__ import annotations

import importlib.util
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
    def run_scanner_cli(
        self,
        args: list[str],
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            check=False,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_flags_third_party_url_in_public_api_context(self) -> None:
        findings = scanner.scan_text(
            "PR body",
            "GitHub API pagination behavior source: https://stackoverflow.com/questions/1",
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["domain"], "stackoverflow.com")
        self.assertEqual(findings[0]["context"].lower(), "api")

    def test_ignores_non_api_context_url(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "Planning notes live at https://example.com/roadmap for reference.",
        )

        self.assertEqual(findings, [])

    def test_ignores_official_url_in_public_api_context(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "GitHub API pagination source: https://docs.github.com/en/rest/using-the-rest-api",
        )

        self.assertEqual(findings, [])

    def test_configured_official_domain_suppresses_warning(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "Cloud provider API source: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
            scanner.DEFAULT_OFFICIAL_SUFFIXES + ("docs.aws.amazon.com",),
        )

        self.assertEqual(findings, [])

    def test_google_official_doc_domains_are_allowed_by_default(self) -> None:
        urls = [
            "https://cloud.google.com/apis/docs/overview",
            "https://developers.google.com/workspace/gmail/api/guides",
            "https://firebase.google.com/docs/reference",
        ]

        for url in urls:
            with self.subTest(url=url):
                findings = scanner.scan_text(
                    "docs/example.md",
                    f"Google API source: {url}",
                )

                self.assertEqual(findings, [])

    def test_atlassian_official_doc_domains_are_allowed_by_default(self) -> None:
        urls = [
            "https://developer.atlassian.com/cloud/jira/platform/rest/v3/",
            "https://docs.atlassian.com/software/jira/docs/api/latest/",
            "https://support.atlassian.com/jira-cloud-administration/docs/",
        ]

        for url in urls:
            with self.subTest(url=url):
                findings = scanner.scan_text(
                    "docs/example.md",
                    f"Atlassian API source: {url}",
                )

                self.assertEqual(findings, [])

    def test_claude_docs_are_allowed_by_default(self) -> None:
        urls = [
            "https://docs.claude.com/en/docs/claude-code/memory",
            "https://docs.claude.com/en/docs/claude-code/sub-agents",
        ]

        for url in urls:
            with self.subTest(url=url):
                findings = scanner.scan_text(
                    "docs/example.md",
                    f"Claude Code CLI source: {url}",
                )

                self.assertEqual(findings, [])

    def test_openai_developer_docs_are_allowed_by_default(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "OpenAI API source: https://developers.openai.com/api/docs/guides/latest-model",
        )

        self.assertEqual(findings, [])

    def test_broad_openai_domain_still_warns(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "OpenAI API source: https://openai.com/news/example",
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["domain"], "openai.com")

    def test_google_and_atlassian_community_domains_still_warn(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "\n".join(
                [
                    "Google API source: https://blog.google/products/workspace/example",
                    "Atlassian API source: https://community.atlassian.com/t5/example/post",
                ]
            ),
        )

        self.assertEqual(
            [finding["domain"] for finding in findings],
            ["blog.google", "community.atlassian.com"],
        )

    def test_same_org_github_project_reference_is_intentionally_allowed(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "Project API behavior source: https://github.com/ctrl-alt-keith/example-repo/pull/1",
        )

        self.assertEqual(findings, [])

    def test_other_github_project_reference_still_warns(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "Project API behavior source: https://github.com/example/example-repo/pull/1",
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["domain"], "github.com")

    def test_official_github_source_repositories_are_allowed(self) -> None:
        urls = [
            "https://github.com/github/docs/blob/main/content/rest/about-the-rest-api.md",
            "https://github.com/github/rest-api-description/tree/main/descriptions",
        ]

        for url in urls:
            with self.subTest(url=url):
                findings = scanner.scan_text(
                    "docs/example.md",
                    f"GitHub API source: {url}",
                )

                self.assertEqual(findings, [])

    def test_github_path_keywords_do_not_allow_unrelated_repositories(self) -> None:
        urls = [
            "https://github.com/example/openapi-guide",
            "https://github.com/example/github/docs",
            "https://github.com/example/github-rest-api-description",
        ]

        for url in urls:
            with self.subTest(url=url):
                findings = scanner.scan_text(
                    "docs/example.md",
                    f"GitHub API source: {url}",
                )

                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0]["domain"], "github.com")

    def test_configured_domains_accept_comma_and_space_separated_values(self) -> None:
        domains = scanner.configured_domains(
            ["https://docs.aws.amazon.com, cloud.google.com learn.microsoft.com"]
        )

        self.assertEqual(
            domains,
            ("docs.aws.amazon.com", "cloud.google.com", "learn.microsoft.com"),
        )

    def test_changed_markdown_files_returns_only_nonempty_git_output_lines(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["git", "diff"],
            returncode=0,
            stdout="docs/guide.md\n\nREADME.md\n",
        )

        with mock.patch.object(scanner.subprocess, "run", return_value=completed):
            paths = scanner.changed_markdown_files("base", "head")

        self.assertEqual(paths, [Path("docs/guide.md"), Path("README.md")])

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

    def test_nearby_source_justification_suppresses_warning(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "\n".join(
                [
                    "Source justification: official docs unavailable for this API edge case.",
                    "Fallback context: https://medium.com/example/post",
                ]
            ),
        )

        self.assertEqual(findings, [])

    def test_suppression_marker_without_reason_does_not_suppress_warning(self) -> None:
        findings = scanner.scan_text(
            "docs/example.md",
            "\n".join(
                [
                    "non-authoritative-source-ok",
                    "REST retry behavior source: https://medium.com/example/post",
                ]
            ),
        )

        self.assertEqual(len(findings), 1)

    def test_cli_pr_body_file_reports_advisory_warning_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body_path = Path(tmp) / "pr-body.md"
            body_path.write_text(
                "\n".join(
                    [
                        "REST retry behavior source: https://dev.to/example/post",
                        "API pagination source: https://dev.to/example/second",
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
        self.assertIn("- dev.to: https://dev.to/example/post", result.stdout)
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
                        "REST retry behavior source: https://medium.com/example/post",
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
                "REST retry behavior source: https://medium.com/source-doc",
                encoding="utf-8",
            )
            (worktree_docs_dir / "example.md").write_text(
                "REST retry behavior source: https://medium.com/worktree-doc",
                encoding="utf-8",
            )

            result = self.run_scanner_cli(["--all-markdown"], cwd=root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("https://medium.com/source-doc", result.stdout)
        self.assertNotIn("https://medium.com/worktree-doc", result.stdout)

    def test_markdown_sources_skip_symbolic_links_without_reading_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "machine-local-source"
            target.write_text(
                "REST retry behavior source: https://medium.com/private-source",
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
            side_effect=[PermissionError("denied"), "https://example.com/readable"],
        ):
            with mock.patch("builtins.print") as print_mock:
                sources = scanner.markdown_sources([unreadable, readable])

        self.assertEqual(sources, [("docs/readable.md", "https://example.com/readable")])
        print_mock.assert_called_once_with(
            "authoritative-source-check: skipped unreadable file docs/unreadable.md"
        )


if __name__ == "__main__":
    unittest.main()
