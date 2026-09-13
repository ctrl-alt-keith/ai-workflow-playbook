"""Shared exact-candidate review launch for the provider wrappers in this directory.

A wrapper supplies a ``Provider`` and calls ``main``. This module owns the
provider-neutral contract: explicit absolute executable resolution, the
effective-account login context, model/effort-only pass-through, the exact
candidate-commit binding, stdin prompt delivery, the auth-preflight canary,
output capture where an empty or failed response is wrapper failure, and the
bounded redacted diagnostics record that carries the configured envelope.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping


AUTH_FAILURE_EXIT = 78
REVIEWER_FAILURE_EXIT = 70
AUTH_PREFLIGHT_TIMEOUT_SECONDS = 120
MAX_DIAGNOSTIC_CHARS = 1_000
ALLOWED_OPTIONS = {"--model", "--effort"}
EXACT_COMMIT = re.compile(r"[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?")


@dataclass(frozen=True)
class Launch:
    """Per-run values a provider needs to render its command and read its output."""

    preflight: bool
    repository: str | None
    scratch: Path


@dataclass(frozen=True)
class Provider:
    """Provider-specific deltas; everything else is the shared contract above."""

    name: str
    label: str
    auth_response: str
    auth_failure: re.Pattern[str]
    configured_envelope: Callable[..., dict[str, Any]]
    command: Callable[[dict[str, Any], Launch], list[str]]
    output: Callable[[subprocess.CompletedProcess[bytes], Launch], str]
    output_field: str  # record key naming where substantive output is read from
    environment: Mapping[str, str] = field(default_factory=dict)
    require_model: bool = False
    accept: Callable[[str, dict[str, str], dict[str, str]], None] = lambda executable, selection, environment: None
    # Text eligible for auth-failure classification: the provider's diagnostic
    # surface, never its substantive output. Defaults to stderr.
    diagnostic: Callable[[str, str], str] = lambda stdout, stderr: stderr
    # Effective execution evidence: (observed values for the record, failure
    # reason when they do not establish the requested selection). Defaults to
    # no runtime evidence surface.
    effective: Callable[[dict[str, str], str, str], tuple[dict[str, Any], str | None]] = (
        lambda selection, stdout, stderr: ({}, None)
    )

    @property
    def auth_prompt(self) -> bytes:
        return f"Reply exactly: {self.auth_response}\n".encode("utf-8")


def redact(value: str) -> str:
    """Keep operational diagnostics without retaining obvious credentials."""
    value = value[:MAX_DIAGNOSTIC_CHARS]
    value = re.sub(
        r"(?i)\bauthorization\b\s*[:=]\s*(?:bearer\s+)?[^\s,;]+",
        "authorization=[REDACTED]",
        value,
    )
    value = re.sub(
        r"(?i)\b(token|secret|api[_-]?key|credential|cookie)\b\s*[:=]\s*[^\s,;]+",
        r"\1=[REDACTED]",
        value,
    )
    value = re.sub(r"\b(?:sk|gho|ghp)[_-][A-Za-z0-9_=-]+", "[REDACTED]", value)
    return value


def parse_options(provider: Provider, arguments: list[str]) -> dict[str, str]:
    """Allow only model and effort choices; the wrapper owns every review control."""
    selected: dict[str, str] = {}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        option, separator, inline_value = argument.partition("=")
        if option not in ALLOWED_OPTIONS:
            raise ValueError(f"unsupported {provider.label} option: {argument}")
        if option in selected:
            raise ValueError(f"{option} may be provided only once")
        if separator:
            value = inline_value
        else:
            if index + 1 >= len(arguments):
                raise ValueError(f"{option} requires a value")
            value = arguments[index + 1]
            index += 1
        if not value or value.startswith("-"):
            raise ValueError(f"{option} requires a non-option value")
        selected[option.removeprefix("--")] = value
        index += 1
    if provider.require_model and "model" not in selected:
        raise ValueError(f"--model is required: pass the exact {provider.label} selector after --")
    return selected


def child_environment(provider: Provider) -> dict[str, str]:
    """Use one coherent effective-account context for every provider child."""
    account = pwd.getpwuid(os.geteuid())
    environment = os.environ.copy()
    environment.update({"HOME": account.pw_dir, "USER": account.pw_name, "LOGNAME": account.pw_name})
    environment.update(provider.environment)
    return environment


def resolve_executable(provider: Provider, path_value: str | None, environment: dict[str, str]) -> tuple[str, str]:
    option = f"--{provider.name}-bin"
    if path_value is None:
        raise ValueError(f"{option} is required")
    requested = Path(path_value)
    if not requested.is_absolute():
        raise ValueError(f"{option} must be an absolute path")
    resolved = requested.resolve(strict=True)
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError(f"{option} must resolve to an executable file")
    try:
        result = subprocess.run(
            [str(resolved), "--version"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
            timeout=5,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f"could not obtain {provider.label} version: {error}") from error
    version = (result.stdout or result.stderr).strip()
    if result.returncode != 0 or not version:
        raise ValueError(f"the {provider.label} executable did not return a version")
    return str(resolved), redact(version)


def validate_diagnostics_destination(destination: Path | None) -> None:
    if destination is None:
        return
    if not destination.is_absolute() or destination.exists() or destination.is_symlink():
        raise ValueError("--diagnostics-file must be a new absolute path")
    if not destination.parent.is_dir():
        raise ValueError("--diagnostics-file parent must exist")


def diagnostics(provider: Provider, record: dict[str, Any], destination: Path | None) -> bool:
    """Emit the record to stderr and, when requested, to a new file; report whether the file was written."""
    encoded = json.dumps(record, sort_keys=True)
    print(f"{provider.name}-review diagnostics: {encoded}", file=sys.stderr)
    if destination is None:
        return True
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(encoded + "\n")
    except OSError as error:
        print(
            f"{provider.name}-review diagnostics file could not be written: {redact(str(error))}",
            file=sys.stderr,
        )
        return False
    return True


def cleanup_temporary_directory(directory: tempfile.TemporaryDirectory[str]) -> str | None:
    try:
        directory.cleanup()
    except OSError as error:
        return redact(str(error))
    return None


def resolve_candidate(expected_commit: str, environment: dict[str, str]) -> tuple[str, str]:
    """Resolve the current worktree and require its HEAD to match exactly."""
    if not EXACT_COMMIT.fullmatch(expected_commit):
        raise ValueError("--candidate-commit must be an exact commit object ID")
    candidate = Path.cwd().resolve(strict=True)
    results = []
    for arguments in (("--show-toplevel",), ("--verify", "HEAD^{commit}")):
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
            env={**environment, "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"},
        )
        if result.returncode != 0 or not result.stdout.strip():
            raise ValueError("current directory is not a readable Git worktree")
        results.append(result.stdout.strip())
    repository = str(Path(results[0]).resolve(strict=True))
    observed_commit = results[1].lower()
    expected_commit = expected_commit.lower()
    if observed_commit != expected_commit:
        raise ValueError(
            f"candidate commit mismatch: expected {expected_commit}, observed {observed_commit}"
        )
    return repository, observed_commit


def review_prompt(prompt: bytes, repository: str, commit: str) -> bytes:
    context = (
        "Verified review selection:\n"
        f"- repository/worktree: {json.dumps(repository)}\n"
        f"- HEAD commit at launch: {commit}\n"
        "Use this commit as the candidate identity. The wrapper does not claim that "
        "uncommitted worktree bytes were validated.\n\n"
        "Review question:\n"
    )
    return context.encode("utf-8") + prompt


def parse_arguments(provider: Provider, argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Run a constrained {provider.label} review; provide the review prompt on standard input."
    )
    parser.add_argument(f"--{provider.name}-bin", dest="binary")
    parser.add_argument("--auth-preflight", action="store_true")
    parser.add_argument("--diagnostics-file", type=Path)
    parser.add_argument("--candidate-commit")
    parser.add_argument("provider_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.provider_args[:1] == ["--"]:
        args.provider_args = args.provider_args[1:]
    return args


def main(provider: Provider, argv: list[str] | None = None) -> int:
    args = parse_arguments(provider, argv or sys.argv[1:])
    preflight = args.auth_preflight
    record: dict[str, Any] = {
        "kind": f"{provider.name}_review",
        "attempt_kind": "auth_preflight" if preflight else "review",
    }

    def fail(failure: str, destination: Path | None) -> int:
        diagnostics(provider, {**record, "status": "failed", "failure": redact(failure)}, destination)
        return REVIEWER_FAILURE_EXIT

    try:
        validate_diagnostics_destination(args.diagnostics_file)
    except ValueError as error:
        return fail(str(error), None)
    try:
        environment = child_environment(provider)
        executable, version = resolve_executable(provider, args.binary, environment)
        record[f"{provider.name}_version"] = version
        selection = parse_options(provider, args.provider_args)
        record["configured_envelope"] = provider.configured_envelope(selection, preflight=preflight)
        prompt = provider.auth_prompt if preflight else sys.stdin.buffer.read()
        if not preflight and not prompt.strip():
            raise ValueError("review prompt must be supplied on standard input")
        if preflight and args.candidate_commit is not None:
            raise ValueError("--candidate-commit is only valid for review execution")
        if not preflight and args.candidate_commit is None:
            raise ValueError("--candidate-commit is required for review execution")
        provider.accept(executable, selection, environment)
    except (OSError, ValueError) as error:
        return fail(str(error), args.diagnostics_file)

    try:
        scratch = tempfile.TemporaryDirectory(prefix=f"{provider.name}-review-")
    except OSError as error:
        return fail(f"could not allocate a scratch directory: {error}", args.diagnostics_file)
    try:
        repository: str | None = None
        if preflight:
            cwd = scratch.name
        else:
            repository, commit = resolve_candidate(args.candidate_commit, environment)
            record["candidate"] = {"repository": repository, "commit": commit}
            prompt = review_prompt(prompt, repository, commit)
            cwd = repository
        launch = Launch(preflight=preflight, repository=repository, scratch=Path(scratch.name))
        result = subprocess.run(
            [executable, *provider.command(record["configured_envelope"], launch)],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            cwd=cwd,
            env=environment,
            timeout=AUTH_PREFLIGHT_TIMEOUT_SECONDS if preflight else None,
        )
        output = provider.output(result, launch)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        failure = (
            f"{provider.label} preflight exceeded {AUTH_PREFLIGHT_TIMEOUT_SECONDS} seconds"
            if isinstance(error, subprocess.TimeoutExpired)
            else str(error)
        )
        cleanup_error = cleanup_temporary_directory(scratch)
        if cleanup_error is not None:
            failure = f"{failure}; temporary-directory cleanup failed: {cleanup_error}"
        return fail(failure, args.diagnostics_file)
    cleanup_error = cleanup_temporary_directory(scratch)

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    expected = output.strip() == provider.auth_response if preflight else bool(output.strip())
    successful = result.returncode == 0 and expected
    if cleanup_error is not None:
        successful = False
        stderr = "\n".join(filter(None, (stderr, f"temporary-directory cleanup failed: {cleanup_error}")))
    effective, substitution = provider.effective(selection, stdout, stderr)
    if substitution is not None:
        successful = False
    auth_failure = not successful and bool(provider.auth_failure.search(provider.diagnostic(stdout, stderr).lower()))
    record.update(
        {
            "status": "ok" if successful else "failed",
            f"{provider.name}_exit_code": result.returncode,
            provider.output_field: bool(output.strip()),
            "stderr": redact(stderr),
        }
    )
    if effective:
        record["effective"] = effective
    if not successful:
        record["failure"] = (
            f"{provider.label} authentication needs operator attention"
            if auth_failure
            else f"{provider.label} temporary-directory cleanup failed"
            if cleanup_error is not None
            else substitution
            if substitution is not None
            else f"{provider.label} preflight did not return the expected canary response"
            if preflight
            else f"{provider.label} did not return substantive review output"
        )
        if stdout:
            record["stdout"] = redact(stdout)
    if not diagnostics(provider, record, args.diagnostics_file):
        return REVIEWER_FAILURE_EXIT
    if not successful:
        return AUTH_FAILURE_EXIT if auth_failure else REVIEWER_FAILURE_EXIT
    sys.stdout.write(f"{provider.auth_response}\n" if preflight else output)
    return 0
