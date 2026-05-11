from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import difflib
from pathlib import Path
import re
import sys
from typing import Callable

import generate_context_refresh
import generate_github_context
import generate_workspace_bootstrap
from workspace_repos import (
    WorkspaceRepoManifestError,
    read_workspace_repos,
)


DEFAULT_MANIFEST = Path("config/workspace-repos.txt")
GENERATED_LINE = re.compile(r"^Generated: .*$", re.MULTILINE)


@dataclass(frozen=True)
class Artifact:
    path: Path
    make_target: str
    render_expected: Callable[[Path], str]
    normalize: Callable[[str], str] | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check existing generated dist artifacts for source drift."
    )
    parser.add_argument(
        "--repo-manifest",
        default=DEFAULT_MANIFEST,
        type=Path,
        help="Workspace repo manifest to read.",
    )
    parser.add_argument(
        "--require-existing",
        action="store_true",
        help="Fail when an expected dist artifact is missing.",
    )
    return parser.parse_args()


def expected_workspace_bootstrap(_manifest: Path) -> str:
    return generate_workspace_bootstrap.render_workspace_bootstrap()


def expected_context_refresh(manifest: Path) -> str:
    repos = read_workspace_repos(manifest)
    generate_context_refresh.require_gh()
    reports, unavailable = generate_context_refresh.collect_reports(repos)
    return generate_context_refresh.render_report(
        reports=reports,
        unavailable=unavailable,
        generated_at=datetime.now(timezone.utc),
        repos=repos,
    )


def expected_github_context(manifest: Path) -> str:
    return generate_github_context.render_github_context(read_workspace_repos(manifest))


def normalize_context_refresh(content: str) -> str:
    return GENERATED_LINE.sub("Generated: <normalized>", content)


def artifacts() -> tuple[Artifact, ...]:
    return (
        Artifact(
            path=Path("dist/workspace-bootstrap.md"),
            make_target="workspace-bootstrap",
            render_expected=expected_workspace_bootstrap,
        ),
        Artifact(
            path=Path("dist/context-refresh.md"),
            make_target="context-refresh",
            render_expected=expected_context_refresh,
            normalize=normalize_context_refresh,
        ),
        Artifact(
            path=Path("dist/github-context.md"),
            make_target="github-context",
            render_expected=expected_github_context,
        ),
    )


def normalized(content: str, artifact: Artifact) -> str:
    if artifact.normalize is None:
        return content
    return artifact.normalize(content)


def diff_artifact(path: Path, expected: str, actual: str) -> str:
    return "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=f"expected/{path}",
            tofile=f"actual/{path}",
        )
    )


def check_artifact(artifact: Artifact, manifest: Path, require_existing: bool) -> bool:
    if not artifact.path.exists():
        if require_existing:
            print(
                f"dist-check: missing {artifact.path}; run `make {artifact.make_target}`.",
                file=sys.stderr,
            )
            return False
        print(f"dist-check: skipped missing {artifact.path}")
        return True

    expected = artifact.render_expected(manifest)
    actual = artifact.path.read_text(encoding="utf-8")
    if normalized(actual, artifact) == normalized(expected, artifact):
        print(f"dist-check: {artifact.path} is current")
        return True

    print(
        f"dist-check: {artifact.path} is stale; run `make {artifact.make_target}`.",
        file=sys.stderr,
    )
    print(diff_artifact(artifact.path, expected, actual), file=sys.stderr)
    return False


def main() -> int:
    args = parse_args()
    try:
        ok = True
        found = False
        for artifact in artifacts():
            if artifact.path.exists():
                found = True
            ok = check_artifact(artifact, args.repo_manifest, args.require_existing) and ok
    except WorkspaceRepoManifestError as exc:
        print(f"dist-check failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"dist-check failed: {exc}", file=sys.stderr)
        return 1

    if not found and not args.require_existing:
        print("dist-check: no generated dist artifacts found; nothing to compare")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
