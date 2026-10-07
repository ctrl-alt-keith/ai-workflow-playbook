"""Candidate transport identity, distinct from accepted live qualification."""

from importlib.metadata import PackageNotFoundError, version

from .model import Blocked


SDK_VERSION = "12.2.1"
DEPENDENCIES = (("dropbox", SDK_VERSION), ("requests", "2.34.2"), ("urllib3", "2.8.0"))
BUILD = SDK_VERSION + "".join(f"/{name}-{pin}" for name, pin in DEPENDENCIES[1:])


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
