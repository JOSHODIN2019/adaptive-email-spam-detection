# Adaptive Email Spam Detection System

Academic final-year project. A local web app that classifies emails as
spam/ham using a static SVM baseline plus an online-learning model that
updates from user feedback, with ADWIN-based drift monitoring.

See `PROJECT_MEMORY.md` for the full architecture, roadmap, and current
project status — it is the source of truth for this repo. See
`notebooks/Python SVM Spam Detection System.ipynb` for the original
baseline notebook this system is built from.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

NLTK data downloads automatically on first app startup
(`ensure_nltk_data()` in `backend/app/ml/preprocessing.py`) — no
separate step needed.

`requirements.txt` covers everything the *deployed app* needs to serve
predictions (kept intentionally lean for Vercel's serverless function
size limit). It does not include `pandas`, which the app never imports
at runtime — only the training scripts below use it.

## Train the models (first run only)

Trained artifacts (`artifacts/**/*.joblib`, ~4.2MB total) are committed
to the repo, so a fresh clone can serve predictions immediately without
retraining. Only regenerate them if you want to retrain from scratch —
this requires the raw dataset (`data/raw/LEVI_DATASET.csv`, gitignored
for size) and `pandas`:

```bash
pip install -r requirements-training.txt   # adds pandas
python scripts/train_static_model.py        # baseline LinearSVC + TF-IDF
python scripts/initialize_adaptive_model.py  # warm-starts the adaptive River MultinomialNB pipeline + ADWIN
```

## Run

```bash
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8020
```

Open http://127.0.0.1:8020/. Port 8000 is used by an unrelated project
on this machine (APPLYAI) — this app defaults to 8020 (see `.env.example`).

## Test

```bash
source .venv/bin/activate
python -m pytest backend/tests/ -v
```

Tests run against an isolated copy of `artifacts/`/`logs/` in a temp
directory, so running the suite never mutates the live demo's adaptive
model state.

## Project layout

```
backend/app/        FastAPI application (api/, services/, ml/, storage/, core/)
frontend/            Vanilla HTML/CSS/JS served by FastAPI
scripts/             One-off training / initialization scripts
artifacts/           Trained model, vectorizer, ADWIN detector, metadata (gitignored)
data/raw/            LEVI_DATASET.csv (gitignored, ~65MB)
logs/                Append-only JSONL event streams (gitignored)
notebooks/           Original supplied SVM notebook (baseline reference)
```
