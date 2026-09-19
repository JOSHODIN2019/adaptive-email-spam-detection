"""
Stage 06 — Baseline Artifact Export.

Reproduces notebooks/Python SVM Spam Detection System.ipynb end to end and
persists the trained artifacts so the backend can serve predictions without
re-running the notebook.

This is a faithful port, not a redesign:
  - Same dataset loading / column selection (email_text = subject + body)
  - Same dedup / null-drop order
  - Same cleaning steps (via backend.app.ml.preprocessing.clean_text)
  - Same frequent-word (top 20) / rare-word (<2 occurrences) pruning,
    computed over the FULL corpus before the train/test split — this
    matches the notebook's own cell order (cells 20-21 run before the
    split in cell 30). That is a pre-existing train/test leakage in the
    supplied baseline. It is preserved here deliberately so the exported
    baseline metrics match the original notebook's evaluation and are not
    silently invalidated. See PROJECT_MEMORY.md > Known Issues.
  - Same tokenize/stem/lemmatize step
  - Same TfidfVectorizer(max_features=5000)
  - Same 80/20 stratified split, random_state=42
  - Same LinearSVC(C=1.0, max_iter=1000, random_state=42)

Run:
    source .venv/bin/activate
    python scripts/train_static_model.py
"""

import json
import multiprocessing
import sys
import time
from collections import Counter
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.preprocessing import clean_text, tokenize_stem_lemmatize  # noqa: E402

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "LEVI_DATASET.csv"
STATIC_MODEL_PATH = PROJECT_ROOT / "artifacts" / "static_svm" / "model.joblib"
VECTORIZER_PATH = PROJECT_ROOT / "artifacts" / "vectorizer" / "tfidf_vectorizer.joblib"
METADATA_PATH = PROJECT_ROOT / "artifacts" / "metadata" / "model_metadata.json"

TOP_N_FREQUENT = 20
RARE_THRESHOLD = 2
MAX_FEATURES = 5000
TEST_SIZE = 0.20
RANDOM_STATE = 42
N_WORKERS = max(1, multiprocessing.cpu_count() - 1)


def log(msg: str) -> None:
    print(f"[train_static_model] {msg}", flush=True)


def _parallel_apply(series: pd.Series, fn) -> pd.Series:
    """Apply fn to each element of series using a process pool. Same
    per-row logic as series.apply(fn), just spread across cores — this is
    the one deliberate deviation from a literal notebook port, purely for
    runtime on a 1.3M-row dataset, not a behavior change."""
    with multiprocessing.Pool(processes=N_WORKERS) as pool:
        results = pool.map(fn, series.tolist(), chunksize=2000)
    return pd.Series(results, index=series.index)


def main() -> None:
    t0 = time.time()

    log(f"Loading dataset from {DATA_PATH}")
    raw_df = pd.read_csv(DATA_PATH)
    raw_df["email_text"] = raw_df["subject"].fillna("") + " " + raw_df["body"].fillna("")
    df = raw_df[["email_text", "label"]].copy()
    log(f"Loaded {len(df)} rows")

    count_before = len(df)
    df = df.drop_duplicates(subset=["email_text"]).reset_index(drop=True)
    log(f"Dropped {count_before - len(df)} duplicate rows -> {len(df)} remaining")

    count_before = len(df)
    df = df.dropna(subset=["email_text", "label"]).reset_index(drop=True)
    log(f"Dropped {count_before - len(df)} null rows -> {len(df)} remaining")

    log(f"Cleaning text (HTML/URL/email/punctuation/numbers/stopwords) using {N_WORKERS} workers...")
    df["email_text"] = _parallel_apply(df["email_text"], clean_text)

    log("Computing and removing top-frequent words (corpus-wide)...")
    all_words = " ".join(df["email_text"]).split()
    word_frequency = Counter(all_words)
    most_frequent_words = set(w for w, _ in word_frequency.most_common(TOP_N_FREQUENT))
    df["email_text"] = df["email_text"].apply(
        lambda t: " ".join(w for w in t.split() if w not in most_frequent_words)
    )

    log("Computing and removing rare words (corpus-wide, count < 2)...")
    all_words = " ".join(df["email_text"]).split()
    word_frequency = Counter(all_words)
    rare_words = set(w for w, c in word_frequency.items() if c < RARE_THRESHOLD)
    df["email_text"] = df["email_text"].apply(
        lambda t: " ".join(w for w in t.split() if w not in rare_words)
    )
    log(f"Removed {len(most_frequent_words)} frequent words and {len(rare_words)} rare words")

    log(f"Tokenizing / stemming / lemmatizing using {N_WORKERS} workers (this is the slow step)...")
    df["processed_text"] = _parallel_apply(df["email_text"], tokenize_stem_lemmatize)

    log("Fitting TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(max_features=MAX_FEATURES)
    X = vectorizer.fit_transform(df["processed_text"])
    y = df["label"]

    log("Splitting train/test (80/20, stratified, random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    log(f"Training LinearSVC on {X_train.shape[0]} samples, {X_train.shape[1]} features...")
    model = LinearSVC(C=1.0, max_iter=1000, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    log(f"Accuracy={accuracy:.4f} Precision={precision:.4f} Recall={recall:.4f} F1={f1:.4f}")
    log(f"Confusion matrix: TN={tn} FP={fp} FN={fn} TP={tp}")

    STATIC_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, STATIC_MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    metadata = {
        "model_type": "LinearSVC",
        "model_version": "static-1.0.0",
        "hyperparameters": {"C": 1.0, "max_iter": 1000, "random_state": RANDOM_STATE},
        "vectorizer_type": "TfidfVectorizer",
        "vectorizer_max_features": MAX_FEATURES,
        "dataset_source": "data/raw/LEVI_DATASET.csv",
        "dataset_rows_after_cleaning": len(df),
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "frequent_words_removed_count": len(most_frequent_words),
        "rare_words_removed_count": len(rare_words),
        "metrics": {
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
        },
        "known_limitations": [
            "Frequent-word and rare-word pruning were fitted on the full "
            "corpus (train+test) before the train/test split, matching the "
            "supplied notebook's own cell order. This is a pre-existing "
            "train/test leakage in the baseline pipeline, preserved here "
            "to keep exported metrics faithful to the original notebook "
            "rather than silently changed.",
            "LinearSVC is a batch model with no incremental-learning support. "
            "It is the static baseline only; the adaptive online model is a "
            "separate River MultinomialNB pipeline (see artifacts/adaptive_model).",
        ],
        "trained_at_unix": time.time(),
        "training_duration_seconds": round(time.time() - t0, 1),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    log(f"Saved model -> {STATIC_MODEL_PATH}")
    log(f"Saved vectorizer -> {VECTORIZER_PATH}")
    log(f"Saved metadata -> {METADATA_PATH}")
    log(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
