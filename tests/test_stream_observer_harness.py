"""Test-only qualification harness for CAK-154 Phase A.

Anthropic documentation checked 2026-08-22 establishes only the broad shapes
used here: stream-json is newline-delimited JSON, the final stream message is
``result``, and ``system/api_retry`` exists. Session placement, lifecycle
payloads, retry counters, and every fixture field below are synthetic test
data, not a production compatibility promise.
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


LIVE_POLL_TIMEOUT = 0.05
DRAIN_TIMEOUT = 1.5
CHILD_TIMEOUT = 1.0
MAX_QUEUE_ITEMS = 16
MAX_LINE_CHARS = 256
MAX_EVENT_IDS = 4
MAX_RETAINED_EVENTS = 3
SESSION = "session-synthetic"


def write_record(record: object) -> None:
    print(json.dumps(record, separators=(",", ":")), flush=True)


def event(event_type: str, **fields: object) -> dict[str, object]:
    return {"type": event_type, "session_id": SESSION, **fields}


def wait_for_release(release: Path) -> int:
    deadline = time.monotonic() + CHILD_TIMEOUT
    while not release.exists():
        if time.monotonic() >= deadline:
            return 1
        time.sleep(0.005)
    return 0


def fake_child(scenario: str, ready: Path, release: Path) -> int:
    """Emit synthetic JSONL; the file barrier, not scheduling, controls exit."""
    records: dict[str, list[object]] = {
        "normal": [
            event("system", subtype="init"),
            event("stream_event", uuid="event-start", event={"type": "message_start"}),
            event("stream_event", uuid="event-usage", event={"type": "message_delta", "usage": {"output_tokens": 2}}),
            event("stream_event", uuid="event-tool", event={"type": "content_block_start", "content_block": {"type": "tool_use", "name": "Read", "input": {"secret": "never-retain"}}}),
            event("system", subtype="api_retry"),
            event("tool_result", tool_name="Read", result="never-retain"),
            event("stream_event", uuid="event-stop", event={"type": "message_stop"}),
            event("result", usage={"output_tokens": 7}, result="never-retain"),
        ],
        "foreign": [
            event("system", subtype="init"),
            {"type": "stream_event", "session_id": "session-foreign", "uuid": "foreign-usage", "event": {"type": "message_delta", "usage": {"output_tokens": 99}}},
            {"type": "result", "session_id": "session-foreign", "usage": {"output_tokens": 99}},
            event("stream_event", uuid="event-start", event={"type": "message_start"}),
            event("stream_event", uuid="event-stop", event={"type": "message_stop"}),
            event("result", usage={"output_tokens": 7}),
        ],
        "duplicate": [event("system", subtype="init"), event("stream_event", uuid="event-start", event={"type": "message_start"}), event("stream_event", uuid="event-start", event={"type": "message_start"}), event("stream_event", uuid="event-stop", event={"type": "message_stop"}), event("result")],
        "out-of-order": [event("system", subtype="init"), event("stream_event", uuid="event-delta", event={"type": "message_delta", "usage": {"output_tokens": 2}}), event("result")],
        "after-result": [event("system", subtype="init"), event("stream_event", uuid="event-start", event={"type": "message_start"}), event("stream_event", uuid="event-stop", event={"type": "message_stop"}), event("result", usage={"output_tokens": 7}), event("stream_event", uuid="late", event={"type": "message_delta", "usage": {"output_tokens": 99}})],
        "no-final": [event("system", subtype="init")],
        "nonzero": [event("system", subtype="init")],
        "failure": [event("system", subtype="init"), event("system", subtype="api_retry"), event("result", is_error=True, error="never-retain")],
        "unknown": [event("system", subtype="init"), event("unknown_type", prompt="never-retain"), event("result")],
        "retry-missing-session": [event("system", subtype="init"), {"type": "system", "subtype": "api_retry"}, event("result")],
        "invalid-usage": [event("system", subtype="init"), event("stream_event", uuid="bool", event={"type": "message_start"}), event("stream_event", uuid="negative", event={"type": "message_delta", "usage": {"output_tokens": -1}}), event("stream_event", uuid="boolean", event={"type": "message_delta", "usage": {"output_tokens": True}}), event("stream_event", uuid="malformed", event={"type": "message_delta", "usage": "not-a-map"}), event("stream_event", uuid="stop", event={"type": "message_stop"}), event("result", usage={"unsupported": 4})],
        "noisy": [event("system", subtype="init"), *[event("stream_event", uuid=f"event-{index}", event={"type": "message_delta", "usage": {"output_tokens": index}}) for index in range(30)], event("result", usage={"output_tokens": 30})],
    }
    if scenario == "malformed":
        print('{"type":', flush=True)
        return 0
    if scenario == "truncated":
        sys.stdout.write('{"type":"result"')
        sys.stdout.flush()
        return 0
    if scenario == "oversized":
        sys.stdout.write("x" * (MAX_LINE_CHARS + 1) + "\n")
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
    return 9 if scenario == "nonzero" else 0


class StreamObserver:
    """Bounded dropping observer that retains only safe test-local evidence."""

    def __init__(self, stream, *, max_queue: int = MAX_QUEUE_ITEMS, max_events: int = MAX_RETAINED_EVENTS, max_ids: int = MAX_EVENT_IDS, fail_after: int | None = None):
        self.stream = stream
        self.max_events, self.max_ids, self.fail_after = max_events, max_ids, fail_after
        self.events: list[dict[str, object]] = []
        self.outcomes: set[str] = set()
        self.session_id: str | None = None
        self.incremental_usage: dict[str, int] | None = None
        self.final_usage: dict[str, int] | None = None
        self.duplicates = self.telemetry_dropped = self._records_seen = 0
        self.ordering = "unsupported_without_documented_ordering_key"
        self.observer_failed = self.terminal = self._message_open = False
        self._seen_ids: set[str] = set()
        self._queue: queue.Queue[tuple[str, object]] = queue.Queue(maxsize=max_queue)
        self._reader_done = threading.Event()
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _enqueue(self, item: tuple[str, object]) -> None:
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            self.telemetry_dropped += 1
            self.outcomes.add("telemetry_dropped")

    def _read(self) -> None:
        try:
            while True:
                line = self.stream.readline(MAX_LINE_CHARS + 1)
                if not line:
                    return
                if len(line) > MAX_LINE_CHARS:
                    while not line.endswith("\n"):
                        line = self.stream.readline(MAX_LINE_CHARS + 1)
                        if not line:
                            break
                    self._enqueue(("oversized", None))
                else:
                    self._enqueue(("line", (line, line.endswith("\n"))))
        except BaseException as error:
            self._enqueue(("reader_failure", type(error).__name__))
        finally:
            self._reader_done.set()

    def observe_live(self, timeout: float = LIVE_POLL_TIMEOUT) -> bool:
        """Poll a known-live child; no event means silence, never completion."""
        try:
            item = self._queue.get(timeout=timeout)
        except queue.Empty:
            self.outcomes.add("structured_event_silence")
            return False
        self._consume(item)
        return True

    def drain_to_eof(self, timeout: float = DRAIN_TIMEOUT) -> bool:
        """Drain through reader EOF with one deadline, not repeated short polls."""
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self.outcomes.add("drain_timeout")
                return False
            try:
                item = self._queue.get(timeout=min(remaining, 0.05))
            except queue.Empty:
                if self._reader_done.is_set():
                    if not self.terminal:
                        self.outcomes.add("child_exit_without_final_result")
                    return True
                continue
            self._consume(item)

    def _consume(self, item: tuple[str, object]) -> None:
        kind, value = item
        if kind == "oversized":
            self.outcomes.add("oversized_record")
        elif kind == "reader_failure":
            self._fail("observer_reader_failure")
        else:
            line, completed = value
            self._project_line(line, completed)

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
        if self.terminal:
            self.outcomes.add("post_terminal_protocol_evidence")
            return
        event_type = record.get("type")
        if event_type == "system" and record.get("subtype") == "init":
            identity = record.get("session_id")
            if isinstance(identity, str):
                self.session_id = identity
                self._append({"kind": "session_started"})
            else:
                self.outcomes.add("missing_session_identity")
            return
        session = record.get("session_id")
        if not isinstance(session, str):
            self.outcomes.add("missing_session_identity")
            return
        if self.session_id is None or session != self.session_id:
            self.outcomes.add("foreign_session_event")
            return
        event_id = record.get("uuid") if event_type == "stream_event" else None
        if isinstance(event_id, str):
            if event_id in self._seen_ids:
                self.duplicates += 1
                self.outcomes.add("duplicate_documented_event_identity")
                return
            if len(self._seen_ids) >= self.max_ids:
                self.outcomes.add("event_identity_capacity_reached")
            else:
                self._seen_ids.add(event_id)
        self._project_record(record)

    def _project_record(self, record: dict[str, object]) -> None:
        event_type = record.get("type")
        safe_event: dict[str, object] | None = None
        if event_type == "system" and record.get("subtype") == "api_retry":
            self.outcomes.add("retry_exhaustion_unknown")
            safe_event = {"kind": "retry_activity"}
        elif event_type == "stream_event":
            raw = record.get("event")
            if not isinstance(raw, dict):
                self.outcomes.add("unknown_operational_evidence")
            elif raw.get("type") == "message_start":
                if self._message_open:
                    self.outcomes.add("invalid_message_lifecycle")
                self._message_open = True
                safe_event = {"kind": "message_started"}
            elif raw.get("type") == "message_delta":
                if not self._message_open:
                    self.outcomes.add("invalid_message_lifecycle")
                usage = safe_usage(raw.get("usage"))
                if usage is None:
                    self.outcomes.add("invalid_usage")
                else:
                    self.incremental_usage = usage
                    safe_event = {"kind": "incremental_usage"}
            elif raw.get("type") == "message_stop":
                if not self._message_open:
                    self.outcomes.add("invalid_message_lifecycle")
                self._message_open = False
                safe_event = {"kind": "message_stopped"}
            elif raw.get("type") == "content_block_start":
                block = raw.get("content_block")
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    safe_event = {"kind": "tool_started", "tool_name": safe_name(block.get("name"))}
                else:
                    self.outcomes.add("unknown_operational_evidence")
            else:
                self.outcomes.add("unknown_operational_evidence")
        elif event_type == "tool_result":
            safe_event = {"kind": "tool_completed", "tool_name": safe_name(record.get("tool_name"))}
        elif event_type == "result":
            if self._message_open:
                self.outcomes.add("invalid_message_lifecycle")
            usage = record.get("usage")
            if usage is not None:
                self.final_usage = safe_usage(usage)
                if self.final_usage is None:
                    self.outcomes.add("invalid_usage")
            self.terminal = True
            self.outcomes.add("terminal_failure" if record.get("is_error") else "terminal_success")
            safe_event = {"kind": "terminal_result"}
        else:
            self.outcomes.add("unknown_operational_evidence")
            safe_event = {"kind": "unknown"}
        if safe_event is not None:
            self._append(safe_event)

    def _append(self, event: dict[str, object]) -> None:
        if len(self.events) >= self.max_events:
            self.telemetry_dropped += 1
            self.outcomes.add("telemetry_dropped")
            return
        self.events.append(event)

    def _fail(self, outcome: str) -> None:
        self.observer_failed = True
        self.outcomes.add(outcome)

    @property
    def semantic_progress(self) -> bool:
        return False


def safe_usage(value: object) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    safe: dict[str, int] = {}
    for key, amount in value.items():
        if key not in {"input_tokens", "output_tokens"}:
            continue
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            return None
        safe[key] = amount
    return safe or None


def safe_name(value: object) -> str:
    return value if isinstance(value, str) and len(value) <= 64 else "unknown"


class FakeClaudeChild:
    def __init__(self, scenario: str, **observer_kwargs: object):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.ready, self.release_path = root / "ready", root / "release"
        self.process = subprocess.Popen([sys.executable, __file__, "--fake-child", scenario, str(self.ready), str(self.release_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert self.process.stdout is not None
        self.observer = StreamObserver(self.process.stdout, **observer_kwargs)

    def wait_ready(self) -> None:
        deadline = time.monotonic() + CHILD_TIMEOUT
        while not self.ready.exists():
            if time.monotonic() >= deadline:
                self.cleanup()
                raise AssertionError("fake child did not reach synchronization barrier")
            time.sleep(0.005)

    def release(self) -> None:
        self.release_path.write_text("release", encoding="utf-8")

    def finish(self) -> int:
        self.release()
        self.observer.drain_to_eof()
        exit_code = self.process.wait(timeout=CHILD_TIMEOUT)
        if exit_code != 0:
            self.observer.outcomes.add("nonzero_child_exit")
        return exit_code

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
    def start(self, scenario: str, **kwargs: object) -> FakeClaudeChild:
        child = FakeClaudeChild(scenario, **kwargs)
        self.addCleanup(child.cleanup)
        child.wait_ready()
        return child

    def direct(self, scenario: str, **kwargs: object) -> FakeClaudeChild:
        child = FakeClaudeChild(scenario, **kwargs)
        self.addCleanup(child.cleanup)
        return child

    def test_receives_flushed_session_event_before_child_exit(self):
        child = self.start("normal", max_events=10)
        self.assertTrue(child.observer.observe_live())
        self.assertEqual(child.observer.session_id, SESSION)
        self.assertIsNone(child.process.poll())
        self.assertEqual(child.finish(), 0)
        self.assertIn("terminal_success", child.observer.outcomes)

    def test_drain_waits_for_eof_and_distinguishes_live_silence(self):
        child = self.start("silent")
        self.assertFalse(child.observer.observe_live())
        self.assertIn("structured_event_silence", child.observer.outcomes)
        self.assertIsNone(child.process.poll())
        self.assertEqual(child.finish(), 0)
        self.assertIn("child_exit_without_final_result", child.observer.outcomes)
        truncated = self.direct("truncated")
        self.assertTrue(truncated.observer.drain_to_eof())
        self.assertIn("incomplete_stream_record", truncated.observer.outcomes)

    def test_usage_tool_retry_and_privacy_are_safe(self):
        child = self.start("normal", max_events=10)
        child.observer.observe_live()
        child.finish()
        self.assertEqual(child.observer.incremental_usage, {"output_tokens": 2})
        self.assertEqual(child.observer.final_usage, {"output_tokens": 7})
        self.assertIn("retry_activity", [item["kind"] for item in child.observer.events])
        self.assertIn("retry_exhaustion_unknown", child.observer.outcomes)
        self.assertNotIn("never-retain", json.dumps(child.observer.events))
        self.assertFalse(child.observer.semantic_progress)

    def test_foreign_session_cannot_mutate_usage_or_completion(self):
        child = self.start("foreign", max_events=10)
        child.observer.observe_live()
        child.finish()
        self.assertIn("foreign_session_event", child.observer.outcomes)
        self.assertEqual(child.observer.final_usage, {"output_tokens": 7})
        self.assertNotEqual(child.observer.incremental_usage, {"output_tokens": 99})

    def test_malformed_truncated_and_oversized_records_fail_conservatively(self):
        for scenario, expected in (("malformed", "malformed_json"), ("truncated", "incomplete_stream_record"), ("oversized", "oversized_record")):
            child = self.direct(scenario)
            self.assertTrue(child.observer.drain_to_eof())
            self.assertIn(expected, child.observer.outcomes)

    def test_unknown_and_incomplete_retry_evidence_remain_conservative(self):
        unknown = self.start("unknown", max_events=10)
        unknown.observer.observe_live()
        unknown.finish()
        self.assertIn("unknown_operational_evidence", unknown.observer.outcomes)
        self.assertNotIn("never-retain", json.dumps(unknown.observer.events))
        retry = self.start("retry-missing-session", max_events=10)
        retry.observer.observe_live()
        retry.finish()
        self.assertIn("missing_session_identity", retry.observer.outcomes)
        self.assertNotIn("retry_activity", [item["kind"] for item in retry.observer.events])

    def test_usage_validation_rejects_invalid_values_without_zeroing(self):
        child = self.start("invalid-usage", max_events=10)
        child.observer.observe_live()
        child.finish()
        self.assertIn("invalid_usage", child.observer.outcomes)
        self.assertIsNone(child.observer.incremental_usage)
        self.assertIsNone(child.observer.final_usage)
        self.assertEqual(safe_usage({"input_tokens": 1, "output_tokens": 2}), {"input_tokens": 1, "output_tokens": 2})
        self.assertIsNone(safe_usage({"output_tokens": True}))
        self.assertIsNone(safe_usage({"output_tokens": -1}))
        self.assertIsNone(safe_usage("not-a-map"))

    def test_duplicate_identity_and_minimum_lifecycle_ordering(self):
        duplicate = self.start("duplicate", max_events=10)
        duplicate.observer.observe_live()
        duplicate.finish()
        self.assertEqual(duplicate.observer.duplicates, 1)
        self.assertIn("duplicate_documented_event_identity", duplicate.observer.outcomes)
        self.assertEqual(duplicate.observer.ordering, "unsupported_without_documented_ordering_key")
        out_of_order = self.start("out-of-order", max_events=10)
        out_of_order.observer.observe_live()
        out_of_order.finish()
        self.assertIn("invalid_message_lifecycle", out_of_order.observer.outcomes)

    def test_terminal_result_closes_logical_stream(self):
        child = self.start("after-result", max_events=10)
        child.observer.observe_live()
        child.finish()
        self.assertEqual(child.observer.final_usage, {"output_tokens": 7})
        self.assertIn("post_terminal_protocol_evidence", child.observer.outcomes)

    def test_exit_failure_classes_are_not_verdicts_or_progress(self):
        no_final = self.start("no-final")
        no_final.observer.observe_live()
        self.assertEqual(no_final.finish(), 0)
        self.assertIn("child_exit_without_final_result", no_final.observer.outcomes)
        nonzero = self.start("nonzero")
        nonzero.observer.observe_live()
        self.assertEqual(nonzero.finish(), 9)
        self.assertIn("child_exit_without_final_result", nonzero.observer.outcomes)
        self.assertIn("nonzero_child_exit", nonzero.observer.outcomes)
        self.assertFalse(nonzero.observer.semantic_progress)
        failure = self.start("failure", max_events=10)
        failure.observer.observe_live()
        self.assertEqual(failure.finish(), 0)
        self.assertIn("terminal_failure", failure.observer.outcomes)

    def test_observer_failure_reaps_child(self):
        child = self.start("normal", fail_after=1)
        child.observer.observe_live()
        self.assertTrue(child.observer.observer_failed)
        child.cleanup()
        self.assertIsNotNone(child.process.poll())

    def test_raw_ingestion_is_bounded_and_drops_slow_consumer_telemetry(self):
        child = self.start("noisy", max_queue=1, max_events=2, max_ids=2)
        child.observer.observe_live()
        child.finish()
        self.assertLessEqual(child.observer._queue.maxsize, MAX_QUEUE_ITEMS)
        self.assertLessEqual(len(child.observer.events), 2)
        self.assertLessEqual(len(child.observer._seen_ids), 2)
        self.assertGreater(child.observer.telemetry_dropped, 0)
        self.assertIn("telemetry_dropped", child.observer.outcomes)
        self.assertFalse(child.observer.semantic_progress)
        identities = self.start("noisy", max_events=20, max_ids=2)
        identities.observer.observe_live()
        identities.finish()
        self.assertIn("event_identity_capacity_reached", identities.observer.outcomes)


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
