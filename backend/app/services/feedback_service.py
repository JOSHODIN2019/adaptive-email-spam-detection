"""Stage 17/18/19 — Feedback-driven incremental update, ADWIN error
monitoring, and event logging, wired together per PROJECT_MEMORY.md §8.3:
  1. Use the corrected label to calculate the error.
  2. Send the error to ADWIN.
  3. Update the adaptive model using the confirmed label.
  4. If ADWIN signals drift, record a drift event.
  5. Persist event and model metadata.
"""

import time
import uuid

from app.core.state import AppState
from app.storage.event_log import append_event
from app.storage.privacy import safe_preview

LABEL_TO_INT = {"spam": 1, "legitimate": 0}
INT_TO_NAME = {1: "spam", 0: "ham"}


class UnknownPredictionError(ValueError):
    pass


class FeedbackAlreadyAppliedError(ValueError):
    pass


def submit_feedback(app_state: AppState, prediction_id: str, corrected_label: str) -> dict:
    settings = app_state.settings
    record = app_state.prediction_store.get(prediction_id)
    if record is None:
        raise UnknownPredictionError(
            f"No prediction found for prediction_id={prediction_id}. "
            "It may have expired from the in-memory store or never existed."
        )
    if record.get("feedback_applied"):
        raise FeedbackAlreadyAppliedError(
            f"Feedback was already recorded for prediction_id={prediction_id}."
        )

    true_label = LABEL_TO_INT[corrected_label]
    processed_text = record["processed_text"]

    original_adaptive_label = record["adaptive_label"]

    updated_metadata = app_state.adaptive_service.update_one(processed_text, true_label)

    drift_result = app_state.drift_monitor.record_confirmed_prediction(
        predicted_label=original_adaptive_label, true_label=true_label
    )

    app_state.prediction_store.mark_feedback_applied(prediction_id)

    append_event(settings.feedback_log_path, {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "event_type": "feedback",
        "prediction_id": prediction_id,
        "original_adaptive_prediction": INT_TO_NAME[original_adaptive_label],
        "corrected_label": corrected_label,
        "adaptive_model_version_after_update": updated_metadata["model_version"],
        **safe_preview(processed_text, settings.log_full_email_body),
    })

    append_event(settings.model_updates_log_path, {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "event_type": "model_update",
        "prediction_id": prediction_id,
        "model_version": updated_metadata["model_version"],
        "update_count": updated_metadata["update_count"],
    })

    if drift_result["drift_detected"]:
        append_event(settings.drift_events_log_path, {
            "event_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "event_type": "drift",
            "prediction_id": prediction_id,
            "stream_position": drift_result["state"]["monitored_predictions"],
            "error_rate_at_detection": drift_result["state"]["error_rate"],
            "adaptive_model_version": updated_metadata["model_version"],
        })

    return {
        "success": True,
        "prediction_id": prediction_id,
        "original_prediction": INT_TO_NAME[original_adaptive_label],
        "corrected_label": corrected_label,
        "adaptive_model_updated": True,
        "adaptive_model_version": updated_metadata["model_version"],
        "drift_detected": drift_result["drift_detected"],
        "message": (
            "Adaptive model updated. The next prediction will reflect this feedback."
            if not drift_result["drift_detected"]
            else "Adaptive model updated. ADWIN detected a significant change in the "
                 "recent error stream — see the Drift Monitoring panel for details."
        ),
    }
