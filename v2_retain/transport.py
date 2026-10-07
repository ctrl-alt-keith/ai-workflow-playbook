"""Candidate transport identity, distinct from accepted live qualification."""

from importlib.metadata import PackageNotFoundError, version

from .model import Blocked


# The installed SDK/HTTP runtime, including trust, encoding and serialization.
# Stone's generator dependencies are not imported by this runtime path.
DEPENDENCIES = (
    ("dropbox", "12.2.1"),
    ("requests", "2.34.2"),
    ("urllib3", "2.8.0"),
    ("certifi", "2026.7.22"),
    ("idna", "3.19"),
    ("charset-normalizer", "3.5.1"),
    ("stone", "3.5.4"),
)
SDK_VERSION = dict(DEPENDENCIES)["dropbox"]
BUILD = "/".join(f"{name}-{pin}" for name, pin in DEPENDENCIES)


def require_transport(build=BUILD):
    """Check both installed dependencies and any supplied route evidence identity."""
    try:
        matches = all(version(name) == pin for name, pin in DEPENDENCIES)
    except PackageNotFoundError:
        matches = False
    if not matches or build != BUILD:
        raise Blocked("transport dependency drift")


def require_operator_qualification():
    # No accepted evidence binds this candidate to operator-live use. Neither
    # a local pass nor a future harness result automatically changes that fact.
    require_transport()
    raise Blocked("operator-live requires accepted qualification for transport " + BUILD)
