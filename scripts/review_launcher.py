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
MAX_OPTION_VALUE_CHARS = 128
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
    # Names may be quoted (JSON/TOML) and values may be quoted strings.
    value = re.sub(
        r"(?i)\bauthorization\b[\"']?\s*[:=]\s*[\"']?(?:bearer\s+)?[^\s,;\"']+",
        "authorization=[REDACTED]",
        value,
    )
    value = re.sub(
        r"(?i)\b(token|secret|api[_-]?key|credential|cookie)\b[\"']?\s*[:=]\s*[\"']?[^\s,;\"']+",
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
        name = option.removeprefix("--")
        if name in selected:
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
        if len(value) > MAX_OPTION_VALUE_CHARS:
            raise ValueError(f"{option} value exceeds {MAX_OPTION_VALUE_CHARS} characters")
        selected[name] = value
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


def bounded(value: Any) -> Any:
    """Apply the diagnostic bound and credential redaction to every string in a record."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {key: bounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [bounded(item) for item in value]
    return value


def compose(causes: list[str]) -> str:
    """One failure string from already-sanitized causes, primary first, sharing the single bound."""
    share = MAX_DIAGNOSTIC_CHARS // len(causes)
    return redact("; ".join(cause[:share] for cause in causes))


def write_record(record: dict[str, Any], destination: Path) -> tuple[str | None, str]:
    """Create the requested diagnostics file exclusively.

    Returns ``(cause, state)``: ``cause`` is None on success, otherwise the
    bounded failure text; ``state`` is what is durably at the path afterwards:
    ``written``, ``absent`` (nothing created, or removed after a failed write),
    or ``residue`` (created, write failed, removal also failed — the bytes are
    incomplete and untrusted). Only a file this call created is ever removed.
    """
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as error:
        return f"requested diagnostics file could not be created: {redact(str(error))}", "absent"
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError as error:
        cause = f"requested diagnostics file could not be written: {redact(str(error))}"
        try:
            os.unlink(destination)
        except OSError as removal:
            return (
                f"{cause}; the incomplete file could not be removed and may contain incomplete, "
                f"untrusted bytes ({redact(str(removal))})",
                "residue",
            )
        return cause, "absent"
    return None, "written"


def classify(
    provider: Provider,
    *,
    preflight: bool,
    returncode: int,
    received: bool,
    expected: bool,
    substitution: str | None,
    cleanup_error: str | None,
) -> list[str]:
    """The result-classification policy for a returned provider attempt, in one place.

    Returns the ordered causes: the first is primary — the most fundamental
    reason the result cannot be accepted — and the rest are preserved as
    secondary. Order: provider process failure; unacceptable output (missing
    canary or empty review) on a clean exit; effective-selection evidence
    failure; scratch cleanup failure. Authentication classification is layered
    on top by the caller from the qualified diagnostic surface.
    """
    causes: list[str] = []
    if returncode != 0:
        qualifier = "despite producing output" if received else "without substantive output"
        causes.append(f"{provider.label} exited {returncode} {qualifier}")
    elif not expected:
        causes.append(
            f"{provider.label} preflight did not return the expected canary response"
            if preflight
            else f"{provider.label} did not return substantive review output"
        )
    if substitution is not None:
        causes.append(substitution)
    if cleanup_error is not None:
        causes.append(f"{provider.label} temporary-directory cleanup failed: {cleanup_error}")
    return causes


def finish(
    provider: Provider,
    record: dict[str, Any],
    *,
    causes: list[str],
    auth_failure: bool = False,
    destination: Path | None,
    output: str = "",
) -> int:
    """The one result path: emit the record, then exit with the primary classification.

    ``causes`` is the policy-ordered list from ``classify`` (or a single
    pre-launch failure); the first entry stays primary. A failed write of the
    requested diagnostics file is appended as a further cause and fails an
    otherwise successful attempt. Every cause passes through ``redact`` before
    it can enter the record, so composition never reintroduces raw text; the
    record as a whole is bounded once, and the corrected record goes to stderr.
    """
    causes = [redact(cause) for cause in causes]
    record = bounded({**record, "status": "failed" if causes else "ok", **({"failure": compose(causes)} if causes else {})})
    if destination is not None:
        write_cause, state = write_record(record, destination)
        record["diagnostics_file"] = state
        if write_cause is not None:
            causes.append(write_cause)
            record["status"] = "failed"
            record["failure"] = compose(causes)
    print(f"{provider.name}-review diagnostics: {json.dumps(record, sort_keys=True)}", file=sys.stderr)
    if causes:
        return AUTH_FAILURE_EXIT if auth_failure else REVIEWER_FAILURE_EXIT
    sys.stdout.write(output)
    return 0


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
        return finish(provider, record, causes=[failure], destination=destination)

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
        causes = [failure]
        cleanup_error = cleanup_temporary_directory(scratch)
        if cleanup_error is not None:
            causes.append(f"{provider.label} temporary-directory cleanup failed: {cleanup_error}")
        return finish(provider, record, causes=causes, destination=args.diagnostics_file)
    cleanup_error = cleanup_temporary_directory(scratch)

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    received = bool(output.strip())
    expected = output.strip() == provider.auth_response if preflight else received
    effective, substitution = provider.effective(selection, stdout, stderr)
    causes = classify(
        provider,
        preflight=preflight,
        returncode=result.returncode,
        received=received,
        expected=expected,
        substitution=substitution,
        cleanup_error=cleanup_error,
    )
    # Authentication is established only from the provider's qualified diagnostic surface and
    # only for a failed attempt; when established it is the primary classification.
    auth_failure = bool(causes) and bool(provider.auth_failure.search(provider.diagnostic(stdout, stderr).lower()))
    if auth_failure:
        causes.insert(0, f"{provider.label} authentication needs operator attention")
    record.update({f"{provider.name}_exit_code": result.returncode, provider.output_field: received, "stderr": stderr})
    if effective:
        record["effective"] = effective
    if causes and stdout:
        record["stdout"] = stdout
    return finish(
        provider,
        record,
        causes=causes,
        auth_failure=auth_failure,
        destination=args.diagnostics_file,
        output=f"{provider.auth_response}\n" if preflight else output,
    )
