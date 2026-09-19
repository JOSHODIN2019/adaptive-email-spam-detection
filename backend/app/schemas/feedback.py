from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    prediction_id: str
    corrected_label: Literal["spam", "legitimate"]


class FeedbackResponse(BaseModel):
    success: bool
    prediction_id: str
    original_prediction: str
    corrected_label: str
    adaptive_model_updated: bool
    adaptive_model_version: str
    drift_detected: bool
    message: str
