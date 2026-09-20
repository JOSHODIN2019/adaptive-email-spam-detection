import os
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _make_writable(path: Path, project_root: Path) -> Path:
    """Return a writable copy of `path` if it isn't writable in place.

    On platforms with a read-only deployment filesystem (Vercel serverless
    functions - only /tmp is writable there), the bundled artifacts/logs
    directories can be read but not written to, so the adaptive model's
    every-feedback joblib.dump() would crash. Rather than branching
    per-platform, this detects non-writability directly and transparently
    redirects to a /tmp copy - a no-op everywhere else (local dev, Render),
    where these directories are already writable.

    Within one warm serverless instance this makes feedback genuinely work
    end-to-end; a fresh cold start begins again from the bundled baseline,
    which is the accepted, understood limitation of deploying a
    stateful-by-design app to a stateless platform (see PROJECT_MEMORY.md
    §24) - this fix's job is only to stop it from crashing, not to grant
    Vercel a persistent filesystem it doesn't have."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok")
        probe.unlink()
        return path
    except OSError:
        # Covers two distinct failure modes on a read-only mount: the
        # directory already exists but can't be written into (e.g.
        # artifacts/, shipped with real files), and the directory doesn't
        # exist at all so even mkdir() itself fails (e.g. logs/, which has
        # no tracked files - git doesn't track empty directories, so it
        # is simply absent from the deployed bundle).
        relative = path.relative_to(project_root) if path.is_relative_to(project_root) else path.name
        writable_copy = Path(tempfile.gettempdir()) / "spam_detection_writable" / relative
        if not writable_copy.exists():
            writable_copy.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                shutil.copytree(path, writable_copy)
            else:
                writable_copy.mkdir(parents=True, exist_ok=True)
        return writable_copy


class Settings:
    def __init__(self) -> None:
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.app_host: str = os.getenv("APP_HOST", "127.0.0.1")
        self.app_port: int = int(os.getenv("APP_PORT", "8000"))

        self.data_dir: Path = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
        self.artifacts_dir: Path = _make_writable(
            PROJECT_ROOT / os.getenv("ARTIFACTS_DIR", "artifacts"), PROJECT_ROOT
        )
        self.logs_dir: Path = _make_writable(
            PROJECT_ROOT / os.getenv("LOGS_DIR", "logs"), PROJECT_ROOT
        )

        # Derived from self.artifacts_dir (not PROJECT_ROOT directly) so that
        # when _make_writable() redirects to a /tmp copy, both the initial
        # read AND every subsequent adaptive-model write consistently use
        # that same copy - otherwise the read would succeed against the
        # original read-only bundle while every write to it still failed.
        self.static_model_path: Path = self.artifacts_dir / os.getenv(
            "STATIC_MODEL_PATH", "static_svm/model.joblib"
        )
        self.static_vectorizer_path: Path = self.artifacts_dir / os.getenv(
            "STATIC_VECTORIZER_PATH", "vectorizer/tfidf_vectorizer.joblib"
        )
        self.adaptive_model_path: Path = self.artifacts_dir / os.getenv(
            "ADAPTIVE_MODEL_PATH", "adaptive_model/adaptive_model.joblib"
        )
        self.metadata_path: Path = self.artifacts_dir / os.getenv(
            "METADATA_PATH", "metadata/model_metadata.json"
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
