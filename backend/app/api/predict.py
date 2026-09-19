from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_app_state
from app.core.state import AppState
from app.ml.email_parser import EmailParseError, parse_eml_bytes
from app.schemas.common import error, success
from app.schemas.prediction import PredictRequest
from app.services.prediction_service import run_prediction

router = APIRouter()


@router.post("/api/predict")
def predict(
    payload: PredictRequest,
    app_state: AppState = Depends(get_app_state),
) -> dict:
    if not payload.body.strip():
        raise HTTPException(status_code=422, detail="A valid email body is required")

    result = run_prediction(app_state, payload.subject, payload.body)
    return success(result)


@router.post("/api/predict/eml")
async def predict_from_eml(
    file: UploadFile = File(...),
    app_state: AppState = Depends(get_app_state),
) -> dict:
    settings = app_state.settings
    raw_bytes = await file.read()

    if len(raw_bytes) > settings.max_upload_size_bytes:
        return error(
            "FILE_TOO_LARGE",
            f"Uploaded file exceeds the {settings.max_upload_size_bytes} byte limit",
        )

    try:
        parsed = parse_eml_bytes(raw_bytes)
    except EmailParseError as exc:
        return error("INVALID_EML", str(exc))

    result = run_prediction(app_state, parsed["subject"], parsed["body"])
    result["parsed_subject"] = parsed["subject"]
    return success(result)
