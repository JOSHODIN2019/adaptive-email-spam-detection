import os
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings:
    def __init__(self) -> None:
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.app_host: str = os.getenv("APP_HOST", "127.0.0.1")
        self.app_port: int = int(os.getenv("APP_PORT", "8000"))

        self.data_dir: Path = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
        self.artifacts_dir: Path = PROJECT_ROOT / os.getenv("ARTIFACTS_DIR", "artifacts")
        self.logs_dir: Path = PROJECT_ROOT / os.getenv("LOGS_DIR", "logs")

        self.static_model_path: Path = PROJECT_ROOT / os.getenv(
            "STATIC_MODEL_PATH", "artifacts/static_svm/model.joblib"
        )
        self.static_vectorizer_path: Path = PROJECT_ROOT / os.getenv(
            "STATIC_VECTORIZER_PATH", "artifacts/vectorizer/tfidf_vectorizer.joblib"
        )
        self.adaptive_model_path: Path = PROJECT_ROOT / os.getenv(
            "ADAPTIVE_MODEL_PATH", "artifacts/adaptive_model/adaptive_model.joblib"
        )
        self.metadata_path: Path = PROJECT_ROOT / os.getenv(
            "METADATA_PATH", "artifacts/metadata/model_metadata.json"
        )
        self.adaptive_metadata_path: Path = (
            self.artifacts_dir / "metadata" / "adaptive_model_metadata.json"
        )
        self.adwin_detector_path: Path = self.artifacts_dir / "adaptive_model" / "adwin_detector.joblib"
        self.drift_state_path: Path = self.artifacts_dir / "metadata" / "drift_state.json"
        self.predictions_store_path: Path = self.artifacts_dir / "metadata" / "predictions_store.jsonl"

        self.predictions_log_path: Path = self.logs_dir / "predictions.jsonl"
        self.feedback_log_path: Path = self.logs_dir / "feedback.jsonl"
        self.model_updates_log_path: Path = self.logs_dir / "model_updates.jsonl"
        self.drift_events_log_path: Path = self.logs_dir / "drift_events.jsonl"

        self.max_upload_size_bytes: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", "2000000"))
        self.log_full_email_body: bool = os.getenv("LOG_FULL_EMAIL_BODY", "false").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()
