import json

from fastapi import APIRouter, Depends

from app.api.deps import get_app_state
from app.core.state import AppState
from app.schemas.common import success

router = APIRouter()


@router.get("/api/evaluation/summary")
def evaluation_summary(app_state: AppState = Depends(get_app_state)) -> dict:
    settings = app_state.settings
    static_metadata = json.loads(settings.metadata_path.read_text()) if settings.metadata_path.exists() else {}
    adaptive_metadata = app_state.adaptive_service.metadata
    drift_state = app_state.drift_monitor.state

    return success({
        "static_baseline": {
            "model_version": static_metadata.get("model_version"),
            "metrics": static_metadata.get("metrics"),
            "trained_on_rows": static_metadata.get("dataset_rows_after_cleaning"),
            "known_limitations": static_metadata.get("known_limitations", []),
        },
        "adaptive_model": {
            "model_version": app_state.adaptive_service.model_version,
            "initial_eval_on_held_out_test_set": adaptive_metadata.get("initial_eval_on_held_out_test_set"),
            "update_count": adaptive_metadata.get("update_count", 0),
            "feedback_count": adaptive_metadata.get("feedback_count", 0),
            "known_limitations": adaptive_metadata.get("known_limitations", []),
        },
        "streaming_error_monitoring": {
            "monitored_predictions": drift_state.get("monitored_predictions", 0),
            "error_count": drift_state.get("error_count", 0),
            "error_rate": drift_state.get("error_rate"),
            "drift_event_count": drift_state.get("drift_event_count", 0),
        },
        "note": (
            "The adaptive model's initial evaluation was measured once, at "
            "warm-up time, on the same held-out test set as the static "
            "baseline. Streaming error monitoring reflects only feedback-"
            "confirmed predictions received after that point, not a "
            "re-evaluation on the full test set."
        ),
    })
