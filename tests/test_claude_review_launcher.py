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
        installed.mkdir(mode=0o755)
        launcher = installed / "claude-review-fixture"
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
        entry_contract = {
            "entry_contract_schema_version": 2,
            "installation_schema_version": 3,
            "qualification_schema_version": 3,
            "launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
            "rule_template_sha256": "fixture-rule-template",
            "claude_selector": str(selector),
            "active_rule_path": str(active_rule),
            "forbidden_roots": [str(candidate)],
            "auth_diagnostics_directory": str(auth_diagnostics),
            "installation_directory": str(installed),
        }
        entry_contract_id = "sha256:" + self.launcher.sha256_bytes(
            self.launcher.canonical_json_bytes(entry_contract)
        )
        receipt_path = installed / f".{launcher.name}.json"
        manifest = {
            "schema_version": 3,
            "entry_contract_id": entry_contract_id,
            "entry_contract": entry_contract,
            "installed_launcher_path": str(launcher),
            "installed_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
            "active_rule_path": str(active_rule),
            "active_rule_sha256": self.launcher.sha256_bytes(active_rule.read_bytes()),
            "claude_selector": str(selector),
            "forbidden_roots": [str(candidate)],
            "auth_diagnostics_directory": str(auth_diagnostics),
            "qualification_schema_version": 3,
            "installation_directory": str(installed),
        }
        receipt = {
            "kind": "claude_reviewer_qualification_receipt",
            "schema_version": 3,
            "entry_contract_id": entry_contract_id,
            "claude_selector": str(selector),
            "file_identity": qualified_identity["file_identity"],
            "version": qualified_identity["version"],
            "predecessor_receipt_sha256": None,
            "producing_launcher_path": str(launcher),
            "producing_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
            "authority_semantics": "capability qualification only; grants zero task or review authority",
        }
        manifest.update(receipt)
        receipt_bytes = self.launcher.canonical_json_bytes(manifest)
        receipt_sha256 = self.launcher.sha256_bytes(receipt_bytes)
        receipt_path.write_bytes(receipt_bytes)
        receipt_path.chmod(0o400)
        current = {
            "kind": "claude_reviewer_current_selection",
            "schema_version": 3,
            "entry_contract_id": entry_contract_id,
            "claude_selector": str(selector),
            "receipt_path": str(receipt_path),
            "receipt_sha256": receipt_sha256,
        }
        manifest_path = receipt_path
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
            "installation_directory": installed,
            # Compatibility aliases keep mutation-focused tests concise while
            # the production schema stores one flat current receipt.
            "qualification": installed,
            "receipts": installed,
            "current_path": receipt_path,
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
            active_rule=root / "active.rules",
            activation_receipt=activation_receipt,
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
        with mock.patch.object(
            self.installer, "parse_arguments", return_value=arguments
        ), mock.patch.object(
            self.installer, "production_install_root", return_value=root / "install-root"
        ), mock.patch.object(self.installer, "git", side_effect=fake_git), contextlib.redirect_stdout(
            output
        ):
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

    def test_installer_cli_rejects_alternate_install_root_while_fixture_seam_isolated(self):
        arguments = [
            "--claude-bin",
            "/operator/bin/claude",
            "--activation-receipt",
            "/private/receipt.json",
            "--install-root",
            "/alternate/bin",
        ]
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.installer.parse_arguments(arguments)

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            installed, _ = self.run_installer(root, selector, "activation.json", "1" * 40)
            self.assertEqual(installed["installation_directory"], str(root / "install-root"))

    def test_installer_production_root_uses_effective_account_home_not_environment(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            account_home = Path(temporary_directory).resolve() / "account-home"
            account_home.mkdir()
            account = mock.Mock(pw_dir=str(account_home))
            with mock.patch.object(
                self.installer.pwd, "getpwuid", return_value=account
            ), mock.patch.dict(os.environ, {"HOME": "/attacker-selected-home"}):
                self.assertEqual(
                    self.installer.production_install_root(),
                    account_home / ".local" / "bin",
                )

    def test_rule_template_binds_only_one_exact_absolute_launcher(self):
        template = CODEX_RULE_TEMPLATE.read_text(encoding="utf-8")
        rendered = template.replace("__CLAUDE_REVIEW_LAUNCHER__", "/operator/bin/claude-review")
        self.assertEqual(rendered.count('decision="allow"'), 2)
        self.assertIn('["/operator/bin/claude-review", "--auth-preflight"]', rendered)
        self.assertIn('["/operator/bin/claude-review", "--review-config"]', rendered)
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
            updated_record = json.loads(fixture["manifest_path"].read_text(encoding="utf-8"))
            self.assertEqual(updated_record["entry_contract"], fixture["manifest"]["entry_contract"])
            self.assertEqual(updated_record["file_identity"], observed)

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
            self.assertEqual(receipt["qualification_event"], "identity_transition")

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

    def test_runtime_qualification_replaces_only_the_flat_receipt(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
            installed_module = load_script("claude_review_receipt_durability", fixture["launcher"])
            fixture["selector"].unlink()
            fixture["selector"].symlink_to(fixture["versions"][1])
            observed = installed_module.executable_file_identity(
                fixture["selector"], os.geteuid(), [fixture["candidate"]]
            )
            events = []
            original_replace = installed_module.atomic_replace_qualification_receipt

            def record_replace(*arguments):
                events.append(("replace", arguments[0]))
                return original_replace(*arguments)

            with mock.patch.object(
                installed_module, "atomic_replace_qualification_receipt", record_replace
            ), mock.patch.dict(os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}):
                installed_module.qualify_claude_identity(
                    os.geteuid(),
                    expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                    expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                )

            self.assertEqual(events, [("replace", fixture["receipt_path"])])

    def test_runtime_receipt_replace_failure_preserves_current_receipt(self):
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
                "atomic_replace_qualification_receipt",
                side_effect=OSError("fixture receipt replacement failure"),
            ), mock.patch.dict(os.environ, {"FIXTURE_PROVIDER_RUNS": str(fixture["marker"])}), self.assertRaisesRegex(
                OSError, "receipt replacement failure"
            ):
                installed_module.qualify_claude_identity(
                    os.geteuid(),
                    expected_current_receipt_sha256=fixture["current"]["receipt_sha256"],
                    expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                )

            self.assertEqual(fixture["current_path"].read_bytes(), before_current)

    def test_atomic_qualification_receipt_cleanup_and_ambiguous_residue(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            current = root / ".claude-review.qualification.json"
            current.write_bytes(b"prior\n")
            current.chmod(0o400)
            with self.assertRaisesRegex(ValueError, "compare-and-swap"):
                self.launcher.atomic_replace_qualification_receipt(
                    current, {"next": True}, b"stale\n", os.geteuid()
                )
            self.assertEqual(current.read_bytes(), b"prior\n")
            self.assertEqual(list(root.glob("..claude-review.qualification.json.*.tmp")), [])

            def contaminate_then_fail(source, destination):
                Path(source).chmod(0o644)
                raise OSError("fixture replacement failure")

            with mock.patch.object(self.launcher.os, "replace", contaminate_then_fail):
                with self.assertRaisesRegex(RuntimeError, "residue preserved") as raised:
                    self.launcher.atomic_replace_qualification_receipt(
                        current, {"next": True}, b"prior\n", os.geteuid()
                    )
            self.assertIsInstance(raised.exception.__cause__, OSError)
            self.assertEqual(str(raised.exception.__cause__), "fixture replacement failure")
            residue = list(root.glob("..claude-review.qualification.json.*.tmp"))
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
            self.assertEqual(
                list(fixture["installation_directory"].glob(".*.json")),
                [fixture["receipt_path"]],
            )

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
        scenarios = ("receipt_mode", "receipt_symlink")
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
                fixture["receipt_path"].chmod(0o600)
                fixture["receipt_path"].write_bytes(receipt_bytes)
                fixture["receipt_path"].chmod(0o400)
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
                installed_module = load_script("claude_review_foreign_receipt", fixture["launcher"])
                with self.assertRaisesRegex(ValueError, "private regular file"):
                    installed_module.current_qualification(fixture["manifest"], os.geteuid())

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

    def test_initial_installation_fsyncs_flat_receipt_to_install_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            events = []
            original_exclusive = self.installer.exclusive_or_identical

            def record_fsync(path):
                events.append(("fsync", path))

            def record_exclusive(path, payload, mode):
                if path.name == ".claude-review.json":
                    events.append(("receipt", path))
                return original_exclusive(path, payload, mode)

            with mock.patch.object(self.installer, "fsync_directory", record_fsync), mock.patch.object(
                self.installer, "exclusive_or_identical", record_exclusive
            ):
                installed, _ = self.run_installer(root, selector, "initial.json", "1" * 40)

            receipt = Path(installed["qualification_receipt_path"])
            install_directory = Path(installed["installation_directory"])
            self.assertLess(
                events.index(("receipt", receipt)),
                events.index(("fsync", install_directory)),
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

    def test_installer_rejects_unsafe_activation_and_install_directories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            activation = root / "activation"
            activation.mkdir(mode=0o755)
            activation.chmod(0o755)

            with self.assertRaisesRegex(ValueError, "private operator-controlled"):
                self.run_installer(root, selector, "receipt.json", "1" * 40)

            activation.chmod(0o700)
            contract_id = "sha256:" + "a" * 64
            install_directory = root / "install-root"
            install_directory.mkdir()
            install_directory.chmod(0o775)
            with mock.patch.object(
                self.installer, "entry_contract_identity", return_value=contract_id
            ), self.assertRaisesRegex(ValueError, "operator-controlled"):
                self.run_installer(root, selector, "receipt-2.json", "2" * 40)

    def test_installer_rejects_unsafe_activation_grandparent_before_mutation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            unsafe_grandparent = root / "activation"
            unsafe_grandparent.mkdir(mode=0o700)
            unsafe_grandparent.chmod(0o777)
            activation_parent = unsafe_grandparent / "new-private"

            with self.assertRaisesRegex(ValueError, "destination ancestor"):
                self.run_installer(
                    root,
                    selector,
                    "new-private/receipt.json",
                    "1" * 40,
                )

            self.assertFalse(activation_parent.exists())
            self.assertFalse((root / "install-root").exists())

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
            self.assertEqual(launcher.name, "claude-review")
            manifest_path = Path(initial["installation_manifest_path"])
            current_path = Path(initial["qualification_receipt_path"])
            install_directory = Path(initial["installation_directory"])
            active_rule = Path(initial["active_rule_path"])
            immutable = {
                "launcher": launcher.read_bytes(),
                "manifest": manifest_path.read_bytes(),
                "entry_contract": json.loads(manifest_path.read_text(encoding="utf-8"))[
                    "entry_contract"
                ],
                "active_rule": active_rule.read_bytes(),
                "entry": initial["entry_contract_id"],
            }
            installed_module = load_script("claude_review_installer_rerun", launcher)
            initial_current = current_path.read_bytes()
            initial_files = {path.name for path in install_directory.iterdir()}
            initial_rerun, _ = self.run_installer(
                root, selector, "activation-initial-rerun.json", "2" * 40
            )
            self.assertEqual(initial_rerun["entry_contract_id"], immutable["entry"])
            self.assertEqual(current_path.read_bytes(), initial_current)
            self.assertEqual({path.name for path in install_directory.iterdir()}, initial_files)

            for index, target in enumerate((targets[1], targets[2], targets[0]), start=3):
                selector.unlink()
                selector.symlink_to(target)
                current_sha256 = self.launcher.sha256_bytes(current_path.read_bytes())
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                forbidden = [Path(value) for value in manifest["forbidden_roots"]]
                observed = installed_module.executable_file_identity(
                    selector, os.geteuid(), forbidden
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(
                        installed_module.qualify_claude_identity(
                            os.geteuid(),
                            expected_current_receipt_sha256=current_sha256,
                            expected_observed_file_identity_sha256=installed_module.file_identity_digest(observed),
                        ),
                        0,
                    )
                before_current = current_path.read_bytes()
                before_files = {path.name for path in install_directory.iterdir()}
                rerun, activation = self.run_installer(
                    root, selector, f"activation-{index}.json", f"{index}" * 40
                )
                self.assertEqual(rerun["entry_contract_id"], immutable["entry"])
                self.assertEqual(launcher.read_bytes(), immutable["launcher"])
                self.assertEqual(
                    json.loads(manifest_path.read_text(encoding="utf-8"))["entry_contract"],
                    immutable["entry_contract"],
                )
                self.assertEqual(active_rule.read_bytes(), immutable["active_rule"])
                self.assertEqual(current_path.read_bytes(), before_current)
                self.assertEqual({path.name for path in install_directory.iterdir()}, before_files)
                self.assertEqual(
                    rerun["qualification_receipt_sha256"],
                    self.launcher.sha256_bytes(before_current),
                )
                self.assertTrue(activation.exists())
                self.assertEqual(rerun["source_provenance"]["source_commit"], str(index) * 40)

    def test_activation_receipt_keeps_its_distinct_record_identity(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            installed, activation = self.run_installer(
                root, selector, "activation.json", "1" * 40
            )

            self.assertEqual(installed["kind"], "claude_review_activation_receipt")
            self.assertEqual(
                json.loads(activation.read_text(encoding="utf-8"))["kind"],
                "claude_review_activation_receipt",
            )
            combined = json.loads(
                Path(installed["installation_manifest_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(combined["kind"], "claude_reviewer_qualification_receipt")

    def test_existing_launcher_without_combined_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            selector, _ = self.create_installer_targets(root)
            installed, _ = self.run_installer(root, selector, "initial.json", "1" * 40)
            record = Path(installed["installation_manifest_path"])
            record.unlink()

            with self.assertRaisesRegex(ValueError, "missing its combined"):
                self.run_installer(root, selector, "replacement.json", "2" * 40)
            self.assertFalse((root / "activation" / "replacement.json").exists())

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
            current_path = Path(initial["qualification_receipt_path"])
            install_directory = Path(initial["installation_directory"])
            active_rule = Path(initial["active_rule_path"])
            before_current = current_path.read_bytes()
            before_files = {path.name for path in install_directory.iterdir()}
            active_rule.write_bytes(b"operator-prior-rule\n")
            active_rule.chmod(0o600)
            before_rule = active_rule.read_bytes()
            activation = root / "activation" / "drift-rerun.json"
            with self.assertRaisesRegex(self.installer.QualificationRequiredError, "qualification required"):
                self.run_installer(root, selector, activation.name, "2" * 40)
            self.assertFalse(marker.exists())
            self.assertEqual(current_path.read_bytes(), before_current)
            self.assertEqual({path.name for path in install_directory.iterdir()}, before_files)
            self.assertEqual(active_rule.read_bytes(), before_rule)
            self.assertFalse(activation.exists())

    def test_installer_and_launcher_share_the_full_invalid_state_matrix(self):
        scenarios = (
            "receipt_symlink", "receipt_mode", "foreign_owner", "malformed_receipt",
            "wrong_kind", "wrong_schema", "wrong_entry", "wrong_selector",
            "wrong_producer", "wrong_authority", "wrong_file_identity",
            "missing_receipt", "invalid_predecessor",
            "self_predecessor",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.create_installed_fixture(Path(temporary_directory).resolve())
                receipt = json.loads(fixture["receipt_path"].read_text(encoding="utf-8"))
                manifest = dict(fixture["manifest"])
                installed_module = load_script(
                    f"claude_review_invalid_flat_state_{scenario}", fixture["launcher"]
                )

                def write_receipt(payload):
                    payload_bytes = (
                        payload
                        if isinstance(payload, bytes)
                        else self.launcher.canonical_json_bytes(payload)
                    )
                    fixture["receipt_path"].chmod(0o600)
                    fixture["receipt_path"].write_bytes(payload_bytes)
                    fixture["receipt_path"].chmod(0o400)

                if scenario == "receipt_symlink":
                    replacement = fixture["installation_directory"] / "replacement.json"
                    replacement.write_bytes(fixture["receipt_path"].read_bytes())
                    replacement.chmod(0o400)
                    fixture["receipt_path"].unlink()
                    fixture["receipt_path"].symlink_to(replacement)
                elif scenario == "receipt_mode":
                    fixture["receipt_path"].chmod(0o600)
                elif scenario == "malformed_receipt":
                    write_receipt(b"{malformed\n")
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
                    write_receipt({**receipt, field: value})
                elif scenario == "wrong_file_identity":
                    write_receipt({
                        **receipt,
                        "file_identity": {
                            **receipt["file_identity"],
                            "resolved_sha256": "not-a-digest",
                        },
                    })
                elif scenario == "missing_receipt":
                    fixture["receipt_path"].unlink()
                elif scenario == "invalid_predecessor":
                    write_receipt({**receipt, "predecessor_receipt_sha256": "not-a-digest"})
                elif scenario == "self_predecessor":
                    write_receipt({**receipt, "predecessor_receipt_sha256": "e" * 64})

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
                    context = contextlib.ExitStack()
                    context.enter_context(
                        mock.patch.object(self.installer, "digest", return_value="e" * 64)
                    )
                    context.enter_context(
                        mock.patch.object(installed_module, "sha256_bytes", return_value="e" * 64)
                    )
                else:
                    context = contextlib.nullcontext()

                with context:
                    with self.assertRaises((OSError, ValueError)):
                        self.installer.validated_existing_qualification(manifest)
                    with self.assertRaises((OSError, ValueError)):
                        installed_module.current_qualification(manifest, os.geteuid())

    def test_temporary_production_install_binds_launcher_rule_and_claude_identity(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            installed = root / "installed"
            installed.mkdir(mode=0o755)
            launcher = installed / "claude-review-fixture"
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
                "entry_contract_schema_version": 2,
                "installation_schema_version": 3,
                "qualification_schema_version": 3,
                "launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
                "rule_template_sha256": "fixture-rule-template",
                "claude_selector": str(selector),
                "active_rule_path": str(active_rule),
                "forbidden_roots": [str(candidate)],
                "auth_diagnostics_directory": str(auth_diagnostics),
                "installation_directory": str(installed),
            }
            entry_contract_id = "sha256:" + self.launcher.sha256_bytes(
                self.launcher.canonical_json_bytes(entry_contract)
            )
            receipt_path = installed / f".{launcher.name}.json"
            manifest = {
                "schema_version": 3,
                "entry_contract_id": entry_contract_id,
                "entry_contract": entry_contract,
                "installed_launcher_path": str(launcher),
                "installed_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
                "active_rule_path": str(active_rule),
                "active_rule_sha256": self.launcher.sha256_bytes(active_rule.read_bytes()),
                "claude_selector": str(selector),
                "forbidden_roots": [str(candidate)],
                "auth_diagnostics_directory": str(auth_diagnostics),
                "qualification_schema_version": 3,
                "installation_directory": str(installed),
            }
            receipt = {
                "kind": "claude_reviewer_qualification_receipt",
                "schema_version": 3,
                "entry_contract_id": entry_contract_id,
                "claude_selector": str(selector),
                "file_identity": qualified_identity["file_identity"],
                "version": qualified_identity["version"],
                "predecessor_receipt_sha256": None,
                "producing_launcher_path": str(launcher),
                "producing_launcher_sha256": self.launcher.sha256_bytes(launcher_bytes),
                "authority_semantics": "capability qualification only; grants zero task or review authority",
            }
            manifest.update(receipt)
            receipt_bytes = self.launcher.canonical_json_bytes(manifest)
            receipt_sha256 = self.launcher.sha256_bytes(receipt_bytes)
            receipt_path.write_bytes(receipt_bytes)
            receipt_path.chmod(0o400)
            manifest_path = receipt_path
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

        self.assertEqual(completed.returncode, 0, diagnostic)
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

    def test_stream_json_oauth_error_is_an_infrastructure_failure_even_with_exit_zero(self):
        completed, diagnostic = self.run_launcher(
            "print('{\"type\": \"system\", \"subtype\": \"init\"}')\n"
            "print('{\"type\": \"result\", \"subtype\": \"error_during_execution\", \"is_error\": true, \"result\": \"API Error: 401 OAuth access token has expired\"}')\n"
        )

        self.assertEqual(completed.returncode, 78)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(diagnostic["failure_classification"], "AUTH_OAUTH_TOKEN_EXPIRED_401")

    def test_authentication_error_on_stderr_does_not_discard_a_completed_review(self):
        completed, diagnostic = self.run_launcher(
            "print('API Error: 401 OAuth access token has expired', file=sys.stderr)\n"
            "print('ACCEPT')\n"
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "ACCEPT\n")
        self.assertIsNone(diagnostic["failure_classification"])

    def test_auth_preflight_uses_fixed_prompt_and_omits_review_tools(self):
        completed, diagnostic = self.run_launcher(
            "prompt = sys.stdin.read()\n"
            "assert prompt == 'Reply exactly: CLAUDE_AUTH_OK\\n'\n"
            "assert sys.argv[sys.argv.index('--tools') + 1] == ''\n"
            "assert '--model' in sys.argv\n"
            "assert '--effort' in sys.argv\n"
            "assert os.environ['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] == '1'\n"
            "assert os.environ['CLAUDE_CODE_DISABLE_CLAUDE_MDS'] == '1'\n"
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
            "    scenario = os.environ.get('FAKE_SCENARIO')\n"
            "    if scenario == 'version_banner': print('Node 22.1.0; fake-claude 2.1.252')\n"
            "    else:\n"
            "        version = '2.1.247' if scenario == 'restricted_unsupported' else '2.1.252'\n"
            "        print(f'{version} (fake-claude)')\n"
            "    raise SystemExit(0)\n"
            "prompt = sys.stdin.read()\n"
            "count = pathlib.Path(os.environ['FAKE_COUNT'])\n"
            "attempt = int(count.read_text()) + 1 if count.exists() else 1\n"
            "count.write_text(str(attempt))\n"
            "scenario = os.environ.get('FAKE_SCENARIO', 'success')\n"
            "if scenario in {'early_server_error','early_auth_error'}:\n"
            "    error = 'server_error' if scenario == 'early_server_error' else 'authentication_failed'\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':error}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
            "    raise SystemExit(1)\n"
            "if scenario == 'ignore_term': signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "candidate = pathlib.Path(os.environ['FAKE_CANDIDATE'])\n"
            "package = pathlib.Path(os.environ['FAKE_PACKAGE'])\n"
            "tools = ['Bash','Glob','Grep'] if scenario == 'tool_mismatch' else ['Bash','Glob','Grep','Read']\n"
            "model = 'wrong-exact-model' if scenario == 'model_mismatch' else os.environ.get('FAKE_EFFECTIVE_MODEL', 'claude-opus-5')\n"
            "cwd = str(candidate) if scenario == 'cwd_mismatch' else os.getcwd()\n"
            "print(json.dumps({'type':'system','subtype':'init','session_id':f's{attempt}','model':model,'tools':tools,'mcp_servers':[],'permissionMode':'dontAsk','plugins':[],'skills':[],'slash_commands':[],'cwd':cwd} ), flush=True)\n"
            "canary_id = f'canary-{attempt}'\n"
            "canary_command = f'git -C {candidate} status --porcelain=v2 --untracked-files=all'\n"
            "canary_input = {'command': canary_command}\n"
            "if scenario == 'canary_bypass': canary_input['dangerouslyDisableSandbox'] = True\n"
            "print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use','id':canary_id,'name':'Bash','input':canary_input}]}}), flush=True)\n"
            "settings_index = sys.argv.index('--settings')\n"
            "settings = json.loads(sys.argv[settings_index + 1])\n"
            "hook = settings['hooks']['PreToolUse'][0]['hooks'][0]\n"
            "hook_input = {'cwd':os.getcwd(),'permission_mode':'dontAsk','hook_event_name':'PreToolUse','tool_name':'Bash','tool_input':canary_input}\n"
            "effective_effort = os.environ.get('FAKE_EFFECTIVE_EFFORT','high')\n"
            "if scenario == 'inherited_effort_override': effective_effort = os.environ.get('CLAUDE_CODE_EFFORT_LEVEL', effective_effort)\n"
            "if scenario != 'effort_unobservable': hook_input['effort'] = {'level':effective_effort}\n"
            "hook_denied = False\n"
            "if scenario != 'hook_unobservable':\n"
            "    hook_result = subprocess.run([hook['command'], *hook['args']], input=json.dumps(hook_input), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n"
            "    hook_output = json.loads(hook_result.stdout)\n"
            "    hook_denied = hook_output['hookSpecificOutput']['permissionDecision'] != 'allow'\n"
            "print(json.dumps({'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':canary_id,'content':'canary','is_error':scenario == 'dead_command_grant' or hook_denied}]}}), flush=True)\n"
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
            "if scenario in {'unrelated_worktree_commit_then_wait','unrelated_worktree_and_candidate_mutation'}:\n"
            "    other = pathlib.Path(os.environ['FAKE_OTHER_WORKTREE'])\n"
            "    (other / 'tracked.txt').write_text(f'unrelated {attempt}\\n')\n"
            "    subprocess.run(['git','-C',str(other),'add','tracked.txt'], check=True)\n"
            "    subprocess.run(['git','-C',str(other),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm',f'unrelated {attempt}'], check=True)\n"
            "    if scenario == 'unrelated_worktree_and_candidate_mutation':\n"
            "        (candidate / 'tracked.txt').write_text('candidate mutation\\n')\n"
            "        time.sleep(10)\n"
            "    time.sleep(0.08)\n"
            "if scenario in {'primary_worktree_commit_then_wait','primary_worktree_and_candidate_mutation'}:\n"
            "    primary = pathlib.Path(os.environ['FAKE_PRIMARY_WORKTREE'])\n"
            "    (primary / 'tracked.txt').write_text(f'primary unrelated {attempt}\\n')\n"
            "    subprocess.run(['git','-C',str(primary),'add','tracked.txt'], check=True)\n"
            "    subprocess.run(['git','-C',str(primary),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm',f'primary unrelated {attempt}'], check=True)\n"
            "    if scenario == 'primary_worktree_and_candidate_mutation':\n"
            "        (candidate / 'tracked.txt').write_text('candidate mutation\\n')\n"
            "        time.sleep(10)\n"
            "    time.sleep(0.08)\n"
            "if scenario == 'unattributed_object_then_wait':\n"
            "    subprocess.run(['git','-C',str(candidate),'hash-object','-w','--stdin'], input=b'unattached reviewer object\\n', check=True)\n"
            "    time.sleep(10)\n"
            "if scenario == 'git_lock_then_wait':\n"
            "    (candidate / '.git' / 'index.lock').write_text('reviewer lock\\n')\n"
            "    time.sleep(10)\n"
            "if scenario == 'special_object_then_wait':\n"
            "    os.mkfifo(candidate / 'reviewer.fifo')\n"
            "    time.sleep(0.5)\n"
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
            "if scenario == 'live_receipts': time.sleep(0.15)\n"
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
            "if scenario == 'hostile_retry_error':\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':'authorization: Bearer secret-token-value' + 'x' * 2000}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
            "    raise SystemExit(1)\n"
            "print(json.dumps({'type':'result','subtype':'success','is_error':False,'session_id':f's{attempt}','result':'ACCEPT'}), flush=True)\n",
            encoding="utf-8",
        )
        self.fake.chmod(0o755)

    def config_body(self, *, launch_root=None, additional=None):
        candidate_head = subprocess.run(
            ["git", "-C", str(self.candidate), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        return {
            "schema_version": 2,
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
            "attempt_stream": str(self.evidence / "attempt-stream.jsonl"),
            "attempt_terminal_receipt": str(self.evidence / "attempt-terminal-receipt.json"),
            "allowed_commands": [
                ["git", "-C", str(self.candidate), "status", "--porcelain=v2", "--untracked-files=all"]
            ],
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

    def environment(self, scenario, *, effective_model=None, effective_effort=None):
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
        if hasattr(self, "other_worktree"):
            environment["FAKE_OTHER_WORKTREE"] = str(self.other_worktree)
        if hasattr(self, "primary_worktree"):
            environment["FAKE_PRIMARY_WORKTREE"] = str(self.primary_worktree)
        if hasattr(self, "isolated_home"):
            environment["CLAUDE_REVIEW_TEST_EFFECTIVE_HOME"] = str(self.isolated_home)
        if effective_model is not None:
            environment["FAKE_EFFECTIVE_MODEL"] = effective_model
        if effective_effort is not None:
            environment["FAKE_EFFECTIVE_EFFORT"] = effective_effort
        return environment

    def run_governed(
        self,
        scenario="success",
        *,
        body=None,
        model="opus",
        effort="high",
        effective_model=None,
        effective_effort=None,
    ):
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
        for key in ("attempt_stream", "attempt_terminal_receipt"):
            artifact = Path((body or self.config_body())[key])
            if artifact.exists() or artifact.is_symlink():
                artifact.unlink()
        claude_arguments = ["--model", model]
        if effort is not None:
            claude_arguments.extend(("--effort", effort))
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
                *claude_arguments,
            ],
            check=False,
            input="exact review prompt\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environment(
                scenario,
                effective_model=effective_model,
                effective_effort=effective_effort,
            ),
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

    def use_linked_candidate(self, branch="fixture-linked-candidate"):
        self.primary_worktree = self.candidate
        linked = self.root / branch
        subprocess.run(
            ["git", "-C", str(self.primary_worktree), "worktree", "add", "-q", "-b", branch, str(linked)],
            check=True,
        )
        self.candidate = linked
        return self.primary_worktree, linked

    def commit_tracked(self, worktree, content, message):
        (worktree / "tracked.txt").write_text(content, encoding="utf-8")
        subprocess.run(["git", "-C", str(worktree), "add", "tracked.txt"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(worktree),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                message,
            ],
            check=True,
        )

    def run_governed_with_head_mutation(
        self,
        *,
        verification_call,
        scenario="success",
        symbolic_ref_only=False,
    ):
        module = load_script(f"claude_review_head_drift_{verification_call}_{scenario}", LAUNCHER)
        body = self.config_body()
        config = module.load_governed_config(self.write_config(body))
        diagnostics = self.evidence / "overall.json"
        environment = self.environment(scenario)
        original_verifier = module.verified_candidate_head
        calls = 0

        def mutate_at_boundary(candidate, expected_head, command_environment, **verification_options):
            nonlocal calls
            calls += 1
            if calls == verification_call:
                if symbolic_ref_only:
                    subprocess.run(
                        ["git", "-C", str(self.candidate), "switch", "-q", "-c", f"fixture-symbolic-drift-{calls}"],
                        check=True,
                    )
                else:
                    self.commit_tracked(self.candidate, f"head drift {calls}\n", f"head drift {calls}")
            return original_verifier(candidate, expected_head, command_environment, **verification_options)

        with mock.patch.dict(os.environ, environment), mock.patch.object(
            module,
            "verified_candidate_head",
            side_effect=mutate_at_boundary,
        ), contextlib.redirect_stderr(io.StringIO()):
            executable, execution_identity = module.qualified_execution(
                str(self.fake),
                os.geteuid(),
                explicit_test_fixture=True,
            )
            result = module.run_governed_review(
                config,
                executable,
                execution_identity,
                environment,
                ["--model", "opus", "--effort", "high"],
                b"exact review prompt\n",
                diagnostics,
            )
        return result, json.loads(diagnostics.read_text(encoding="utf-8"))

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
        exact, _ = self.run_governed(model="fake-opus", effective_model="fake-opus")
        self.assertEqual(exact.returncode, 0)
        mismatch, diagnostic = self.run_governed(
            "model_mismatch",
            model="fake-opus",
            effective_model="fake-opus",
        )
        self.assertEqual(mismatch.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_model_mismatch")

    def test_fable_family_accepts_current_exact_runtime_identity(self):
        completed, _ = self.run_governed(model="fable", effective_model="claude-fable-5")
        self.assertEqual(completed.returncode, 0)

    def test_fable_family_rejects_other_or_unknown_runtime_identities(self):
        for effective_model in (
            "claude-opus-5",
            "claude-sonnet-5",
            "unknown",
            "claude-fable-6",
            "claude-fable-5-preview",
            "Claude-Fable-5",
        ):
            with self.subTest(effective_model=effective_model):
                completed, diagnostic = self.run_governed(
                    model="fable",
                    effective_model=effective_model,
                )
                self.assertEqual(completed.returncode, 70)
                self.assertEqual(diagnostic["failure_classification"], "effective_model_mismatch")

    def test_non_fable_family_rejects_fable_runtime_identity(self):
        completed, diagnostic = self.run_governed(
            model="opus",
            effective_model="claude-fable-5",
        )
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_model_mismatch")

    def test_existing_family_aliases_accept_canonical_runtime_identities(self):
        for family in ("haiku", "sonnet", "opus"):
            with self.subTest(family=family):
                completed, _ = self.run_governed(
                    model=family,
                    effective_model=f"claude-{family}-5",
                )
                self.assertEqual(completed.returncode, 0)

    def test_effective_high_effort_is_observed_separately_from_request(self):
        completed, _ = self.run_governed(effort="high", effective_effort="high")
        self.assertEqual(completed.returncode, 0)
        qualification = self.receipts()[0]["runtime"]["configuration_qualification"]
        self.assertEqual(qualification["requested"]["effort"], "high")
        self.assertEqual(
            qualification["effective"]["effort"],
            {
                "status": "observed",
                "value": "high",
                "source": "pre_tool_use_hook_input",
            },
        )
        self.assertTrue(qualification["effort_matches"])
        self.assertTrue(qualification["permission_hook_liveness"]["observed"])

    def test_effective_effort_mismatch_fails_closed(self):
        completed, diagnostic = self.run_governed(effort="high", effective_effort="low")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_effort_mismatch")
        qualification = self.receipts()[0]["runtime"]["configuration_qualification"]
        self.assertEqual(qualification["effective"]["effort"]["value"], "low")
        self.assertFalse(qualification["effort_matches"])

    def test_explicit_effort_removes_inherited_effort_override(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_EFFORT_LEVEL": "low"}):
            completed, _ = self.run_governed("inherited_effort_override", effort="high")
        self.assertEqual(completed.returncode, 0)
        qualification = self.receipts()[0]["runtime"]["configuration_qualification"]
        self.assertEqual(qualification["effective"]["effort"]["value"], "high")

    def test_unobservable_effective_effort_fails_closed_without_claiming_high(self):
        completed, diagnostic = self.run_governed("effort_unobservable", effort="high")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "effective_effort_unobservable")
        qualification = self.receipts()[0]["runtime"]["configuration_qualification"]
        self.assertEqual(qualification["requested"]["effort"], "high")
        self.assertEqual(qualification["effective"]["effort"]["status"], "unobservable")
        self.assertIsNone(qualification["effective"]["effort"]["value"])
        self.assertFalse(qualification["effort_matches"])

    def test_permission_hook_liveness_is_required_without_an_effort_request(self):
        completed, diagnostic = self.run_governed("hook_unobservable", effort=None)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "permission_hook_unobservable")
        qualification = self.receipts()[0]["runtime"]["configuration_qualification"]
        self.assertEqual(qualification["requested"]["effort"], None)
        self.assertEqual(qualification["permission_hook_liveness"], {"observed": False})

    def test_restricted_mode_version_floor_stops_before_provider_spawn(self):
        completed, diagnostic = self.run_governed("restricted_unsupported")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(
            diagnostic["failure_classification"],
            "claude_restricted_mode_version_unsupported",
        )
        self.assertFalse(diagnostic["substantive_review_started"])
        self.assertFalse(self.count.exists())

    def test_restricted_mode_version_floor_rejects_a_prefixed_version_banner(self):
        completed, diagnostic = self.run_governed("version_banner")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(
            diagnostic["failure_classification"],
            "claude_restricted_mode_version_unsupported",
        )
        self.assertFalse(self.count.exists())

    def test_candidate_head_drift_before_first_attempt_baseline_stops_without_provider_spawn(self):
        result, diagnostic = self.run_governed_with_head_mutation(verification_call=2)
        self.assertEqual(result, 70)
        self.assertEqual(diagnostic["failure_classification"], "candidate_identity_changed_before_attempt")
        self.assertEqual(diagnostic["candidate_identity_stage"], "before_attempt_baseline")
        self.assertFalse(self.count.exists())
        self.assertTrue(diagnostic["no_delta_postflight"]["changed_paths"])

    def test_candidate_symbolic_ref_drift_before_spawn_stops_without_provider_spawn(self):
        result, diagnostic = self.run_governed_with_head_mutation(
            verification_call=3,
            symbolic_ref_only=True,
        )
        self.assertEqual(result, 70)
        self.assertEqual(diagnostic["failure_classification"], "candidate_identity_changed_before_execution")
        self.assertEqual(diagnostic["candidate_identity_stage"], "immediately_before_provider_spawn")
        self.assertFalse(self.count.exists())
        self.assertEqual(
            diagnostic["candidate_identity_observation"]["observed_commit"],
            diagnostic["candidate_identity_observation"]["expected_commit"],
        )
        self.assertNotEqual(
            diagnostic["candidate_identity_observation"]["symbolic_ref"],
            diagnostic["candidate_identity_observation"]["expected_symbolic_ref"],
        )
        self.assertTrue(
            any(
                record["classification"] == "blocking_candidate_worktree_administration"
                for record in diagnostic["no_delta_postflight"]["git_admin_changes"]
            )
        )

    def test_detached_candidate_remains_bound_to_configured_commit(self):
        subprocess.run(["git", "-C", str(self.candidate), "checkout", "--detach", "-q", "HEAD"], check=True)
        completed, diagnostic = self.run_governed("success", body=self.config_body())
        self.assertEqual(completed.returncode, 0, diagnostic)
        self.assertEqual(diagnostic["preflight"]["candidate_identity"]["symbolic_ref"], None)
        self.assertEqual(
            diagnostic["preflight"]["candidate_identity"]["observed_commit"],
            diagnostic["preflight"]["candidate_identity"]["expected_commit"],
        )

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
            scratch / module.HOOK_LIVENESS_EVIDENCE_NAME,
            scratch / module.EFFORT_EVIDENCE_NAME,
        )
        self.assertIn("--restricted", arguments)
        self.assertEqual(arguments[arguments.index("--setting-sources") + 1], "")
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

    def test_terminal_transient_failure_stops_without_controller_retry(self):
        completed, diagnostic = self.run_governed("transient_once")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "terminal_provider_server_error")
        self.assertFalse(diagnostic["automated_retry_attempted"])
        self.assertEqual(len(diagnostic["attempts"]), 1)
        receipts = self.receipts()
        self.assertEqual(len(receipts), 1)
        self.assertEqual({receipt["controller_id"] for receipt in receipts}, {diagnostic["controller_id"]})
        self.assertEqual(receipts[0]["execution_kind"], "fresh_execution")
        scratch_paths = [receipt["attempt_scratch"]["path"] for receipt in receipts]
        self.assertTrue(all(receipt["attempt_scratch"]["cleanup"]["passed"] for receipt in receipts))
        self.assertTrue(all(not Path(path).exists() for path in scratch_paths))

    def test_unknown_provider_retry_error_uses_a_fixed_safe_classification(self):
        completed, diagnostic = self.run_governed("hostile_retry_error")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "terminal_provider_failure")
        serialized = json.dumps({"diagnostic": diagnostic, "receipts": self.receipts()})
        self.assertNotIn("secret-token-value", serialized)
        self.assertLess(len(diagnostic["failure_classification"]), 100)

    def test_provider_failure_before_init_preserves_terminal_class_and_exit_policy(self):
        server, server_diagnostic = self.run_governed("early_server_error")
        self.assertEqual(server.returncode, 70)
        self.assertEqual(server_diagnostic["failure_classification"], "terminal_provider_server_error")

        auth, auth_diagnostic = self.run_governed("early_auth_error")
        self.assertEqual(auth.returncode, 78)
        self.assertEqual(auth_diagnostic["failure_classification"], "AUTH_UNKNOWN_FAIL_CLOSED")

    def test_provider_terminal_failure_does_not_recheck_for_a_second_spawn(self):
        completed, diagnostic = self.run_governed("transient_then_executable_drift")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(self.count.read_text(encoding="utf-8"), "1")
        self.assertEqual(diagnostic["failure_classification"], "terminal_provider_server_error")
        self.assertEqual(diagnostic["candidate_verdict"], "not_produced")
        self.assertEqual(self.receipts()[0]["attempt_number"], 1)
        self.assertFalse(diagnostic["substantive_review_output"])
        self.assertFalse(diagnostic["automated_retry_attempted"])
        self.assertEqual((self.root / "version-count").read_text(encoding="utf-8"), "2")
        self.assertEqual(len(diagnostic["attempts"]), 1)
        prior_attempt = diagnostic["attempts"][0]
        self.assertTrue(Path(prior_attempt["receipt"]).exists())
        receipt = json.loads(Path(prior_attempt["receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["attempt_number"], 1)
        self.assertTrue(Path(receipt["raw_output"]["path"]).exists())
        self.assertEqual(len(self.receipts()), 1)

    def test_lingering_process_group_reaches_terminal_before_attempt_receipt(self):
        completed, diagnostic = self.run_governed("transient_with_lingering_child")
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(len(diagnostic["attempts"]), 1)
        receipts = self.receipts()
        self.assertTrue(all(receipt["lifecycle"]["process_group_terminal"] for receipt in receipts))
        self.assertTrue(
            all(
                receipt["stream_evidence"]["collectors_reached_eof_before_stream_freeze"]
                for receipt in receipts
            )
        )
        self.assertEqual((self.root / "lingering-child-terminal").read_text(), "terminal")

    def test_partial_reader_failure_cannot_qualify_as_complete_stream_evidence(self):
        module = load_script("claude_review_partial_reader_failure", LAUNCHER)

        class PartialThenFailedStream:
            def __init__(self):
                self.reads = 0

            def readline(self):
                self.reads += 1
                if self.reads == 1:
                    return b"partial review evidence\n"
                raise OSError("fixture reader failure")

        failed = module.PipeCollector(PartialThenFailedStream())
        complete = module.PipeCollector(io.BytesIO(b"complete stderr\n"))
        failed.thread.join(timeout=1)
        complete.thread.join(timeout=1)

        stream_evidence = {
            "collectors_reached_eof_before_stream_freeze": (
                failed.eof.is_set() and complete.eof.is_set()
            ),
            "collector_read_errors": {"stdout": failed.error, "stderr": complete.error},
        }

        self.assertEqual(failed.bytes(), b"partial review evidence\n")
        self.assertFalse(stream_evidence["collectors_reached_eof_before_stream_freeze"])
        self.assertEqual(stream_evidence["collector_read_errors"]["stdout"], "fixture reader failure")

    def test_live_telemetry_callback_failure_preserves_raw_stream(self):
        module = load_script("claude_review_callback_failure", LAUNCHER)
        degraded_arrivals = []

        def fail_interpretation(_line, _arrival):
            raise ValueError("sensitive callback failure")

        collector = module.PipeCollector(
            io.BytesIO(b"exact raw record\n"),
            fail_interpretation,
            degraded_arrivals.append,
        )
        collector.thread.join(timeout=1)

        self.assertEqual(collector.bytes(), b"exact raw record\n")
        self.assertTrue(collector.eof.is_set())
        self.assertTrue(collector.done.is_set())
        self.assertIsNone(collector.error)
        self.assertEqual(collector.callback_error, "telemetry_interpretation_error")
        self.assertEqual(len(degraded_arrivals), 1)

    def test_live_telemetry_finalization_wires_collector_and_callback_degradation(self):
        module = load_script("claude_review_live_telemetry_finalization", LAUNCHER)

        class FailingReader:
            def __init__(self):
                self.calls = 0

            def readline(self):
                self.calls += 1
                if self.calls == 1:
                    return b"exact raw record\n"
                raise OSError("sensitive collector failure")

        telemetry = module.LiveTelemetry("attempt-finalization")

        def fail_interpretation(_line, _arrival):
            raise ValueError("sensitive callback failure")

        collector = module.PipeCollector(
            FailingReader(),
            fail_interpretation,
            telemetry.interpretation_failed,
        )
        collector.thread.join(timeout=1)
        finalized = module.finalize_live_telemetry(telemetry, collector)

        self.assertEqual(collector.bytes(), b"exact raw record\n")
        self.assertEqual(finalized["callback_error"], "telemetry_interpretation_error")
        reasons = [
            receipt["metadata"]["reason"]
            for receipt in finalized["snapshot"]["receipts"]
        ]
        self.assertEqual(reasons, ["telemetry_interpretation_error", "collector_error"])
        self.assertNotIn("sensitive", json.dumps(finalized, sort_keys=True))

    def test_live_telemetry_normalizes_only_allowlisted_metadata(self):
        module = load_script("claude_review_live_telemetry_privacy", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-1")
        records = (
            {
                "type": "system",
                "subtype": "init",
                "session_id": "session-secret-token-value-" + "s" * 300,
                "model": "sensitive-model-config",
            },
            {
                "type": "assistant",
                "message": {
                    "id": "message-secret-token-value-" + "m" * 300,
                    "usage": {
                        "input_tokens": 2,
                        "output_tokens": 4,
                        "cache_read_input_tokens": True,
                        "ignored": "secret-token-value",
                    },
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "tool-secret-token-value-" + "t" * 300,
                            "name": "Bash",
                            "input": {"command": "secret-command --token secret-token-value"},
                        }
                    ],
                },
            },
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tool-secret-token-value-" + "t" * 300,
                            "content": "sensitive tool output",
                        }
                    ]
                },
            },
            {
                "type": "result",
                "subtype": "success",
                "session_id": "session-secret-token-value-" + "s" * 300,
                "usage": {"input_tokens": 3, "output_tokens": 5, "ignored": "secret-token-value"},
                "result": "sensitive reviewer prose",
            },
        )
        for ordinal, record in enumerate(records, start=1):
            telemetry.observe((json.dumps(record) + "\n").encode("utf-8"), float(ordinal))
        telemetry.observe((json.dumps(records[1]) + "\n").encode("utf-8"), 5.0)
        telemetry.observe(b'{"type":"assistant"}', 6.0)
        telemetry.observe(b'{"type":"future","prompt":"secret-token-value"}\n', 7.0)

        snapshot = telemetry.snapshot()
        encoded = json.dumps(snapshot, sort_keys=True)
        self.assertNotIn("secret-token-value", encoded)
        self.assertNotIn("sensitive reviewer prose", encoded)
        self.assertNotIn("sensitive tool output", encoded)
        self.assertNotIn("sensitive-model-config", encoded)
        self.assertNotIn("session-secret-token-value", encoded)
        self.assertNotIn("message-secret-token-value", encoded)
        self.assertNotIn("tool-secret-token-value", encoded)
        event_types = [receipt["event_type"] for receipt in snapshot["receipts"]]
        self.assertEqual(
            event_types,
            [
                "provider_session_initialized",
                "substantive_model_activity",
                "source_tool_request",
                "usage_sample",
                "source_tool_completion",
                "provider_terminal",
                "usage_sample",
                "telemetry_degraded",
                "telemetry_degraded",
                "telemetry_degraded",
            ],
        )
        self.assertEqual(snapshot["receipts"][2]["metadata"], {"tool_class": "shell"})
        self.assertEqual(
            snapshot["receipts"][3]["metadata"],
            {"scope": "assistant_event", "counters": {"input_tokens": 2, "output_tokens": 4}},
        )
        self.assertEqual(
            snapshot["receipts"][6]["metadata"],
            {"scope": "review_attempt_terminal", "counters": {"input_tokens": 3, "output_tokens": 5}},
        )
        self.assertEqual(snapshot["receipts"][3]["evidence"], "direct")
        self.assertEqual(snapshot["receipts"][6]["evidence"], "inferred")
        self.assertEqual(
            snapshot["receipts"][2]["provider_tool_correlation_id"],
            snapshot["receipts"][4]["provider_tool_correlation_id"],
        )
        self.assertNotEqual(
            module.correlation_identity("session", "same-provider-id"),
            module.correlation_identity("tool", "same-provider-id"),
        )
        self.assertEqual(
            module.correlation_identity("session", "same-provider-id"),
            module.correlation_identity("session", "same-provider-id"),
        )
        for key in (
            "provider_session_correlation_id",
            "provider_event_correlation_id",
            "provider_message_correlation_id",
            "provider_tool_correlation_id",
        ):
            for receipt in snapshot["receipts"]:
                if key in receipt:
                    self.assertRegex(receipt[key], r"^[0-9a-f]{64}$")
        self.assertEqual(snapshot["receipts"][-3]["metadata"], {"reason": "duplicate_or_replayed_record"})
        self.assertEqual(snapshot["receipts"][-2]["metadata"], {"reason": "truncated_record"})
        self.assertEqual(snapshot["receipts"][-1]["metadata"], {"reason": "unknown_provider_event"})
        self.assertRegex(telemetry._provider_session_correlation_id, r"^[0-9a-f]{64}$")
        for tracked in (
            telemetry._seen_event_ids,
            telemetry._seen_raw_record_digests,
            telemetry._seen_usage_samples,
            telemetry._tool_classes,
        ):
            self.assertTrue(all(len(identity) == 64 for identity in tracked))

    def test_live_telemetry_normalizes_non_string_provider_errors(self):
        module = load_script("claude_review_live_telemetry_error_type", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-error")
        telemetry.observe(
            b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
            1.0,
        )
        for ordinal, value in enumerate(({"secret": "value"}, ["secret"]), start=2):
            record = {
                "type": "system",
                "subtype": "api_retry",
                "session_id": "session-1",
                "uuid": f"event-{ordinal}",
                "error": value,
            }
            telemetry.observe((json.dumps(record) + "\n").encode("utf-8"), float(ordinal))

        snapshot = telemetry.snapshot()
        failures = [receipt for receipt in snapshot["receipts"] if receipt["event_type"] == "provider_failure"]
        self.assertEqual([receipt["metadata"] for receipt in failures], [{"error_class": "provider_failure"}] * 2)
        self.assertNotIn("secret", json.dumps(snapshot, sort_keys=True))

    def test_live_telemetry_rejects_oversized_usage_counters(self):
        module = load_script("claude_review_live_telemetry_usage_bound", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-counter")
        telemetry.observe(
            b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
            1.0,
        )
        record = {
            "type": "assistant",
            "session_id": "session-1",
            "message": {
                "id": "message-1",
                "content": [],
                "usage": {
                    "input_tokens": module.MAX_LIVE_TELEMETRY_USAGE_COUNTER + 1,
                    "output_tokens": 3,
                },
            },
        }
        telemetry.observe((json.dumps(record) + "\n").encode("utf-8"), 2.0)

        receipts = telemetry.snapshot()["receipts"]
        self.assertIn(
            {"reason": "usage_counter_out_of_range"},
            [receipt["metadata"] for receipt in receipts if receipt["event_type"] == "telemetry_degraded"],
        )
        usage = next(receipt for receipt in receipts if receipt["event_type"] == "usage_sample")
        self.assertEqual(usage["metadata"]["counters"], {"output_tokens": 3})

    def test_live_telemetry_rejects_provider_session_rebinding(self):
        module = load_script("claude_review_live_telemetry_session_rebind", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-session")
        telemetry.observe(
            b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
            1.0,
        )
        initial_session = telemetry._provider_session_correlation_id
        telemetry.observe(
            b'{"type":"assistant","session_id":"session-2","message":{"id":"message-1","content":[]}}\n',
            2.0,
        )

        snapshot = telemetry.snapshot()
        self.assertEqual(telemetry._provider_session_correlation_id, initial_session)
        self.assertEqual(snapshot["receipts"][-1]["event_type"], "telemetry_degraded")
        self.assertEqual(
            snapshot["receipts"][-1]["metadata"],
            {"reason": "provider_session_identity_changed"},
        )
        self.assertNotIn(
            "substantive_model_activity",
            [receipt["event_type"] for receipt in snapshot["receipts"]],
        )

    def test_live_telemetry_refreshes_state_only_after_new_receipts(self):
        module = load_script("claude_review_live_telemetry_refresh", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-refresh")
        state = {
            "live_telemetry": telemetry.snapshot(),
            "last_supported_evidence_at_epoch": 0.0,
        }

        published_total, changed = module.refresh_live_telemetry(state, telemetry, 0)
        self.assertEqual(published_total, 0)
        self.assertFalse(changed)
        self.assertEqual(state["last_supported_evidence_at_epoch"], 0.0)

        telemetry.observe(
            b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
            1.0,
        )
        published_total, changed = module.refresh_live_telemetry(state, telemetry, published_total)
        self.assertEqual(published_total, 1)
        self.assertTrue(changed)
        last_supported = state["last_supported_evidence_at_epoch"]

        published_total, changed = module.refresh_live_telemetry(state, telemetry, published_total)
        self.assertEqual(published_total, 1)
        self.assertFalse(changed)
        self.assertEqual(state["last_supported_evidence_at_epoch"], last_supported)

    def test_live_state_reassertion_detects_external_document_replacement(self):
        module = load_script("claude_review_live_state_reassertion", LAUNCHER)
        path = self.root / "live-state-reassertion.json"
        state = {"state": "running", "partial_output_exists": True}
        path.write_bytes(module.canonical_json_bytes(state))

        self.assertFalse(module.live_state_needs_reassertion(path, state))
        path.write_text('{"state":"running"}', encoding="utf-8")
        self.assertTrue(module.live_state_needs_reassertion(path, state))
        path.unlink()
        self.assertTrue(module.live_state_needs_reassertion(path, state))

    def test_live_telemetry_preserves_distinct_usage_without_event_uuid(self):
        module = load_script("claude_review_live_telemetry_usage_dedupe", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-usage")
        telemetry.observe(
            b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
            1.0,
        )
        for output_tokens in (1, 2):
            record = {
                "type": "assistant",
                "session_id": "session-1",
                "message": {
                    "id": "message-1",
                    "content": [],
                    "usage": {"input_tokens": 3, "output_tokens": output_tokens},
                },
            }
            telemetry.observe((json.dumps(record) + "\n").encode("utf-8"), float(output_tokens + 1))

        receipts = telemetry.snapshot()["receipts"]
        usage_samples = [receipt for receipt in receipts if receipt["event_type"] == "usage_sample"]
        self.assertEqual(
            [sample["metadata"]["counters"]["output_tokens"] for sample in usage_samples],
            [1, 2],
        )
        self.assertEqual(
            len([receipt for receipt in receipts if receipt["event_type"] == "substantive_model_activity"]),
            2,
        )

        duplicate_usage_record = {
            "type": "assistant",
            "session_id": "session-1",
            "message": {
                "id": "message-1",
                "content": [{"type": "text", "text": "different sensitive body"}],
                "usage": {"input_tokens": 3, "output_tokens": 2},
            },
        }
        telemetry.observe((json.dumps(duplicate_usage_record) + "\n").encode("utf-8"), 4.0)
        duplicate_event_record = {
            "type": "assistant",
            "session_id": "session-1",
            "uuid": "event-1",
            "message": {"id": "message-2", "content": [], "usage": {"output_tokens": 3}},
        }
        telemetry.observe((json.dumps(duplicate_event_record) + "\n").encode("utf-8"), 5.0)
        duplicate_event_record["message"] = {
            "id": "message-3",
            "content": [{"type": "text", "text": "another sensitive body"}],
            "usage": {"output_tokens": 4},
        }
        telemetry.observe((json.dumps(duplicate_event_record) + "\n").encode("utf-8"), 6.0)

        reasons = [
            receipt["metadata"]["reason"]
            for receipt in telemetry.snapshot()["receipts"]
            if receipt["event_type"] == "telemetry_degraded"
        ]
        self.assertIn("duplicate_usage_sample", reasons)
        self.assertIn("duplicate_event_identity", reasons)
        self.assertNotIn("different sensitive body", json.dumps(telemetry.snapshot(), sort_keys=True))
        self.assertNotIn("another sensitive body", json.dumps(telemetry.snapshot(), sort_keys=True))

    def test_live_telemetry_bounds_retention_and_preserves_terminal_tail(self):
        module = load_script("claude_review_live_telemetry_retention", LAUNCHER)
        with mock.patch.object(module, "MAX_LIVE_TELEMETRY_RECEIPTS", 6):
            telemetry = module.LiveTelemetry("attempt-bounded")
            telemetry.observe(
                b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
                1.0,
            )
            for number in range(1, 6):
                record = {
                    "type": "assistant",
                    "session_id": "session-1",
                    "message": {
                        "id": f"message-{number}",
                        "content": [],
                        "usage": {"output_tokens": number},
                    },
                }
                telemetry.observe((json.dumps(record) + "\n").encode("utf-8"), float(number + 1))
            telemetry.observe(
                b'{"type":"result","subtype":"success","session_id":"session-1","usage":{"output_tokens":6}}\n',
                7.0,
            )

            snapshot = telemetry.snapshot()

        self.assertEqual(len(snapshot["receipts"]), 6)
        self.assertGreater(snapshot["retention"]["dropped_receipts"], 0)
        self.assertEqual(snapshot["receipts"][-2]["event_type"], "provider_terminal")
        self.assertEqual(snapshot["receipts"][-1]["event_type"], "usage_sample")
        marker = snapshot["receipts"][-3]
        self.assertEqual(marker["event_type"], "telemetry_degraded")
        self.assertEqual(marker["metadata"]["reason"], "receipt_retention_limit")
        self.assertEqual(
            [receipt["monotonic_arrival_seconds"] for receipt in snapshot["receipts"]],
            sorted(receipt["monotonic_arrival_seconds"] for receipt in snapshot["receipts"]),
        )

    def test_live_telemetry_retention_pins_terminal_evidence_after_later_degradation(self):
        module = load_script("claude_review_live_telemetry_terminal_pin", LAUNCHER)
        with mock.patch.object(module, "MAX_LIVE_TELEMETRY_RECEIPTS", 6):
            telemetry = module.LiveTelemetry("attempt-terminal-pin")
            telemetry.observe(
                b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
                1.0,
            )
            for number in range(1, 6):
                record = {
                    "type": "assistant",
                    "session_id": "session-1",
                    "message": {
                        "id": f"message-{number}",
                        "content": [],
                        "usage": {"output_tokens": number},
                    },
                }
                telemetry.observe((json.dumps(record) + "\n").encode("utf-8"), float(number + 1))
            terminal = {
                "type": "result",
                "subtype": "success",
                "session_id": "session-1",
                "usage": {
                    "input_tokens": module.MAX_LIVE_TELEMETRY_USAGE_COUNTER + 1,
                    "output_tokens": 6,
                },
            }
            telemetry.observe((json.dumps(terminal) + "\n").encode("utf-8"), 7.0)
            telemetry.collector_failed(8.0)
            snapshot = telemetry.snapshot()

        terminal_tail = snapshot["receipts"][-3:]
        self.assertEqual(
            [receipt["event_type"] for receipt in terminal_tail],
            ["provider_terminal", "usage_sample", "telemetry_degraded"],
        )
        self.assertEqual(terminal_tail[-1]["metadata"], {"reason": "collector_error"})
        self.assertEqual(
            [receipt["monotonic_arrival_seconds"] for receipt in snapshot["receipts"]],
            sorted(receipt["monotonic_arrival_seconds"] for receipt in snapshot["receipts"]),
        )

    def test_synthetic_degraded_receipts_do_not_advance_stream_ordinal(self):
        module = load_script("claude_review_live_telemetry_synthetic", LAUNCHER)
        telemetry = module.LiveTelemetry("attempt-synthetic")
        telemetry.observe(
            b'{"type":"system","subtype":"init","session_id":"session-1"}\n',
            1.0,
        )
        telemetry.interpretation_failed(2.0)
        telemetry.collector_failed(3.0)

        receipts = telemetry.snapshot()["receipts"]
        self.assertEqual([receipt["stream_ordinal"] for receipt in receipts], [1, 1, 1])

    def test_live_telemetry_is_visible_before_provider_terminal_and_reconciled(self):
        config = self.write_config()
        diagnostics = self.evidence / "overall.json"
        process = subprocess.Popen(
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
                "opus",
                "--effort",
                "high",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment("live_receipts"),
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        assert process.stdin is not None
        process.stdin.write("exact review prompt\n")
        process.stdin.close()
        observed = None
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            matches = list(self.root.glob("claude-review-controller-*/*-live-state.json"))
            if matches:
                state = json.loads(matches[0].read_text(encoding="utf-8"))
                receipts = state["live_telemetry"]["receipts"]
                event_types = {receipt["event_type"] for receipt in receipts}
                if {
                    "provider_session_initialized",
                    "substantive_model_activity",
                    "source_tool_request",
                    "source_tool_completion",
                }.issubset(event_types) and process.poll() is None:
                    observed = (state, receipts)
                    break
            time.sleep(0.01)
        self.assertIsNotNone(observed)
        state, live_receipts = observed
        self.assertEqual(state["state"], "running")
        self.assertTrue(
            all(receipt["controller_attempt_id"] == state["attempt_id"] for receipt in live_receipts)
        )
        self.assertEqual(
            [receipt["monotonic_arrival_seconds"] for receipt in live_receipts],
            sorted(receipt["monotonic_arrival_seconds"] for receipt in live_receipts),
        )
        process.wait(timeout=5)
        terminal_receipt = self.receipts()[0]
        terminal_receipts = terminal_receipt["live_telemetry"]["receipts"]
        terminal_types = {receipt["event_type"] for receipt in terminal_receipts}
        self.assertIn("provider_terminal", terminal_types)
        self.assertTrue({receipt["event_type"] for receipt in live_receipts}.issubset(terminal_types))
        self.assertEqual(terminal_receipt["live_telemetry"]["retention"]["dropped_receipts"], 0)
        self.assertTrue(all(receipt in terminal_receipts for receipt in live_receipts))

    def test_provider_failure_and_auth_each_stop_after_one_explicit_attempt(self):
        exhausted, exhausted_diagnostic = self.run_governed("transient_always")
        self.assertEqual(exhausted.returncode, 70)
        self.assertEqual(exhausted_diagnostic["failure_classification"], "terminal_provider_server_error")
        self.assertEqual(len(exhausted_diagnostic["attempts"]), 1)
        self.assertFalse(exhausted_diagnostic["automated_retry_attempted"])

        auth_root = self.root / "auth-evidence"
        auth_root.mkdir()
        body = self.config_body()
        body["review_id"] = "CAK-155-auth"
        body["evidence_directory"] = str(auth_root)
        body["preflight_receipt"] = str(auth_root / "preflight-receipt.json")
        body["final_output"] = str(auth_root / "review-output.md")
        body["attempt_stream"] = str(auth_root / "attempt-stream.jsonl")
        body["attempt_terminal_receipt"] = str(auth_root / "attempt-terminal-receipt.json")
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

    def test_schema_two_rejects_obsolete_automatic_retry_fields(self):
        module = load_script("claude_review_obsolete_retry_fields", LAUNCHER)
        for obsolete_field, value in (("max_attempts", 2), ("attempt_artifacts", [])):
            body = self.config_body()
            body[obsolete_field] = value
            with self.subTest(obsolete_field=obsolete_field), self.assertRaisesRegex(
                ValueError, "one explicit provider attempt"
            ):
                module.load_governed_config(self.write_config(body))

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
                "cwd": str(self.root),
                "tool_name": "Bash",
                "tool_input": {"command": shlex.join(self.config_body()["allowed_commands"][0])},
            }
        )
        liveness_evidence = self.root / module.HOOK_LIVENESS_EVIDENCE_NAME
        command = [
            str(LAUNCHER),
            "--permission-hook",
            str(config),
            "--permission-hook-digest",
            digest,
            "--permission-hook-liveness-evidence",
            str(liveness_evidence),
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

        changed = self.config_body()
        changed["contract_id"] = "sha256:changed-fixture-contract"
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

    def test_idempotent_hook_evidence_accepts_an_identical_concurrent_winner(self):
        module = load_script("claude_review_hook_evidence_race", LAUNCHER)
        evidence_path = self.root / "hook-race-evidence.json"
        encoded = b'{"observed":true}'
        real_link = module.os.link

        def concurrent_winner(source, destination, **kwargs):
            real_link(source, destination, **kwargs)
            raise FileExistsError(destination)

        with mock.patch.object(module.os, "link", side_effect=concurrent_winner):
            module.write_idempotent_hook_evidence(evidence_path, encoded, "hook")
        self.assertEqual(evidence_path.read_bytes(), encoded)

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
            [str(LAUNCHER), "--terminate", str(live), "--termination-authority", "fixture post-exit group authority", "--grace-seconds", "1.0"],
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
        self.assertIn("git-admin:config", module.snapshot_delta(baseline, changed))

    def test_unknown_common_root_file_is_not_primary_worktree_administration(self):
        module = load_script("claude_review_primary_unknown", LAUNCHER)
        environment = os.environ.copy()
        _, linked = self.use_linked_candidate("fixture-primary-unknown")
        common = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--git-common-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        baseline = module.source_snapshot([linked], linked, environment)
        unknown = common / "fixture-primary-observation"
        unknown.write_text("not Git-managed primary state\n", encoding="utf-8")
        changed = module.source_snapshot([linked], linked, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        record = next(record for record in comparison["git_admin_changes"] if record["path"] == unknown.name)
        self.assertEqual(record["classification"], "blocking_ambiguous_shared_administration")

    def test_live_primary_worktree_commit_passes_for_a_linked_candidate(self):
        self.use_linked_candidate("fixture-live-primary")
        body = self.config_body()
        # Observe the completed Git operation, not its deliberately blocking transient lock.
        body["observation_interval_seconds"] = 0.5
        completed, diagnostic = self.run_governed("primary_worktree_commit_then_wait", body=body)
        self.assertEqual(completed.returncode, 0, diagnostic)
        receipt = self.receipts()[0]
        self.assertTrue(receipt["no_delta_postflight"]["passed"])
        self.assertTrue(
            any(
                record["owner_scope"] == "other_primary_worktree" and record["disposition"] == "tolerated"
                for record in receipt["no_delta_postflight"]["git_admin_changes"]
            )
        )

    def test_primary_worktree_activity_does_not_hide_linked_candidate_mutation(self):
        self.use_linked_candidate("fixture-primary-mixed")
        completed, diagnostic = self.run_governed(
            "primary_worktree_and_candidate_mutation",
            body=self.config_body(),
        )
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")
        receipt = self.receipts()[0]
        self.assertEqual(receipt["lifecycle"]["emergency_condition"], "unauthorized_mutation")
        self.assertTrue(any(path.endswith(":tracked.txt") for path in receipt["no_delta_postflight"]["changed_paths"]))

    def test_network_free_unrelated_push_activity_is_tolerated(self):
        module = load_script("claude_review_unrelated_push", LAUNCHER)
        environment = os.environ.copy()
        remote = self.root / "remote.git"
        linked = self.root / "push-worktree"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        subprocess.run(["git", "-C", str(self.candidate), "remote", "add", "fixture", str(remote)], check=True)
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-push", str(linked)],
            check=True,
        )
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        (linked / "tracked.txt").write_text("pushed commit\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(linked), "add", "tracked.txt"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(linked),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "push fixture",
            ],
            check=True,
        )
        subprocess.run(["git", "-C", str(linked), "push", "-q", "fixture", "HEAD:refs/heads/fixture-push"], check=True)
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertTrue(comparison["passed"], comparison)
        self.assertTrue(comparison["tolerated_paths"])

    def test_safe_command_environment_disables_background_maintenance(self):
        module = load_script("claude_review_maintenance_env", LAUNCHER)
        environment = module.safe_command_environment(os.environ.copy(), self.root)
        declared = int(environment["GIT_CONFIG_COUNT"])
        pairs = {
            environment[f"GIT_CONFIG_KEY_{index}"]: environment[f"GIT_CONFIG_VALUE_{index}"]
            for index in range(declared)
        }
        # Git silently ignores pairs beyond GIT_CONFIG_COUNT, so a stale count
        # would disable these settings without producing any error.
        self.assertEqual(len(pairs), declared)
        self.assertEqual(pairs["maintenance.auto"], "false")
        self.assertEqual(pairs["gc.auto"], "0")

    def test_git_worktree_capability_probe_reports_named_causes(self):
        module = load_script("claude_review_git_capability", LAUNCHER)
        environment = os.environ.copy()
        environment["PATH"] = "/usr/bin:/bin"

        # A Git supporting the required switch clears the probe.
        self.assertIsNone(module.git_worktree_capability_error(self.candidate, environment))

        # The caller has no exception handling around this probe, so an absent
        # or untrusted Git must return a named cause rather than raise. It is
        # also not a capability gap, so it keeps the ordinary command-preflight
        # classification.
        absent = module.git_worktree_capability_error(
            self.candidate, {"PATH": str(self.root / "absent")}
        )
        self.assertIsNotNone(absent)
        classification, cause = absent
        self.assertEqual(classification, "access_or_command_preflight_failure")
        self.assertIn("git", cause)

    def test_git_probe_does_not_blame_the_git_version_for_other_failures(self):
        # A nonzero exit is not evidence of an unsupported switch. Config
        # loading only requires the candidate to be an existing directory, so a
        # non-repository reaches this probe and previously produced the
        # self-contradicting claim that a supported Git was too old.
        module = load_script("claude_review_git_non_repository", LAUNCHER)
        environment = os.environ.copy()
        environment["PATH"] = "/usr/bin:/bin"
        non_repository = self.root / "not-a-repository"
        non_repository.mkdir()

        failure = module.git_worktree_capability_error(non_repository, environment)
        self.assertIsNotNone(failure)
        classification, cause = failure
        self.assertEqual(classification, "access_or_command_preflight_failure")
        self.assertNotIn("does not support", cause)
        self.assertIn("is not a capability gap", cause)

    def test_arbitrary_other_linked_worktree_administration_is_blocking(self):
        module = load_script("claude_review_other_worktree_admin", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "admin-worktree"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-admin", str(linked)],
            check=True,
        )
        common = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--git-common-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        gitdir = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--absolute-git-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        self.assertTrue(gitdir.is_relative_to(common / "worktrees"))
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        (gitdir / "fixture-observation").write_text("other worktree\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        record = next(record for record in comparison["git_admin_changes"] if record["path"].endswith("fixture-observation"))
        self.assertEqual(record["owner_scope"], "other_linked_worktree")
        self.assertEqual(record["classification"], "blocking_unknown_other_worktree_administration")
        self.assertEqual(record["disposition"], "blocking")

    def test_other_linked_worktree_git_managed_admin_creation_is_provisional(self):
        module = load_script("claude_review_worktree_admin_creation", LAUNCHER)
        environment = os.environ.copy()

        # exact_other_worktree_admin resolves any worktree present in both
        # snapshots, because worktree_admin_identity records every
        # WORKTREE_ADMIN_PATHS key unconditionally — absent files simply carry a
        # None identity. Reaching the fallback therefore requires a worktree
        # that the baseline snapshot does not know about at all, which is what
        # adding it after the baseline produces.
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        linked = self.root / "provisional-admin-worktree"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-provisional", str(linked)],
            check=True,
        )
        gitdir = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--absolute-git-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        (gitdir / "COMMIT_EDITMSG").write_text("fixture\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)

        # A Git-managed per-worktree administration file cannot yet be
        # attributed to that worktree's HEAD transition. It stays blocking, but
        # is eligible for the bounded window rather than triggering an
        # immediate emergency stop on an intermediate observation.
        admin_record = next(
            record
            for record in comparison["git_admin_changes"]
            if record["path"].endswith("COMMIT_EDITMSG")
        )
        self.assertEqual(
            admin_record["classification"], "blocking_unattributed_other_worktree_administration"
        )
        self.assertEqual(admin_record["disposition"], "blocking")
        self.assertEqual(
            admin_record["evidence"]["provisional_attribution"],
            "worktree_transition_not_yet_observed",
        )

        # Adding a worktree also writes files that are not Git-managed
        # per-worktree administration, such as gitdir and commondir. Those are
        # not eligible, which both proves the predicate is exact and means this
        # observation as a whole is not deferrable.
        non_admin = [
            record
            for record in comparison["git_admin_changes"]
            if record["path"].startswith("worktrees/")
            and record["classification"] == "blocking_unknown_other_worktree_administration"
        ]
        self.assertTrue(non_admin)
        self.assertFalse(module.provisional_attribution_only(comparison))
        self.assertFalse(comparison["passed"])

        # An arbitrary planted file under the same worktree is likewise never
        # eligible, so it cannot buy itself a window.
        (gitdir / "fixture-observation").write_text("planted\n", encoding="utf-8")
        contaminated = module.source_snapshot([self.candidate], self.candidate, environment)
        planted = next(
            record
            for record in module.snapshot_comparison(
                baseline, contaminated
            )["git_admin_changes"]
            if record["path"].endswith("fixture-observation")
        )
        self.assertEqual(planted["classification"], "blocking_unknown_other_worktree_administration")
        self.assertEqual(planted["disposition"], "blocking")

    def test_other_linked_worktree_lock_is_bounded_provisional_activity(self):
        module = load_script("claude_review_other_worktree_lock", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "lock-worktree"
        subprocess.run(
            [
                "git",
                "-C",
                str(self.candidate),
                "worktree",
                "add",
                "-q",
                "-b",
                "fixture-lock",
                str(linked),
            ],
            check=True,
        )
        gitdir = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--absolute-git-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        lock = gitdir / "index.lock"
        lock.write_text("in-progress unrelated commit\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        record = next(
            record
            for record in comparison["git_admin_changes"]
            if record["path"].endswith("index.lock")
        )
        self.assertEqual(
            record["classification"],
            "blocking_unattributed_other_worktree_administration",
        )
        self.assertEqual(record["disposition"], "blocking")
        self.assertTrue(module.provisional_attribution_only(comparison))

    def test_unprotected_ref_lock_is_bounded_provisional_activity(self):
        module = load_script("claude_review_unprotected_ref_lock", LAUNCHER)
        environment = os.environ.copy()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        common = Path(
            subprocess.run(
                ["git", "-C", str(self.candidate), "rev-parse", "--git-common-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        )
        if not common.is_absolute():
            common = self.candidate / common
        common = common.resolve()
        lock = common / "refs" / "heads" / "unrelated.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text("in-progress unrelated ref update\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        record = next(
            record
            for record in comparison["git_admin_changes"]
            if record["path"] == "refs/heads/unrelated.lock"
        )
        self.assertEqual(
            record["classification"],
            "blocking_unattributed_unrelated_ref_administration",
        )
        self.assertEqual(record["disposition"], "blocking")
        self.assertTrue(module.provisional_attribution_only(comparison))

    def test_unrelated_linked_commit_with_arbitrary_admin_contamination_is_blocking(self):
        module = load_script("claude_review_other_worktree_mixed_admin", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "mixed-admin-worktree"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-mixed-admin", str(linked)],
            check=True,
        )
        gitdir = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--absolute-git-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        self.commit_tracked(linked, "unrelated plus contamination\n", "mixed admin")
        contamination = gitdir / "fixture-contamination"
        contamination.write_text("reviewer contamination\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        contamination_record = next(
            record for record in comparison["git_admin_changes"] if record["path"].endswith(contamination.name)
        )
        self.assertEqual(contamination_record["classification"], "blocking_unknown_other_worktree_administration")
        self.assertTrue(any(record["disposition"] == "tolerated" for record in comparison["git_admin_changes"]))

    def test_unknown_other_worktree_path_identity_changes_remain_blocking(self):
        module = load_script("claude_review_other_worktree_identity_shapes", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "identity-shape-worktree"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-admin-shapes", str(linked)],
            check=True,
        )
        gitdir = Path(
            subprocess.run(
                ["git", "-C", str(linked), "rev-parse", "--absolute-git-dir"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        ).resolve()
        path = gitdir / "fixture-unknown"

        def assert_blocking(baseline):
            changed = module.source_snapshot([self.candidate], self.candidate, environment)
            record = next(
                record
                for record in module.snapshot_comparison(baseline, changed)["git_admin_changes"]
                if record["path"].endswith(path.name)
            )
            self.assertEqual(record["classification"], "blocking_unknown_other_worktree_administration")
            self.assertEqual(record["disposition"], "blocking")

        with self.subTest(change="addition"):
            baseline = module.source_snapshot([self.candidate], self.candidate, environment)
            path.write_text("added\n", encoding="utf-8")
            assert_blocking(baseline)
            path.unlink()
        with self.subTest(change="removal"):
            path.write_text("remove\n", encoding="utf-8")
            baseline = module.source_snapshot([self.candidate], self.candidate, environment)
            path.unlink()
            assert_blocking(baseline)
        with self.subTest(change="content"):
            path.write_text("before\n", encoding="utf-8")
            baseline = module.source_snapshot([self.candidate], self.candidate, environment)
            path.write_text("after\n", encoding="utf-8")
            assert_blocking(baseline)
            path.unlink()
        with self.subTest(change="mode"):
            path.write_text("mode\n", encoding="utf-8")
            path.chmod(0o600)
            baseline = module.source_snapshot([self.candidate], self.candidate, environment)
            path.chmod(0o644)
            assert_blocking(baseline)
            path.unlink()
        with self.subTest(change="replacement"):
            path.write_text("file\n", encoding="utf-8")
            baseline = module.source_snapshot([self.candidate], self.candidate, environment)
            path.unlink()
            path.mkdir()
            assert_blocking(baseline)
            path.rmdir()
        with self.subTest(change="symlink"):
            path.write_text("file\n", encoding="utf-8")
            baseline = module.source_snapshot([self.candidate], self.candidate, environment)
            path.unlink()
            path.symlink_to(gitdir / "HEAD")
            assert_blocking(baseline)
            path.unlink()

    def test_protected_remote_ref_and_candidate_branch_reflog_remain_blocking(self):
        module = load_script("claude_review_protected_refs", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "protected-ref-worktree"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-ref-source", str(linked)],
            check=True,
        )
        subprocess.run(["git", "-C", str(self.candidate), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        commands = (
            (
                "git",
                "-C",
                str(self.candidate),
                "diff",
                "--no-ext-diff",
                "--no-textconv",
                "origin/main...HEAD",
            ),
        )
        baseline = module.source_snapshot([self.candidate], self.candidate, environment, commands)
        (linked / "tracked.txt").write_text("new protected target\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(linked), "add", "tracked.txt"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(linked),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "new target",
            ],
            check=True,
        )
        linked_head = subprocess.run(
            ["git", "-C", str(linked), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        subprocess.run(
            ["git", "-C", str(self.candidate), "update-ref", "refs/remotes/origin/main", linked_head], check=True
        )
        changed = module.source_snapshot([self.candidate], self.candidate, environment, commands)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        remote_record = next(
            record for record in comparison["git_admin_changes"] if record["path"] == "refs/remotes/origin/main"
        )
        self.assertEqual(remote_record["classification"], "blocking_protected_ref_or_reflog")

        branch = subprocess.run(
            ["git", "-C", str(self.candidate), "symbolic-ref", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        subprocess.run(["git", "-C", str(self.candidate), "update-ref", branch, linked_head], check=True)
        branch_changed = module.source_snapshot([self.candidate], self.candidate, environment, commands)
        branch_comparison = module.snapshot_comparison(baseline, branch_changed)
        self.assertFalse(branch_comparison["passed"])
        self.assertTrue(
            any(
                record["path"] in {branch, f"logs/{branch}"}
                and record["classification"] == "blocking_protected_ref_or_reflog"
                for record in branch_comparison["git_admin_changes"]
            )
        )

    def test_semantic_object_lookup_controls_remain_fail_closed(self):
        module = load_script("claude_review_object_controls", LAUNCHER)
        environment = os.environ.copy()
        alternate = self.root / "alternate.git"
        subprocess.run(["git", "init", "--bare", "-q", str(alternate)], check=True)
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        alternates = self.candidate / ".git" / "objects" / "info" / "alternates"
        alternates.write_text(f"{alternate / 'objects'}\n", encoding="utf-8")
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        record = next(record for record in comparison["git_admin_changes"] if record["path"] == "objects/info/alternates")
        self.assertEqual(record["owner_scope"], "ambiguous_shared_administration")
        self.assertEqual(record["disposition"], "blocking")

        alternates.unlink()
        for relative, content in (
            ("info/grafts", f"{subprocess.run(['git', '-C', str(self.candidate), 'rev-parse', 'HEAD'], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()}\n"),
            ("shallow", f"{subprocess.run(['git', '-C', str(self.candidate), 'rev-parse', 'HEAD'], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()}\n"),
        ):
            with self.subTest(control=relative):
                control_baseline = module.source_snapshot([self.candidate], self.candidate, environment)
                control = self.candidate / ".git" / relative
                control.parent.mkdir(parents=True, exist_ok=True)
                control.write_text(content, encoding="utf-8")
                control_changed = module.source_snapshot([self.candidate], self.candidate, environment)
                control_comparison = module.snapshot_comparison(control_baseline, control_changed)
                self.assertFalse(control_comparison["passed"])
                self.assertIn(f"git-admin:{relative}", control_comparison["blocking_paths"])
                control.unlink()

        head = subprocess.run(
            ["git", "-C", str(self.candidate), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        object_path = self.candidate / ".git" / "objects" / head[:2] / head[2:]
        object_bytes = object_path.read_bytes()
        object_mode = object_path.stat().st_mode
        object_path.unlink()
        try:
            with self.assertRaisesRegex(
                RuntimeError,
                "Git identity observation|protected Git object observation|shared Git reachability observation",
            ):
                module.source_snapshot([self.candidate], self.candidate, environment)
        finally:
            object_path.write_bytes(object_bytes)
            object_path.chmod(object_mode)

    def test_candidate_head_mode_and_symlink_identity_remain_blocking(self):
        module = load_script("claude_review_candidate_identity", LAUNCHER)
        environment = os.environ.copy()
        branch = subprocess.run(
            ["git", "-C", str(self.candidate), "symbolic-ref", "--short", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        subprocess.run(["git", "-C", str(self.candidate), "checkout", "-q", "--detach"], check=True)
        detached = module.source_snapshot([self.candidate], self.candidate, environment)
        head_comparison = module.snapshot_comparison(baseline, detached)
        self.assertFalse(head_comparison["passed"])
        self.assertIn("git-admin:HEAD", head_comparison["blocking_paths"])

        subprocess.run(["git", "-C", str(self.candidate), "checkout", "-q", branch], check=True)
        mode_baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        tracked = self.candidate / "tracked.txt"
        tracked.chmod(0o755)
        mode_changed = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn(f"{self.candidate}:tracked.txt", module.snapshot_delta(mode_baseline, mode_changed))

        tracked.chmod(0o644)
        symlink = self.candidate / "candidate-link"
        symlink.symlink_to("tracked.txt")
        symlink_baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        symlink.unlink()
        symlink.symlink_to(".gitignore")
        symlink_changed = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn(f"{self.candidate}:candidate-link", module.snapshot_delta(symlink_baseline, symlink_changed))

    def test_replacement_ref_contamination_is_blocking(self):
        module = load_script("claude_review_replace_ref", LAUNCHER)
        environment = os.environ.copy()
        linked = self.root / "replace-worktree"
        subprocess.run(
            ["git", "-C", str(self.candidate), "worktree", "add", "-q", "-b", "fixture-replace", str(linked)],
            check=True,
        )
        (linked / "tracked.txt").write_text("replacement object\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(linked), "add", "tracked.txt"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(linked),
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "replacement object",
            ],
            check=True,
        )
        replacement = subprocess.run(
            ["git", "-C", str(linked), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        head = subprocess.run(
            ["git", "-C", str(self.candidate), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        subprocess.run(["git", "-C", str(self.candidate), "replace", head, replacement], check=True)
        changed = module.source_snapshot([self.candidate], self.candidate, environment)
        comparison = module.snapshot_comparison(baseline, changed)
        self.assertFalse(comparison["passed"])
        record = next(
            record for record in comparison["git_admin_changes"] if record["path"] == f"refs/replace/{head}"
        )
        self.assertEqual(record["classification"], "blocking_protected_ref_or_reflog")

    def test_live_unrelated_worktree_commit_passes_and_records_tolerated_changes(self):
        self.other_worktree = self.root / "live-unrelated-worktree"
        subprocess.run(
            [
                "git",
                "-C",
                str(self.candidate),
                "worktree",
                "add",
                "-q",
                "-b",
                "fixture-live-unrelated",
                str(self.other_worktree),
            ],
            check=True,
        )
        completed, diagnostic = self.run_governed("unrelated_worktree_commit_then_wait", body=self.config_body())
        receipts = self.receipts()
        self.assertEqual(completed.returncode, 0, {"diagnostic": diagnostic, "receipts": receipts})
        self.assertIsNone(diagnostic["failure_classification"])
        receipt = receipts[0]
        self.assertTrue(receipt["no_delta_postflight"]["passed"])
        self.assertEqual(receipt["no_delta_postflight"]["changed_paths"], [])
        self.assertTrue(receipt["no_delta_postflight"]["raw_changed_paths"])
        self.assertTrue(receipt["no_delta_postflight"]["tolerated_changed_paths"])
        self.assertTrue(receipt["no_delta_postflight"]["live_observed_tolerated_changed_paths"])
        self.assertTrue(receipt["no_delta_postflight"]["git_admin_changes"])
        for record in receipt["no_delta_postflight"]["git_admin_changes"]:
            self.assertTrue(
                {
                    "path",
                    "git_directory",
                    "owner_scope",
                    "change_type",
                    "before",
                    "after",
                    "classification",
                    "evidence",
                    "disposition",
                }
                <= set(record)
            )
            self.assertFalse(record["path"].startswith("git-admin"))
        self.assertNotIn("emergency_condition", receipt["lifecycle"])

    def test_live_unattributed_object_write_remains_fail_closed_after_stabilization(self):
        completed, diagnostic = self.run_governed("unattributed_object_then_wait", body=self.config_body())
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")
        receipt = self.receipts()[0]
        self.assertEqual(receipt["lifecycle"]["emergency_condition"], "unauthorized_mutation")
        self.assertTrue(
            any(
                record["classification"] == "blocking_ambiguous_shared_administration"
                and record["path"].startswith("objects/")
                for record in receipt["no_delta_postflight"]["git_admin_changes"]
            )
        )

    def test_governed_review_creates_no_local_or_cross_attempt_state(self):
        self.isolated_home = self.root / "isolated-home"
        self.isolated_home.mkdir()
        completed, diagnostic = self.run_governed("success", body=self.config_body())
        self.assertEqual(completed.returncode, 0)
        self.assertIsNone(diagnostic["failure_classification"])
        receipt = self.receipts()[0]
        self.assertEqual(receipt["runtime"]["HOME"], str(self.isolated_home.resolve()))
        self.assertFalse((self.isolated_home / ".local").exists())
        self.assertFalse((self.isolated_home / ".cache").exists())
        self.assertFalse((self.isolated_home / ".config").exists())

    def test_fixture_effective_home_override_is_ignored_outside_explicit_fixture_execution(self):
        module = load_script("claude_review_fixture_home_boundary", LAUNCHER)
        self.isolated_home = self.root / "isolated-home-negative"
        self.isolated_home.mkdir()
        account_home = pwd.getpwuid(os.geteuid()).pw_dir
        selected = module.effective_home_for_execution(
            account_home,
            {"CLAUDE_REVIEW_TEST_EFFECTIVE_HOME": str(self.isolated_home)},
            explicit_test_fixture=False,
        )
        self.assertEqual(selected, account_home)

    def test_unrelated_activity_does_not_hide_simultaneous_candidate_mutation(self):
        self.other_worktree = self.root / "mixed-mutation-worktree"
        subprocess.run(
            [
                "git",
                "-C",
                str(self.candidate),
                "worktree",
                "add",
                "-q",
                "-b",
                "fixture-mixed-mutation",
                str(self.other_worktree),
            ],
            check=True,
        )
        completed, diagnostic = self.run_governed(
            "unrelated_worktree_and_candidate_mutation", body=self.config_body()
        )
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(diagnostic["failure_classification"], "reviewer_side_effect_failure")
        receipt = self.receipts()[0]
        self.assertFalse(receipt["no_delta_postflight"]["passed"])
        self.assertTrue(any(path.endswith(":tracked.txt") for path in receipt["no_delta_postflight"]["changed_paths"]))
        self.assertEqual(receipt["lifecycle"]["emergency_condition"], "unauthorized_mutation")

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
                self.assertIn(f"git-admin:{lock.relative_to(git_directory)}", module.snapshot_delta(baseline, changed))
                lock.unlink()

        preexisting = git_directory / "preexisting.lock"
        preexisting.write_text("original\n", encoding="utf-8")
        baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        unchanged = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertEqual(module.snapshot_delta(baseline, unchanged), [])
        preexisting.unlink()
        removed = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn("git-admin:preexisting.lock", module.snapshot_delta(baseline, removed))
        preexisting.write_text("replacement\n", encoding="utf-8")
        replaced = module.source_snapshot([self.candidate], self.candidate, environment)
        self.assertIn("git-admin:preexisting.lock", module.snapshot_delta(baseline, replaced))

        preexisting.write_text("original\n", encoding="utf-8")
        preexisting.chmod(0o600)
        mode_baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        preexisting.chmod(0o644)
        mode_changed = module.source_snapshot([self.candidate], self.candidate, environment)
        mode_record = next(
            record
            for record in module.snapshot_comparison(mode_baseline, mode_changed)["git_admin_changes"]
            if record["path"] == "preexisting.lock"
        )
        self.assertEqual(mode_record["change_type"], "mode_changed")
        self.assertEqual(mode_record["disposition"], "blocking")

        preexisting.unlink()
        symlink_baseline = module.source_snapshot([self.candidate], self.candidate, environment)
        preexisting.symlink_to(self.candidate / "tracked.txt")
        symlink_changed = module.source_snapshot([self.candidate], self.candidate, environment)
        symlink_record = next(
            record
            for record in module.snapshot_comparison(symlink_baseline, symlink_changed)["git_admin_changes"]
            if record["path"] == "preexisting.lock"
        )
        self.assertEqual(symlink_record["change_type"], "added")
        self.assertEqual(symlink_record["classification"], "blocking_lock_change")

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
                self.assertIn(f"git-admin:{lock.relative_to(common_directory)}", module.snapshot_delta(baseline, changed))
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
        self.assertIn(
            f"git-admin:{additional.resolve()}:config.lock",
            module.snapshot_delta(baseline, changed),
        )

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
        self.assertIn("git-admin:index.lock", receipt["no_delta_postflight"]["changed_paths"])

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
