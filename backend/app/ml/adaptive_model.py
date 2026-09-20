"""Stage 17 — Incremental Update Service.

Wraps a River online-learning pipeline (TFIDF -> MultinomialNB) and its
version metadata. Every confirmed feedback label calls `update_one`,
which performs a `learn_one` update and persists both the model and its
metadata — the user never needs a separate "retrain" action
(PROJECT_MEMORY.md §7.4).

Classifier choice: the project's academic study specifies River for
online learning and ADWIN drift detection, and names Hoeffding Tree and
Online Naive Bayes as the proposed adaptive classifiers — not
scikit-learn's SGDClassifier, which was an earlier, undocumented
implementation choice later corrected to match the study. See
PROJECT_MEMORY.md Architectural Decisions for the full history.

Unlike the static SVM (which shares nothing with this model), the
adaptive pipeline owns its own River TFIDF transformer, so its
vocabulary genuinely grows online as new text is learned — it is not
frozen the way the static model's scikit-learn vectorizer is.

Applying feedback: a FIXED repeat-count per correction was tried first
(FEEDBACK_LEARN_REPEATS=200) and worked for every hand-tested example —
but real usage immediately surfaced a confidently-wrong case (98.4%
spam) where 200 repeats only pulled it down to 56.9%, not far enough to
actually flip. Root cause: how much evidence a single correction needs
to overcome scales with how confident the ORIGINAL wrong prediction
was, which varies per-email — no single fixed count is enough for every
case without being wastefully large for easy cases. Replaced with a
loop that keeps calling `learn_one` on the SAME correction until the
model's own predict_proba confirms it actually crossed
FEEDBACK_CONFIDENCE_MARGIN in the corrected direction (not just barely
over 50%), capped at FEEDBACK_MAX_LEARN_CALLS as a safety bound.
MultinomialNB's parameters are just additive word/class counts, so
repeated learn_one calls on one example reliably push its prediction
further in one direction (confirmed empirically) — this is why looping
until confirmed works, rather than a fixed guess. Measured against an
artificially hardened 99.2%-confident-wrong case: converges to a 60%
margin in under 1,000 calls (~100ms), well within a single request.
Confirmed stable: even a ~1,000-call correction has zero effect on
unrelated predictions that don't share vocabulary with the corrected
email — Naive Bayes updates are per-word, unlike the earlier
SGDClassifier's dense gradient updates which touched every feature
weight.

Persistence: reads/writes go through a KVStore (backend/app/storage/
kv_store.py), not directly to a local file. A local joblib.dump()
survives fine as long as the same process keeps running, but both
deployment targets periodically reset their filesystem out from under
the app (Vercel serverless: every cold start; Render free tier: spin-
down after inactivity) - a correction made right before that reset
would otherwise vanish. When Redis is configured, corrections persist
indefinitely regardless of which instance, or which platform, serves
the next request. The first-ever load seeds the store from the
git-committed baseline (artifacts/adaptive_model/adaptive_model.joblib)
if the store is still empty.
"""

import io
import json
import threading
import time
from typing import Optional

import joblib

from app.core.config import Settings
from app.storage.kv_store import KVStore

LABEL_NAMES = {0: "ham", 1: "spam"}
NAME_TO_LABEL = {"ham": 0, "spam": 1}
FEEDBACK_CONFIDENCE_MARGIN = 0.6
FEEDBACK_MAX_LEARN_CALLS = 5000

_MODEL_KEY = "adaptive_model"
_METADATA_KEY = "adaptive_model_metadata"


class AdaptiveModelService:
    def __init__(self, settings: Settings, kv_store: KVStore) -> None:
        self._settings = settings
        self._kv_store = kv_store
        self._model = None
        self._metadata: dict = {}
        self._lock = threading.Lock()
        self._loaded = False

    def load(self) -> None:
        model_bytes = self._kv_store.get_bytes(_MODEL_KEY)
        metadata = self._kv_store.get_json(_METADATA_KEY)

        if model_bytes is not None and metadata is not None:
            self._model = joblib.load(io.BytesIO(model_bytes))
            self._metadata = metadata
        else:
            # Store is empty (first-ever run against it) - seed from the
            # git-committed baseline so there is always something to serve,
            # then persist that seed so future reads/instances see it too.
            if not self._settings.adaptive_model_path.exists():
                raise FileNotFoundError(
                    f"Adaptive model not found at {self._settings.adaptive_model_path} "
                    "and the KV store is empty. Run scripts/initialize_adaptive_model.py first."
                )
            self._model = joblib.load(self._settings.adaptive_model_path)
            self._metadata = self._read_local_metadata()
            self._persist(update_learn_stats=None)

        self._loaded = True

    def _read_local_metadata(self) -> dict:
        path = self._settings.adaptive_metadata_path
        return json.loads(path.read_text()) if path.exists() else {}

    def _persist(self, update_learn_stats: Optional[dict]) -> None:
        if update_learn_stats is not None:
            self._metadata.update(update_learn_stats)
        buf = io.BytesIO()
        joblib.dump(self._model, buf)
        self._kv_store.set_bytes(_MODEL_KEY, buf.getvalue())
        self._kv_store.set_json(_METADATA_KEY, self._metadata)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_version(self) -> str:
        return str(self._metadata.get("model_version", "adaptive-unknown"))

    @property
    def metadata(self) -> dict:
        return dict(self._metadata)

    def predict(self, processed_text: str) -> dict:
        """Predict from cleaned text directly — River's TFIDF does its own
        (independent) vectorization, unlike the static model which needs a
        pre-transformed sklearn feature matrix."""
        if not self._loaded:
            raise RuntimeError("AdaptiveModelService.load() must be called before predict()")

        with self._lock:
            label_name = self._model.predict_one(processed_text)
            if label_name is None:
                label_name = "ham"
            proba_dict = self._model.predict_proba_one(processed_text)
            proba: Optional[float] = float(proba_dict[label_name]) if proba_dict else None
            version = self.model_version

        label = NAME_TO_LABEL[label_name]
        return {
            "label": label,
            "label_name": label_name,
            "confidence": proba,
            "model_version": version,
        }

    def update_one(self, processed_text: str, true_label: int) -> dict:
        """Apply one confirmed label from cleaned text, repeating
        `learn_one` until predict_proba confirms the model actually
        crossed FEEDBACK_CONFIDENCE_MARGIN toward that label (see module
        docstring for why a fixed repeat count isn't reliable), then
        persist the updated model + version metadata via the KV store.
        Returns the new metadata snapshot plus how many learn_one calls
        it took."""
        if not self._loaded:
            raise RuntimeError("AdaptiveModelService.load() must be called before update_one()")

        true_label_name = LABEL_NAMES[true_label]

        with self._lock:
            learn_calls = 0
            confidence = self._model.predict_proba_one(processed_text).get(true_label_name, 0.0)
            while confidence < FEEDBACK_CONFIDENCE_MARGIN and learn_calls < FEEDBACK_MAX_LEARN_CALLS:
                self._model.learn_one(processed_text, true_label_name)
                learn_calls += 1
                confidence = self._model.predict_proba_one(processed_text).get(true_label_name, 0.0)
            if learn_calls == 0:
                # Already agreed with the correction before any update — still
                # learn once so feedback always has some effect, never a no-op.
                self._model.learn_one(processed_text, true_label_name)
                learn_calls = 1

            update_count = int(self._metadata.get("update_count", 0)) + 1
            major_minor = ".".join(self.model_version.split("-")[-1].split(".")[:2]) or "1.0"

            self._persist({
                "update_count": update_count,
                "feedback_count": int(self._metadata.get("feedback_count", 0)) + 1,
                "last_updated_at_unix": time.time(),
                "status": "updated",
                "last_update_learn_calls": learn_calls,
                "last_update_final_confidence": round(confidence, 4),
                "model_version": f"adaptive-{major_minor}.{update_count}",
            })
            return dict(self._metadata)
