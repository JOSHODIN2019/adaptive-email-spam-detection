"""Operational store mapping prediction_id -> the processed text needed
to later apply user feedback (learn_one + ADWIN update). This is distinct
from the human-readable event logs in logs/ (see event_log.py + privacy.py):
it exists so /api/feedback can find what a given prediction_id actually
predicted and on what text, and is capped in memory to bound growth for a
long-running demo process.
"""

import threading
import time
from collections import OrderedDict
from typing import Optional

MAX_ENTRIES = 5000


class PredictionStore:
    def __init__(self) -> None:
        self._store: "OrderedDict[str, dict]" = OrderedDict()
        self._lock = threading.Lock()

    def save(self, prediction_id: str, record: dict) -> None:
        with self._lock:
            record = dict(record)
            record["stored_at_unix"] = time.time()
            self._store[prediction_id] = record
            self._store.move_to_end(prediction_id)
            while len(self._store) > MAX_ENTRIES:
                self._store.popitem(last=False)

    def get(self, prediction_id: str) -> Optional[dict]:
        with self._lock:
            return self._store.get(prediction_id)

    def mark_feedback_applied(self, prediction_id: str) -> None:
        with self._lock:
            if prediction_id in self._store:
                self._store[prediction_id]["feedback_applied"] = True
