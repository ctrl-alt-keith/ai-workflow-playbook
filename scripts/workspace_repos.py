from __future__ import annotations

from pathlib import Path
import re


REPO_FULL_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class WorkspaceRepoManifestError(ValueError):
    """Raised when the workspace repo manifest cannot be used."""


def parse_workspace_repos(
    manifest_text: str,
    source: str = "workspace repo manifest",
) -> tuple[str, ...]:
    repos: list[str] = []
    invalid_entries: list[str] = []

    for line_number, raw_line in enumerate(manifest_text.splitlines(), start=1):
        repo = raw_line.strip()
        if not repo or repo.startswith("#"):
            continue
        if REPO_FULL_NAME_RE.fullmatch(repo) is None:
            invalid_entries.append(f"line {line_number}: {repo}")
            continue
        repos.append(repo)

    if invalid_entries:
        details = "; ".join(invalid_entries)
        raise WorkspaceRepoManifestError(
            f"{source} contains invalid repo entries; expected owner/name: {details}"
        )
    if not repos:
        raise WorkspaceRepoManifestError(f"{source} does not contain any repo entries")

    return tuple(repos)


def read_workspace_repos(manifest_path: Path) -> tuple[str, ...]:
    if not manifest_path.is_file():
        raise WorkspaceRepoManifestError(
            f"workspace repo manifest is missing: {manifest_path}"
        )

    return parse_workspace_repos(
        manifest_path.read_text(encoding="utf-8"),
        source=str(manifest_path),
    )
