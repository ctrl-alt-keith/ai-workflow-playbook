#!/usr/bin/env python3
"""Emit advisory warnings for non-authoritative public API source links."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
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

DEFAULT_OFFICIAL_SUFFIXES = (
    "akamai.com",
    "linode.com",
    "python.org",
    "cloud.google.com",
    "developers.google.com",
    "firebase.google.com",
    "developer.atlassian.com",
    "docs.atlassian.com",
    "support.atlassian.com",
)
OFFICIAL_GITHUB_DOMAINS = {"api.github.com", "docs.github.com"}
OFFICIAL_GITHUB_PATH_MARKERS = (
    "/github/docs",
    "/github/rest-api-description",
    "openapi",
)
SAME_ORG_GITHUB_OWNERS = {"ctrl-alt-keith"}
KNOWN_THIRD_PARTY_SUFFIXES = ("stackoverflow.com", "medium.com", "dev.to")
JUSTIFICATION_RE = re.compile(
    r"\b("
    r"source justification|source exception|"
    r"non-authoritative-source-ok|third-party-source-ok"
    r")\s*:\s*\S",
    re.IGNORECASE,
)


def normalize_domain(hostname: str | None) -> str:
    domain = (hostname or "").lower().rstrip(".")
    return domain[4:] if domain.startswith("www.") else domain


def matches(domain: str, suffix: str) -> bool:
    return domain == suffix or domain.endswith(f".{suffix}")


def clean_url(url: str) -> str:
    url = url.rstrip(".,;:!?")
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def is_same_org_github_repo(path: str) -> bool:
    parts = [part for part in path.lower().split("/") if part]
    return len(parts) >= 2 and parts[0] in SAME_ORG_GITHUB_OWNERS


def configured_domains(raw_values: list[str]) -> tuple[str, ...]:
    domains: list[str] = []
    for raw_value in raw_values:
        for value in re.split(r"[\s,]+", raw_value):
            if not value:
                continue
            parsed = urlparse(value if "://" in value else f"//{value}")
            domain = normalize_domain(parsed.hostname or value)
            if domain and domain not in domains:
                domains.append(domain)
    return tuple(domains)


def is_official(
    url: str,
    official_suffixes: tuple[str, ...] = DEFAULT_OFFICIAL_SUFFIXES,
) -> bool:
    parsed = urlparse(url)
    domain = normalize_domain(parsed.hostname)
    path = parsed.path.lower()

    if any(matches(domain, suffix) for suffix in official_suffixes):
        return True
    if domain in OFFICIAL_GITHUB_DOMAINS:
        return True
    if domain == "github.com":
        return is_same_org_github_repo(path) or any(
            marker in path for marker in OFFICIAL_GITHUB_PATH_MARKERS
        )
    return False


def reason_for(url: str) -> tuple[str, str]:
    domain = normalize_domain(urlparse(url).hostname)
    if any(matches(domain, suffix) for suffix in KNOWN_THIRD_PARTY_SUFFIXES):
        return domain, "known third-party discussion or publishing domain"
    return domain, "domain is not in the authoritative source allowlist"


def justified(lines: list[str], index: int) -> bool:
    nearby = " ".join(lines[max(0, index - 1) : min(len(lines), index + 2)]).lower()
    return JUSTIFICATION_RE.search(nearby) is not None


def public_api_context(lines: list[str], index: int) -> str | None:
    """Return the nearby API evidence phrase that makes a URL worth checking."""
    nearby = " ".join(lines[max(0, index - 1) : min(len(lines), index + 2)])
    match = PUBLIC_API_CONTEXT_RE.search(nearby)
    return match.group(0) if match else None


def scan_text(
    label: str,
    text: str,
    official_suffixes: tuple[str, ...] = DEFAULT_OFFICIAL_SUFFIXES,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    lines = text.splitlines()

    for index, line in enumerate(lines):
        for match in URL_RE.findall(line):
            url = clean_url(match)
            if is_official(url, official_suffixes) or justified(lines, index):
                continue
            context = public_api_context(lines, index)
            if context is None:
                continue

            domain, reason = reason_for(url)
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

    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def markdown_sources(paths: list[Path]) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            sources.append((str(path), path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            print(f"authoritative-source-check: skipped non-UTF-8 file {path}")
    return sources


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
        return f"::warning file={label},line={finding['line']},title={title}::{message}"
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
        help="Additional official documentation domain suffix. May be repeated or comma-separated.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = event_payload()
    official_suffixes = DEFAULT_OFFICIAL_SUFFIXES + configured_domains(
        args.official_domain + [os.environ.get("AUTHORITATIVE_SOURCE_OFFICIAL_DOMAINS", "")]
    )
    sources: list[tuple[str, str]] = []

    if args.pr_body_file:
        sources.append(("PR body", args.pr_body_file.read_text(encoding="utf-8")))
    elif body := pr_body(payload):
        sources.append(("PR body", body))

    if args.all_markdown:
        markdown_files = sorted(Path(".").glob("**/*.md"))
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
        findings.extend(scan_text(label, text, official_suffixes))

    report(dedupe(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
