import json
import os
from pathlib import Path
import pwd
import subprocess
import tempfile
import textwrap
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
            command.extend(("--", "--model", "opus", "--effort", "high", "--tools", "Read"))
            completed = subprocess.run(
                command,
                check=False,
                input="review prompt that must not enter argv\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment or os.environ.copy(),
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
            )

        self.assertEqual(completed.returncode, 0)

    def test_argv_diagnostics_redact_credential_values(self):
        import importlib.machinery
        import importlib.util

        loader = importlib.machinery.SourceFileLoader("claude_review", str(LAUNCHER))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
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


if __name__ == "__main__":
    unittest.main()
