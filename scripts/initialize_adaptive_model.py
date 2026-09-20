"""
Stage 16 — Adaptive Model Initialization.

Warm-starts a River online-learning pipeline (TFIDF -> MultinomialNB)
on the same TRAIN split used by the static LinearSVC baseline, so:
  - The adaptive model begins from a reasonable, non-random state rather
    than cold (a freshly-initialized Naive Bayes would predict close to
    chance).
  - The held-out TEST split stays identical and unseen by both models,
    keeping Stage 34's static-vs-adaptive comparison fair.
  - Unlike the static SVM, this model owns its own River TFIDF
    transformer — its vocabulary genuinely grows online as new emails
    are learned, rather than sharing the static model's frozen
    scikit-learn vectorizer.

Classifier choice: the project's academic study specifies River for
online learning + ADWIN drift detection, naming Hoeffding Tree and
Online Naive Bayes as the proposed adaptive classifiers. This
implementation uses River's MultinomialNB per the study author's
explicit recommendation (see PROJECT_MEMORY.md Architectural
Decisions) — not scikit-learn's SGDClassifier, an earlier,
undocumented implementation choice that has since been corrected.

Warm-up text is prepared with `preprocess_for_inference` (clean +
tokenize/stem/lemmatize, no frequent/rare-word pruning) — the same
pipeline the adaptive model will see for every future feedback-driven
update. Training and serving must share one preprocessing path for an
online model; pruning is a one-off, corpus-wide statistic that only
makes sense at batch-training time (see
backend/app/ml/preprocessing.py docstring).

Run:
    source .venv/bin/activate
    python scripts/initialize_adaptive_model.py
"""

import json
import multiprocessing
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from river import compose, feature_extraction, naive_bayes
from river.drift import ADWIN
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.preprocessing import clean_text, ensure_nltk_data, tokenize_stem_lemmatize  # noqa: E402

ensure_nltk_data()

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "LEVI_DATASET.csv"
ADAPTIVE_MODEL_PATH = PROJECT_ROOT / "artifacts" / "adaptive_model" / "adaptive_model.joblib"
ADAPTIVE_METADATA_PATH = PROJECT_ROOT / "artifacts" / "metadata" / "adaptive_model_metadata.json"
ADWIN_DETECTOR_PATH = PROJECT_ROOT / "artifacts" / "adaptive_model" / "adwin_detector.joblib"
DRIFT_STATE_PATH = PROJECT_ROOT / "artifacts" / "metadata" / "drift_state.json"

TEST_SIZE = 0.20
RANDOM_STATE = 42
WARM_UP_EPOCHS = 8
N_WORKERS = max(1, multiprocessing.cpu_count() - 1)
LABEL_NAME = {0: "ham", 1: "spam"}


def log(msg: str) -> None:
    print(f"[initialize_adaptive_model] {msg}", flush=True)


def _parallel_apply(series: pd.Series, fn) -> pd.Series:
    with multiprocessing.Pool(processes=N_WORKERS) as pool:
        results = pool.map(fn, series.tolist(), chunksize=2000)
    return pd.Series(results, index=series.index)


def main() -> None:
    t0 = time.time()

    log(f"Loading dataset from {DATA_PATH}")
    raw_df = pd.read_csv(DATA_PATH)
    raw_df["email_text"] = raw_df["subject"].fillna("") + " " + raw_df["body"].fillna("")
    df = raw_df[["email_text", "label"]].copy()
    df = df.drop_duplicates(subset=["email_text"]).reset_index(drop=True)
    df = df.dropna(subset=["email_text", "label"]).reset_index(drop=True)
    log(f"{len(df)} rows after dedup/null-drop (matches static baseline's row set)")

    log(f"Preparing text via preprocess_for_inference using {N_WORKERS} workers...")
    cleaned = _parallel_apply(df["email_text"], clean_text)
    processed = _parallel_apply(cleaned, tokenize_stem_lemmatize)
    df["processed_text"] = processed

    y = df["label"].to_numpy()

    log("Splitting train/test with the SAME parameters as the static baseline "
        "(test_size=0.20, random_state=42, stratify=y) to keep the held-out set identical...")
    train_idx, test_idx = train_test_split(
        np.arange(len(df)), test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    train_texts = df["processed_text"].iloc[train_idx].to_numpy()
    train_labels = y[train_idx]
    test_texts = df["processed_text"].iloc[test_idx].to_numpy()
    test_labels = y[test_idx]
    log(f"Warm-up train rows: {len(train_texts)}, held-out test rows: {len(test_texts)}")

    model = compose.Pipeline(
        ("tfidf", feature_extraction.TFIDF()),
        ("nb", naive_bayes.MultinomialNB()),
    )

    log(f"Warm-starting River MultinomialNB via learn_one over {WARM_UP_EPOCHS} shuffled epochs "
        f"({len(train_texts) * WARM_UP_EPOCHS} total learn_one calls)...")
    for epoch in range(WARM_UP_EPOCHS):
        texts_epoch, labels_epoch = shuffle(train_texts, train_labels, random_state=RANDOM_STATE + epoch)
        for text, label in zip(texts_epoch, labels_epoch):
            model.learn_one(text, LABEL_NAME[label])
        log(f"  epoch {epoch + 1}/{WARM_UP_EPOCHS} done ({time.time() - t0:.1f}s elapsed)")

    log("Evaluating on held-out test set...")
    tp = fp = tn = fn = 0
    for text, true_label in zip(test_texts, test_labels):
        pred_name = model.predict_one(text) or "ham"
        pred = 1 if pred_name == "spam" else 0
        if pred == 1 and true_label == 1:
            tp += 1
        elif pred == 1 and true_label == 0:
            fp += 1
        elif pred == 0 and true_label == 0:
            tn += 1
        else:
            fn += 1

    accuracy = (tp + tn) / len(test_texts)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    log(f"Held-out test: Accuracy={accuracy:.4f} Precision={precision:.4f} Recall={recall:.4f} F1={f1:.4f}")
    log(f"Confusion matrix: TN={tn} FP={fp} FN={fn} TP={tp}")

    ADAPTIVE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ADAPTIVE_MODEL_PATH)
    log(f"Saved adaptive model -> {ADAPTIVE_MODEL_PATH}")

    adwin = ADWIN()
    joblib.dump(adwin, ADWIN_DETECTOR_PATH)
    log(f"Saved fresh ADWIN detector -> {ADWIN_DETECTOR_PATH}")

    DRIFT_STATE_PATH.write_text(json.dumps({
        "monitored_predictions": 0,
        "error_count": 0,
        "error_rate": None,
        "drift_event_count": 0,
        "last_drift_at": None,
        "status": "initialized",
    }, indent=2))
    log(f"Saved drift state -> {DRIFT_STATE_PATH}")

    metadata = {
        "model_type": "River Pipeline (TFIDF -> MultinomialNB)",
        "model_version": "adaptive-1.0.0",
        "shares_vectorizer_with_static": False,
        "vectorizer_vocabulary_fixed": False,
        "warm_up_epochs": WARM_UP_EPOCHS,
        "warm_up_train_rows": len(train_texts),
        "held_out_test_rows": len(test_texts),
        "random_state": RANDOM_STATE,
        "update_count": 0,
        "feedback_count": 0,
        "created_at_unix": time.time(),
        "last_updated_at_unix": None,
        "status": "initialized",
        "initial_eval_on_held_out_test_set": {
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
        },
        "known_limitations": [
            "Naive Bayes assumes conditional independence between words given "
            "the class label, which is rarely exactly true for natural "
            "language but works well in practice for spam/ham text "
            "classification.",
            "Warm-up uses a fixed number of shuffled passes over the train "
            "split rather than true streaming order; it establishes a "
            "reasonable starting point before online feedback updates begin.",
        ],
    }
    ADAPTIVE_METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    log(f"Saved adaptive model metadata -> {ADAPTIVE_METADATA_PATH}")
    log(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
