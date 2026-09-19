"""Stage 18 — Feedback Event Logging. Simple append-only JSONL writer used
for predictions, feedback, model_updates and drift_events streams."""

import json
import threading
from pathlib import Path

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _lock_for(path: Path) -> threading.Lock:
    key = str(path)
    with _locks_guard:
        if key not in _locks:
            _locks[key] = threading.Lock()
        return _locks[key]


def append_event(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, default=str) + "\n"
    with _lock_for(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)


def read_events(path: Path, limit: int | None = None) -> list[dict]:
    if not path.exists():
        return []
    with _lock_for(path):
        lines = path.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    if limit is not None:
        return records[-limit:]
    return records
