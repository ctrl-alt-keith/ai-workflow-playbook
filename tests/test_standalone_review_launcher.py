"""Behavioral coverage of artifact targets through both shipped wrappers."""

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from launcher_support import ROOT, current_commit
import test_claude_review_launcher as claude_tests
import test_codex_review_launcher as codex_tests


class StandaloneReviewLauncherTests(unittest.TestCase):
    def run_case(self, provider, root, *args, prompt=b""):
        if provider == "claude":
            binary = claude_tests.ClaudeReviewLauncherTests().make_fake_claude(root, "cat\n")
            command = [str(ROOT / "scripts/claude-review"), "--claude-bin", str(binary)]
        else:
            binary = codex_tests.CodexReviewLauncherTests().make_fake_codex(root, 'cat > "$out"\n')
            command = [str(ROOT / "scripts/codex-review"), "--codex-bin", str(binary)]
        command.extend(args)
        if provider == "codex":
            command.extend(codex_tests.TERRA)
        return subprocess.run(command, cwd=root, input=prompt, capture_output=True, check=False)

    def test_standalone_artifact_is_primary_candidate_without_git(self):
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                content = b"Architecture proposal CAK-344\n"
                artifact = root / "proposal.md"
                artifact.write_bytes(content)
                digest = hashlib.sha256(content).hexdigest()
                request = root / "request.txt"
                request.write_bytes(b"Review this proposal.\n")
                request_digest = hashlib.sha256(request.read_bytes()).hexdigest()
                diagnostics = root / "diagnostics.json"
                output = root / "review.txt"
                result = self.run_case(provider, root, "--candidate-artifact", str(artifact),
                                       "--candidate-sha256", digest, "--diagnostics-file", str(diagnostics),
                                       "--review-request-file", str(request),
                                       "--review-request-sha256", request_digest,
                                       "--review-output-file", str(output))
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                record = json.loads(diagnostics.read_text())
                self.assertEqual(record["candidate"], {"kind": "immutable_artifact", "path": str(artifact),
                                                       "byte_length": len(content), "sha256": digest})
                self.assertEqual(record["target_kind"], "immutable_artifact")
                self.assertEqual(record["review_request"], {"path": str(request),
                                                            "byte_length": len(request.read_bytes()),
                                                            "sha256": request_digest})
                self.assertIn(content, output.read_bytes())
                self.assertIn(b"Review question:\nReview this proposal.", output.read_bytes())
                self.assertNotIn(b"HEAD commit at launch", output.read_bytes())

    def test_missing_conflicting_and_mismatched_target_fail(self):
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                artifact = root / "proposal.md"
                artifact.write_text("review me")
                digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
                request = root / "request.txt"
                request.write_text("Review the artifact")
                request_digest = hashlib.sha256(request.read_bytes()).hexdigest()
                request_args = ("--review-request-file", str(request),
                                "--review-request-sha256", request_digest)
                cases = [
                    ((), b"review target"),
                    (("--candidate-artifact", str(artifact)), b"--candidate-sha256"),
                    (("--candidate-sha256", digest), b"--candidate-artifact"),
                    (("--candidate-artifact", str(artifact), "--candidate-sha256", "0" * 64,
                      *request_args), b"mismatch"),
                    (("--candidate-artifact", str(artifact), "--candidate-sha256", digest,
                      *request_args, "--candidate-commit", current_commit()), b"mutually exclusive"),
                    (("--candidate-artifact", str(artifact), "--candidate-sha256", digest),
                     b"--review-request-file"),
                    (("--candidate-artifact", str(artifact), "--candidate-sha256", digest,
                      "--review-request-file", str(request)), b"--review-request-sha256"),
                    (("--candidate-artifact", str(artifact), "--candidate-sha256", digest,
                      "--review-request-file", str(request), "--review-request-sha256", "0" * 64),
                     b"review request SHA-256 mismatch"),
                    (("--candidate-artifact", str(artifact), "--candidate-artifact", str(artifact),
                      "--candidate-sha256", digest, *request_args), b"may be provided only once"),
                ]
                for arguments, message in cases:
                    with self.subTest(arguments=arguments):
                        result = self.run_case(provider, root, *arguments)
                        self.assertEqual(result.returncode, 70)
                        self.assertIn(message, result.stderr)
                with self.subTest(arguments="nonempty stdin"):
                    result = self.run_case(provider, root, "--candidate-artifact", str(artifact),
                                           "--candidate-sha256", digest, *request_args,
                                           prompt=b"unbound conversational request")
                    self.assertEqual(result.returncode, 70)
                    self.assertIn(b"standard input must be empty", result.stderr)

    def test_repository_mismatch_still_fails(self):
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                result = self.run_case(provider, root, "--candidate-commit", current_commit(),
                                       prompt=b"Review repository candidate.\n")
                self.assertEqual(result.returncode, 70)
                self.assertIn(b"not a readable Git worktree", result.stderr)
