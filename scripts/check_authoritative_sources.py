#!/usr/bin/env python3
"""Emit advisory warnings for non-authoritative public API source links."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse


URL_RE = re.compile(r"https?://[^\s<>)\]}\"']+")
GUIDANCE = "Use official provider documentation for public API evidence"
PUBLIC_API_CONTEXT_RE = re.compile(
    r"\b("
    r"api reference|cloud provider|eventual consistency|rate limits?|release notes|"
    r"saas api|api|auth|authentication|authorization|changelog|cli|endpoint|graphql|"
    r"idempotency|openapi|pagination|rest|retry|retryability|sdk|token|webhook"
    r")\b",
    re.IGNORECASE,
)

POLICY_PATH = Path(__file__).with_name("authoritative_sources.json")
DNS_LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
DOMAIN_RE = re.compile(rf"{DNS_LABEL}(?:\.{DNS_LABEL})+")
IGNORED_MARKDOWN_PATH_PARTS = (
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".worktrees",
    "node_modules",
    "vendor",
)
JUSTIFICATION_RE = re.compile(
    r"\b("
    r"source justification|source exception|"
    r"non-authoritative-source-ok|third-party-source-ok"
    r")\s*:\s*\S",
    re.IGNORECASE,
)


class SourcePolicy(NamedTuple):
    exact_hosts: frozenset[str]
    exact_urls: frozenset[str]
    repository_host: str
    repositories: frozenset[str]
    project_owners: frozenset[str]
    third_party_domain_suffixes: frozenset[str]


def load_source_policy(path: Path) -> SourcePolicy:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("source policy must be a JSON object")

    def entries(name: str) -> frozenset[str]:
        values = data.get(name)
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values
        ):
            raise ValueError(f"source policy {name} must be an array of non-empty strings")
        return frozenset(values)

    repository_host = data.get("repository_host")
    if not isinstance(repository_host, str) or not DOMAIN_RE.fullmatch(repository_host):
        raise ValueError("source policy repository_host must be a bare DNS host")
    return SourcePolicy(
        entries("exact_hosts"),
        entries("exact_urls"),
        repository_host,
        entries("repositories"),
        entries("project_owners"),
        entries("third_party_domain_suffixes"),
    )


def normalize_domain(hostname: str | None) -> str:
    return (hostname or "").lower().removesuffix(".")


def matches_domain_suffix(domain: str, suffix: str) -> bool:
    return domain == suffix or domain.endswith(f".{suffix}")


def clean_url(url: str) -> str:
    url = url.rstrip(".,;:!?")
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def configured_domains(raw_values: list[str]) -> frozenset[str]:
    domains: set[str] = set()
    for raw_value in raw_values:
        for value in re.split(r"[\s,]+", raw_value):
            if not value:
                continue
            domain = normalize_domain(value)
            if len(domain) > 253 or not DOMAIN_RE.fullmatch(domain):
                raise ValueError("invalid official domain override. Use only bare DNS domains")
            domains.add(domain)
    return frozenset(domains)


def is_official(
    url: str,
    policy: SourcePolicy,
    official_suffixes: frozenset[str],
) -> bool:
    if url in policy.exact_urls:
        return True

    parsed = urlparse(url)
    domain = normalize_domain(parsed.hostname)
    if domain in policy.exact_hosts or any(
        matches_domain_suffix(domain, suffix) for suffix in official_suffixes
    ):
        return True
    if domain != policy.repository_host:
        return False

    parts = parsed.path.removeprefix("/").lower().split("/", 2)
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return False
    owner, repository = parts[:2]
    return owner in policy.project_owners or f"{owner}/{repository}" in policy.repositories


def reason_for(url: str, policy: SourcePolicy) -> tuple[str, str]:
    domain = normalize_domain(urlparse(url).hostname)
    if any(matches_domain_suffix(domain, suffix) for suffix in policy.third_party_domain_suffixes):
        return domain, "known third-party discussion or publishing domain"
    return domain, "domain is not in the authoritative source allowlist"


def justified(lines: list[str], index: int) -> bool:
    for marker_index in range(max(0, index - 1), min(len(lines), index + 2)):
        if JUSTIFICATION_RE.search(lines[marker_index]) is None:
            continue
        marker_neighborhood = lines[
            max(0, marker_index - 1) : min(len(lines), marker_index + 2)
        ]
        # A marker with multiple nearby links cannot identify which it excuses.
        if sum(len(URL_RE.findall(line)) for line in marker_neighborhood) == 1:
            return True
    return False


def public_api_context(lines: list[str], index: int) -> str | None:
    """Return the nearby API evidence phrase that makes a URL worth checking."""
    nearby = " ".join(lines[max(0, index - 1) : min(len(lines), index + 2)])
    match = PUBLIC_API_CONTEXT_RE.search(nearby)
    return match.group(0) if match else None


def scan_text(
    label: str,
    text: str,
    policy: SourcePolicy,
    official_suffixes: frozenset[str] = frozenset(),
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    lines = text.splitlines()

    for index, line in enumerate(lines):
        for match in URL_RE.findall(line):
            url = clean_url(match)
            try:
                parsed_url = urlparse(url)
            except ValueError:
                # URL-like text can still contain malformed hosts (for
                # example, an unmatched IPv6 bracket). It is not actionable
                # source evidence, so do not emit a warning with an empty or
                # misleading domain.
                continue
            if not parsed_url.hostname:
                continue
            if is_official(url, policy, official_suffixes) or justified(lines, index):
                continue
            context = public_api_context(lines, index)
            if context is None:
                continue

            domain, reason = reason_for(url, policy)
            findings.append(
                {
                    "domain": domain,
                    "url": url,
                    "label": label,
                    "line": index + 1,
                    "reason": reason,
                    "context": context,
                    "count": 1,
                }
            )

    return findings


def event_payload() -> dict:
    path = Path(os.environ.get("GITHUB_EVENT_PATH", ""))
    if not path.is_file():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def pr_body(payload: dict) -> str | None:
    return os.environ.get("AUTHORITATIVE_SOURCE_PR_BODY") or payload.get("pull_request", {}).get("body")


def changed_markdown_files(base_ref: str | None, head_ref: str | None) -> list[Path]:
    if not base_ref or not head_ref:
        return []

    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "-z",
            "--diff-filter=ACMRT",
            base_ref,
            head_ref,
            "--",
            "*.md",
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        print("authoritative-source-check: changed Markdown detection unavailable; scanning PR body only")
        return []

    return [Path(name) for name in result.stdout.split("\0") if name]


def markdown_sources(paths: list[Path]) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    for path in paths:
        if path.is_symlink():
            print(f"authoritative-source-check: skipped symbolic link {path}")
            continue
        if not path.is_file():
            continue
        try:
            sources.append((str(path), path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            print(f"authoritative-source-check: skipped non-UTF-8 file {path}")
        except OSError:
            print(f"authoritative-source-check: skipped unreadable file {path}")
    return sources


def is_scannable_markdown_path(path: Path) -> bool:
    return not any(part in IGNORED_MARKDOWN_PATH_PARTS for part in path.parts)


def all_markdown_files(root: Path = Path(".")) -> list[Path]:
    return sorted(
        path
        for path in root.glob("**/*.md")
        if not path.is_symlink() and is_scannable_markdown_path(path)
    )


def dedupe(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    by_domain: dict[str, dict[str, object]] = {}
    for finding in findings:
        domain = str(finding["domain"])
        if domain in by_domain:
            by_domain[domain]["count"] = int(by_domain[domain]["count"]) + 1
        else:
            by_domain[domain] = finding
    return [by_domain[domain] for domain in sorted(by_domain)]


def warning_line(finding: dict[str, object]) -> str:
    message = f"{finding['url']} detected. {GUIDANCE}."
    if int(finding["count"]) > 1:
        message += f" {finding['count']} URLs from this domain were detected."
    message += (
        f" Matched public API context: {finding['context']}. "
        "Replace with official docs or add a visible source justification if official docs are unavailable."
    )
    message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")

    title = "Non-authoritative public API source"
    label = str(finding["label"])
    if label.endswith(".md"):
        safe_label = (
            label.replace("%", "%25")
            .replace("\r", "%0D")
            .replace("\n", "%0A")
            .replace(":", "%3A")
            .replace(",", "%2C")
        )
        return f"::warning file={safe_label},line={finding['line']},title={title}::{message}"
    return f"::warning title={title}::{message}"


def report(findings: list[dict[str, object]]) -> None:
    if not findings:
        print("Authoritative source check: no non-authoritative source URLs found.")
        return

    print("Authoritative source check: advisory warnings only; build will continue.")
    for finding in findings:
        location = str(finding["label"])
        if location.endswith(".md"):
            location = f"{location}:{finding['line']}"
        location = location.replace("\r", "\\r").replace("\n", "\\n")

        print(warning_line(finding))
        print(f"- {finding['domain']}: {finding['url']}")
        print(f"  location: {location}")
        print(f"  reason: {finding['reason']}")
        print(f"  matched public API context: {finding['context']}")
        print(f"  guidance: {GUIDANCE}.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref")
    parser.add_argument("--head-ref")
    parser.add_argument("--all-markdown", action="store_true")
    parser.add_argument("--pr-body-file", type=Path)
    parser.add_argument(
        "--official-domain",
        action="append",
        default=[],
        help="Additional bare documentation domain covering that host and its subdomains.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        policy = load_source_policy(POLICY_PATH)
        official_suffixes = configured_domains(
            args.official_domain + [os.environ.get("AUTHORITATIVE_SOURCE_OFFICIAL_DOMAINS", "")]
        )
    except (OSError, ValueError) as error:
        print(f"authoritative-source-check: {error}", file=sys.stderr)
        return 2
    payload = event_payload()
    sources: list[tuple[str, str]] = []

    if args.pr_body_file:
        sources.append(("PR body", args.pr_body_file.read_text(encoding="utf-8")))
    elif body := pr_body(payload):
        sources.append(("PR body", body))

    if args.all_markdown:
        markdown_files = all_markdown_files()
    else:
        pull_request = payload.get("pull_request", {})
        base_ref = (
            args.base_ref
            or os.environ.get("AUTHORITATIVE_SOURCE_BASE_REF")
            or pull_request.get("base", {}).get("sha")
        )
        head_ref = (
            args.head_ref
            or os.environ.get("AUTHORITATIVE_SOURCE_HEAD_REF")
            or os.environ.get("GITHUB_SHA")
            or pull_request.get("head", {}).get("sha")
        )
        markdown_files = changed_markdown_files(base_ref, head_ref)

    findings: list[dict[str, object]] = []
    for label, text in sources + markdown_sources(markdown_files):
        findings.extend(scan_text(label, text, policy, official_suffixes))

    report(dedupe(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
