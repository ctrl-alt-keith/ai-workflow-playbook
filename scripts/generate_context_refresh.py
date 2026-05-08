from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

from workspace_repos import (
    WorkspaceRepoManifestError,
    read_workspace_repos,
)

DEFAULT_MANIFEST = Path("config/workspace-repos.txt")
OPEN_ITEM_LIMIT = 100
MERGED_PR_LIMIT = 5

REPO_CONTEXT_QUERY = """
query RepoContext($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    nameWithOwner
    defaultBranchRef {
      name
    }
    openPullRequests: pullRequests(
      states: OPEN
      first: 100
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      totalCount
      nodes {
        number
        title
        url
        updatedAt
        author {
          login
        }
      }
    }
    openIssues: issues(
      states: OPEN
      first: 100
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      totalCount
      nodes {
        number
        title
        url
        updatedAt
        author {
          login
        }
      }
    }
    recentMergedPullRequests: pullRequests(
      states: MERGED
      first: 5
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      nodes {
        number
        title
        url
        mergedAt
        author {
          login
        }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class RepoReport:
    name: str
    default_branch: str | None
    open_prs: dict[str, Any]
    open_issues: dict[str, Any]
    recent_merged_prs: list[dict[str, Any]]


@dataclass(frozen=True)
class UnavailableRepo:
    name: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a non-canonical current-state context refresh."
    )
    parser.add_argument(
        "--output",
        default="dist/context-refresh.md",
        type=Path,
        help="Markdown file to write.",
    )
    parser.add_argument(
        "--repo-manifest",
        default=DEFAULT_MANIFEST,
        type=Path,
        help="Workspace repo manifest to read.",
    )
    return parser.parse_args()


def require_gh() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI `gh` is required for make context-refresh.")

    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        detail = one_line(result.stderr or result.stdout or "unknown auth failure")
        raise RuntimeError(f"GitHub CLI is not authenticated: {detail}")


def run_graphql(owner: str, name: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-f",
            f"query={REPO_CONTEXT_QUERY}",
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        detail = one_line(result.stderr or result.stdout or "query failed")
        raise RuntimeError(detail)

    payload = json.loads(result.stdout)
    if payload.get("errors"):
        detail = one_line(json.dumps(payload["errors"], sort_keys=True))
        raise RuntimeError(detail)

    repository = payload.get("data", {}).get("repository")
    if not repository:
        raise RuntimeError("repository was not returned by GitHub")
    return repository


def collect_repo(repo: str) -> RepoReport:
    owner, name = repo.split("/", 1)
    repository = run_graphql(owner, name)
    default_branch = repository.get("defaultBranchRef") or {}
    return RepoReport(
        name=repo,
        default_branch=default_branch.get("name"),
        open_prs=repository["openPullRequests"],
        open_issues=repository["openIssues"],
        recent_merged_prs=repository["recentMergedPullRequests"]["nodes"],
    )


def collect_reports(repos: tuple[str, ...]) -> tuple[list[RepoReport], list[UnavailableRepo]]:
    reports: list[RepoReport] = []
    unavailable: list[UnavailableRepo] = []
    for repo in repos:
        try:
            reports.append(collect_repo(repo))
        except Exception as exc:
            unavailable.append(UnavailableRepo(repo, one_line(str(exc))))
    return reports, unavailable


def render_report(
    reports: list[RepoReport],
    unavailable: list[UnavailableRepo],
    generated_at: datetime,
    repos: tuple[str, ...],
) -> str:
    timestamp = generated_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Context Refresh",
        "",
        "Status: generated snapshot",
        "Canonical: false",
        "",
        "This file is a generated current-state brief for fresh-thread handoff.",
        "",
        "Repository code, issues, pull requests, and docs remain the source of truth.",
        "",
        "Do not edit this file directly. Regenerate it with `make context-refresh`.",
        "",
        f"Generated: {timestamp}",
        "",
        "## Snapshot Notice",
        "",
        "This report is a point-in-time snapshot, not canonical guidance.",
        "Use GitHub and repository state as the source of truth before acting.",
        "",
        "## Tracked Repositories",
        "",
    ]
    lines.extend(f"- `{repo}`" for repo in repos)
    lines.extend(["", "## Repository State", ""])

    by_name = {report.name: report for report in reports}
    for repo in repos:
        report = by_name.get(repo)
        if report is None:
            continue
        lines.extend(render_repo(report))
        lines.append("")

    lines.extend(["## Blocked Or Unavailable", ""])
    if unavailable:
        lines.extend(
            f"- `{repo.name}`: {repo.reason}"
            for repo in unavailable
        )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Reminder",
            "",
            "This file is a generated convenience artifact.",
            "It is useful for fresh-thread handoff and repo-state refresh,",
            "but it does not replace repository docs, issues, pull requests,",
            "or current GitHub state.",
            "",
        ]
    )
    return "\n".join(lines)


def render_repo(report: RepoReport) -> list[str]:
    lines = [
        f"### `{report.name}`",
        "",
        f"- Default branch: `{report.default_branch or 'unknown'}`",
        f"- Open PRs: {report.open_prs['totalCount']}",
        f"- Open issues: {report.open_issues['totalCount']}",
        "",
        "#### Open PRs",
        "",
    ]
    lines.extend(render_items(report.open_prs, "PR", "updatedAt"))
    lines.extend(["", "#### Open Issues", ""])
    lines.extend(render_items(report.open_issues, "Issue", "updatedAt"))
    lines.extend(
        [
            "",
            f"#### Recent Merged PRs (latest {MERGED_PR_LIMIT})",
            "",
        ]
    )
    lines.extend(render_node_list(report.recent_merged_prs, "PR", "mergedAt"))
    return lines


def render_items(items: dict[str, Any], kind: str, date_field: str) -> list[str]:
    nodes = items["nodes"]
    total_count = items["totalCount"]
    lines = render_node_list(nodes, kind, date_field)
    if total_count > len(nodes):
        lines.append(
            f"- Showing {len(nodes)} of {total_count}; rerun with direct GitHub"
            " inspection for the complete list."
        )
    return lines


def render_node_list(
    nodes: list[dict[str, Any]],
    kind: str,
    date_field: str,
) -> list[str]:
    if not nodes:
        return ["- None."]
    return [render_node(node, kind, date_field) for node in nodes]


def render_node(node: dict[str, Any], kind: str, date_field: str) -> str:
    author = (node.get("author") or {}).get("login") or "unknown"
    date_value = node.get(date_field) or "unknown date"
    title = one_line(node.get("title") or "untitled")
    url = node.get("url") or "unknown url"
    return (
        f"- {kind} #{node['number']}: {title} "
        f"({date_field}: {date_value}; author: {author}) {url}"
    )


def one_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def write_report(output: Path, content: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(f"{output.name}.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(output)


def main() -> int:
    args = parse_args()
    try:
        repos = read_workspace_repos(args.repo_manifest)
        require_gh()
        reports, unavailable = collect_reports(repos)
        content = render_report(
            reports,
            unavailable,
            datetime.now(timezone.utc),
            repos,
        )
        write_report(args.output, content)
    except WorkspaceRepoManifestError as exc:
        print(f"context-refresh failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"context-refresh failed: {exc}", file=sys.stderr)
        return 1

    print(f"Generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
