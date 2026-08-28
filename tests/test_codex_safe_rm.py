from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import importlib.machinery
import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SAFE_RM_PATH = ROOT / "scripts" / "codex-safe-rm"
INSTALLER_PATH = ROOT / "scripts" / "install-codex-safe-rm"


def load_script(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


safe_rm = load_script("playbook_codex_safe_rm", SAFE_RM_PATH)
installer = load_script("playbook_install_codex_safe_rm", INSTALLER_PATH)


class CodexSafeRmTests(unittest.TestCase):
    def test_accepts_literal_relative_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cwd = Path(temporary_directory).resolve()
            for operand in ("build", ".pytest_cache", "docs/_build", "foo/bar.baz_qux-1"):
                with self.subTest(operand=operand):
                    self.assertTrue(safe_rm.validate_operand(operand, cwd))

    def test_rejects_unsafe_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cwd = Path(temporary_directory).resolve()
            rejected = (
                "*", ".", "./", "..", "../foo", "/tmp/foo", "~/foo",
                "${DIR}", "$(pwd)", "foo/../bar", "foo//bar", "foo/",
                "build;whoami", "path with spaces", ".git", "repo/.git/objects",
            )
            for operand in rejected:
                with self.subTest(operand=operand), self.assertRaises(safe_rm.SafeRmError):
                    safe_rm.validate_operand(operand, cwd)

    def test_removes_only_validated_trees_and_does_not_follow_internal_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            cwd = root / "repo"
            outside = root / "outside"
            (cwd / "build" / "nested").mkdir(parents=True)
            outside.mkdir()
            protected = outside / "protected.txt"
            protected.write_text("keep\n", encoding="utf-8")
            (cwd / "build" / "outside-link").symlink_to(outside, target_is_directory=True)
            safe_rm.remove_directories(["build", "missing"], cwd=cwd)
            self.assertFalse((cwd / "build").exists())
            self.assertTrue(protected.is_file())

    def test_rejects_top_level_symlinks_files_and_overlapping_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cwd = Path(temporary_directory).resolve()
            (cwd / "real" / "nested").mkdir(parents=True)
            (cwd / "link").symlink_to(cwd / "real", target_is_directory=True)
            (cwd / "file").write_text("keep\n", encoding="utf-8")
            for operand in ("link", "file"):
                with self.subTest(operand=operand), self.assertRaisesRegex(
                    safe_rm.SafeRmError, "not a real directory"
                ):
                    safe_rm.remove_directories([operand], cwd=cwd)
            with self.assertRaisesRegex(safe_rm.SafeRmError, "overlapping"):
                safe_rm.remove_directories(["real", "real/nested"], cwd=cwd)

    def test_fails_closed_without_symlink_resistant_runtime(self) -> None:
        with mock.patch.object(shutil.rmtree, "avoids_symlink_attacks", False):
            with self.assertRaisesRegex(safe_rm.SafeRmError, "symlink-resistant"):
                safe_rm.remove_directories(["missing"], cwd=Path.cwd())

    def test_cli_grammar_and_version_are_exact(self) -> None:
        for arguments in ([], ["-r", "--", "build"], ["-rf", "build"], ["-rf", "--"]):
            with self.subTest(arguments=arguments):
                stdout = StringIO()
                stderr = StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    self.assertEqual(safe_rm.main(arguments), 2)
                self.assertIn("usage:", stderr.getvalue())
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(safe_rm.main(["--version"]), 0)
        self.assertEqual(stdout.getvalue(), "codex-safe-rm 1\n")


class CodexSafeRmInstallerTests(unittest.TestCase):
    def test_production_cli_rejects_relocation_and_uses_fixed_destination(self) -> None:
        alternate = "/tmp/alternate-codex-safe-rm"
        for action in ("install", "verify", "uninstall"):
            with self.subTest(action=action), redirect_stderr(StringIO()), self.assertRaises(
                SystemExit
            ):
                installer.build_parser().parse_args([action, "--destination", alternate])

        destination = Path("/effective/home/.local/bin/codex-safe-rm")
        metadata = {"control_version": "1", "source_commit": "1" * 40}
        with mock.patch.object(
            installer, "production_destination", return_value=destination
        ), mock.patch.object(
            installer, "install", return_value=metadata
        ) as install_call, redirect_stdout(StringIO()):
            self.assertEqual(installer.main(["install"]), 0)
        install_call.assert_called_once_with(destination)

    def test_production_destination_uses_effective_account_home_not_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            account_home = Path(temporary_directory).resolve() / "account-home"
            account_home.mkdir()
            account = mock.Mock(pw_dir=str(account_home))
            with mock.patch.object(
                installer.pwd, "getpwuid", return_value=account
            ), mock.patch.dict("os.environ", {"HOME": "/attacker-selected-home"}):
                self.assertEqual(
                    installer.production_destination(),
                    account_home / ".local" / "bin" / "codex-safe-rm",
                )

    def test_clean_install_is_exact_recorded_and_verifiable(self) -> None:
        with installation_fixture() as fixture:
            metadata = installer.install(
                fixture.destination, source=fixture.source, repo_root=fixture.repo
            )
            self.assertEqual(fixture.source.read_bytes(), fixture.destination.read_bytes())
            self.assertEqual(stat.S_IMODE(fixture.destination.stat().st_mode), 0o755)
            self.assertEqual(
                metadata,
                installer.verify(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                ),
            )

    def test_dirty_enforcement_owned_predecessor_is_rejected(self) -> None:
        with installation_fixture() as fixture:
            fixture.destination.parent.mkdir(parents=True)
            predecessor_bytes = fixture.source.read_bytes()
            fixture.destination.write_bytes(predecessor_bytes)
            fixture.destination.chmod(0o755)
            digest = hashlib.sha256(predecessor_bytes).hexdigest()
            legacy = {
                "schema_version": 1,
                "control": "codex-safe-rm",
                "control_version": "1",
                "source_repository": "ctrl-alt-keith/ai-workflow-enforcement",
                "source_path": "enforcement/safe_rm.py",
                "source_commit": "1" * 40,
                "source_dirty": True,
                "source_sha256": digest,
                "installed_sha256": digest,
            }
            record = installer.metadata_path(fixture.destination)
            record.write_text(json.dumps(legacy) + "\n", encoding="utf-8")
            record.chmod(0o644)

            with self.assertRaisesRegex(installer.InstallError, "unrecognized"):
                installer.install(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                )

    def test_dirty_source_and_unrecognized_destination_fail_closed(self) -> None:
        with installation_fixture() as fixture:
            (fixture.repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
            with self.assertRaisesRegex(installer.InstallError, "dirty"):
                installer.install(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                )
        with installation_fixture() as fixture:
            fixture.destination.parent.mkdir(parents=True)
            fixture.destination.write_text("unrelated\n", encoding="utf-8")
            with self.assertRaises(installer.InstallError):
                installer.install(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                )
            self.assertEqual(fixture.destination.read_text(encoding="utf-8"), "unrelated\n")

    def test_exact_enforcement_owned_predecessor_is_migrated(self) -> None:
        with installation_fixture() as fixture:
            fixture.destination.parent.mkdir(parents=True)
            predecessor_bytes = fixture.source.read_bytes()
            fixture.destination.write_bytes(predecessor_bytes)
            fixture.destination.chmod(0o755)
            digest = hashlib.sha256(predecessor_bytes).hexdigest()
            legacy = {
                "schema_version": 1,
                "control": "codex-safe-rm",
                "control_version": "1",
                "source_repository": "ctrl-alt-keith/ai-workflow-enforcement",
                "source_path": "enforcement/safe_rm.py",
                "source_commit": "1" * 40,
                "source_dirty": False,
                "source_sha256": digest,
                "installed_sha256": digest,
            }
            record = installer.metadata_path(fixture.destination)
            record.write_text(json.dumps(legacy) + "\n", encoding="utf-8")
            record.chmod(0o644)

            metadata = installer.install(
                fixture.destination, source=fixture.source, repo_root=fixture.repo
            )

            self.assertEqual(metadata["source_repository"], "ctrl-alt-keith/ai-workflow-playbook")
            self.assertEqual(
                metadata,
                installer.verify(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                ),
            )

    def test_verify_rejects_byte_metadata_and_mode_drift(self) -> None:
        with installation_fixture() as fixture:
            installer.install(fixture.destination, source=fixture.source, repo_root=fixture.repo)
            fixture.destination.write_text("modified\n", encoding="utf-8")
            with self.assertRaisesRegex(installer.InstallError, "digest"):
                installer.verify(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                )
        with installation_fixture() as fixture:
            installer.install(fixture.destination, source=fixture.source, repo_root=fixture.repo)
            fixture.destination.chmod(0o775)
            with self.assertRaisesRegex(installer.InstallError, "mode"):
                installer.verify(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                )

    def test_uninstall_removes_only_a_recognized_pair(self) -> None:
        with installation_fixture() as fixture:
            installer.install(fixture.destination, source=fixture.source, repo_root=fixture.repo)
            installer.uninstall(fixture.destination)
            self.assertFalse(fixture.destination.exists())
            self.assertFalse(installer.metadata_path(fixture.destination).exists())
        with installation_fixture() as fixture:
            fixture.destination.parent.mkdir(parents=True)
            fixture.destination.write_text("unrelated\n", encoding="utf-8")
            with self.assertRaises(installer.InstallError):
                installer.uninstall(fixture.destination)
            self.assertTrue(fixture.destination.exists())

    def test_group_writable_install_directory_is_rejected(self) -> None:
        with installation_fixture() as fixture:
            fixture.destination.parent.mkdir(parents=True)
            fixture.destination.parent.chmod(0o775)
            with self.assertRaisesRegex(installer.InstallError, "install directory"):
                installer.install(
                    fixture.destination, source=fixture.source, repo_root=fixture.repo
                )


class InstallationFixture:
    def __init__(self, root: Path):
        self.repo = root / "repo"
        self.destination = root / "bin" / "codex-safe-rm"
        self.source = self.repo / "scripts" / "codex-safe-rm"

    def prepare(self) -> "InstallationFixture":
        (self.repo / "scripts").mkdir(parents=True)
        self.source.write_bytes(SAFE_RM_PATH.read_bytes())
        self.source.chmod(0o755)
        git(self.repo, "init")
        git(self.repo, "config", "user.email", "tests@example.com")
        git(self.repo, "config", "user.name", "Tests")
        git(self.repo, "config", "commit.gpgsign", "false")
        git(self.repo, "add", "scripts/codex-safe-rm")
        git(self.repo, "commit", "-m", "Add reviewed source")
        return self


class InstallationContext:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory()

    def __enter__(self) -> InstallationFixture:
        return InstallationFixture(Path(self.temporary.name).resolve()).prepare()

    def __exit__(self, *args: object) -> None:
        self.temporary.cleanup()


def installation_fixture() -> InstallationContext:
    return InstallationContext()


def git(cwd: Path, *arguments: str) -> None:
    result = subprocess.run(
        ("git", *arguments),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(arguments)} failed: {result.stderr or result.stdout}"
        )


if __name__ == "__main__":
    unittest.main()
