import contextlib
import io
import json
import os
from pathlib import Path
import pwd
import shlex
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "claude-review"
CODEX_RULE = ROOT / ".codex" / "rules" / "claude-review.rules"
CODEX_RULE_TEMPLATE = ROOT / ".codex" / "rule-templates" / "claude-review.rules"
INSTALLER = ROOT / "scripts" / "install-claude-review"


def load_script(name, path):
    import importlib.machinery
    import importlib.util

    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class ClaudeReviewIdentityAndGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.launcher = load_script("claude_review_identity_grammar", LAUNCHER)
        cls.installer = load_script("claude_review_installer", INSTALLER)

    def create_installed_fixture(self, root: Path):
        installed = root / "installed"
        installed.mkdir(mode=0o700)
        launcher = installed / "claude-review"
        launcher_bytes = LAUNCHER.read_bytes()
        launcher.write_bytes(launcher_bytes)
        launcher.chmod(0o500)
        active_rule = root / "active.rules"
        active_rule.write_text("fixture active rule\n", encoding="utf-8")
        active_rule.chmod(0o600)
        auth_diagnostics = root / "auth-diagnostics"
        auth_diagnostics.mkdir(mode=0o700)
        candidate = root / "candidate"
        candidate.mkdir()
        marker = root / "provider-runs"
        versions = []
        for number in (1, 2, 3):
            version = root / f"claude-{number}"
            version.write_text(
                "#!/usr/bin/env python3\n"
                "import os, pathlib, sys\n"
                f"VERSION = 'fixture-claude {number}'\n"
                "pathlib.Path(os.environ['FIXTURE_PROVIDER_RUNS']).open('a').write(VERSION + (':version\\n' if '--version' in sys.argv else ':run\\n'))\n"
                "if '--version' in sys.argv:\n"
                "    print(VERSION)\n"
                "    raise SystemExit(0)\n"
                "print('CLAUDE_AUTH_OK')\n",
                encoding="utf-8",
            )
            version.chmod(0o755)
            versions.append(version)
        selector = root / "claude"
        selector.symlink_to(versions[0])
        with mock.patch.dict(os.environ, {"FIXTURE_PROVIDER_RUNS": str(marker)}):
            qualified_identity = self.launcher.qualified_executable_identity(
                selector, os.geteuid(), [candidate]
            )
        marker.unlink()
        qualification_root = root / "qualification-root"
        entry_contract = {
            "entry_contract_schema_version": 1,
            "installation_schema_version": 2,
            "qualification_schema_version": 2,
            "launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
            "rule_template_sha256": "fixture-rule-template",
            "claude_selector": str(selector),
            "active_rule_path": str(active_rule),
            "forbidden_roots": [str(candidate)],
            "auth_diagnostics_directory": str(auth_diagnostics),
            "qualification_root": str(qualification_root),
        }
        entry_contract_id = "sha256:" + self.launcher.sha256_bytes(
            self.launcher.canonical_json_bytes(entry_contract)
        )
        qualification = qualification_root / entry_contract_id.removeprefix("sha256:")
        receipts = qualification / "receipts"
        receipts.mkdir(parents=True)
        qualification_root.chmod(0o700)
        qualification.chmod(0o700)
        receipts.chmod(0o700)
        lock = qualification / "qualification.lock"
        lock.write_text("fixture lock\n", encoding="utf-8")
        lock.chmod(0o600)
        manifest = {
            "schema_version": 2,
            "entry_contract_id": entry_contract_id,
            "entry_contract": entry_contract,
            "installed_launcher_path": str(launcher),
            "installed_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
            "active_rule_path": str(active_rule),
            "active_rule_sha256": self.launcher.sha256_bytes(active_rule.read_bytes()),
            "claude_selector": str(selector),
            "forbidden_roots": [str(candidate)],
            "auth_diagnostics_directory": str(auth_diagnostics),
            "qualification_schema_version": 2,
            "qualification_directory": str(qualification),
            "qualification_receipts_directory": str(receipts),
            "current_selection_path": str(qualification / "current-selection.json"),
            "qualification_lock_path": str(lock),
        }
        receipt = {
            "kind": "claude_reviewer_qualification_receipt",
            "schema_version": 2,
            "entry_contract_id": entry_contract_id,
            "claude_selector": str(selector),
            "file_identity": qualified_identity["file_identity"],
            "version": qualified_identity["version"],
            "predecessor_receipt_sha256": None,
            "predecessor_receipt_path": None,
            "producing_launcher_path": str(launcher),
            "producing_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
            "authority_semantics": "capability qualification only; grants zero task or review authority",
        }
        receipt_bytes = self.launcher.canonical_json_bytes(receipt)
        receipt_sha256 = self.launcher.sha256_bytes(receipt_bytes)
        receipt_path = receipts / f"{receipt_sha256}.json"
        receipt_path.write_bytes(receipt_bytes)
        receipt_path.chmod(0o400)
        current = {
            "kind": "claude_reviewer_current_selection",
            "schema_version": 2,
            "entry_contract_id": entry_contract_id,
            "claude_selector": str(selector),
            "receipt_path": str(receipt_path),
            "receipt_sha256": receipt_sha256,
        }
        current_path = qualification / "current-selection.json"
        current_path.write_bytes(self.launcher.canonical_json_bytes(current))
        current_path.chmod(0o600)
        manifest_path = installed / "claude-review-installation.json"
        manifest_path.write_bytes(self.launcher.canonical_json_bytes(manifest))
        manifest_path.chmod(0o400)
        return {
            "launcher": launcher,
            "launcher_bytes": launcher_bytes,
            "active_rule": active_rule,
            "auth_diagnostics": auth_diagnostics,
            "candidate": candidate,
            "marker": marker,
            "versions": versions,
            "selector": selector,
            "manifest": manifest,
            "manifest_path": manifest_path,
            "qualification": qualification,
            "receipts": receipts,
            "current_path": current_path,
            "current": current,
            "receipt_path": receipt_path,
        }

    def run_production_preflight(self, fixture, name: str):
        diagnostics = fixture["auth_diagnostics"] / f"{name}.json"
        completed = subprocess.run(
            [str(fixture["launcher"]), "--auth-preflight", "--diagnostics-file", str(diagnostics)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "FIXTURE_PROVIDER_RUNS": str(fixture["marker"])},
        )
        return completed, diagnostics

    def run_installer(self, root: Path, selector: Path, activation_name: str, commit: str):
        activation_receipt = root / "activation" / activation_name
        arguments = SimpleNamespace(
            claude_bin=selector,
            install_root=root / "install-root",
            active_rule=root / "active.rules",
            activation_receipt=activation_receipt,
            qualification_root=root / "qualification-root",
            expected_existing_rule_sha256=None,
            forbidden_root=[],
        )

        def fake_git(*git_arguments):
            if git_arguments[0] == "status":
                return ""
            if git_arguments == ("rev-parse", "HEAD"):
                return commit
            if git_arguments == ("remote", "get-url", "origin"):
                return "git@github.com:ctrl-alt-keith/ai-workflow-playbook.git"
            raise AssertionError(git_arguments)

        output = io.StringIO()
        with mock.patch.object(self.installer, "parse_arguments", return_value=arguments), mock.patch.object(
            self.installer, "git", side_effect=fake_git
        ), contextlib.redirect_stdout(output):
            self.assertEqual(self.installer.main(), 0)
        return json.loads(output.getvalue()), activation_receipt

    def create_installer_targets(self, root: Path):
        targets = []
        for number in (1, 2, 3):
            target = root / f"installer-claude-{number}"
            target.write_text(
                "#!/bin/sh\n"
                f"printf 'installer-claude {number}\\n'\n",
                encoding="utf-8",
            )
            target.chmod(0o755)
            targets.append(target)
        selector = root / "installer-claude"
        selector.symlink_to(targets[0])
        return selector, targets

    def test_project_rule_never_allows_repository_relative_launcher(self):
        rule = CODEX_RULE.read_text(encoding="utf-8")
        self.assertNotIn('decision="allow"', rule)
        self.assertIn('decision="prompt"', rule)

    def test_rule_template_binds_only_one_exact_absolute_launcher(self):
        template = CODEX_RULE_TEMPLATE.read_text(encoding="utf-8")
        rendered = template.replace("__CLAUDE_REVIEW_LAUNCHER__", "/operator/libexec/cak-155/claude-review")
        self.assertEqual(rendered.count('decision="allow"'), 2)
        self.assertIn('["/operator/libexec/cak-155/claude-review", "--auth-preflight"]', rendered)
        self.assertIn('["/operator/libexec/cak-155/claude-review", "--review-config"]', rendered)
        self.assertIn('"--qualify-claude-identity"', rendered)
        self.assertEqual(rendered.count('decision="prompt"'), 1)
        self.assertNotIn("./scripts/claude-review", rendered)

    def test_entry_contract_identity_excludes_source_provenance(self):
        contract = {
            "launcher_sha256": "a" * 64,
            "rule_template_sha256": "b" * 64,
            "installation_schema_version": 2,
            "qualification_schema_version": 2,
        }
        first = self.installer.entry_contract_identity(contract)
        second = self.installer.entry_contract_identity({**contract})
        self.assertEqual(first, second)
        self.assertNotIn("source_commit", contract)
        self.assertNotEqual(
            first,
            self.installer.entry_contract_identity({**contract, "launcher_sha256": "c" * 64}),
        )
        self.assertNotEqual(
            first,
            self.installer.entry_contract_identity({**contract, "qualification_schema_version": 3}),
        )

    def test_managed_selector_advance_uses_prompted_qualification_without_entry_or_rule_change(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            launcher_sha256 = self.launcher.sha256_bytes(fixture["launcher"].read_bytes())
            rule_bytes = fixture["active_rule"].read_bytes()
            current_bytes = fixture["current_path"].read_bytes()

            accepted, accepted_diagnostics = self.run_production_preflight(fixture, "accepted-v1")
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(fixture["current_path"].read_bytes(), current_bytes)
            first_record = json.loads(accepted_diagnostics.read_text(encoding="utf-8"))
            self.assertEqual(
                first_record["runtime"]["reviewer_execution_identity"]["qualification_receipt_sha256"],
                fixture["current"]["receipt_sha256"],
            )

            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            rejected, _ = self.run_production_preflight(fixture, "rejected-v2")
            self.assertEqual(rejected.returncode, 70)
            self.assertIn('"failure_classification": "reviewer_identity_qualification_required"', rejected.stderr)
            self.assertIn("--qualify-claude-identity", rejected.stderr)
            self.assertEqual(
                fixture["marker"].read_text(encoding="utf-8"),
                "fixture-claude 1:version\n" * 2 + "fixture-claude 1:run\n",
            )

            observed = self.launcher.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            observed_digest = self.launcher.file_identity_digest(observed)
            qualify = subprocess.run(
                [
                    str(fixture["launcher"]),
                    "--qualify-claude-identity",
                    "--expected-current-receipt-sha256",
                    fixture["current"]["receipt_sha256"],
                    "--expected-observed-file-identity-sha256",
                    observed_digest,
                ],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "FIXTURE_PROVIDER_RUNS": str(fixture["marker"])},
            )
            self.assertEqual(qualify.returncode, 0, qualify.stderr)
            qualification_result = json.loads(qualify.stdout)
            self.assertEqual(qualification_result["file_identity"]["resolved_path"], str(fixture["versions"][1]))
            self.assertEqual(self.launcher.sha256_bytes(fixture["launcher"].read_bytes()), launcher_sha256)
            self.assertEqual(fixture["active_rule"].read_bytes(), rule_bytes)
            self.assertEqual(fixture["manifest_path"].read_bytes(), self.launcher.canonical_json_bytes(fixture["manifest"]))

            post, post_diagnostics = self.run_production_preflight(fixture, "accepted-v2")
            self.assertEqual(post.returncode, 0, post.stderr)
            post_record = json.loads(post_diagnostics.read_text(encoding="utf-8"))
            execution_identity = post_record["runtime"]["reviewer_execution_identity"]
            self.assertEqual(execution_identity["resolved_path"], str(fixture["versions"][1]))
            self.assertEqual(execution_identity["version"], "fixture-claude 2")
            self.assertEqual(execution_identity["qualification_receipt_sha256"], qualification_result["qualification_receipt_sha256"])

    def test_unqualified_malicious_version_is_never_invoked_by_auth_or_review(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            malicious_marker = Path(temporary_directory) / "malicious-version"
            malicious = Path(temporary_directory) / "malicious-claude"
            malicious.write_text(
                "#!/usr/bin/env python3\n"
                "import pathlib, sys\n"
                f"marker = pathlib.Path({str(malicious_marker)!r})\n"
                "marker.open('a').write('version-side-effect\\n' if '--version' in sys.argv else 'run-side-effect\\n')\n"
                "print('malicious-claude 2' if '--version' in sys.argv else 'CLAUDE_AUTH_OK')\n",
                encoding="utf-8",
            )
            malicious.chmod(0o755)
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(malicious)
            current_bytes = fixture["current_path"].read_bytes()
            receipt_names = {path.name for path in fixture["receipts"].iterdir()}

            for arguments in (
                ["--auth-preflight", "--diagnostics-file", str(fixture["auth_diagnostics"] / "drift-auth.json")],
                ["--review-config", str(Path(temporary_directory) / "unread-review-config.json")],
            ):
                completed = subprocess.run(
                    [str(fixture["launcher"]), *arguments],
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(completed.returncode, 70, completed.stderr)
                self.assertIn("reviewer_identity_qualification_required", completed.stderr)
                self.assertIn("observed_file_identity_sha256", completed.stderr)
                self.assertIn("--expected-observed-file-identity-sha256", completed.stderr)
                self.assertNotIn("observed_version", completed.stderr)
                self.assertFalse(malicious_marker.exists())
                self.assertEqual(fixture["current_path"].read_bytes(), current_bytes)
                self.assertEqual({path.name for path in fixture["receipts"].iterdir()}, receipt_names)

            observed = self.launcher.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            qualified = subprocess.run(
                [
                    str(fixture["launcher"]),
                    "--qualify-claude-identity",
                    "--expected-current-receipt-sha256",
                    fixture["current"]["receipt_sha256"],
                    "--expected-observed-file-identity-sha256",
                    self.launcher.file_identity_digest(observed),
                ],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(qualified.returncode, 0, qualified.stderr)
            self.assertEqual(malicious_marker.read_text(encoding="utf-8"), "version-side-effect\n")
            result = json.loads(qualified.stdout)
            receipt = json.loads(Path(result["qualification_receipt_path"]).read_text(encoding="utf-8"))
            self.assertEqual(receipt["file_identity"], observed)
            self.assertEqual(receipt["version"], "malicious-claude 2")

    def test_noop_qualification_is_rejected_without_execution_or_state_change(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            installed_module = load_script("claude_review_noop_qualification", fixture["launcher"])
            observed = installed_module.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            before_current = fixture["current_path"].read_bytes()
            before_receipts = {path.name for path in fixture["receipts"].iterdir()}
            with self.assertRaisesRegex(ValueError, "no-op"):
                installed_module.qualify_claude_identity(
                    os.geteuid(),
                    expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                    expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                )
            self.assertFalse(fixture["marker"].exists())
            self.assertEqual(fixture["current_path"].read_bytes(), before_current)
            self.assertEqual({path.name for path in fixture["receipts"].iterdir()}, before_receipts)

    def test_qualification_races_never_replace_current_selection(self):
        scenarios = ("before_lock", "before_version", "during_version", "after_version")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
                installed_module = load_script(f"claude_review_race_{scenario}", fixture["launcher"])
                fixture["selector"].unlink()
                fixture["selector"].symlink_to(fixture["versions"][1])
                observed = installed_module.executable_file_identity(
                    fixture["selector"], os.geteuid(), [fixture["candidate"]]
                )
                before_current = fixture["current_path"].read_bytes()
                before_receipts = {path.name for path in fixture["receipts"].iterdir()}

                if scenario == "before_lock":
                    fixture["selector"].unlink()
                    fixture["selector"].symlink_to(fixture["versions"][2])
                    patches = contextlib.nullcontext()
                elif scenario in {"before_version", "during_version"}:
                    original_version = installed_module.version_of

                    def move_before_version(executable, environment, *, cwd):
                        if scenario == "before_version":
                            fixture["selector"].unlink()
                            fixture["selector"].symlink_to(fixture["versions"][2])
                        result = original_version(executable, environment, cwd=cwd)
                        if scenario == "during_version":
                            fixture["selector"].unlink()
                            fixture["selector"].symlink_to(fixture["versions"][2])
                        return result

                    patches = mock.patch.object(installed_module, "version_of", move_before_version)
                else:
                    original_observation = installed_module.executable_file_identity
                    observations = 0

                    def move_on_final_observation(path, effective_uid, forbidden_roots=None):
                        nonlocal observations
                        observations += 1
                        if observations == 3:
                            fixture["selector"].unlink()
                            fixture["selector"].symlink_to(fixture["versions"][2])
                        return original_observation(path, effective_uid, forbidden_roots)

                    patches = mock.patch.object(
                        installed_module, "executable_file_identity", move_on_final_observation
                    )
                with patches, mock.patch.dict(
                    os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}
                ), self.assertRaises(ValueError):
                    installed_module.qualify_claude_identity(
                        os.geteuid(),
                        expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                        expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                    )
                self.assertEqual(fixture["current_path"].read_bytes(), before_current)
                self.assertEqual({path.name for path in fixture["receipts"].iterdir()}, before_receipts)

    def test_runtime_qualification_fsyncs_receipt_directory_before_current_selection(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            installed_module = load_script("claude_review_receipt_durability", fixture["launcher"])
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            observed = installed_module.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            events = []
            original_replace = installed_module.atomic_replace_current_selection

            def record_fsync(path):
                events.append(("fsync", path))

            def record_replace(*arguments):
                events.append(("replace", arguments[0]))
                return original_replace(*arguments)

            with mock.patch.object(installed_module, "fsync_directory", record_fsync), mock.patch.object(
                installed_module, "atomic_replace_current_selection", record_replace
            ), mock.patch.dict(os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}):
                installed_module.qualify_claude_identity(
                    os.geteuid(),
                    expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                    expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                )

            receipt_fsync = events.index(("fsync", fixture["receipts"]))
            current_replace = next(
                index for index, event in enumerate(events) if event == ("replace", fixture["current_path"])
            )
            self.assertLess(receipt_fsync, current_replace)

    def test_runtime_receipt_directory_fsync_failure_preserves_current_selection(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            installed_module = load_script("claude_review_receipt_fsync_failure", fixture["launcher"])
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            observed = installed_module.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            before_current = fixture["current_path"].read_bytes()

            with mock.patch.object(
                installed_module,
                "fsync_directory",
                side_effect=OSError("fixture receipt-directory fsync failure"),
            ), mock.patch.dict(os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}), self.assertRaisesRegex(
                OSError, "receipt-directory fsync failure"
            ):
                installed_module.qualify_claude_identity(
                    os.geteuid(),
                    expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                    expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                )

            self.assertEqual(fixture["current_path"].read_bytes(), before_current)

    def test_atomic_current_selection_cleanup_and_ambiguous_residue(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            current = root / "current-selection.json"
            current.write_bytes(b"prior\n")
            current.chmod(0o600)
            with self.assertRaisesRegex(ValueError, "compare-and-swap"):
                self.launcher.atomic_replace_current_selection(
                    current, {"next": True}, b"stale\n", os.geteuid()
                )
            self.assertEqual(current.read_bytes(), b"prior\n")
            self.assertEqual(list(root.glob(".current-selection.json.*.tmp")), [])

            def contaminate_then_fail(source, destination):
                Path(source).chmod(0o644)
                raise OSError("fixture replacement failure")

            with mock.patch.object(self.launcher.os, "replace", contaminate_then_fail):
                with self.assertRaisesRegex(RuntimeError, "residue preserved") as raised:
                    self.launcher.atomic_replace_current_selection(
                        current, {"next": True}, b"prior\n", os.geteuid()
                    )
            self.assertIsInstance(raised.exception.__cause__, OSError)
            self.assertEqual(str(raised.exception.__cause__), "fixture replacement failure")
            residue = list(root.glob(".current-selection.json.*.tmp"))
            self.assertEqual(len(residue), 1)
            self.assertEqual(current.read_bytes(), b"prior\n")

    def test_consecutive_upgrades_and_rollback_require_singular_lineage_transitions(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            predecessor = fixture["current"]["receipt_sha256"]
            lineage = []
            for target in (fixture["versions"][1], fixture["versions"][2], fixture["versions"][0]):
                fixture["selector"].unlink()
                fixture["selector"].symlink_to(target)
                rejected, _ = self.run_production_preflight(fixture, f"reject-{target.name}")
                self.assertEqual(rejected.returncode, 70)
                observed = self.launcher.executable_file_identity(
                    fixture["selector"], os.geteuid(), [fixture["candidate"]]
                )
                qualified = subprocess.run(
                    [
                        str(fixture["launcher"]),
                        "--qualify-claude-identity",
                        "--expected-current-receipt-sha256",
                        predecessor,
                        "--expected-observed-file-identity-sha256",
                        self.launcher.file_identity_digest(observed),
                    ],
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={**os.environ, "FIXTURE_PROVIDER_RUNS": str(fixture["marker"])},
                )
                self.assertEqual(qualified.returncode, 0, qualified.stderr)
                result = json.loads(qualified.stdout)
                receipt = json.loads(Path(result["qualification_receipt_path"]).read_text(encoding="utf-8"))
                self.assertEqual(receipt["predecessor_receipt_sha256"], predecessor)
                predecessor = result["qualification_receipt_sha256"]
                lineage.append(predecessor)
                accepted, _ = self.run_production_preflight(fixture, f"accept-{target.name}")
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(len(set(lineage)), 3)
            self.assertEqual(len(list(fixture["receipts"].glob("*.json"))), 4)

    def test_stale_or_arbitrary_qualification_request_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            observed = self.launcher.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            base = [str(fixture["launcher"]), "--qualify-claude-identity"]
            stale = subprocess.run(
                [
                    *base,
                    "--expected-current-receipt-sha256",
                    "0" * 64,
                    "--expected-observed-file-identity-sha256",
                    self.launcher.file_identity_digest(observed),
                ],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(stale.returncode, 70)
            self.assertIn("stale predecessor", stale.stderr)
            arbitrary = subprocess.run(
                [
                    *base,
                    "--claude-bin",
                    "/bin/echo",
                    "--expected-current-receipt-sha256",
                    fixture["current"]["receipt_sha256"],
                    "--expected-observed-file-identity-sha256",
                    self.launcher.file_identity_digest(observed),
                ],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(arbitrary.returncode, 2)
            self.assertIn("derives the selector", arbitrary.stderr)

    def test_qualification_rejects_selector_race_without_replacing_current_selection(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            installed_module = load_script("claude_review_qualification_race", fixture["launcher"])
            expected = installed_module.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            expected_digest = installed_module.file_identity_digest(expected)
            original = installed_module.executable_file_identity
            observations = 0

            def move_after_first_observation(path, effective_uid, forbidden_roots=None):
                nonlocal observations
                observations += 1
                if observations == 2:
                    fixture["selector"].unlink()
                    fixture["selector"].symlink_to(fixture["versions"][2])
                return original(path, effective_uid, forbidden_roots)

            installed_module.executable_file_identity = move_after_first_observation
            current_bytes = fixture["current_path"].read_bytes()
            with mock.patch.dict(
                os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}
            ), self.assertRaisesRegex(ValueError, "changed during qualification"):
                installed_module.qualify_claude_identity(
                    os.geteuid(),
                    expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                    expected_observed_file_identity_sha256=expected_digest,
                )
            self.assertEqual(fixture["current_path"].read_bytes(), current_bytes)

    def test_ordinary_execution_recheck_rejects_selector_change_before_spawn(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            installed_module = load_script("claude_review_execution_race", fixture["launcher"])
            with mock.patch.dict(
                os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}
            ):
                executable, execution_identity = installed_module.qualified_execution(
                    None, os.geteuid()
                )
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            with self.assertRaisesRegex(
                installed_module.QualificationRequiredError,
                "new exact identity",
            ):
                installed_module.revalidate_execution_identity(
                    executable,
                    execution_identity,
                    os.geteuid(),
                )

    def test_tampered_or_unsafe_qualification_state_fails_closed(self):
        scenarios = ("receipt_mode", "receipt_symlink", "current_symlink")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
                if scenario == "receipt_mode":
                    fixture["receipt_path"].chmod(0o600)
                elif scenario == "receipt_symlink":
                    receipt_bytes = fixture["receipt_path"].read_bytes()
                    replacement = fixture["receipts"] / "replacement.json"
                    replacement.write_bytes(receipt_bytes)
                    replacement.chmod(0o400)
                    fixture["receipt_path"].unlink()
                    fixture["receipt_path"].symlink_to(replacement)
                else:
                    current_bytes = fixture["current_path"].read_bytes()
                    replacement = fixture["qualification"] / "replacement-current.json"
                    replacement.write_bytes(current_bytes)
                    replacement.chmod(0o600)
                    fixture["current_path"].unlink()
                    fixture["current_path"].symlink_to(replacement)
                completed, _ = self.run_production_preflight(fixture, f"unsafe-{scenario}")
                self.assertEqual(completed.returncode, 70)
                self.assertIn('"failure_classification": "reviewer_executable_not_authorized"', completed.stderr)

    def test_malformed_or_mismatched_qualification_receipt_fails_closed(self):
        scenarios = ("malformed", "schema", "entry_contract", "selector", "launcher")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
                receipt = json.loads(fixture["receipt_path"].read_text(encoding="utf-8"))
                if scenario == "malformed":
                    receipt_bytes = b"{malformed\n"
                else:
                    if scenario == "schema":
                        receipt["schema_version"] = 1
                    elif scenario == "entry_contract":
                        receipt["entry_contract_id"] = "sha256:" + "0" * 64
                    elif scenario == "selector":
                        receipt["claude_selector"] = "/bin/echo"
                    else:
                        receipt["producing_launcher_sha256"] = "0" * 64
                    receipt_bytes = self.launcher.canonical_json_bytes(receipt)
                receipt_sha256 = self.launcher.sha256_bytes(receipt_bytes)
                receipt_path = fixture["receipts"] / f"{receipt_sha256}.json"
                receipt_path.write_bytes(receipt_bytes)
                receipt_path.chmod(0o400)
                current = {
                    **fixture["current"],
                    "receipt_path": str(receipt_path),
                    "receipt_sha256": receipt_sha256,
                }
                fixture["current_path"].write_bytes(
                    self.launcher.canonical_json_bytes(current)
                )
                fixture["current_path"].chmod(0o600)
                completed, _ = self.run_production_preflight(
                    fixture, f"mismatched-{scenario}"
                )
                self.assertEqual(completed.returncode, 70)
                self.assertIn(
                    '"failure_classification": "reviewer_executable_not_authorized"',
                    completed.stderr,
                )

    def test_installed_manifest_schema_and_contract_divergence_fail_closed(self):
        scenarios = ("schema_v1", "wrong_entry_contract_id", "selector_contract_divergence")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
                manifest = json.loads(json.dumps(fixture["manifest"]))
                if scenario == "schema_v1":
                    manifest["schema_version"] = 1
                elif scenario == "wrong_entry_contract_id":
                    manifest["entry_contract_id"] = "sha256:" + "0" * 64
                else:
                    manifest["claude_selector"] = "/bin/echo"

                fixture["manifest_path"].chmod(0o600)
                fixture["manifest_path"].write_bytes(self.launcher.canonical_json_bytes(manifest))
                fixture["manifest_path"].chmod(0o400)
                self.assertEqual(stat.S_IMODE(fixture["manifest_path"].stat().st_mode), 0o400)

                completed, _ = self.run_production_preflight(fixture, f"manifest-{scenario}")
                self.assertEqual(completed.returncode, 70)
                self.assertIn(
                    '"failure_classification": "reviewer_executable_not_authorized"',
                    completed.stderr,
                )

    def test_foreign_owned_qualification_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            path_type = type(fixture["receipt_path"])

            def foreign_receipt_owner(path):
                metadata = os.lstat(path)
                if path == fixture["receipt_path"]:
                    fields = list(metadata)
                    fields[4] = metadata.st_uid + 1
                    return os.stat_result(fields)
                return metadata

            with mock.patch.object(path_type, "lstat", foreign_receipt_owner):
                with self.assertRaisesRegex(ValueError, "private regular file"):
                    self.launcher.current_qualification(fixture["manifest"], os.geteuid())

    def test_untrusted_or_same_path_drifted_executable_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            non_regular = root / "non-regular"
            non_regular.mkdir()
            selector = root / "claude-directory"
            selector.symlink_to(non_regular)
            with self.assertRaisesRegex(ValueError, "regular file"):
                self.launcher.executable_file_identity(selector, os.geteuid())

            invalid_version = root / "invalid-version"
            invalid_version.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            invalid_version.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "version identity"):
                self.launcher.qualified_executable_identity(invalid_version, os.geteuid())

            owned = root / "foreign-owned"
            owned.write_text("#!/bin/sh\necho fixture-claude\n", encoding="utf-8")
            owned.chmod(0o755)
            path_type = type(owned)

            def foreign_target_owner(path, *, follow_symlinks=True):
                metadata = os.stat(path, follow_symlinks=follow_symlinks)
                if path == owned and follow_symlinks:
                    fields = list(metadata)
                    fields[4] = metadata.st_uid + 1
                    return os.stat_result(fields)
                return metadata

            with mock.patch.object(path_type, "stat", foreign_target_owner):
                with self.assertRaisesRegex(ValueError, "user-owned regular file"):
                    self.launcher.executable_file_identity(owned, os.geteuid())

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            accepted, _ = self.run_production_preflight(fixture, "same-path-before-drift")
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            target = fixture["versions"][0]
            target.write_text(target.read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")
            target.chmod(0o755)
            rejected, _ = self.run_production_preflight(fixture, "same-path-after-drift")
            self.assertEqual(rejected.returncode, 70)
            self.assertIn(
                '"failure_classification": "reviewer_identity_qualification_required"',
                rejected.stderr,
            )
            self.assertEqual(
                fixture["marker"].read_text(encoding="utf-8"),
                "fixture-claude 1:version\n" * 2 + "fixture-claude 1:run\n",
            )

    def test_production_selector_never_uses_inherited_path(self):
        with self.assertRaisesRegex(ValueError, "absolute path"):
            self.launcher.executable_file_identity(Path("claude"), os.geteuid())

    def test_installer_rule_replacement_requires_exact_prior_identity(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            rule = Path(temporary_directory) / "claude-review.rules"
            rule.write_bytes(b"prior\n")
            with self.assertRaisesRegex(ValueError, "expected-existing-rule-sha256"):
                self.installer.replace_expected(rule, b"replacement\n", "0" * 64)
            result = self.installer.replace_expected(
                rule,
                b"replacement\n",
                self.installer.digest(b"prior\n"),
            )
            self.assertEqual(result["result"], "replaced")
            self.assertEqual(rule.read_bytes(), b"replacement\n")

    def test_installer_existing_identical_rule_requires_safe_exact_file(self):
        scenarios = ("safe", "group_writable", "world_writable", "foreign_owned", "symlink", "nonregular")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory).resolve()
                selector, _ = self.create_installer_targets(root)
                initial, _ = self.run_installer(root, selector, "initial.json", "1" * 40)
                active_rule = Path(initial["active_rule_path"])
                active_rule_bytes = active_rule.read_bytes()
                next_activation = root / "activation" / f"{scenario}.json"
                context = contextlib.nullcontext()

                if scenario == "group_writable":
                    active_rule.chmod(0o620)
                elif scenario == "world_writable":
                    active_rule.chmod(0o602)
                elif scenario == "foreign_owned":
                    path_type = type(active_rule)
                    original_lstat = path_type.lstat

                    def foreign_lstat(path):
                        metadata = original_lstat(path)
                        if path == active_rule:
                            fields = list(metadata)
                            fields[4] = metadata.st_uid + 1
                            return os.stat_result(fields)
                        return metadata

                    context = mock.patch.object(path_type, "lstat", foreign_lstat)
                elif scenario == "symlink":
                    target = root / "identical-rule-target"
                    target.write_bytes(active_rule_bytes)
                    target.chmod(0o600)
                    active_rule.unlink()
                    active_rule.symlink_to(target)
                elif scenario == "nonregular":
                    active_rule.unlink()
                    active_rule.mkdir(mode=0o700)

                with context:
                    if scenario == "safe":
                        rerun, receipt = self.run_installer(root, selector, next_activation.name, "2" * 40)
                        self.assertEqual(rerun["active_rule_result"]["result"], "existing_identical")
                        self.assertTrue(receipt.exists())
                    else:
                        with self.assertRaises((OSError, ValueError)):
                            self.run_installer(root, selector, next_activation.name, "2" * 40)
                        self.assertFalse(next_activation.exists())

    def test_initial_installation_fsyncs_receipt_directory_before_current_selection(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            events = []
            original_exclusive = self.installer.exclusive_or_identical

            def record_fsync(path):
                events.append(("fsync", path))

            def record_exclusive(path, payload, mode):
                if path.name == "current-selection.json":
                    events.append(("current", path))
                return original_exclusive(path, payload, mode)

            with mock.patch.object(self.installer, "fsync_directory", record_fsync), mock.patch.object(
                self.installer, "exclusive_or_identical", record_exclusive
            ):
                installed, _ = self.run_installer(root, selector, "initial.json", "1" * 40)

            receipt_directory = Path(installed["qualification_receipt_path"]).parent
            current_selection = receipt_directory.parent / "current-selection.json"
            self.assertLess(
                events.index(("fsync", receipt_directory)),
                events.index(("current", current_selection)),
            )
            self.assertLess(
                events.index(("current", current_selection)),
                events.index(("fsync", receipt_directory.parent)),
            )

    def test_installer_qualifies_exact_selector_target_and_rejects_writable_target(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            target = root / "claude-version"
            target.write_text("#!/bin/sh\necho fixture-claude-1\n", encoding="utf-8")
            target.chmod(0o755)
            selector = root / "claude"
            selector.symlink_to(target.name)
            identity = self.installer.exact_executable_file_identity(selector)
            self.assertEqual(identity["requested_selector"], str(selector))
            self.assertEqual(identity["resolved_path"], str(target.resolve()))
            self.assertEqual(identity["selector_kind"], "symlink")
            target.chmod(0o775)
            with self.assertRaisesRegex(ValueError, "group/world-writable"):
                self.installer.exact_executable_file_identity(selector)

    def test_installer_version_observation_matches_launcher_context_and_redaction(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            target = root / "claude-version"
            target.write_text(
                "#!/bin/sh\nprintf 'cwd=%s token=secret-value\\n' \"$PWD\"\n",
                encoding="utf-8",
            )
            target.chmod(0o755)
            selector = root / "claude"
            selector.symlink_to(target.name)

            installer_identity = self.installer.qualified_executable_identity(selector)
            launcher_identity = self.launcher.qualified_executable_identity(
                selector, os.geteuid()
            )

            self.assertEqual(installer_identity["version"], launcher_identity["version"])
            self.assertIn(str(root), installer_identity["version"])
            self.assertIn("[REDACTED]", installer_identity["version"])
            self.assertNotIn("secret-value", installer_identity["version"])

    def test_installer_rejects_nonprivate_existing_state_directories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            activation = root / "activation"
            activation.mkdir(mode=0o755)

            with self.assertRaisesRegex(ValueError, "private operator-controlled"):
                self.run_installer(root, selector, "receipt.json", "1" * 40)

            activation.chmod(0o700)
            contract_id = "sha256:" + "a" * 64
            entry_directory = root / "install-root" / f"entry-{contract_id.removeprefix('sha256:')}"
            entry_directory.mkdir(parents=True, mode=0o755)
            with mock.patch.object(
                self.installer, "entry_contract_identity", return_value=contract_id
            ), self.assertRaisesRegex(ValueError, "private operator-controlled"):
                self.run_installer(root, selector, "receipt-2.json", "2" * 40)

    def test_drift_action_quotes_launcher_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve() / "review root"
            root.mkdir()
            fixture = self.create_installed_fixture(root)
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])

            rejected, _ = self.run_production_preflight(fixture, "quoted-action")

            self.assertEqual(rejected.returncode, 70)
            encoded = rejected.stderr.split("claude-review diagnostics: ", 1)[1].strip()
            diagnostic = json.loads(encoded)
            action = diagnostic["qualification_transition"]["next_qualification_action"]
            self.assertEqual(
                shlex.split(action),
                [
                    str(fixture["launcher"]),
                    "--qualify-claude-identity",
                    "--expected-current-receipt-sha256",
                    fixture["current"]["receipt_sha256"],
                    "--expected-observed-file-identity-sha256",
                    diagnostic["qualification_transition"]["observed_file_identity_sha256"],
                ],
            )

    def test_installer_rejects_destinations_overlapping_forbidden_writable_roots(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            with self.assertRaisesRegex(ValueError, "forbidden writable root"):
                self.installer.validate_destination(root / "installed" / "claude-review", [root])

    def test_installer_reruns_preserve_upgrade_and_rollback_lineage(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, targets = self.create_installer_targets(root)
            initial, _ = self.run_installer(root, selector, "activation-1.json", "1" * 40)
            launcher = Path(initial["installed_launcher_path"])
            manifest_path = Path(initial["installation_manifest_path"])
            current_path = Path(initial["current_selection_path"])
            receipts = Path(initial["qualification_receipts_directory"])
            active_rule = Path(initial["active_rule_path"])
            immutable = {
                "launcher": launcher.read_bytes(),
                "manifest": manifest_path.read_bytes(),
                "active_rule": active_rule.read_bytes(),
                "entry": initial["entry_contract_id"],
            }
            installed_module = load_script("claude_review_installer_rerun", launcher)
            initial_current = current_path.read_bytes()
            initial_receipts = {path.name for path in receipts.iterdir()}
            self.assertEqual(len(initial_receipts), 1)
            initial_rerun, _ = self.run_installer(
                root, selector, "activation-initial-rerun.json", "2" * 40
            )
            self.assertEqual(initial_rerun["entry_contract_id"], immutable["entry"])
            self.assertEqual(current_path.read_bytes(), initial_current)
            self.assertEqual({path.name for path in receipts.iterdir()}, initial_receipts)

            for index, target in enumerate((targets[1], targets[2], targets[0]), start=3):
                selector.unlink()
                selector.symlink_to(target)
                current = json.loads(current_path.read_text(encoding="utf-8"))
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                forbidden = [Path(value) for value in manifest["forbidden_roots"]]
                observed = installed_module.executable_file_identity(
                    selector, os.geteuid(), forbidden
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(
                        installed_module.qualify_claude_identity(
                            os.geteuid(),
                            expected_current_receipt_sha256=current["receipt_sha256"],
                            expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                        ),
                        0,
                    )
                before_current = current_path.read_bytes()
                before_receipts = {path.name for path in receipts.iterdir()}
                rerun, activation = self.run_installer(
                    root, selector, f"activation-{index}.json", f"{index}" * 40
                )
                self.assertEqual(rerun["entry_contract_id"], immutable["entry"])
                self.assertEqual(launcher.read_bytes(), immutable["launcher"])
                self.assertEqual(manifest_path.read_bytes(), immutable["manifest"])
                self.assertEqual(active_rule.read_bytes(), immutable["active_rule"])
                self.assertEqual(current_path.read_bytes(), before_current)
                self.assertEqual({path.name for path in receipts.iterdir()}, before_receipts)
                self.assertEqual(
                    rerun["qualification_receipt_sha256"],
                    json.loads(before_current)["receipt_sha256"],
                )
                self.assertTrue(activation.exists())
                provenance = launcher.parent / f"source-provenance-{str(index) * 40}.json"
                self.assertTrue(provenance.exists())

    def test_installer_selector_drift_is_qualification_required_before_rule_or_receipt(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            marker = root / "unqualified-version-marker"
            selector, targets = self.create_installer_targets(root)
            initial, _ = self.run_installer(root, selector, "activation-1.json", "1" * 40)
            malicious = targets[1]
            malicious.write_text(
                "#!/bin/sh\n"
                f"touch {shlex.quote(str(marker))}\n"
                "printf 'malicious 2\\n'\n",
                encoding="utf-8",
            )
            malicious.chmod(0o755)
            selector.unlink()
            selector.symlink_to(malicious)
            current_path = Path(initial["current_selection_path"])
            receipts = Path(initial["qualification_receipts_directory"])
            active_rule = Path(initial["active_rule_path"])
            before_current = current_path.read_bytes()
            before_receipts = {path.name for path in receipts.iterdir()}
            active_rule.write_bytes(b"operator-prior-rule\n")
            active_rule.chmod(0o600)
            before_rule = active_rule.read_bytes()
            activation = root / "activation" / "drift-rerun.json"
            with self.assertRaisesRegex(self.installer.QualificationRequiredError, "qualification required"):
                self.run_installer(root, selector, activation.name, "2" * 40)
            self.assertFalse(marker.exists())
            self.assertEqual(current_path.read_bytes(), before_current)
            self.assertEqual({path.name for path in receipts.iterdir()}, before_receipts)
            self.assertEqual(active_rule.read_bytes(), before_rule)
            self.assertFalse(activation.exists())

    def test_installer_and_launcher_share_the_full_invalid_state_matrix(self):
        scenarios = (
            "current_symlink", "receipt_symlink", "current_mode", "receipt_mode",
            "foreign_owner", "malformed_current", "nonobject_current", "malformed_receipt",
            "current_wrong_kind", "current_wrong_schema", "current_wrong_entry",
            "current_wrong_selector", "wrong_kind", "wrong_schema", "wrong_entry",
            "wrong_selector", "wrong_producer", "wrong_authority", "wrong_file_identity",
            "missing_receipt",
            "receipt_digest", "escaped_receipt", "ambiguous_predecessor",
            "self_predecessor", "predecessor_digest",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
                current = dict(fixture["current"])
                receipt = json.loads(fixture["receipt_path"].read_text(encoding="utf-8"))

                def write_current(record):
                    fixture["current_path"].write_bytes(self.launcher.canonical_json_bytes(record))
                    fixture["current_path"].chmod(0o600)

                def select_receipt(payload, *, path=None):
                    receipt_bytes = payload if isinstance(payload, bytes) else self.launcher.canonical_json_bytes(payload)
                    receipt_sha256 = self.launcher.sha256_bytes(receipt_bytes)
                    selected = path or fixture["receipts"] / f"{receipt_sha256}.json"
                    selected.parent.mkdir(parents=True, exist_ok=True)
                    selected.write_bytes(receipt_bytes)
                    selected.chmod(0o400)
                    write_current({**current, "receipt_path": str(selected), "receipt_sha256": receipt_sha256})
                    return selected

                if scenario == "current_symlink":
                    replacement = fixture["qualification"] / "replacement-current.json"
                    replacement.write_bytes(fixture["current_path"].read_bytes())
                    replacement.chmod(0o600)
                    fixture["current_path"].unlink()
                    fixture["current_path"].symlink_to(replacement)
                elif scenario == "receipt_symlink":
                    replacement = fixture["receipts"] / "replacement.json"
                    replacement.write_bytes(fixture["receipt_path"].read_bytes())
                    replacement.chmod(0o400)
                    fixture["receipt_path"].unlink()
                    fixture["receipt_path"].symlink_to(replacement)
                elif scenario == "current_mode":
                    fixture["current_path"].chmod(0o644)
                elif scenario == "receipt_mode":
                    fixture["receipt_path"].chmod(0o600)
                elif scenario == "malformed_current":
                    fixture["current_path"].write_bytes(b"{malformed\n")
                elif scenario == "nonobject_current":
                    fixture["current_path"].write_bytes(b"[]\n")
                elif scenario.startswith("current_wrong_"):
                    field, value = {
                        "current_wrong_kind": ("kind", "wrong"),
                        "current_wrong_schema": ("schema_version", 1),
                        "current_wrong_entry": ("entry_contract_id", "sha256:" + "0" * 64),
                        "current_wrong_selector": ("claude_selector", "/bin/echo"),
                    }[scenario]
                    write_current({**current, field: value})
                elif scenario == "malformed_receipt":
                    select_receipt(b"{malformed\n")
                elif scenario in {
                    "wrong_kind", "wrong_schema", "wrong_entry", "wrong_selector",
                    "wrong_producer", "wrong_authority",
                }:
                    field, value = {
                        "wrong_kind": ("kind", "wrong"),
                        "wrong_schema": ("schema_version", 1),
                        "wrong_entry": ("entry_contract_id", "sha256:" + "0" * 64),
                        "wrong_selector": ("claude_selector", "/bin/echo"),
                        "wrong_producer": ("producing_launcher_sha256", "0" * 64),
                        "wrong_authority": ("authority_semantics", "approval proof"),
                    }[scenario]
                    select_receipt({**receipt, field: value})
                elif scenario == "wrong_file_identity":
                    select_receipt({
                        **receipt,
                        "file_identity": {
                            **receipt["file_identity"],
                            "resolved_sha256": "not-a-digest",
                        },
                    })
                elif scenario == "missing_receipt":
                    missing_sha = "a" * 64
                    write_current({
                        **current,
                        "receipt_path": str(fixture["receipts"] / f"{missing_sha}.json"),
                        "receipt_sha256": missing_sha,
                    })
                elif scenario == "receipt_digest":
                    wrong_sha = "b" * 64
                    wrong_path = fixture["receipts"] / f"{wrong_sha}.json"
                    wrong_path.write_bytes(fixture["receipt_path"].read_bytes())
                    wrong_path.chmod(0o400)
                    write_current({**current, "receipt_path": str(wrong_path), "receipt_sha256": wrong_sha})
                elif scenario == "escaped_receipt":
                    select_receipt(receipt, path=Path(temporary_directory) / "escaped" / "receipt.json")
                elif scenario == "ambiguous_predecessor":
                    select_receipt({**receipt, "predecessor_receipt_sha256": "c" * 64})
                elif scenario == "predecessor_digest":
                    predecessor_sha = "d" * 64
                    predecessor_path = fixture["receipts"] / f"{predecessor_sha}.json"
                    predecessor_path.write_bytes(b"not-the-declared-digest\n")
                    predecessor_path.chmod(0o400)
                    select_receipt({
                        **receipt,
                        "predecessor_receipt_sha256": predecessor_sha,
                        "predecessor_receipt_path": str(predecessor_path),
                    })

                if scenario == "foreign_owner":
                    path_type = type(fixture["receipt_path"])
                    original_lstat = path_type.lstat

                    def foreign_lstat(path):
                        metadata = original_lstat(path)
                        if path == fixture["receipt_path"]:
                            fields = list(metadata)
                            fields[4] = metadata.st_uid + 1
                            return os.stat_result(fields)
                        return metadata

                    context = mock.patch.object(path_type, "lstat", foreign_lstat)
                elif scenario == "self_predecessor":
                    self_sha = "e" * 64
                    self_path = fixture["receipts"] / f"{self_sha}.json"
                    self_receipt = {
                        **receipt,
                        "predecessor_receipt_sha256": self_sha,
                        "predecessor_receipt_path": str(self_path),
                    }
                    self_path.write_bytes(self.launcher.canonical_json_bytes(self_receipt))
                    self_path.chmod(0o400)
                    write_current({**current, "receipt_path": str(self_path), "receipt_sha256": self_sha})
                    context = contextlib.ExitStack()
                    context.enter_context(mock.patch.object(self.installer, "digest", return_value=self_sha))
                    context.enter_context(mock.patch.object(self.launcher, "sha256_bytes", return_value=self_sha))
                else:
                    context = contextlib.nullcontext()

                with context:
                    with self.assertRaises((OSError, ValueError)):
                        self.installer.validated_existing_qualification(fixture["manifest"])
                    with self.assertRaises((OSError, ValueError)):
                        self.launcher.current_qualification(fixture["manifest"], os.geteuid())

    def test_temporary_production_install_binds_launcher_rule_and_claude_identity(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            installed = root / "installed"
            installed.mkdir(mode=0o700)
            launcher = installed / "claude-review"
            launcher_bytes = LAUNCHER.read_bytes()
            launcher.write_bytes(launcher_bytes)
            launcher.chmod(0o500)
            active_rule = root / "active.rules"
            active_rule.write_text("fixture active rule\n", encoding="utf-8")
            auth_diagnostics = root / "auth-diagnostics"
            auth_diagnostics.mkdir(mode=0o700)
            candidate = root / "candidate"
            candidate.mkdir()
            count = root / "count"
            qualified = root / "qualified-claude"
            shadow = candidate / "claude"
            fake_body = (
                "#!/usr/bin/env python3\n"
                "import os, pathlib, sys\n"
                "if '--version' in sys.argv:\n"
                "    print('fixture-claude 1')\n"
                "    raise SystemExit(0)\n"
                "pathlib.Path(os.environ['FIXTURE_COUNT']).open('a').write('run\\n')\n"
                "print('CLAUDE_AUTH_OK')\n"
            )
            qualified.write_text(fake_body, encoding="utf-8")
            qualified.chmod(0o755)
            selector = root / "claude"
            selector.symlink_to(qualified)
            shadow.write_text(fake_body.replace("fixture-claude 1", "shadow-claude 1"), encoding="utf-8")
            shadow.chmod(0o755)
            with mock.patch.dict(os.environ, {"FIXTURE_COUNT": str(count)}):
                qualified_identity = self.launcher.qualified_executable_identity(
                    selector, os.geteuid(), [candidate]
                )
            count.unlink(missing_ok=True)
            entry_contract = {
                "entry_contract_schema_version": 1,
                "installation_schema_version": 2,
                "qualification_schema_version": 2,
                "launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
                "rule_template_sha256": "fixture-rule-template",
                "claude_selector": str(selector),
                "active_rule_path": str(active_rule),
                "forbidden_roots": [str(candidate)],
                "auth_diagnostics_directory": str(auth_diagnostics),
                "qualification_root": str(root / "qualification-root"),
            }
            entry_contract_id = "sha256:" + self.launcher.sha256_bytes(
                self.launcher.canonical_json_bytes(entry_contract)
            )
            qualification = root / "qualification-root" / entry_contract_id.removeprefix("sha256:")
            receipts = qualification / "receipts"
            receipts.mkdir(parents=True, mode=0o700)
            qualification.chmod(0o700)
            receipts.chmod(0o700)
            lock = qualification / "qualification.lock"
            lock.write_text("fixture lock\n", encoding="utf-8")
            lock.chmod(0o600)
            manifest = {
                "schema_version": 2,
                "entry_contract_id": entry_contract_id,
                "entry_contract": entry_contract,
                "installed_launcher_path": str(launcher),
                "installed_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
                "active_rule_path": str(active_rule),
                "active_rule_sha256": self.launcher.sha256_bytes(active_rule.read_bytes()),
                "claude_selector": str(selector),
                "forbidden_roots": [str(candidate)],
                "auth_diagnostics_directory": str(auth_diagnostics),
                "qualification_schema_version": 2,
                "qualification_directory": str(qualification),
                "qualification_receipts_directory": str(receipts),
                "current_selection_path": str(qualification / "current-selection.json"),
                "qualification_lock_path": str(lock),
            }
            receipt = {
                "kind": "claude_reviewer_qualification_receipt",
                "schema_version": 2,
                "entry_contract_id": entry_contract_id,
                "claude_selector": str(selector),
                "file_identity": qualified_identity["file_identity"],
                "version": qualified_identity["version"],
                "predecessor_receipt_sha256": None,
                "predecessor_receipt_path": None,
                "producing_launcher_path": str(launcher),
                "producing_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
                "authority_semantics": "capability qualification only; grants zero task or review authority",
            }
            receipt_bytes = self.launcher.canonical_json_bytes(receipt)
            receipt_sha256 = self.launcher.sha256_bytes(receipt_bytes)
            receipt_path = receipts / f"{receipt_sha256}.json"
            receipt_path.write_bytes(receipt_bytes)
            receipt_path.chmod(0o400)
            current = {
                "kind": "claude_reviewer_current_selection",
                "schema_version": 2,
                "entry_contract_id": entry_contract_id,
                "claude_selector": str(selector),
                "receipt_path": str(receipt_path),
                "receipt_sha256": receipt_sha256,
            }
            current_path = qualification / "current-selection.json"
            current_path.write_bytes(self.launcher.canonical_json_bytes(current))
            current_path.chmod(0o600)
            manifest_path = installed / "claude-review-installation.json"
            manifest_path.write_bytes(self.launcher.canonical_json_bytes(manifest))
            manifest_path.chmod(0o400)
            environment = os.environ.copy()
            environment.pop("CLAUDE_REVIEW_TEST_FIXTURE", None)
            environment.update({"FIXTURE_COUNT": str(count), "PATH": f"{candidate}{os.pathsep}/usr/bin:/bin"})

            accepted_diagnostics = auth_diagnostics / "accepted.json"
            accepted = subprocess.run(
                [str(launcher), "--auth-preflight", "--diagnostics-file", str(accepted_diagnostics)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(count.read_text(encoding="utf-8"), "run\n")
            accepted_record = json.loads(accepted_diagnostics.read_text(encoding="utf-8"))
            self.assertEqual(accepted_record["runtime"]["claude_executable"], str(qualified))
            self.assertEqual(
                accepted_record["runtime"]["reviewer_execution_identity"]["qualification"],
                "current_qualification_receipt",
            )

            inherited_fixture_diagnostics = auth_diagnostics / "inherited-fixture.json"
            inherited_fixture_environment = environment.copy()
            inherited_fixture_environment.update(
                {
                    "CLAUDE_REVIEW_TEST_FIXTURE": "1",
                    "CLAUDE_REVIEW_TEST_SCRATCH_PARENT": str(candidate),
                }
            )
            inherited_fixture = subprocess.run(
                [
                    str(launcher),
                    "--auth-preflight",
                    "--diagnostics-file",
                    str(inherited_fixture_diagnostics),
                ],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=inherited_fixture_environment,
            )
            self.assertEqual(inherited_fixture.returncode, 0)
            inherited_fixture_record = json.loads(
                inherited_fixture_diagnostics.read_text(encoding="utf-8")
            )
            self.assertNotEqual(
                inherited_fixture_record["attempt_scratch"]["projection"],
                "test_fixture_explicit_parent",
            )
            self.assertNotEqual(
                Path(inherited_fixture_record["attempt_scratch"]["path"]).parent,
                candidate,
            )

            outside_diagnostics = root / "outside.json"
            outside = subprocess.run(
                [str(launcher), "--auth-preflight", "--diagnostics-file", str(outside_diagnostics)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            self.assertEqual(outside.returncode, 70)
            self.assertFalse(outside_diagnostics.exists())
            self.assertEqual(count.read_text(encoding="utf-8"), "run\nrun\n")

            launcher.chmod(0o700)
            launcher.write_bytes(launcher_bytes + b"\n")
            launcher.chmod(0o500)
            drifted_diagnostics = auth_diagnostics / "drifted.json"
            drifted = subprocess.run(
                [str(launcher), "--auth-preflight", "--diagnostics-file", str(drifted_diagnostics)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            self.assertEqual(drifted.returncode, 70)
            self.assertFalse(drifted_diagnostics.exists())
            self.assertEqual(count.read_text(encoding="utf-8"), "run\nrun\n")

            launcher.chmod(0o700)
            launcher.write_bytes(launcher_bytes)
            launcher.chmod(0o500)
            arbitrary_diagnostics = auth_diagnostics / "arbitrary.json"
            arbitrary = subprocess.run(
                [
                    str(launcher),
                    "--auth-preflight",
                    "--claude-bin",
                    "/bin/echo",
                    "--diagnostics-file",
                    str(arbitrary_diagnostics),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            self.assertEqual(arbitrary.returncode, 70)
            self.assertFalse(arbitrary_diagnostics.exists())
            self.assertEqual(count.read_text(encoding="utf-8"), "run\nrun\n")

            selector.unlink()
            selector.symlink_to(shadow)
            forbidden_diagnostics = auth_diagnostics / "forbidden.json"
            forbidden = subprocess.run(
                [str(launcher), "--auth-preflight", "--diagnostics-file", str(forbidden_diagnostics)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            self.assertEqual(forbidden.returncode, 70)
            self.assertFalse(forbidden_diagnostics.exists())
            self.assertEqual(count.read_text(encoding="utf-8"), "run\nrun\n")

    def test_exact_git_grammar_accepts_only_qualifying_review_forms(self):
        root = "/tmp/declared-candidate"
        commit = "a" * 40
        accepted = (
            ["git", "-C", root, "status", "--porcelain=v2", "--untracked-files=all"],
            ["git", "-C", root, "diff", "--no-ext-diff", "--no-textconv", "--check", "origin/main...HEAD"],
            ["git", "-C", root, "diff", "--no-ext-diff", "--no-textconv", f"{commit}..HEAD"],
            ["git", "-C", root, "log", "--oneline", "origin/main..HEAD"],
            ["git", "-C", root, "rev-parse", "HEAD"],
        )
        for command in accepted:
            with self.subTest(command=command):
                self.assertEqual(self.launcher.validate_command(command), command)

    def test_exact_git_grammar_rejects_no_index_and_every_path_operand_shape(self):
        root = "/tmp/declared-candidate"
        prefix = ["git", "-C", root, "diff", "--no-ext-diff", "--no-textconv"]
        rejected = (
            [*prefix, "--no-index", "/outside/a", "/outside/b"],
            [*prefix, "/outside/a", "/outside/b"],
            [*prefix, "../outside"],
            [*prefix, "HEAD", "--", "/outside"],
            [*prefix, "HEAD", "--", "inside", "/outside"],
            [*prefix, "HEAD", "--", "symlink-outside"],
            [*prefix, "HEAD", "--", ":(top,glob)../outside/**"],
            ["git", "diff", "--no-ext-diff", "--no-textconv", "HEAD"],
            ["git", "-C", root, "diff", "--", "HEAD"],
        )
        for command in rejected:
            with self.subTest(command=command), self.assertRaises(ValueError):
                self.launcher.validate_command(command)


class ClaudeReviewLauncherTests(unittest.TestCase):
    def test_project_codex_rule_tracks_every_launcher_operation_mode(self):
        rule = CODEX_RULE.read_text(encoding="utf-8")

        for mode in (
            "--qualify-claude-identity",
            "--auth-preflight",
            "--review-config",
            "--permission-hook",
            "--request-termination",
            "--decline-termination",
            "--terminate",
        ):
            with self.subTest(mode=mode):
                self.assertIn(f'"{mode}"', rule)

    def test_review_modes_cannot_be_combined_with_lifecycle_controls(self):
        for review_mode in (("--auth-preflight",), ("--review-config", "review-config.json")):
            for control_mode in (
                ("--permission-hook", "review-config.json"),
                ("--request-termination", "live-state.json"),
                ("--decline-termination", "live-state.json"),
                ("--terminate", "live-state.json"),
            ):
                with self.subTest(review_mode=review_mode, control_mode=control_mode):
                    completed = subprocess.run(
                        [str(LAUNCHER), *review_mode, *control_mode],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                    )

                    self.assertEqual(completed.returncode, 2)
                    self.assertIn("not allowed with argument", completed.stderr)

    def test_review_modes_reject_termination_only_modifiers(self):
        for modifier in (
            ("--termination-authority", "operator-approved"),
            ("--grace-seconds", "1"),
            ("--force-authorized",),
        ):
            with self.subTest(modifier=modifier):
                completed = subprocess.run(
                    [str(LAUNCHER), "--auth-preflight", *modifier],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )

                self.assertEqual(completed.returncode, 2)
                self.assertIn("require", completed.stderr)
                self.assertIn("--terminate", completed.stderr)

    def test_arbitrary_claude_executable_selector_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            diagnostics = Path(temporary_directory) / "diagnostics.json"
            completed = subprocess.run(
                [
                    str(LAUNCHER),
                    "--auth-preflight",
                    "--claude-bin",
                    "/bin/echo",
                    "--diagnostics-file",
                    str(diagnostics),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(completed.returncode, 70)
        self.assertFalse(diagnostics.exists())
        self.assertIn('"failure_classification": "reviewer_executable_not_authorized"', completed.stderr)

    def test_fixture_environment_alone_cannot_bypass_installed_identity(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            marker = root / "executed"
            fake_claude = root / "claude"
            fake_claude.write_text(
                "#!/bin/sh\ntouch \"$FIXTURE_MARKER\"\necho CLAUDE_AUTH_OK\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            completed = subprocess.run(
                [str(LAUNCHER), "--auth-preflight", "--claude-bin", str(fake_claude)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={
                    **os.environ,
                    "CLAUDE_REVIEW_TEST_FIXTURE": "1",
                    "FIXTURE_MARKER": str(marker),
                },
                check=False,
            )
            self.assertEqual(completed.returncode, 70)
            self.assertFalse(marker.exists())
            self.assertIn('"failure_classification": "reviewer_executable_not_authorized"', completed.stderr)

    def run_launcher(
        self,
        fake_body: str,
        *,
        auth_preflight: bool = False,
        environment: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            fake_claude = temporary / "claude"
            fake_claude.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                "import sys\n"
                "if '--version' in sys.argv:\n"
                "    print('fake-claude 1.0')\n"
                "    raise SystemExit(0)\n"
                "count_path = os.environ.get('CLAUDE_REVIEW_TEST_COUNT')\n"
                "if count_path:\n"
                "    with open(count_path, 'a', encoding='utf-8') as count_file:\n"
                "        count_file.write('review\\n')\n"
                "print(os.environ['USER'], os.environ['LOGNAME'], os.environ['HOME'], file=sys.stderr)\n"
                + textwrap.dedent(fake_body),
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            diagnostics = temporary / "diagnostics.json"
            command = [
                str(LAUNCHER),
                "--claude-bin",
                str(fake_claude),
                "--diagnostics-file",
                str(diagnostics),
            ]
            if auth_preflight:
                command.append("--auth-preflight-fixture")
            effective_environment = (environment or os.environ.copy()).copy()
            effective_environment["CLAUDE_REVIEW_TEST_FIXTURE"] = "1"
            effective_environment["CLAUDE_REVIEW_TEST_SCRATCH_PARENT"] = str(temporary)
            if not auth_preflight:
                command.append("--classification-fixture")
            command.extend(("--", "--model", "opus", "--effort", "high", "--tools", "Read"))
            completed = subprocess.run(
                command,
                check=False,
                input="review prompt that must not enter argv\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=effective_environment,
            )
            return completed, json.loads(diagnostics.read_text(encoding="utf-8"))

    def test_normalizes_missing_user_and_mismatched_logname_to_effective_user(self):
        effective = pwd.getpwuid(os.geteuid())
        environment = os.environ.copy()
        environment.update({"LOGNAME": "stale-login", "HOME": effective.pw_dir})
        environment.pop("USER", None)
        completed, diagnostic = self.run_launcher("print('ACCEPT')\n", environment=environment)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "ACCEPT\n")
        self.assertEqual(diagnostic["runtime"]["effective_user"], effective.pw_name)
        self.assertEqual(diagnostic["runtime"]["USER"], effective.pw_name)
        self.assertEqual(diagnostic["runtime"]["LOGNAME"], effective.pw_name)
        self.assertEqual(diagnostic["runtime"]["HOME"], effective.pw_dir)
        self.assertEqual(diagnostic["runtime"]["inherited_HOME"], effective.pw_dir)
        self.assertEqual(
            diagnostic["runtime"]["argv"][-6:],
            ["--model", "opus", "--effort", "high", "--tools", "Read"],
        )
        self.assertNotIn("review prompt that must not enter argv", json.dumps(diagnostic))

    def test_already_correct_user_and_logname_remain_bound_to_effective_user(self):
        effective = pwd.getpwuid(os.geteuid())
        environment = os.environ.copy()
        environment.update({"USER": effective.pw_name, "LOGNAME": effective.pw_name, "HOME": effective.pw_dir})
        completed, diagnostic = self.run_launcher("print('ACCEPT')\n", environment=environment)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(diagnostic["runtime"]["USER"], effective.pw_name)
        self.assertEqual(diagnostic["runtime"]["LOGNAME"], effective.pw_name)
        self.assertEqual(diagnostic["runtime"]["HOME"], effective.pw_dir)

    def test_oauth_expiry_is_an_infrastructure_failure_not_a_reject_verdict(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            count_path = temporary / "review-count"
            candidate_state = temporary / "candidate-state"
            auth_state = temporary / "claude-auth-state"
            candidate_state.write_text("frozen candidate bytes", encoding="utf-8")
            auth_state.write_text("operator-owned auth state", encoding="utf-8")
            environment = os.environ.copy()
            environment["CLAUDE_REVIEW_TEST_COUNT"] = str(count_path)
            completed, diagnostic = self.run_launcher(
                "print('Failed to authenticate. API Error: 401 OAuth access token has expired')\n"
                "raise SystemExit(1)\n",
                environment=environment,
            )

            self.assertEqual(completed.returncode, 78)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(diagnostic["failure_classification"], "AUTH_OAUTH_TOKEN_EXPIRED_401")
            self.assertEqual(
                diagnostic["disposition"],
                "REVIEWER INFRASTRUCTURE FAILURE — OPERATOR REAUTHENTICATION REQUIRED",
            )
            self.assertIn("reauthenticate Claude interactively", diagnostic["operator_action"])
            self.assertEqual(diagnostic["candidate_verdict"], "not_produced")
            self.assertEqual(diagnostic["candidate_review_state"], "unchanged_by_launcher")
            self.assertFalse(diagnostic["automated_retry_attempted"])
            self.assertFalse(diagnostic["substantive_review_output"])
            self.assertTrue(diagnostic["claude_output_received"])
            self.assertTrue(diagnostic["claude_output_withheld"])
            self.assertEqual(diagnostic["claude_exit_code"], 1)
            self.assertEqual(count_path.read_text(encoding="utf-8"), "review\n")
            self.assertEqual(candidate_state.read_text(encoding="utf-8"), "frozen candidate bytes")
            self.assertEqual(auth_state.read_text(encoding="utf-8"), "operator-owned auth state")

    def test_invalid_oauth_authentication_is_also_an_operator_reauthentication_failure(self):
        completed, diagnostic = self.run_launcher(
            "print('Failed to authenticate: 401 OAuth token invalid', file=sys.stderr)\n"
            "raise SystemExit(1)\n"
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(diagnostic["failure_classification"], "AUTH_UNKNOWN_FAIL_CLOSED")
        self.assertEqual(diagnostic["candidate_verdict"], "not_produced")

    def test_diagnostics_include_required_runtime_metadata_and_redact_credentials(self):
        completed, diagnostic = self.run_launcher(
            "print('authorization: Bearer secret-token-value cookie=session-secret sk-ant-secret-value', file=sys.stderr)\n"
            "raise SystemExit(1)\n"
        )

        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_execution_failure")
        for key in ("claude_executable", "claude_version", "argv", "effective_uid", "effective_user", "HOME", "USER", "LOGNAME", "cwd"):
            self.assertIn(key, diagnostic["runtime"])
        serialized = json.dumps(diagnostic)
        self.assertNotIn("secret-token-value", serialized)
        self.assertNotIn("session-secret", serialized)
        self.assertNotIn("sk-ant-secret-value", serialized)
        self.assertNotIn("secret-token-value", completed.stderr)
        self.assertNotIn("session-secret", completed.stderr)
        self.assertNotIn("sk-ant-secret-value", completed.stderr)
        self.assertIn("[REDACTED]", diagnostic["stderr"])

    def test_review_prose_about_oauth_is_not_mistaken_for_an_authentication_failure(self):
        completed, diagnostic = self.run_launcher(
            "print('The docs mention 401 OAuth access token has expired, but this is review prose.')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIsNone(diagnostic["failure_classification"])
        self.assertTrue(diagnostic["substantive_review_output"])

    def test_json_oauth_error_is_an_infrastructure_failure_even_with_exit_zero(self):
        completed, diagnostic = self.run_launcher(
            "print('{\"type\": \"result\", \"subtype\": \"error_during_execution\", \"is_error\": true, \"result\": \"API Error: 401 OAuth access token has expired\"}')\n"
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(diagnostic["failure_classification"], "AUTH_OAUTH_TOKEN_EXPIRED_401")

    def test_stream_json_oauth_error_is_an_infrastructure_failure_even_with_exit_zero(self):
        completed, diagnostic = self.run_launcher(
            "print('{\"type\": \"system\", \"subtype\": \"init\"}')\n"
            "print('{\"type\": \"result\", \"subtype\": \"error_during_execution\", \"is_error\": true, \"result\": \"API Error: 401 OAuth access token has expired\"}')\n"
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(diagnostic["failure_classification"], "AUTH_OAUTH_TOKEN_EXPIRED_401")

    def test_review_prose_on_stderr_is_not_mistaken_for_an_authentication_failure(self):
        completed, diagnostic = self.run_launcher(
            "print('Review note: 401 OAuth access token has expired is documented behavior.', file=sys.stderr)\n"
            "print('ACCEPT')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "ACCEPT\n")
        self.assertIsNone(diagnostic["failure_classification"])

    def test_authentication_error_on_stderr_does_not_discard_a_completed_review(self):
        completed, diagnostic = self.run_launcher(
            "print('API Error: 401 OAuth access token has expired', file=sys.stderr)\n"
            "print('ACCEPT')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "ACCEPT\n")
        self.assertIsNone(diagnostic["failure_classification"])

    def test_review_prose_beginning_with_an_api_error_quote_is_not_an_authentication_failure(self):
        completed, diagnostic = self.run_launcher(
            "print('API Error: 401 OAuth access token has expired is a quote from the docs.')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertTrue(diagnostic["substantive_review_output"])
        self.assertIsNone(diagnostic["failure_classification"])

    def test_review_prose_beginning_with_a_failed_to_authenticate_quote_is_not_an_authentication_failure(self):
        completed, diagnostic = self.run_launcher(
            "print('Failed to authenticate is the literal under review, not a runtime failure.')\n"
            "print('ACCEPT WITH CHANGES')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertTrue(diagnostic["substantive_review_output"])
        self.assertIsNone(diagnostic["failure_classification"])

    def test_auth_preflight_uses_fixed_prompt_and_omits_review_tools(self):
        completed, diagnostic = self.run_launcher(
            "prompt = sys.stdin.read()\n"
            "assert prompt == 'Reply exactly: CLAUDE_AUTH_OK\\n'\n"
            "assert sys.argv[sys.argv.index('--tools') + 1] == ''\n"
            "assert '--model' in sys.argv\n"
            "assert '--effort' in sys.argv\n"
            "assert not os.path.exists('.git')\n"
            "print('CLAUDE_AUTH_OK')\n",
            auth_preflight=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "CLAUDE_AUTH_OK\n")
        self.assertEqual(diagnostic["attempt_kind"], "auth_preflight")
        self.assertEqual(diagnostic["auth_preflight_status"], "AUTH_PREFLIGHT_OK")
        self.assertEqual(diagnostic["candidate_verdict"], "not_applicable")
        self.assertFalse(diagnostic["substantive_review_output"])
        self.assertIn("--tools", diagnostic["runtime"]["requested_argv"])
        self.assertEqual(diagnostic["runtime"]["argv"][-3:], ["--tools", "", "--no-session-persistence"])
        self.assertEqual(diagnostic["runtime"]["cwd_class"], "temporary")

    def test_auth_preflight_distinguishes_saved_login_refresh_rejection(self):
        completed, diagnostic = self.run_launcher(
            "print('Failed to authenticate: OAuth session expired and could not be refreshed')\n"
            "raise SystemExit(1)\n",
            auth_preflight=True,
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(diagnostic["failure_classification"], "AUTH_SAVED_LOGIN_REFRESH_REJECTED")
        self.assertIn("Reauthenticate Claude interactively", diagnostic["operator_action"])
        self.assertFalse(diagnostic["automated_retry_attempted"])
        self.assertEqual(diagnostic["candidate_verdict"], "not_applicable")

    def test_auth_preflight_classifies_documented_oauth_expired_401(self):
        completed, diagnostic = self.run_launcher(
            "print('API Error: 401 OAuth access token has expired')\n"
            "raise SystemExit(1)\n",
            auth_preflight=True,
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(diagnostic["failure_classification"], "AUTH_OAUTH_TOKEN_EXPIRED_401")

    def test_auth_preflight_unknown_auth_failure_fails_closed_without_provider_cause(self):
        completed, diagnostic = self.run_launcher(
            "print('Authentication could not continue')\n"
            "raise SystemExit(1)\n",
            auth_preflight=True,
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(diagnostic["failure_classification"], "AUTH_UNKNOWN_FAIL_CLOSED")
        self.assertEqual(diagnostic["candidate_verdict"], "not_applicable")

    def test_auth_preflight_non_auth_output_mismatch_is_not_labeled_as_authentication(self):
        completed, diagnostic = self.run_launcher("print('unexpected preflight output')\n", auth_preflight=True)

        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "PREFLIGHT_OUTPUT_MISMATCH")
        self.assertEqual(diagnostic["preflight_output"], "unexpected preflight output\n")

    def test_successful_review_quoting_terminal_auth_text_is_not_discarded(self):
        completed, diagnostic = self.run_launcher(
            "print('Failed to authenticate. API Error: 401 OAuth access token has expired')\n"
            "print('ACCEPT')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIsNone(diagnostic["failure_classification"])
        self.assertTrue(diagnostic["substantive_review_output"])

    def test_split_terminal_auth_text_fails_closed_without_an_expiry_cause(self):
        completed, diagnostic = self.run_launcher(
            "print('Failed to authenticate.')\n"
            "print('unrelated output')\n"
            "print('API Error: 401 OAuth access token has expired')\n"
            "raise SystemExit(1)\n"
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(diagnostic["failure_classification"], "AUTH_UNKNOWN_FAIL_CLOSED")

    def test_successful_review_survives_incidental_context_stderr(self):
        completed, diagnostic = self.run_launcher(
            "print('note: home directory scanned', file=sys.stderr)\n"
            "print('ACCEPT')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "ACCEPT\n")
        self.assertIsNone(diagnostic["failure_classification"])

    def test_auth_preflight_accepts_fixed_response_without_a_trailing_newline(self):
        completed, diagnostic = self.run_launcher(
            "sys.stdout.write('CLAUDE_AUTH_OK')\n", auth_preflight=True
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(diagnostic["auth_preflight_status"], "AUTH_PREFLIGHT_OK")

    def test_auth_preflight_accepts_exact_no_tools_notice_but_rejects_other_suffixes(self):
        accepted, accepted_diagnostic = self.run_launcher(
            "print('CLAUDE_AUTH_OK')\n"
            "print('Client.listTools() called but server does not advertise tools capability - returning empty list')\n",
            auth_preflight=True,
        )

        self.assertEqual(accepted.returncode, 0)
        self.assertEqual(accepted.stdout, "CLAUDE_AUTH_OK\n")
        self.assertEqual(
            accepted_diagnostic["preflight_notices"],
            ["Client.listTools() called but server does not advertise tools capability - returning empty list"],
        )

        rejected, rejected_diagnostic = self.run_launcher(
            "print('CLAUDE_AUTH_OK')\nprint('unexpected suffix')\n",
            auth_preflight=True,
        )

        self.assertEqual(rejected.returncode, 70)
        self.assertEqual(rejected_diagnostic["failure_classification"], "PREFLIGHT_OUTPUT_MISMATCH")

        repeated, repeated_diagnostic = self.run_launcher(
            "print('CLAUDE_AUTH_OK')\n"
            "print('Client.listTools() called but server does not advertise tools capability - returning empty list')\n"
            "print('Client.listTools() called but server does not advertise tools capability - returning empty list')\n",
            auth_preflight=True,
        )

        self.assertEqual(repeated.returncode, 70)
        self.assertEqual(repeated_diagnostic["failure_classification"], "PREFLIGHT_OUTPUT_MISMATCH")

    def test_auth_preflight_retains_equals_form_model_and_effort(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            fake_claude = temporary / "claude"
            fake_claude.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "if '--version' in sys.argv:\n"
                "    print('fake-claude 1.0')\n"
                "    raise SystemExit(0)\n"
                "assert '--model=opus' in sys.argv\n"
                "assert '--effort=high' in sys.argv\n"
                "print('CLAUDE_AUTH_OK')\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            completed = subprocess.run(
                [str(LAUNCHER), "--claude-bin", str(fake_claude), "--auth-preflight-fixture", "--", "--model=opus", "--effort=high"],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={
                    **os.environ,
                    "CLAUDE_REVIEW_TEST_FIXTURE": "1",
                    "CLAUDE_REVIEW_TEST_SCRATCH_PARENT": str(temporary),
                },
            )

        self.assertEqual(completed.returncode, 0)

    def test_argv_diagnostics_redact_credential_values(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)

        self.assertEqual(
            module.redacted_argv(
                [
                    "claude",
                    "--token",
                    "secret",
                    "--api-key=another-secret",
                    "--anthropic-api-key",
                    "another-secret",
                    "--session-token",
                    "session-secret",
                    "--settings",
                    '{"apiKey":"settings-secret"}',
                ]
            ),
            [
                "claude",
                "--token",
                "[REDACTED]",
                "--api-[REDACTED]",
                "--anthropic-api-key",
                "[REDACTED]",
                "--session-token",
                "[REDACTED]",
                "--settings",
                "[REDACTED]",
            ],
        )


class GovernedClaudeReviewLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.candidate = self.root / "candidate"
        self.package = self.root / "review-package"
        self.evidence = self.root / "evidence"
        self.candidate.mkdir()
        self.package.mkdir()
        self.evidence.mkdir()
        (self.package / "brief.md").write_text("review brief\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.candidate)], check=True)
        (self.candidate / ".gitignore").write_text("*.cache\n", encoding="utf-8")
        (self.candidate / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.candidate), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.candidate),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ],
            check=True,
        )
        self.count = self.root / "count"
        self.fake = self.root / "claude"
        self.fake.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, signal, subprocess, sys, time\n"
            "if '--version' in sys.argv:\n"
            "    version_count = pathlib.Path(os.environ['FAKE_VERSION_COUNT'])\n"
            "    count = int(version_count.read_text()) + 1 if version_count.exists() else 1\n"
            "    version_count.write_text(str(count))\n"
            "    print('fake-claude 2.1.241')\n"
            "    raise SystemExit(0)\n"
            "prompt = sys.stdin.read()\n"
            "count = pathlib.Path(os.environ['FAKE_COUNT'])\n"
            "attempt = int(count.read_text()) + 1 if count.exists() else 1\n"
            "count.write_text(str(attempt))\n"
            "scenario = os.environ.get('FAKE_SCENARIO', 'success')\n"
            "if scenario == 'ignore_term': signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "candidate = pathlib.Path(os.environ['FAKE_CANDIDATE'])\n"
            "package = pathlib.Path(os.environ['FAKE_PACKAGE'])\n"
            "tools = ['Bash','Glob','Grep'] if scenario == 'tool_mismatch' else ['Bash','Glob','Grep','Read']\n"
            "model = 'wrong-exact-model' if scenario == 'model_mismatch' else os.environ.get('FAKE_EFFECTIVE_MODEL', 'fake-opus')\n"
            "cwd = str(candidate) if scenario == 'cwd_mismatch' else os.getcwd()\n"
            "print(json.dumps({'type':'system','subtype':'init','session_id':f's{attempt}','model':model,'tools':tools,'mcp_servers':[],'permissionMode':'dontAsk','plugins':[],'skills':[],'slash_commands':[],'cwd':cwd} ), flush=True)\n"
            "canary_id = f'canary-{attempt}'\n"
            "canary_command = f'git -C {candidate} status --porcelain=v2 --untracked-files=all'\n"
            "canary_input = {'command': canary_command}\n"
            "if scenario == 'canary_bypass': canary_input['dangerouslyDisableSandbox'] = True\n"
            "print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use','id':canary_id,'name':'Bash','input':canary_input}]}}), flush=True)\n"
            "print(json.dumps({'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':canary_id,'content':'canary','is_error':scenario == 'dead_command_grant'}]}}), flush=True)\n"
            "if scenario == 'non_object_json': print('null', flush=True)\n"
            "if scenario == 'tool_mismatch': time.sleep(0.08)\n"
            "if scenario == 'cwd_mismatch': time.sleep(0.08)\n"
            "if scenario == 'provider_bootstrap': (pathlib.Path.cwd() / '.claude' / '.cc-writes').mkdir(parents=True)\n"
            "if scenario == 'mutate_tracked': (candidate / 'tracked.txt').write_text('changed\\n')\n"
            "if scenario == 'mutate_then_wait':\n"
            "    (candidate / 'tracked.txt').write_text('changed\\n')\n"
            "    time.sleep(10)\n"
            "if scenario == 'mutate_ignore_term':\n"
            "    signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "    (candidate / 'tracked.txt').write_text('changed\\n')\n"
            "    time.sleep(10)\n"
            "if scenario == 'new_ignored': (candidate / 'generated.cache').write_text('cache')\n"
            "if scenario == 'remove_untracked': (candidate / 'preexisting.txt').unlink()\n"
            "if scenario == 'index_mutation':\n"
            "    (candidate / 'tracked.txt').write_text('staged\\n')\n"
            "    subprocess.run(['git','-C',str(candidate),'add','tracked.txt'], check=True)\n"
            "if scenario == 'git_lock_then_wait':\n"
            "    (candidate / '.git' / 'index.lock').write_text('reviewer lock\\n')\n"
            "    time.sleep(10)\n"
            "if scenario == 'special_object_then_wait':\n"
            "    os.mkfifo(candidate / 'reviewer.fifo')\n"
            "    time.sleep(0.08)\n"
            "if scenario == 'transient_special_object_then_wait':\n"
            "    fifo = candidate / 'reviewer.fifo'\n"
            "    os.mkfifo(fifo)\n"
            "    time.sleep(0.25)\n"
            "    fifo.unlink()\n"
            "    time.sleep(0.05)\n"
            "if scenario == 'special_object_hang':\n"
            "    os.mkfifo(candidate / 'reviewer.fifo')\n"
            "    time.sleep(10)\n"
            "if scenario == 'escaped_output': (package / 'escaped-review.txt').write_text('escaped')\n"
            "if scenario == 'unsafe_scratch': (pathlib.Path(os.environ['TMPDIR']) / 'escape').symlink_to(candidate)\n"
            "if scenario == 'silent': time.sleep(0.08)\n"
            "if scenario == 'transient_with_lingering_child' and attempt == 1:\n"
            "    marker = os.environ['FAKE_LINGER_MARKER']\n"
            "    subprocess.Popen([sys.executable, '-c', f\"import pathlib,time; time.sleep(0.15); pathlib.Path({marker!r}).write_text('terminal')\"])\n"
            "if scenario == 'transient_with_lingering_child' and attempt == 2:\n"
            "    assert pathlib.Path(os.environ['FAKE_LINGER_MARKER']).read_text() == 'terminal'\n"
            "if scenario == 'linger_after_direct_exit':\n"
            "    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'])\n"
            "if scenario == 'ignore_term':\n"
            "    time.sleep(10)\n"
            "if scenario == 'hang_after_transient':\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':'server_error'}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
            "    time.sleep(10)\n"
            "if scenario in {'transient_once','transient_always','transient_with_lingering_child','transient_then_executable_drift'} and (scenario == 'transient_always' or attempt == 1):\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':'server_error'}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
            "    if scenario == 'transient_then_executable_drift': pathlib.Path(sys.argv[0]).write_text(pathlib.Path(sys.argv[0]).read_text() + '# drift\\n')\n"
            "    raise SystemExit(1)\n"
            "if scenario == 'auth':\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':'authentication_failed'}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
            "    raise SystemExit(1)\n"
            "if scenario == 'auth_precise':\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}','result':'API Error: 401 OAuth access token has expired'}), flush=True)\n"
            "    raise SystemExit(1)\n"
            "print(json.dumps({'type':'result','subtype':'success','is_error':False,'session_id':f's{attempt}','result':'ACCEPT'}), flush=True)\n",
            encoding="utf-8",
        )
        self.fake.chmod(0o755)

    def config_body(self, *, launch_root=None, additional=None, max_attempts=3):
        candidate_head = subprocess.run(
            ["git", "-C", str(self.candidate), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        return {
            "schema_version": 1,
            "review_id": "CAK-155-fixture",
            "contract_id": "sha256:fixture-contract",
            "launch_root": str(launch_root or self.root),
            "additional_directories": [str(path) for path in (additional or [])],
            "source_locations": [
                {"root": str(self.candidate), "representative": str(self.candidate / "tracked.txt")},
                {"root": str(self.package), "representative": str(self.package / "brief.md")},
            ],
            "guard_roots": [str(self.candidate), str(self.package)],
            "candidate_worktree": str(self.candidate),
            "candidate_head": candidate_head,
            "evidence_directory": str(self.evidence),
            "preflight_receipt": str(self.evidence / "preflight-receipt.json"),
            "final_output": str(self.evidence / "review-output.md"),
            "attempt_artifacts": [
                {
                    "stream": str(self.evidence / f"attempt-{number}-stream.jsonl"),
                    "terminal_receipt": str(self.evidence / f"attempt-{number}-terminal-receipt.json"),
                }
                for number in range(1, max_attempts + 1)
            ],
            "allowed_commands": [
                ["git", "-C", str(self.candidate), "status", "--porcelain=v2", "--untracked-files=all"]
            ],
            "max_attempts": max_attempts,
            "observation_interval_seconds": 0.005,
            "soft_liveness_threshold_seconds": 0.02,
            "graceful_termination_seconds": 0.05,
            "cancellation_policy": {
                "mode": "interactive",
                "emergency_stop_conditions": ["unauthorized_mutation"],
            },
        }

    def write_config(self, body=None):
        path = self.evidence / "review-config.json"
        path.write_text(json.dumps(body or self.config_body()), encoding="utf-8")
        return path

    def environment(self, scenario):
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_SCENARIO": scenario,
                "FAKE_COUNT": str(self.count),
                "FAKE_VERSION_COUNT": str(self.root / "version-count"),
                "FAKE_CANDIDATE": str(self.candidate),
                "FAKE_PACKAGE": str(self.package),
                "CLAUDE_REVIEW_TEST_FIXTURE": "1",
                "CLAUDE_REVIEW_TEST_SCRATCH_PARENT": str(self.root),
                "FAKE_LINGER_MARKER": str(self.root / "lingering-child-terminal"),
            }
        )
        return environment

    def run_governed(self, scenario="success", *, body=None, model="opus"):
        config = self.write_config(body)
        diagnostics = self.evidence / "overall.json"
        if diagnostics.exists() or diagnostics.is_symlink():
            diagnostics.unlink()
        preflight_receipt = Path((body or self.config_body())["preflight_receipt"])
        if preflight_receipt.exists() or preflight_receipt.is_symlink():
            preflight_receipt.unlink()
        final_output = Path((body or self.config_body())["final_output"])
        if final_output.exists() or final_output.is_symlink():
            final_output.unlink()
        for item in (body or self.config_body())["attempt_artifacts"]:
            for value in item.values():
                artifact = Path(value)
                if artifact.exists() or artifact.is_symlink():
                    artifact.unlink()
        completed = subprocess.run(
            [
                str(LAUNCHER),
                "--claude-bin",
                str(self.fake),
                "--diagnostics-file",
                str(diagnostics),
                "--review-config-fixture",
                str(config),
                "--",
                "--model",
                model,
                "--effort",
                "high",
            ],
            check=False,
            input="exact review prompt\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment(scenario),
        )
        if diagnostics.exists():
            diagnostic = json.loads(diagnostics.read_text(encoding="utf-8"))
        else:
            prefix = "claude-review diagnostics: "
            diagnostic_line = next(line for line in reversed(completed.stderr.splitlines()) if line.startswith(prefix))
            diagnostic = json.loads(diagnostic_line[len(prefix) :])
        return completed, diagnostic

    def receipts(self):
        return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(self.evidence.glob("*-terminal-receipt.json"))]

    def test_common_root_and_exact_additional_directory_cover_source_graph(self):
        common, diagnostic = self.run_governed()
        self.assertEqual(common.returncode, 0)
        self.assertEqual(common.stdout, "ACCEPT\n")
        self.assertEqual((self.evidence / "review-output.md").read_text(encoding="utf-8"), "ACCEPT")
        self.assertEqual(diagnostic["preflight"]["status"], "passed")
        preflight = json.loads((self.evidence / "preflight-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(preflight["kind"], "claude_governed_review_preflight_receipt")
        receipt = self.receipts()[0]
        requested = receipt["runtime"]["requested_argv"]
        add_directories = [requested[index + 1] for index, value in enumerate(requested) if value == "--add-dir"]
        self.assertEqual(add_directories, [str(self.root.resolve())])
        self.assertEqual(receipt["runtime"]["effective_init"]["cwd"], receipt["runtime"]["provider_runtime_cwd"])
        self.assertNotEqual(receipt["runtime"]["provider_runtime_cwd"], str(self.root.resolve()))
        self.assertIsInstance(receipt["process"]["process_start_identity"], str)

        self.count.unlink()
        for path in self.evidence.glob("CAK-155-fixture-*"):
            path.unlink()
        additional_body = self.config_body(launch_root=self.package, additional=[self.candidate])
        added, added_diagnostic = self.run_governed(body=additional_body)
        self.assertEqual(added.returncode, 0)
        self.assertEqual(added_diagnostic["preflight"]["additional_directories"], [str(self.candidate.resolve())])
        added_requested = self.receipts()[0]["runtime"]["requested_argv"]
        added_directories = [
            added_requested[index + 1]
            for index, value in enumerate(added_requested)
            if value == "--add-dir"
        ]
        self.assertEqual(added_directories, [str(self.package.resolve()), str(self.candidate.resolve())])

    def test_provider_bootstrap_writes_are_contained_in_attempt_scratch(self):
        completed, diagnostic = self.run_governed("provider_bootstrap")
        self.assertEqual(completed.returncode, 0)
        receipt = self.receipts()[0]
        self.assertTrue(receipt["attempt_scratch"]["cleanup"]["passed"])
        self.assertTrue(receipt["no_delta_postflight"]["passed"])
        self.assertFalse((self.candidate / ".claude").exists())
        self.assertFalse((self.package / ".claude").exists())
        self.assertFalse(Path(receipt["runtime"]["provider_runtime_cwd"]).exists())

    def test_dead_or_bypass_command_canary_fails_closed(self):
        for scenario, expected in (
            ("dead_command_grant", "provider_command_canary_failed"),
            ("canary_bypass", "provider_command_canary_requested_sandbox_bypass"),
        ):
            with self.subTest(scenario=scenario):
                completed, diagnostic = self.run_governed(scenario)
                self.assertEqual(completed.returncode, 70)
                self.assertEqual(diagnostic["failure_classification"], expected)
                self.assertFalse(self.receipts()[0]["stream_evidence"]["provider_command_canary"]["passed"])

    def test_non_object_json_is_counted_without_orphaning_attempt(self):
        completed, _ = self.run_governed("non_object_json")
        self.assertEqual(completed.returncode, 0)
        receipt = self.receipts()[0]
        self.assertGreaterEqual(receipt["stream_evidence"]["malformed_records"], 1)
        self.assertTrue(receipt["lifecycle"]["process_group_terminal"])

    def test_exact_model_selector_is_enforced(self):
        exact, _ = self.run_governed(model="fake-opus")
        self.assertEqual(exact.returncode, 0)
        mismatch, diagnostic = self.run_governed("model_mismatch", model="fake-opus")
        self.assertEqual(mismatch.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_model_mismatch")

    def test_safe_environment_disables_claude_instruction_and_auto_memory_loading(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_memory", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        scratch = self.root / "environment-scratch"
        scratch.mkdir(mode=0o700)
        environment = module.safe_command_environment(os.environ.copy(), scratch)
        self.assertEqual(environment["CLAUDE_CODE_DISABLE_AUTO_MEMORY"], "1")
        self.assertEqual(environment["CLAUDE_CODE_DISABLE_CLAUDE_MDS"], "1")

        config = module.load_governed_config(self.write_config())
        arguments, system_prompt = module.governed_claude_arguments(
            config,
            ["--model", "opus", "--effort", "high"],
        )
        settings = json.loads(arguments[arguments.index("--settings") + 1])
        self.assertNotIn("sandbox", settings)
        self.assertIn("Before substantive analysis", system_prompt)
        self.assertIn(shlex.join(self.config_body()["allowed_commands"][0]), system_prompt)

    def test_review_id_and_preflight_selector_values_fail_closed(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_inputs", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)

        body = self.config_body()
        body["review_id"] = "../../escaped-review"
        with self.assertRaisesRegex(ValueError, "path-safe"):
            module.load_governed_config(self.write_config(body))
        for arguments in (
            ["--model"],
            ["--model", ""],
            ["--model="],
            ["--model", "--effort", "high"],
        ):
            with self.subTest(arguments=arguments), self.assertRaisesRegex(ValueError, "requires"):
                module.preflight_arguments(arguments)

    def test_pipe_collector_distinguishes_eof_from_reader_failure(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_collector", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)

        class BrokenStream:
            def readline(self):
                raise OSError("fixture read failure")

        collector = module.PipeCollector(BrokenStream())
        collector.thread.join(timeout=1)
        self.assertTrue(collector.done.is_set())
        self.assertFalse(collector.eof.is_set())
        self.assertEqual(collector.error, "fixture read failure")

    def test_automated_stop_state_is_not_downgraded_by_stale_control_state(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_control_merge", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        live = self.root / "fixture-live-state.json"
        control = self.root / "fixture-control-state.json"
        live.write_text(json.dumps({"state": "emergency_stop_in_progress"}), encoding="utf-8")
        control.write_text(json.dumps({"state": "running", "termination_disposition": "declined_keep_waiting"}), encoding="utf-8")
        merged = module.merged_external_state(live, {"state": "emergency_stop_in_progress"})
        self.assertEqual(merged["state"], "emergency_stop_in_progress")
        self.assertEqual(merged["termination_disposition"], "declined_keep_waiting")

    def test_effective_runtime_cwd_mismatch_stops_the_live_attempt(self):
        completed, diagnostic = self.run_governed("cwd_mismatch")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_runtime_cwd_mismatch")
        self.assertEqual(self.receipts()[0]["lifecycle"]["capability_failure"], "effective_runtime_cwd_mismatch")

    def test_narrow_package_root_fails_before_substantive_review(self):
        body = self.config_body(launch_root=self.package)
        completed, diagnostic = self.run_governed(body=body)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "review_contract_failure")
        self.assertFalse(self.count.exists())

    def test_command_and_guard_scope_fail_before_substantive_review(self):
        command_body = self.config_body()
        command_body["allowed_commands"] = [["stat", "/etc/hosts"]]
        completed, diagnostic = self.run_governed(body=command_body)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "review_contract_failure")
        self.assertFalse(self.count.exists())

        output_body = self.config_body()
        output_body["allowed_commands"] = [
            [
                "git",
                "-C",
                str(self.candidate),
                "diff",
                "--no-ext-diff",
                "--no-textconv",
                f"--output={self.package / 'forbidden.diff'}",
            ]
        ]
        completed, diagnostic = self.run_governed(body=output_body)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "review_contract_failure")
        self.assertFalse((self.package / "forbidden.diff").exists())

        executable_body = self.config_body()
        executable_body["allowed_commands"] = [
            ["/tmp/git", "-C", str(self.candidate), "status", "--porcelain=v2"]
        ]
        completed, diagnostic = self.run_governed(body=executable_body)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "review_contract_failure")
        self.assertFalse(self.count.exists())

        guard_body = self.config_body()
        guard_body["guard_roots"] = [str(self.candidate)]
        completed, diagnostic = self.run_governed(body=guard_body)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "review_contract_failure")
        self.assertFalse(self.count.exists())

        head_body = self.config_body()
        head_body["candidate_head"] = "0" * 40
        completed, diagnostic = self.run_governed(body=head_body)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "access_or_command_preflight_failure")
        self.assertFalse(self.count.exists())

    def test_direct_review_preserves_deliberately_dirty_candidate(self):
        (self.candidate / "tracked.txt").write_text("intentional dirty bytes\n", encoding="utf-8")
        (self.candidate / "preexisting.txt").write_text("untracked\n", encoding="utf-8")
        (self.candidate / "preexisting.cache").write_text("ignored\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.candidate), "add", "tracked.txt"], check=True)
        before = subprocess.run(
            ["git", "-C", str(self.candidate), "status", "--porcelain=v2", "--ignored"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        completed, _ = self.run_governed()
        after = subprocess.run(
            ["git", "-C", str(self.candidate), "status", "--porcelain=v2", "--ignored"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(before, after)
        self.assertTrue(self.receipts()[0]["no_delta_postflight"]["passed"])

    def test_postflight_detects_tracked_ignored_index_untracked_and_escaped_mutation(self):
        scenarios = ("mutate_tracked", "new_ignored", "index_mutation", "escaped_output")
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                if scenario == "mutate_tracked":
                    pass
                completed, diagnostic = self.run_governed(scenario)
                self.assertEqual(completed.returncode, 70)
                self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")
                receipt_path = Path(diagnostic["attempts"][-1]["receipt"])
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                self.assertFalse(receipt["no_delta_postflight"]["passed"])

    def test_live_mutation_triggers_predeclared_emergency_stop(self):
        completed, diagnostic = self.run_governed("mutate_then_wait")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")
        lifecycle = self.receipts()[0]["lifecycle"]
        self.assertEqual(lifecycle["emergency_condition"], "unauthorized_mutation")
        self.assertEqual(lifecycle["graceful_signal"], "SIGTERM")
        self.assertEqual(lifecycle["graceful_signal_delivery"], "sent")

    def test_emergency_stop_state_is_persisted_and_remains_operator_addressable(self):
        config = self.write_config()
        diagnostics = self.evidence / "overall.json"
        process = subprocess.Popen(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment("mutate_ignore_term"),
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        assert process.stdin is not None
        process.stdin.write("prompt\n")
        process.stdin.close()
        deadline = time.monotonic() + 5
        live = None
        while time.monotonic() < deadline:
            matches = list(self.root.glob("claude-review-controller-*/*-live-state.json"))
            if matches and json.loads(matches[0].read_text()).get("state") == "emergency_stop_in_progress":
                live = matches[0]
                break
            time.sleep(0.01)
        self.assertIsNotNone(live)
        terminated = subprocess.run(
            [str(LAUNCHER), "--terminate", str(live), "--termination-authority", "fixture emergency force authority", "--grace-seconds", "0.02", "--force-authorized"],
            check=False,
        )
        self.assertEqual(terminated.returncode, 0)
        process.wait(timeout=5)
        assert process.stdout is not None and process.stderr is not None
        process.stdout.close()
        process.stderr.close()
        receipt = self.receipts()[0]
        self.assertEqual(receipt["lifecycle"]["emergency_condition"], "unauthorized_mutation")
        self.assertEqual(receipt["lifecycle"]["forced_signal"], "SIGKILL")

    def test_removal_of_preexisting_untracked_content_is_detected(self):
        (self.candidate / "preexisting.txt").write_text("untracked\n", encoding="utf-8")
        completed, diagnostic = self.run_governed("remove_untracked")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")

    def test_transient_retry_recovers_without_contract_or_controller_drift(self):
        completed, diagnostic = self.run_governed("transient_once")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(len(diagnostic["attempts"]), 2)
        receipts = self.receipts()
        self.assertEqual(len(receipts), 2)
        self.assertEqual({receipt["controller_id"] for receipt in receipts}, {diagnostic["controller_id"]})
        self.assertEqual(len({json.dumps(receipt["contract_identity"], sort_keys=True) for receipt in receipts}), 1)
        self.assertEqual(receipts[1]["execution_kind"], "fresh_execution_exact_input_repeat")
        scratch_paths = [receipt["attempt_scratch"]["path"] for receipt in receipts]
        self.assertEqual(len(set(scratch_paths)), 2)
        self.assertTrue(all(receipt["attempt_scratch"]["cleanup"]["passed"] for receipt in receipts))
        self.assertTrue(all(not Path(path).exists() for path in scratch_paths))

    def test_retry_identity_drift_preserves_prior_attempt_evidence_and_stops_before_second_spawn(self):
        completed, diagnostic = self.run_governed("transient_then_executable_drift")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(self.count.read_text(encoding="utf-8"), "1")
        self.assertEqual(diagnostic["failure_classification"], "reviewer_identity_changed_before_execution")
        self.assertEqual(diagnostic["candidate_verdict"], "not_produced")
        self.assertEqual(diagnostic["attempt_number"], 2)
        self.assertTrue(diagnostic["substantive_review_started"])
        self.assertTrue(diagnostic["automated_retry_attempted"])
        self.assertEqual((self.root / "version-count").read_text(encoding="utf-8"), "2")
        self.assertEqual(len(diagnostic["attempts"]), 1)
        prior_attempt = diagnostic["attempts"][0]
        self.assertTrue(Path(prior_attempt["receipt"]).exists())
        receipt = json.loads(Path(prior_attempt["receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["attempt_number"], 1)
        self.assertTrue(Path(receipt["raw_output"]["path"]).exists())
        self.assertEqual(len(self.receipts()), 1)

    def test_lingering_process_group_blocks_retry_until_terminal(self):
        completed, diagnostic = self.run_governed("transient_with_lingering_child")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(len(diagnostic["attempts"]), 2)
        receipts = self.receipts()
        self.assertTrue(all(receipt["lifecycle"]["process_group_terminal"] for receipt in receipts))
        self.assertTrue(
            all(
                receipt["stream_evidence"]["collectors_reached_eof_before_stream_freeze"]
                for receipt in receipts
            )
        )
        self.assertEqual((self.root / "lingering-child-terminal").read_text(), "terminal")

    def test_retry_exhaustion_stops_at_three_and_auth_stops_at_one(self):
        exhausted, exhausted_diagnostic = self.run_governed("transient_always")
        self.assertEqual(exhausted.returncode, 70)
        self.assertEqual(len(exhausted_diagnostic["attempts"]), 3)

        auth_root = self.root / "auth-evidence"
        auth_root.mkdir()
        body = self.config_body()
        body["review_id"] = "CAK-155-auth"
        body["evidence_directory"] = str(auth_root)
        body["preflight_receipt"] = str(auth_root / "preflight-receipt.json")
        body["final_output"] = str(auth_root / "review-output.md")
        body["attempt_artifacts"] = [
            {
                "stream": str(auth_root / f"attempt-{number}-stream.jsonl"),
                "terminal_receipt": str(auth_root / f"attempt-{number}-terminal-receipt.json"),
            }
            for number in range(1, body["max_attempts"] + 1)
        ]
        config = auth_root / "review-config.json"
        config.write_text(json.dumps(body), encoding="utf-8")
        diagnostics = auth_root / "overall.json"
        completed = subprocess.run(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            input="prompt\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("auth"),
            check=False,
        )
        self.assertEqual(completed.returncode, 78)
        self.assertEqual(len(json.loads(diagnostics.read_text())["attempts"]), 1)

    def test_precise_terminal_auth_record_stops_without_retry(self):
        completed, diagnostic = self.run_governed("auth_precise")
        self.assertEqual(completed.returncode, 78)
        self.assertEqual(diagnostic["failure_classification"], "AUTH_OAUTH_TOKEN_EXPIRED_401")
        self.assertEqual(len(diagnostic["attempts"]), 1)

    def test_attempt_scratch_cleanup_failure_preserves_residue_and_stops(self):
        completed, diagnostic = self.run_governed("unsafe_scratch")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "attempt_scratch_cleanup_failure")
        receipt = self.receipts()[0]
        self.assertFalse(receipt["attempt_scratch"]["cleanup"]["passed"])
        self.assertTrue(Path(receipt["attempt_scratch"]["cleanup"]["residue"]).exists())

    def test_governed_diagnostics_are_no_overwrite(self):
        config = self.write_config()
        diagnostics = self.evidence / "overall.json"
        diagnostics.write_text("operator-owned\n", encoding="utf-8")
        completed = subprocess.run(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            input="prompt\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("success"),
            check=False,
        )
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostics.read_text(encoding="utf-8"), "operator-owned\n")
        self.assertFalse(self.count.exists())

        diagnostics.unlink()
        preflight_receipt = self.evidence / "preflight-receipt.json"
        preflight_receipt.write_text("operator-owned-preflight\n", encoding="utf-8")
        completed = subprocess.run(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            input="prompt\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("success"),
            check=False,
        )
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(preflight_receipt.read_text(encoding="utf-8"), "operator-owned-preflight\n")
        self.assertEqual(
            json.loads(diagnostics.read_text(encoding="utf-8"))["failure_classification"],
            "access_or_command_preflight_failure",
        )
        self.assertFalse(self.count.exists())

    def test_governed_diagnostics_reject_outside_path_without_fallback_write(self):
        config = self.write_config()
        outside = self.root / "outside-review-diagnostics.json"
        completed = subprocess.run(
            [
                str(LAUNCHER),
                "--claude-bin",
                str(self.fake),
                "--diagnostics-file",
                str(outside),
                "--review-config-fixture",
                str(config),
                "--",
                "--model",
                "opus",
                "--effort",
                "high",
            ],
            input="prompt\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("success"),
            check=False,
        )
        self.assertEqual(completed.returncode, 70)
        self.assertFalse(outside.exists())
        self.assertFalse(self.count.exists())
        self.assertIn('"failure_classification": "review_contract_failure"', completed.stderr)

    def test_permission_hook_fails_closed_if_config_identity_changes(self):
        import importlib.machinery
        import importlib.util

        config = self.write_config()
        loader = importlib.machinery.SourceFileLoader("claude_review_hook", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        digest = module.sha256_bytes(config.read_bytes())
        hook_input = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": shlex.join(self.config_body()["allowed_commands"][0])},
            }
        )
        command = [
            str(LAUNCHER),
            "--permission-hook",
            str(config),
            "--permission-hook-digest",
            digest,
        ]
        allowed = subprocess.run(
            command,
            input=hook_input,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("success"),
            check=False,
        )
        self.assertEqual(json.loads(allowed.stdout)["hookSpecificOutput"]["permissionDecision"], "allow")

        bypass_input = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": shlex.join(self.config_body()["allowed_commands"][0]),
                    "dangerouslyDisableSandbox": True,
                },
            }
        )
        bypass_denied = subprocess.run(
            command,
            input=bypass_input,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("success"),
            check=False,
        )
        self.assertEqual(
            json.loads(bypass_denied.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

        changed = self.config_body(max_attempts=2)
        config.write_text(json.dumps(changed), encoding="utf-8")
        denied = subprocess.run(
            command,
            input=hook_input,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment("success"),
            check=False,
        )
        self.assertEqual(json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_soft_liveness_threshold_never_terminates_or_replaces_attempt(self):
        completed, _ = self.run_governed("silent")
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(self.receipts()[0]["lifecycle"]["soft_liveness_threshold_crossed"])
        self.assertEqual(self.count.read_text(), "1")

    def test_effective_tool_mismatch_stops_the_live_attempt(self):
        completed, diagnostic = self.run_governed("tool_mismatch")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_tool_set_mismatch")
        self.assertEqual(self.receipts()[0]["lifecycle"]["capability_failure"], "effective_tool_set_mismatch")
        self.assertEqual(self.count.read_text(), "1")

    def test_request_and_decline_termination_keep_same_process_live(self):
        config = self.write_config()
        diagnostics = self.evidence / "overall.json"
        process = subprocess.Popen(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment("hang_after_transient"),
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        assert process.stdin is not None
        process.stdin.write("prompt\n")
        process.stdin.close()
        deadline = time.monotonic() + 5
        live = None
        while time.monotonic() < deadline:
            matches = list(self.root.glob("claude-review-controller-*/*-live-state.json"))
            if matches:
                live = matches[0]
                break
            time.sleep(0.01)
        self.assertIsNotNone(live)
        subprocess.run([str(LAUNCHER), "--request-termination", str(live)], check=True)
        self.assertIsNone(process.poll())
        subprocess.run([str(LAUNCHER), "--decline-termination", str(live)], check=True)
        self.assertIsNone(process.poll())
        subprocess.run(
            [str(LAUNCHER), "--terminate", str(live), "--termination-authority", "Keith confirmed fixture termination", "--grace-seconds", "0.2"],
            check=False,
        )
        process.wait(timeout=5)
        assert process.stdout is not None and process.stderr is not None
        process.stdout.close()
        process.stderr.close()
        self.assertEqual(self.count.read_text(), "1")

    def test_force_escalation_requires_separate_authority(self):
        config = self.write_config()
        diagnostics = self.evidence / "overall.json"
        process = subprocess.Popen(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment("ignore_term"),
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        assert process.stdin is not None
        process.stdin.write("prompt\n")
        process.stdin.close()
        deadline = time.monotonic() + 5
        live = None
        while time.monotonic() < deadline:
            matches = list(self.root.glob("claude-review-controller-*/*-live-state.json"))
            if matches and json.loads(matches[0].read_text()).get("partial_output_exists"):
                live = matches[0]
                break
            time.sleep(0.01)
        self.assertIsNotNone(live)
        graceful = subprocess.run(
            [str(LAUNCHER), "--terminate", str(live), "--termination-authority", "fixture graceful authority", "--grace-seconds", "0.02"],
            check=False,
        )
        self.assertEqual(graceful.returncode, 75)
        self.assertIsNone(process.poll())
        forced = subprocess.run(
            [str(LAUNCHER), "--terminate", str(live), "--termination-authority", "fixture force authority", "--grace-seconds", "0.02", "--force-authorized"],
            check=False,
        )
        self.assertEqual(forced.returncode, 0)
        process.wait(timeout=5)
        assert process.stdout is not None and process.stderr is not None
        process.stdout.close()
        process.stderr.close()
        receipt = self.receipts()[0]
        self.assertEqual(receipt["lifecycle"]["forced_signal"], "SIGKILL")

    def test_operator_can_terminate_group_after_direct_process_exit(self):
        config = self.write_config()
        diagnostics = self.evidence / "overall.json"
        process = subprocess.Popen(
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config-fixture", str(config), "--", "--model", "opus", "--effort", "high"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment("linger_after_direct_exit"),
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        assert process.stdin is not None
        process.stdin.write("prompt\n")
        process.stdin.close()
        deadline = time.monotonic() + 5
        live = None
        while time.monotonic() < deadline:
            matches = list(self.root.glob("claude-review-controller-*/*-live-state.json"))
            if matches and json.loads(matches[0].read_text()).get("state") == "awaiting_process_group_terminal":
                live = matches[0]
                break
            time.sleep(0.01)
        self.assertIsNotNone(live)
        subprocess.run([str(LAUNCHER), "--request-termination", str(live)], check=True)
        subprocess.run([str(LAUNCHER), "--decline-termination", str(live)], check=True)
        terminated = subprocess.run(
            [str(LAUNCHER), "--terminate", str(live), "--termination-authority", "fixture post-exit group authority", "--grace-seconds", "0.2"],
            check=False,
        )
        self.assertEqual(terminated.returncode, 0)
        process.wait(timeout=5)
        assert process.stdout is not None and process.stderr is not None
        process.stdout.close()
        process.stderr.close()
        self.assertEqual(self.receipts()[0]["failure_classification"], "operator_authorized_termination")

    def test_observational_import_cache_is_detected_and_scratch_redirect_contains_it(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_governed", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        module_path = self.candidate / "probe_module.py"
        module_path.write_text("VALUE = 1\n", encoding="utf-8")
        environment = os.environ.copy()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        subprocess.run([sys.executable, "-c", "import probe_module"], cwd=self.candidate, env=environment, check=True)
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertTrue(module.snapshot_delta(baseline, changed))

        subprocess.run(["git", "-C", str(self.candidate), "clean", "-fd", "--", "__pycache__"], check=True)
        scratch = self.root / "attempt-scratch"
        scratch.mkdir(mode=0o700)
        contained_baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        environment["PYTHONPYCACHEPREFIX"] = str(scratch)
        subprocess.run([sys.executable, "-c", "import probe_module"], cwd=self.candidate, env=environment, check=True)
        contained_after = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertEqual(module.snapshot_delta(contained_baseline, contained_after), [])
        self.assertTrue(any(scratch.rglob("*.pyc")))

    def test_git_administration_mutation_is_detected(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_git_admin", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        environment = os.environ.copy()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        subprocess.run(["git", "-C", str(self.candidate), "config", "fixture.probe", "changed"], check=True)
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn("git-admin", module.snapshot_delta(baseline, changed))

    def test_git_admin_lock_creation_removal_replacement_and_unchanged_baseline(self):
        module = load_script("claude_review_git_locks", LAUNCHER)
        environment = os.environ.copy()
        git_directory = self.candidate / ".git"
        lock_paths = (
            git_directory / "index.lock",
            git_directory / "config.lock",
            git_directory / "packed-refs.lock",
            git_directory / "refs" / "fixture.lock",
        )
        for lock in lock_paths:
            with self.subTest(created=lock.name):
                baseline = module.source_snapshot([self.candidate], self.candidate, environment)
                lock.parent.mkdir(parents=True, exist_ok=True)
                lock.write_text("created\n", encoding="utf-8")
                changed = module.source_snapshot([self.candidate], self.candidate, environment)
                self.assertIn("git-admin", module.snapshot_delta(baseline, changed))
                lock.unlink()

        preexisting = git_directory / "preexisting.lock"
        preexisting.write_text("original\n", encoding="utf-8")
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        unchanged = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertEqual(module.snapshot_delta(baseline, unchanged), [])
        preexisting.unlink()
        removed = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn("git-admin", module.snapshot_delta(baseline, removed))
        preexisting.write_text("replacement\n", encoding="utf-8")
        replaced = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn("git-admin", module.snapshot_delta(baseline, replaced))

    def test_linked_worktree_common_git_admin_locks_are_detected(self):
        module = load_script("claude_review_linked_worktree_locks", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "linked-candidate"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-linked", str(linked)],
            check=True,
        )
        common_result = subprocess.run(
            ["git", "-C", str(linked), "rev-parse", "--git-common-dir"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        common_directory = Path(common_result)
        if not common_directory.is_absolute():
            common_directory = linked / common_directory
        common_directory = common_directory.resolve()
        for lock in (
            common_directory / "config.lock",
            common_directory / "packed-refs.lock",
            common_directory / "refs" / "heads" / "fixture.lock",
        ):
            with self.subTest(lock=lock.name):
                baseline = module.source_snapshot([linked], linked, environment)
                lock.parent.mkdir(parents=True, exist_ok=True)
                lock.write_text("created\n", encoding="utf-8")
                changed = module.source_snapshot([linked], linked, environment)
                self.assertIn("git-admin", module.snapshot_delta(baseline, changed))
                lock.unlink()

    def test_additional_guarded_repository_admin_delta_is_detected(self):
        module = load_script("claude_review_additional_repository", LAUNCHER)
        environment = os.environ.copy()
        additional = self.root / "additional-repository"
        subprocess.run(["git", "init", "-q", str(additional)], check=True)
        baseline = module.source_snapshot([self.candidate, additional], self.candidate, environment)
        lock = additional / ".git" / "config.lock"
        lock.write_text("created\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate, additional], self.candidate, environment)
        self.assertIn(f"git-admin:{additional.resolve()}", module.snapshot_delta(baseline, changed))

    def test_snapshot_records_a_lock_that_vanishes_during_identity_capture(self):
        module = load_script("claude_review_vanishing_lock", LAUNCHER)
        root = self.root / "vanishing-lock-root"
        root.mkdir()
        lock = root / "index.lock"
        lock.write_text("transient\n", encoding="utf-8")
        original_file_identity = module.file_identity

        def vanishing_file_identity(path):
            if path == lock:
                lock.unlink()
                raise FileNotFoundError(path)
            return original_file_identity(path)

        module.file_identity = vanishing_file_identity
        snapshot = module.snapshot_root(root)
        self.assertEqual(snapshot["index.lock"], {"kind": "vanished_during_snapshot"})

    def test_snapshot_records_a_root_that_vanishes_during_identity_capture(self):
        module = load_script("claude_review_vanishing_root", LAUNCHER)
        root = self.root / "vanishing-root"
        root.mkdir()
        original_file_identity = module.file_identity

        def vanishing_file_identity(path):
            if path == root:
                root.rmdir()
                raise FileNotFoundError(path)
            return original_file_identity(path)

        module.file_identity = vanishing_file_identity
        self.assertEqual(module.snapshot_root(root), {".": {"kind": "vanished_during_snapshot"}})

    def test_git_index_records_vanishing_during_identity_capture(self):
        module = load_script("claude_review_vanishing_index", LAUNCHER)
        environment = os.environ.copy()
        index = self.candidate / ".git" / "index"
        original_bytes = index.read_bytes()
        original_mode = index.stat().st_mode
        original_file_identity = module.file_identity

        def vanishing_file_identity(path):
            if path == index:
                index.unlink()
                raise FileNotFoundError(path)
            return original_file_identity(path)

        module.file_identity = vanishing_file_identity
        try:
            identity = module.git_index_identity(self.candidate, environment)
            self.assertEqual(identity["identity"], {"kind": "vanished_during_snapshot"})
        finally:
            index.write_bytes(original_bytes)
            index.chmod(original_mode)

    def test_live_snapshot_failure_awaits_terminal_and_writes_receipt(self):
        completed, diagnostic = self.run_governed("special_object_then_wait")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "source_observation_failure")
        receipt = self.receipts()[0]
        self.assertEqual(receipt["failure_classification"], "source_observation_failure")
        self.assertEqual(receipt["process"]["state"], "terminal")
        self.assertTrue(receipt["lifecycle"]["process_group_terminal"])
        self.assertIn("unsupported special object", receipt["lifecycle"]["source_observation_failure"])
        self.assertFalse(receipt["no_delta_postflight"]["passed"])
        self.assertEqual(receipt["no_delta_postflight"]["changed_paths"], ["source-snapshot-unavailable"])
        self.assertIsNotNone(receipt["no_delta_postflight"]["postflight_capture_failure"])

    def test_live_only_snapshot_failure_cannot_pass_no_delta(self):
        completed, diagnostic = self.run_governed("transient_special_object_then_wait")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "source_observation_failure")
        receipt = self.receipts()[0]
        self.assertFalse(receipt["no_delta_postflight"]["passed"])
        self.assertIsNotNone(receipt["no_delta_postflight"]["live_observation_failure"])
        self.assertIsNone(receipt["no_delta_postflight"]["postflight_capture_failure"])
        self.assertEqual(receipt["no_delta_postflight"]["changed_paths"], [])

    def test_source_observation_failure_state_remains_operator_addressable(self):
        module = load_script("claude_review_observation_control", LAUNCHER)
        live = self.root / "observation-live-state.json"
        module.replace_live_state(
            live,
            {
                "state": "source_observation_failure_waiting_for_terminal",
                "source_observation_failure": "fixture observation failure",
            },
        )
        self.assertIn("source_observation_failure_waiting_for_terminal", module.LIVE_ATTEMPT_STATES)
        self.assertEqual(module.request_or_decline_termination(live, decline=False), 0)
        self.assertEqual(json.loads(live.read_text())["state"], "awaiting_operator_disposition")
        self.assertEqual(module.request_or_decline_termination(live, decline=True), 0)
        resumed = json.loads(live.read_text())
        self.assertEqual(resumed["state"], "source_observation_failure_waiting_for_terminal")
        self.assertEqual(resumed["termination_disposition"], "declined_keep_waiting")

    def test_interrupted_attempt_performs_lock_sensitive_terminal_postflight(self):
        completed, diagnostic = self.run_governed("git_lock_then_wait")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")
        receipt = self.receipts()[0]
        self.assertFalse(receipt["no_delta_postflight"]["passed"])
        self.assertIn("git-admin", receipt["no_delta_postflight"]["changed_paths"])

    def test_attempt_scratch_cleanup_fails_closed_on_symlink_residue(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_scratch", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        environment = self.environment("success")
        scratch = module.AttemptScratch.allocate(environment, "unsafe-cleanup-")
        unsafe = scratch.path / "escape"
        unsafe.symlink_to(self.candidate)
        with self.assertRaisesRegex(RuntimeError, "unsafe residue"):
            scratch.cleanup()
        self.assertTrue(scratch.path.exists())
        unsafe.unlink()
        scratch.cleanup()
        self.assertFalse(scratch.path.exists())

    def test_host_platform_attempt_scratch_projection_is_qualified(self):
        import importlib.machinery
        import importlib.util

        if sys.platform != "darwin" and not sys.platform.startswith("linux"):
            self.skipTest("host has no qualified attempt-scratch projection")
        loader = importlib.machinery.SourceFileLoader("claude_review_platform_scratch", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        environment = os.environ.copy()
        environment.pop("CLAUDE_REVIEW_TEST_FIXTURE", None)
        environment.pop("CLAUDE_REVIEW_TEST_SCRATCH_PARENT", None)
        scratch = module.AttemptScratch.allocate(environment, "platform-projection-")
        expected = "darwin_getconf_user_temp_dir" if sys.platform == "darwin" else "linux_fhs_tmp"
        self.assertEqual(scratch.projection, expected)
        self.assertEqual(scratch.path.stat().st_mode & 0o777, 0o700)
        scratch.cleanup()
        self.assertFalse(scratch.path.exists())

    def test_linux_attempt_scratch_parent_projection_is_host_independent(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review_linux_shape", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[loader.name] = module
        loader.exec_module(module)
        validate = module.qualified_attempt_scratch_parent_shape
        accepted = {
            "projection": "linux_fhs_tmp",
            "parent_uid": 0,
            "parent_mode": 0o1777,
            "parent_is_directory": True,
            "parent_is_symlink": False,
            "effective_uid": 501,
        }
        self.assertTrue(validate(**accepted))
        for changed in (
            {"parent_uid": 501},
            {"parent_mode": 0o777},
            {"parent_is_directory": False},
            {"parent_is_symlink": True},
        ):
            with self.subTest(changed=changed):
                self.assertFalse(validate(**{**accepted, **changed}))

        private = {
            **accepted,
            "projection": "darwin_getconf_user_temp_dir",
            "parent_uid": 501,
            "parent_mode": 0o700,
        }
        self.assertTrue(validate(**private))
        self.assertFalse(validate(**{**private, "parent_uid": 502}))
        self.assertFalse(validate(**{**private, "parent_mode": 0o750}))


if __name__ == "__main__":
    unittest.main()
