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

python3 -c "
import nltk
for pkg in ['punkt','punkt_tab','stopwords','wordnet','omw-1.4',
            'averaged_perceptron_tagger','averaged_perceptron_tagger_eng']:
    nltk.download(pkg, quiet=True)
"
```

## Train the models (first run only)

The dataset (`data/raw/LEVI_DATASET.csv`) and trained artifacts are
gitignored — regenerate them locally:

```bash
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
