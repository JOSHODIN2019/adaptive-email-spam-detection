"""Operational store mapping prediction_id -> the processed text needed
to later apply user feedback (learn_one + ADWIN update). This is distinct
from the human-readable event logs in logs/ (see event_log.py + privacy.py).

Without Redis configured: an in-memory dict, capped at MAX_ENTRIES to
bound growth for a long-running demo process. Correct for local dev and
Render, where one process serves every request across its own lifetime.

With Redis configured: every prediction is written to the KV store with
a TTL, not kept in memory. This isn't just about long-term persistence -
it's required for basic correctness on Vercel, where a predict request
and the feedback request correcting it can each land on a *different*
serverless instance with its own empty in-memory dict. An in-memory-only
store would make /api/feedback fail with "unknown prediction_id"
whenever that happens, which on serverless is routine, not an edge case.
"""

import threading
import time
from collections import OrderedDict
from typing import Optional

from app.storage.kv_store import KVStore

MAX_ENTRIES = 5000
PREDICTION_TTL_SECONDS = 7 * 24 * 60 * 60  # 1 week - long enough to leave feedback, not unbounded


class PredictionStore:
    def __init__(self, kv_store: Optional[KVStore] = None, use_kv: bool = False) -> None:
        self._kv_store = kv_store
        self._use_kv = use_kv and kv_store is not None
        self._store: "OrderedDict[str, dict]" = OrderedDict()
        self._lock = threading.Lock()

    def save(self, prediction_id: str, record: dict) -> None:
        record = dict(record)
        record["stored_at_unix"] = time.time()
        if self._use_kv:
            self._kv_store.set_json(f"prediction:{prediction_id}", record, ttl_seconds=PREDICTION_TTL_SECONDS)
            return
        with self._lock:
            self._store[prediction_id] = record
            self._store.move_to_end(prediction_id)
            while len(self._store) > MAX_ENTRIES:
                self._store.popitem(last=False)

    def get(self, prediction_id: str) -> Optional[dict]:
        if self._use_kv:
            return self._kv_store.get_json(f"prediction:{prediction_id}")
        with self._lock:
            return self._store.get(prediction_id)

    def mark_feedback_applied(self, prediction_id: str) -> None:
        if self._use_kv:
            record = self._kv_store.get_json(f"prediction:{prediction_id}")
            if record is not None:
                record["feedback_applied"] = True
                self._kv_store.set_json(f"prediction:{prediction_id}", record, ttl_seconds=PREDICTION_TTL_SECONDS)
            return
        with self._lock:
            if prediction_id in self._store:
                self._store[prediction_id]["feedback_applied"] = True
