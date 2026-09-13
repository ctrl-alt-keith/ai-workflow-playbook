"""Shared fixtures for the provider review-launcher tests."""

import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def load_launcher(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def current_commit() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def run_launcher(
    launcher: Path,
    binary_option: str,
    executable: Path,
    *arguments: str,
    prompt: bytes = b"",
    candidate_commit: str | None = "current",
    trailing: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[bytes]:
    """Run a launcher from the repository root against a fake provider executable."""
    command = [str(launcher), binary_option, str(executable)]
    if "--auth-preflight" not in arguments and candidate_commit is not None:
        command.extend(("--candidate-commit", current_commit() if candidate_commit == "current" else candidate_commit))
    command.extend(arguments)
    command.extend(trailing)
    return subprocess.run(
        command,
        input=prompt,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        cwd=ROOT,
    )
