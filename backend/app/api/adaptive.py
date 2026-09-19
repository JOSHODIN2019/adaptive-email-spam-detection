from fastapi import APIRouter, Depends

from app.api.deps import get_app_state
from app.core.state import AppState
from app.schemas.common import success

router = APIRouter()


@router.get("/api/adaptive/status")
def adaptive_status(app_state: AppState = Depends(get_app_state)) -> dict:
    metadata = app_state.adaptive_service.metadata
    return success({
        "model_version": app_state.adaptive_service.model_version,
        "update_count": metadata.get("update_count", 0),
        "feedback_count": metadata.get("feedback_count", 0),
        "last_updated_at_unix": metadata.get("last_updated_at_unix"),
        "status": metadata.get("status", "unknown"),
        "initial_eval_on_held_out_test_set": metadata.get("initial_eval_on_held_out_test_set"),
        "known_limitations": metadata.get("known_limitations", []),
    })
