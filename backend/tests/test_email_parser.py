import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.email_parser import EmailParseError, parse_eml_bytes


def test_parse_simple_eml():
    raw = (
        b"From: a@example.com\r\n"
        b"To: b@example.com\r\n"
        b"Subject: Test Subject\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"\r\n"
        b"Hello, this is the body.\r\n"
    )
    result = parse_eml_bytes(raw)
    assert result["subject"] == "Test Subject"
    assert "Hello, this is the body." in result["body"]


def test_parse_empty_bytes_raises():
    with pytest.raises(EmailParseError):
        parse_eml_bytes(b"")


def test_parse_no_readable_content_raises():
    raw = b"From: a@example.com\r\nSubject: Empty\r\n\r\n"
    with pytest.raises(EmailParseError):
        parse_eml_bytes(raw)


def test_parse_multipart_eml_prefers_plain_text():
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Multipart\r\n"
        b'Content-Type: multipart/alternative; boundary="BOUNDARY"\r\n'
        b"\r\n"
        b"--BOUNDARY\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"\r\n"
        b"Plain text body\r\n"
        b"--BOUNDARY\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"\r\n"
        b"<p>HTML body</p>\r\n"
        b"--BOUNDARY--\r\n"
    )
    result = parse_eml_bytes(raw)
    assert "Plain text body" in result["body"]
