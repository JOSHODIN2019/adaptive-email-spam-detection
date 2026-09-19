import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.preprocessing import clean_text, preprocess_for_inference, tokenize_stem_lemmatize


def test_clean_text_strips_html_tags():
    assert "<div>" not in clean_text("<div>hello</div>")


def test_clean_text_strips_urls():
    result = clean_text("visit http://example.com or www.example.com now")
    assert "http" not in result
    assert "example.com" not in result


def test_clean_text_strips_email_addresses():
    result = clean_text("contact me at user@example.com today")
    assert "@" not in result
    assert "user" not in result


def test_clean_text_removes_stop_words():
    result = clean_text("this is a test of the system")
    words = result.split()
    assert "is" not in words
    assert "the" not in words
    assert "test" in words


def test_clean_text_lowercases():
    assert clean_text("HELLO World") == clean_text("hello world")


def test_tokenize_stem_lemmatize_returns_string():
    result = tokenize_stem_lemmatize("running quickly to the stores")
    assert isinstance(result, str)
    assert len(result) > 0


def test_preprocess_for_inference_end_to_end():
    result = preprocess_for_inference("<b>Click here</b> to win $1,000,000 now! Visit http://spam.com")
    assert "<b>" not in result
    assert "http" not in result
    assert isinstance(result, str)
