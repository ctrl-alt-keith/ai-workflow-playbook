from __future__ import annotations

from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^]]*]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
HTML_TAG_RE = re.compile(r"<[^>]+>")
PUNCTUATION_RE = re.compile(r"[^\w\- ]", re.UNICODE)


def tracked_markdown_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--", "*.md"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [REPO_ROOT / line for line in result.stdout.splitlines() if line]


def markdown_lines_outside_fences(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    fence: str | None = None
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is None:
            lines.append((line_number, line))
    return lines


def github_heading_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    for _, line in markdown_lines_outside_fences(path):
        match = HEADING_RE.match(line)
        if not match:
            continue
        heading = HTML_TAG_RE.sub("", match.group(1)).lower()
        base = PUNCTUATION_RE.sub("", heading).replace(" ", "-")
        anchor = base
        suffix = 0
        while anchor in anchors:
            suffix += 1
            anchor = f"{base}-{suffix}"
        anchors.add(anchor)
    return anchors


class MarkdownLinkTests(unittest.TestCase):
    def test_heading_anchors_remain_unique_when_generated_suffix_is_occupied(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Path(temp_dir) / "headings.md"
            document.write_text("# Foo\n# Foo-1\n# Foo\n", encoding="utf-8")

            anchors = github_heading_anchors(document)

        self.assertEqual(anchors, {"foo", "foo-1", "foo-2"})

    def test_local_links_and_heading_fragments_resolve(self) -> None:
        failures: list[str] = []
        anchors_by_path: dict[Path, set[str]] = {}

        for document in tracked_markdown_files():
            for line_number, line in markdown_lines_outside_fences(document):
                for raw_target in LINK_RE.findall(line):
                    target = raw_target.strip().strip("<>")
                    if target.startswith(("http://", "https://", "mailto:")):
                        continue

                    path_text, _, fragment = target.partition("#")
                    path_text = unquote(path_text.split("?", 1)[0])
                    resolved = (
                        (document.parent / path_text).resolve()
                        if path_text
                        else document
                    )
                    location = f"{document.relative_to(REPO_ROOT)}:{line_number}"
                    if not resolved.exists():
                        failures.append(f"{location}: missing local target {target}")
                        continue

                    if fragment:
                        if not resolved.is_file():
                            failures.append(
                                f"{location}: heading fragment targets a directory {target}"
                            )
                            continue
                        expected = unquote(fragment).lower()
                        anchors = anchors_by_path.setdefault(
                            resolved, github_heading_anchors(resolved)
                        )
                        if expected not in anchors:
                            failures.append(
                                f"{location}: missing heading fragment {target}"
                            )

        self.assertEqual(failures, [], "\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
