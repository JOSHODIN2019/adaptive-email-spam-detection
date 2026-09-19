from fastapi import APIRouter, Depends

from app.api.deps import get_app_state
from app.core.state import AppState
from app.schemas.common import success
from app.storage.event_log import read_events

router = APIRouter()


@router.get("/api/drift/status")
def drift_status(app_state: AppState = Depends(get_app_state)) -> dict:
    state = app_state.drift_monitor.state
    recent_events = read_events(app_state.settings.drift_events_log_path, limit=10)
    return success({**state, "recent_drift_events": recent_events})
