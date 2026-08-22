"""Test-only qualification harness for CAK-154 Phase A.

Official Claude Code documentation checked 2026-08-22 says stream-json is
newline-delimited JSON, ends with a ``result`` event, and can emit
``system/api_retry``.  It does not make this fixture's exact payload fields a
production compatibility promise.  The fixture deliberately uses only
synthetic values and projects events into bounded, payload-free evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest


EVENT_TIMEOUT = 1.0
CHILD_TIMEOUT = 1.0
MAX_RETAINED_EVENTS = 3


def write_record(record: object) -> None:
    print(json.dumps(record, separators=(",", ":")), flush=True)


def fake_child(scenario: str, ready: Path, release: Path) -> int:
    """Emit synthetic JSONL and use files solely as an explicit test barrier."""
    records: dict[str, list[object]] = {
        "normal": [
            {"type": "system", "subtype": "init", "session_id": "session-synthetic"},
            {"type": "stream_event", "uuid": "event-1", "event": {"type": "message_delta", "usage": {"output_tokens": 2}}},
            {"type": "stream_event", "uuid": "event-2", "event": {"type": "content_block_start", "content_block": {"type": "tool_use", "name": "Read", "input": {"secret": "never-retain"}}}},
            {"type": "system", "subtype": "api_retry", "attempt": 1},
            {"type": "tool_result", "tool_name": "Read", "result": "never-retain"},
            {"type": "result", "session_id": "session-synthetic", "usage": {"output_tokens": 7}, "result": "never-retain"},
        ],
        "unknown": [
            {"type": "system", "subtype": "init", "session_id": "session-synthetic"},
            {"type": "new_unrecognized_type", "prompt": "never-retain"},
            {"type": "result", "usage": {"output_tokens": 7}, "result": "never-retain"},
        ],
        "duplicate": [
            {"type": "system", "subtype": "init", "session_id": "session-synthetic"},
            {"type": "stream_event", "uuid": "event-1", "event": {"type": "message_start"}},
            {"type": "stream_event", "uuid": "event-1", "event": {"type": "message_start"}},
            {"type": "result", "usage": {"output_tokens": 7}},
        ],
        "no-final": [{"type": "system", "subtype": "init", "session_id": "session-synthetic"}],
        "failure": [
            {"type": "system", "subtype": "init", "session_id": "session-synthetic"},
            {"type": "system", "subtype": "api_retry", "attempt": 1},
            {"type": "system", "subtype": "api_retry", "attempt": 2, "exhausted": True},
            {"type": "result", "is_error": True, "error": "never-retain"},
        ],
        "noisy": [
            {"type": "system", "subtype": "init", "session_id": "session-synthetic"},
            *[{"type": "stream_event", "uuid": f"event-{index}", "event": {"type": "message_delta", "usage": {"output_tokens": index}}} for index in range(20)],
            {"type": "result", "usage": {"output_tokens": 20}},
        ],
    }
    if scenario == "malformed":
        print('{"type":', flush=True)
        return 0
    if scenario == "truncated":
        sys.stdout.write('{"type":"result"')
        sys.stdout.flush()
        return 0
    if scenario == "silent":
        ready.write_text("ready", encoding="utf-8")
        return wait_for_release(release)

    selected = records[scenario]
    write_record(selected[0])
    ready.write_text("ready", encoding="utf-8")
    if wait_for_release(release) != 0:
        return 1
    for record in selected[1:]:
        write_record(record)
    return 0


def wait_for_release(release: Path) -> int:
    deadline = time.monotonic() + CHILD_TIMEOUT
    while not release.exists():
        if time.monotonic() >= deadline:
            return 1
        time.sleep(0.005)
    return 0


class StreamObserver:
    """Bounded, test-local projection; it intentionally never retains payload fields."""

    def __init__(self, stream, *, max_events: int = MAX_RETAINED_EVENTS, fail_after: int | None = None):
        self.stream = stream
        self.max_events = max_events
        self.fail_after = fail_after
        self.events: list[dict[str, object]] = []
        self.outcomes: set[str] = set()
        self.session_id: str | None = None
        self.incremental_usage: dict[str, int] | None = None
        self.final_usage: dict[str, int] | None = None
        self.duplicates = 0
        self.ordering = "unsupported_without_documented_ordering_key"
        self.telemetry_truncated = False
        self.observer_failed = False
        self._seen_ids: set[str] = set()
        self._records_seen = 0
        self._queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _read(self) -> None:
        try:
            while True:
                line = self.stream.readline()
                if not line:
                    break
                self._queue.put(("line", (line, line.endswith("\n"))))
        except BaseException as error:  # test harness records reader failure conservatively
            self._queue.put(("reader_failure", type(error).__name__))
        finally:
            self._queue.put(("eof", None))

    def observe_next(self, timeout: float = EVENT_TIMEOUT) -> bool:
        try:
            kind, value = self._queue.get(timeout=timeout)
        except queue.Empty:
            self.outcomes.add("structured_event_silence")
            return False
        if kind == "line":
            line, completed = value
            self._project_line(line, completed)
            return True
        if kind == "reader_failure":
            self._fail("observer_reader_failure")
        elif kind == "eof":
            if "terminal_success" not in self.outcomes and "terminal_failure" not in self.outcomes:
                self.outcomes.add("child_exit_without_final_result")
        return False

    def drain(self) -> None:
        while self.observe_next(timeout=0.05):
            pass

    def _project_line(self, line: str, completed: bool) -> None:
        self._records_seen += 1
        if self.fail_after is not None and self._records_seen >= self.fail_after:
            self._fail("observer_failure")
            return
        if not completed:
            self.outcomes.add("incomplete_stream_record")
            return
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            self.outcomes.add("malformed_json")
            return
        if not isinstance(record, dict):
            self.outcomes.add("malformed_json")
            return
        event_id = record.get("uuid") if record.get("type") == "stream_event" else None
        if isinstance(event_id, str):
            if event_id in self._seen_ids:
                self.duplicates += 1
                self.outcomes.add("duplicate_documented_event_identity")
                return
            self._seen_ids.add(event_id)
        self._project_record(record)

    def _project_record(self, record: dict[str, object]) -> None:
        event_type = record.get("type")
        safe_event: dict[str, object] | None = None
        if event_type == "system" and record.get("subtype") == "init":
            value = record.get("session_id")
            if isinstance(value, str):
                self.session_id = value
            safe_event = {"kind": "session_started"}
        elif event_type == "system" and record.get("subtype") == "api_retry":
            safe_event = {"kind": "retry_activity"}
        elif event_type == "stream_event":
            raw_event = record.get("event")
            if not isinstance(raw_event, dict):
                self.outcomes.add("unknown_operational_evidence")
            elif raw_event.get("type") == "message_delta":
                self.incremental_usage = safe_usage(raw_event.get("usage"))
                safe_event = {"kind": "incremental_usage"}
            elif raw_event.get("type") == "content_block_start":
                block = raw_event.get("content_block")
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    safe_event = {"kind": "tool_started", "tool_name": safe_name(block.get("name"))}
                else:
                    self.outcomes.add("unknown_operational_evidence")
            else:
                self.outcomes.add("unknown_operational_evidence")
        elif event_type == "tool_result":
            safe_event = {"kind": "tool_completed", "tool_name": safe_name(record.get("tool_name"))}
        elif event_type == "result":
            self.final_usage = safe_usage(record.get("usage"))
            self.outcomes.add("terminal_failure" if record.get("is_error") else "terminal_success")
            safe_event = {"kind": "terminal_result"}
        else:
            self.outcomes.add("unknown_operational_evidence")
            safe_event = {"kind": "unknown"}
        if safe_event is not None:
            self._append(safe_event)

    def _append(self, event: dict[str, object]) -> None:
        if len(self.events) >= self.max_events:
            self.telemetry_truncated = True
            self.outcomes.add("telemetry_truncated")
            return
        self.events.append(event)

    def _fail(self, outcome: str) -> None:
        self.observer_failed = True
        self.outcomes.add(outcome)

    @property
    def semantic_progress(self) -> bool:
        return False

    @property
    def liveness_only(self) -> bool:
        return "structured_event_silence" in self.outcomes


def safe_usage(value: object) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    safe = {key: amount for key, amount in value.items() if key in {"input_tokens", "output_tokens"} and isinstance(amount, int)}
    return safe or None


def safe_name(value: object) -> str:
    return value if isinstance(value, str) and len(value) <= 64 else "unknown"


class FakeClaudeChild:
    def __init__(self, scenario: str, *, fail_after: int | None = None, max_events: int = MAX_RETAINED_EVENTS):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.ready = root / "ready"
        self.release_path = root / "release"
        self.process = subprocess.Popen(
            [sys.executable, __file__, "--fake-child", scenario, str(self.ready), str(self.release_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert self.process.stdout is not None
        self.observer = StreamObserver(self.process.stdout, fail_after=fail_after, max_events=max_events)

    def wait_ready(self) -> None:
        deadline = time.monotonic() + EVENT_TIMEOUT
        while not self.ready.exists():
            if time.monotonic() >= deadline:
                self.cleanup()
                raise AssertionError("fake child did not reach synchronization barrier")
            time.sleep(0.005)

    def release(self) -> None:
        self.release_path.write_text("release", encoding="utf-8")

    def cleanup(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=CHILD_TIMEOUT)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=CHILD_TIMEOUT)
        self.observer._thread.join(timeout=CHILD_TIMEOUT)
        if self.process.stdout is not None:
            self.process.stdout.close()
        if self.process.stderr is not None:
            self.process.stderr.close()
        self.temporary.cleanup()


class StreamObserverHarnessTests(unittest.TestCase):
    def start(self, scenario: str, **kwargs) -> FakeClaudeChild:
        child = FakeClaudeChild(scenario, **kwargs)
        self.addCleanup(child.cleanup)
        child.wait_ready()
        return child

    def test_receives_flushed_session_event_before_child_exit(self):
        child = self.start("normal", max_events=10)
        self.assertTrue(child.observer.observe_next())
        self.assertEqual(child.observer.session_id, "session-synthetic")
        self.assertIsNone(child.process.poll(), "barrier proves the child remains running")
        child.release()
        child.observer.drain()
        self.assertEqual(child.process.wait(timeout=CHILD_TIMEOUT), 0)
        self.assertIn("terminal_success", child.observer.outcomes)

    def test_usage_lifecycle_retry_and_tool_activity_are_safe_and_not_double_counted(self):
        child = self.start("normal", max_events=10)
        self.assertTrue(child.observer.observe_next())
        child.release()
        child.observer.drain()
        self.assertEqual(child.observer.incremental_usage, {"output_tokens": 2})
        self.assertEqual(child.observer.final_usage, {"output_tokens": 7})
        self.assertIn("retry_activity", [event["kind"] for event in child.observer.events])
        serialized = json.dumps(child.observer.events)
        self.assertNotIn("never-retain", serialized)
        self.assertFalse(child.observer.semantic_progress)

    def test_unknown_malformed_and_truncated_streams_fail_conservatively(self):
        unknown = self.start("unknown")
        unknown.observer.observe_next()
        unknown.release()
        unknown.observer.drain()
        self.assertIn("unknown_operational_evidence", unknown.observer.outcomes)
        self.assertFalse(unknown.observer.semantic_progress)
        for scenario, expected in (("malformed", "malformed_json"), ("truncated", "incomplete_stream_record")):
            child = FakeClaudeChild(scenario)
            self.addCleanup(child.cleanup)
            child.observer.drain()
            self.assertIn(expected, child.observer.outcomes)

    def test_silence_is_liveness_evidence_not_semantic_progress(self):
        child = self.start("silent")
        self.assertFalse(child.observer.observe_next(timeout=0.05))
        self.assertIsNone(child.process.poll())
        self.assertTrue(child.observer.liveness_only)
        self.assertFalse(child.observer.semantic_progress)
        child.release()

    def test_missing_final_result_and_observer_failure_cleanup_fail_closed(self):
        no_final = self.start("no-final")
        no_final.observer.observe_next()
        no_final.release()
        no_final.observer.drain()
        self.assertIn("child_exit_without_final_result", no_final.observer.outcomes)
        failing = self.start("normal", fail_after=1)
        failing.observer.observe_next()
        self.assertTrue(failing.observer.observer_failed)
        failing.cleanup()
        self.assertIsNotNone(failing.process.poll())

    def test_terminal_failure_and_missing_usage_do_not_become_a_verdict_or_zero(self):
        child = self.start("failure", max_events=10)
        child.observer.observe_next()
        child.release()
        child.observer.drain()
        self.assertIn("terminal_failure", child.observer.outcomes)
        self.assertIsNone(child.observer.incremental_usage)
        self.assertIsNone(child.observer.final_usage)
        self.assertFalse(child.observer.semantic_progress)
        self.assertIn("retry_activity", [event["kind"] for event in child.observer.events])

    def test_duplicate_identity_is_detected_but_ordering_remains_unsupported(self):
        child = self.start("duplicate")
        child.observer.observe_next()
        child.release()
        child.observer.drain()
        self.assertEqual(child.observer.duplicates, 1)
        self.assertIn("duplicate_documented_event_identity", child.observer.outcomes)
        self.assertEqual(child.observer.ordering, "unsupported_without_documented_ordering_key")

    def test_noisy_stream_has_bounded_retention_and_reports_truncation(self):
        child = self.start("noisy", max_events=2)
        child.observer.observe_next()
        child.release()
        child.observer.drain()
        self.assertLessEqual(len(child.observer.events), 2)
        self.assertTrue(child.observer.telemetry_truncated)
        self.assertIn("telemetry_truncated", child.observer.outcomes)
        self.assertFalse(child.observer.semantic_progress)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fake-child", action="store_true")
    parser.add_argument("scenario", nargs="?")
    parser.add_argument("ready", nargs="?")
    parser.add_argument("release", nargs="?")
    arguments = parser.parse_args()
    if arguments.fake_child:
        raise SystemExit(fake_child(arguments.scenario, Path(arguments.ready), Path(arguments.release)))
    unittest.main()
