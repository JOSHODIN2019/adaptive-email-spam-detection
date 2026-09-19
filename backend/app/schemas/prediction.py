from typing import Literal, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    subject: str = Field(default="", max_length=998)
    body: str = Field(min_length=1, max_length=200_000)


class ModelPrediction(BaseModel):
    label: int
    label_name: Literal["spam", "ham"]
    decision_score: Optional[float] = None
    model_version: str


class PredictResponse(BaseModel):
    prediction_id: str
    static_prediction: ModelPrediction
    adaptive_prediction: Optional[ModelPrediction] = None
    preprocessing_status: Literal["ok"]
    disclaimer: str
