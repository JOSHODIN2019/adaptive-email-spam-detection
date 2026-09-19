from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_app_state
from app.core.state import AppState
from app.schemas.common import success
from app.storage.event_log import read_events

router = APIRouter()

_STREAMS = {
    "prediction": lambda s: s.predictions_log_path,
    "feedback": lambda s: s.feedback_log_path,
    "model_update": lambda s: s.model_updates_log_path,
    "drift": lambda s: s.drift_events_log_path,
}


@router.get("/api/events")
def events(
    event_type: Optional[str] = Query(default=None, description="Filter: prediction|feedback|model_update|drift"),
    limit: int = Query(default=50, ge=1, le=500),
    app_state: AppState = Depends(get_app_state),
) -> dict:
    settings = app_state.settings
    if event_type and event_type in _STREAMS:
        combined = [{"stream": event_type, **e} for e in read_events(_STREAMS[event_type](settings), limit=limit)]
    else:
        combined = []
        for stream_name, path_fn in _STREAMS.items():
            combined.extend({"stream": stream_name, **e} for e in read_events(path_fn(settings), limit=limit))
        combined.sort(key=lambda e: e.get("timestamp", 0))
        combined = combined[-limit:]

    return success({"events": combined, "count": len(combined)})
