from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_authoritative_sources.py"
SPEC = importlib.util.spec_from_file_location("check_authoritative_sources", SCRIPT_PATH)
assert SPEC is not None
scanner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(scanner)


class AuthoritativeSourceScannerTest(unittest.TestCase):
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

    def test_configured_domains_accept_comma_and_space_separated_values(self) -> None:
        domains = scanner.configured_domains(
            ["https://docs.aws.amazon.com, cloud.google.com learn.microsoft.com"]
        )

        self.assertEqual(
            domains,
            ("docs.aws.amazon.com", "cloud.google.com", "learn.microsoft.com"),
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

    def test_warning_line_describes_actionable_public_api_remediation(self) -> None:
        finding = scanner.scan_text(
            "docs/example.md",
            "REST retry behavior source: https://dev.to/example/post",
        )[0]

        warning = scanner.warning_line(finding)

        self.assertIn("Non-authoritative public API source", warning)
        self.assertIn("Matched public API context: REST", warning)
        self.assertIn("Replace with official docs", warning)


if __name__ == "__main__":
    unittest.main()
