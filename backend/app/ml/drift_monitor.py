"""Stage 24/25 — ADWIN Integration & Error Monitoring.

Strict separation per PROJECT_MEMORY.md §8.1:
  - Feedback learning (adaptive_model.update_one) learns from one label.
  - DriftMonitor only watches the resulting stream of 0/1 prediction
    errors and reports whether ADWIN detects a statistically significant
    change in that error distribution. It is NOT a classifier and does
    not itself learn spam/ham labels.

An error value is fed to ADWIN only when a trusted ground-truth label is
available (i.e. after user feedback), per §8.2 — a prediction with no
confirmed label is never scored as correct or incorrect.

Persistence goes through a KVStore (backend/app/storage/kv_store.py) for
the same reason as AdaptiveModelService: a local joblib.dump() of the
detector's state doesn't survive Vercel's cold starts or Render's
free-tier spin-down. The first-ever load seeds the store from the
git-committed baseline (a fresh ADWIN detector with no prior
observations) if the store is still empty.
"""

import json
import threading
import time

import joblib
from river.drift import ADWIN

from app.core.config import Settings
from app.storage.kv_store import KVStore

_DETECTOR_KEY = "adwin_detector"
_STATE_KEY = "drift_state"

_DEFAULT_STATE = {
    "monitored_predictions": 0,
    "error_count": 0,
    "error_rate": None,
    "drift_event_count": 0,
    "last_drift_at": None,
    "status": "initialized",
}


class DriftMonitor:
    def __init__(self, settings: Settings, kv_store: KVStore) -> None:
        self._settings = settings
        self._kv_store = kv_store
        self._detector: ADWIN | None = None
        self._state: dict = {}
        self._lock = threading.Lock()
        self._loaded = False

    def load(self) -> None:
        detector_bytes = self._kv_store.get_bytes(_DETECTOR_KEY)
        state = self._kv_store.get_json(_STATE_KEY)

        if detector_bytes is not None and state is not None:
            import io

            self._detector = joblib.load(io.BytesIO(detector_bytes))
            self._state = state
        else:
            if not self._settings.adwin_detector_path.exists():
                raise FileNotFoundError(
                    f"ADWIN detector not found at {self._settings.adwin_detector_path} "
                    "and the KV store is empty. Run scripts/initialize_adaptive_model.py first."
                )
            self._detector = joblib.load(self._settings.adwin_detector_path)
            self._state = (
                json.loads(self._settings.drift_state_path.read_text())
                if self._settings.drift_state_path.exists()
                else dict(_DEFAULT_STATE)
            )
            self._persist()

        self._loaded = True

    def _persist(self) -> None:
        import io

        buf = io.BytesIO()
        joblib.dump(self._detector, buf)
        self._kv_store.set_bytes(_DETECTOR_KEY, buf.getvalue())
        self._kv_store.set_json(_STATE_KEY, self._state)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def state(self) -> dict:
        return dict(self._state)

    def record_confirmed_prediction(self, predicted_label: int, true_label: int) -> dict:
        """Feed one confirmed-label error observation (0 = correct,
        1 = incorrect) to ADWIN. Returns {"drift_detected": bool,
        "error": int, "state": <updated state dict>}."""
        if not self._loaded:
            raise RuntimeError("DriftMonitor.load() must be called before record_confirmed_prediction()")

        error = 0 if predicted_label == true_label else 1

        with self._lock:
            self._detector.update(error)
            drift_detected = bool(self._detector.drift_detected)

            self._state["monitored_predictions"] = int(self._state.get("monitored_predictions", 0)) + 1
            self._state["error_count"] = int(self._state.get("error_count", 0)) + error
            monitored = self._state["monitored_predictions"]
            self._state["error_rate"] = round(self._state["error_count"] / monitored, 4) if monitored else None
            self._state["status"] = "monitoring"

            if drift_detected:
                self._state["drift_event_count"] = int(self._state.get("drift_event_count", 0)) + 1
                self._state["last_drift_at"] = time.time()

            self._persist()

            return {
                "drift_detected": drift_detected,
                "error": error,
                "state": dict(self._state),
            }
