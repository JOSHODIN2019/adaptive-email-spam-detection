from fastapi import APIRouter, Depends

from app.api.deps import get_app_state
from app.core.state import AppState
from app.schemas.common import success

router = APIRouter()


@router.get("/api/health")
def health(app_state: AppState = Depends(get_app_state)) -> dict:
    return success({
        "status": "ok",
        "static_model_loaded": app_state.static_service.is_loaded,
        "adaptive_model_loaded": app_state.adaptive_service.is_loaded,
        "drift_monitor_loaded": app_state.drift_monitor.is_loaded,
        "static_model_version": app_state.static_service.model_version,
        "adaptive_model_version": app_state.adaptive_service.model_version,
    })
