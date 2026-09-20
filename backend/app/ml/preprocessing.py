"""
Shared text preprocessing, faithfully extracted from
notebooks/Python SVM Spam Detection System.ipynb (Stage 2 + Stage 3 cells).

`clean_text` and `tokenize_stem_lemmatize` together reproduce the exact
per-email pipeline the notebook applies both during training-corpus
preparation (cells 9-15, 17, 22-24) and at custom/inference time (cell 38).

Frequent-word and rare-word pruning (notebook cells 20-21) are corpus-wide
statistics computed only once, over the full training corpus. They are
deliberately NOT part of this module: the notebook's own custom-email
prediction cell (38) does not re-apply them at inference time, so serving
code must not either. That corpus-fitting step lives in
scripts/train_static_model.py, where it belongs.
"""

import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

_REQUIRED_NLTK_PACKAGES = [
    "stopwords",
    "punkt",
    "punkt_tab",
    "wordnet",
    "omw-1.4",
    "averaged_perceptron_tagger",
    "averaged_perceptron_tagger_eng",
]


def ensure_nltk_data() -> None:
    """Download required NLTK corpora if missing. Safe to call on every
    startup: nltk.download() no-ops when data is already present. Must run
    at application startup, not just at build/deploy time - on platforms
    like Render, the build step and the running container can be separate
    filesystem layers, so data fetched during build is not guaranteed to
    exist wherever the app actually starts."""
    for package in _REQUIRED_NLTK_PACKAGES:
        nltk.download(package, quiet=True)

_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_ADDRESS_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
_PUNCTUATION_PATTERN = re.compile(r"[^\w\s]")
_NUMBER_PATTERN = re.compile(r"\d+")
_NON_ALPHA_PATTERN = re.compile(r"[^a-zA-Z\s]")
_WHITESPACE_PATTERN = re.compile(r"\s+")

_stop_words = None
_stemmer = None
_lemmatizer = None


def _get_stop_words() -> set:
    global _stop_words
    if _stop_words is None:
        _stop_words = set(stopwords.words("english"))
    return _stop_words


def _get_stemmer() -> PorterStemmer:
    global _stemmer
    if _stemmer is None:
        _stemmer = PorterStemmer()
    return _stemmer


def _get_lemmatizer() -> WordNetLemmatizer:
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = WordNetLemmatizer()
    return _lemmatizer


def clean_text(text: str) -> str:
    """Notebook Stage 2 (cells 9-15) + Stage 3 Step 1-2 (cells 17, 19), in order:
    strip HTML, URLs, email addresses, punctuation, numbers, non-alphabetic
    characters, collapse whitespace, lowercase, remove English stop words.
    """
    text = _HTML_TAG_PATTERN.sub(" ", str(text))
    text = _URL_PATTERN.sub(" ", text)
    text = _EMAIL_ADDRESS_PATTERN.sub(" ", text)
    text = _PUNCTUATION_PATTERN.sub(" ", text)
    text = _NUMBER_PATTERN.sub(" ", text)
    text = _NON_ALPHA_PATTERN.sub(" ", text)
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()
    text = text.lower()

    stop_words = _get_stop_words()
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)


def tokenize_stem_lemmatize(text: str) -> str:
    """Notebook Stage 3 Step 5-9 (cells 22-26): tokenize, Porter-stem,
    WordNet-lemmatize, rejoin into the final `processed_text` string that is
    fed to the TF-IDF vectorizer.
    """
    tokens = word_tokenize(text)
    stemmer = _get_stemmer()
    tokens = [stemmer.stem(w) for w in tokens]
    lemmatizer = _get_lemmatizer()
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    return " ".join(tokens)


def preprocess_for_inference(email_text: str) -> str:
    """Full pipeline for a single email at prediction time, matching
    notebook cell 38 exactly (no frequent/rare-word pruning).
    """
    cleaned = clean_text(email_text)
    return tokenize_stem_lemmatize(cleaned)
