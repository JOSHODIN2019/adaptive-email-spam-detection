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
"""

import json
import threading
import time
from pathlib import Path

import joblib
from river.drift import ADWIN

from app.core.config import Settings


class DriftMonitor:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._detector: ADWIN | None = None
        self._state: dict = {}
        self._lock = threading.Lock()
        self._loaded = False

    def load(self) -> None:
        if not self._settings.adwin_detector_path.exists():
            raise FileNotFoundError(
                f"ADWIN detector not found at {self._settings.adwin_detector_path}. "
                "Run scripts/initialize_adaptive_model.py first."
            )
        self._detector = joblib.load(self._settings.adwin_detector_path)
        self._state = self._read_state(self._settings.drift_state_path)
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def state(self) -> dict:
        return dict(self._state)

    @staticmethod
    def _read_state(path: Path) -> dict:
        if not path.exists():
            return {
                "monitored_predictions": 0,
                "error_count": 0,
                "error_rate": None,
                "drift_event_count": 0,
                "last_drift_at": None,
                "status": "initialized",
            }
        return json.loads(path.read_text())

    def _write_state(self) -> None:
        self._settings.drift_state_path.write_text(json.dumps(self._state, indent=2))

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

            joblib.dump(self._detector, self._settings.adwin_detector_path)
            self._write_state()

            return {
                "drift_detected": drift_detected,
                "error": error,
                "state": dict(self._state),
            }
