"""Stage 07 — Baseline Inference Service.

Wraps the persisted LinearSVC + TfidfVectorizer artifacts behind a clean
service interface. LinearSVC has no predict_proba; decision_function gives
the signed distance from the separating hyperplane, exposed as a decision
score rather than a fabricated probability (LinearSVC.predict_proba does
not exist and must not be faked).
"""

import json
from pathlib import Path
from typing import Optional

import joblib

from app.core.config import Settings

LABEL_NAMES = {0: "ham", 1: "spam"}


class StaticSVMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = None
        self._vectorizer = None
        self._model_version = "unknown"
        self._loaded = False

    def load(self) -> None:
        if not self._settings.static_model_path.exists():
            raise FileNotFoundError(
                f"Static model not found at {self._settings.static_model_path}. "
                "Run scripts/train_static_model.py first."
            )
        if not self._settings.static_vectorizer_path.exists():
            raise FileNotFoundError(
                f"Vectorizer not found at {self._settings.static_vectorizer_path}. "
                "Run scripts/train_static_model.py first."
            )
        self._model = joblib.load(self._settings.static_model_path)
        self._vectorizer = joblib.load(self._settings.static_vectorizer_path)
        self._model_version = self._read_model_version(self._settings.metadata_path)
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def vectorizer(self):
        return self._vectorizer

    @staticmethod
    def _read_model_version(metadata_path: Path) -> str:
        if not metadata_path.exists():
            return "static-unknown"
        data = json.loads(metadata_path.read_text())
        return str(data.get("model_version", "static-unknown"))

    def transform(self, processed_text: str):
        return self._vectorizer.transform([processed_text])

    def predict(self, processed_text: str) -> dict:
        if not self._loaded:
            raise RuntimeError("StaticSVMService.load() must be called before predict()")

        features = self.transform(processed_text)
        label = int(self._model.predict(features)[0])

        decision_score: Optional[float] = None
        try:
            decision_score = float(self._model.decision_function(features)[0])
        except (AttributeError, NotImplementedError):
            decision_score = None

        return {
            "label": label,
            "label_name": LABEL_NAMES[label],
            "decision_score": decision_score,
            "model_version": self._model_version,
        }
