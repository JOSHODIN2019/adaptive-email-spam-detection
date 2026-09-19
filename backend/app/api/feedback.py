from fastapi import APIRouter, Depends

from app.api.deps import get_app_state
from app.core.state import AppState
from app.schemas.common import error, success
from app.schemas.feedback import FeedbackRequest
from app.services.feedback_service import (
    FeedbackAlreadyAppliedError,
    UnknownPredictionError,
    submit_feedback,
)

router = APIRouter()


@router.post("/api/feedback")
def feedback(
    payload: FeedbackRequest,
    app_state: AppState = Depends(get_app_state),
) -> dict:
    try:
        result = submit_feedback(app_state, payload.prediction_id, payload.corrected_label)
        return success(result)
    except UnknownPredictionError as exc:
        return error("UNKNOWN_PREDICTION_ID", str(exc))
    except FeedbackAlreadyAppliedError as exc:
        return error("FEEDBACK_ALREADY_APPLIED", str(exc))
