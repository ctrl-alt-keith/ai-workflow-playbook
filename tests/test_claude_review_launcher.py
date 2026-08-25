import json
import os
from pathlib import Path
import pwd
import shlex
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "claude-review"


class ClaudeReviewLauncherTests(unittest.TestCase):
    def run_launcher(
        self,
        fake_body: str,
        *,
        auth_preflight: bool = False,
        environment: dict[str, str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            fake_claude = temporary / "fake-claude"
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
                command.append("--auth-preflight")
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

    def test_auth_preflight_retains_equals_form_model_and_effort(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            fake_claude = temporary / "fake-claude"
            fake_claude.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "if '--version' in sys.argv: raise SystemExit(0)\n"
                "assert '--model=opus' in sys.argv\n"
                "assert '--effort=high' in sys.argv\n"
                "print('CLAUDE_AUTH_OK')\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            completed = subprocess.run(
                [str(LAUNCHER), "--claude-bin", str(fake_claude), "--auth-preflight", "--", "--model=opus", "--effort=high"],
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
        self.fake = self.root / "fake-claude"
        self.fake.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, signal, subprocess, sys, time\n"
            "if '--version' in sys.argv:\n"
            "    print('fake-claude 2.1.241')\n"
            "    raise SystemExit(0)\n"
            "prompt = sys.stdin.read()\n"
            "count = pathlib.Path(os.environ['FAKE_COUNT'])\n"
            "attempt = int(count.read_text()) + 1 if count.exists() else 1\n"
            "count.write_text(str(attempt))\n"
            "scenario = os.environ.get('FAKE_SCENARIO', 'success')\n"
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
            "if scenario == 'new_ignored': (candidate / 'generated.cache').write_text('cache')\n"
            "if scenario == 'remove_untracked': (candidate / 'preexisting.txt').unlink()\n"
            "if scenario == 'index_mutation':\n"
            "    (candidate / 'tracked.txt').write_text('staged\\n')\n"
            "    subprocess.run(['git','-C',str(candidate),'add','tracked.txt'], check=True)\n"
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
            "    signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "    time.sleep(10)\n"
            "if scenario == 'hang_after_transient':\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':'server_error'}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
            "    time.sleep(10)\n"
            "if scenario in {'transient_once','transient_always','transient_with_lingering_child'} and (scenario == 'transient_always' or attempt == 1):\n"
            "    print(json.dumps({'type':'system','subtype':'api_retry','session_id':f's{attempt}','error':'server_error'}), flush=True)\n"
            "    print(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'session_id':f's{attempt}'}), flush=True)\n"
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
                "--review-config",
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
        return completed, json.loads(diagnostics.read_text(encoding="utf-8"))

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

    def test_lingering_process_group_blocks_retry_until_terminal(self):
        completed, diagnostic = self.run_governed("transient_with_lingering_child")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(len(diagnostic["attempts"]), 2)
        receipts = self.receipts()
        self.assertTrue(all(receipt["lifecycle"]["process_group_terminal"] for receipt in receipts))
        self.assertTrue(all(receipt["stream_evidence"]["collectors_complete"] for receipt in receipts))
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
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config", str(config), "--", "--model", "opus", "--effort", "high"],
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
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config", str(config), "--", "--model", "opus", "--effort", "high"],
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
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config", str(config), "--", "--model", "opus", "--effort", "high"],
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
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config", str(config), "--", "--model", "opus", "--effort", "high"],
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
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config", str(config), "--", "--model", "opus", "--effort", "high"],
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
            [str(LAUNCHER), "--claude-bin", str(self.fake), "--diagnostics-file", str(diagnostics), "--review-config", str(config), "--", "--model", "opus", "--effort", "high"],
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


if __name__ == "__main__":
    unittest.main()
