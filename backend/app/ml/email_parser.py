"""Stage 09 — Raw Email Parser. Supports plain subject/body input and
.eml file upload, extracting a plain-text body from multipart messages."""

from email import message_from_bytes
from email.message import Message


class EmailParseError(ValueError):
    pass


def extract_text_body(msg: Message) -> str:
    if msg.is_multipart():
        parts = []
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition") or "")
            if "attachment" in disposition:
                continue
            if content_type == "text/plain":
                parts.append(_decode_payload(part))
            elif content_type == "text/html" and not parts:
                parts.append(_decode_payload(part))
        return "\n".join(p for p in parts if p)
    return _decode_payload(msg)


def _decode_payload(part: Message) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        return str(part.get_payload() or "")
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return payload.decode("utf-8", errors="replace")


def parse_eml_bytes(raw_bytes: bytes) -> dict:
    """Parse raw .eml bytes into {subject, body}. Raises EmailParseError on
    malformed content rather than executing or trusting any embedded
    active content."""
    if not raw_bytes:
        raise EmailParseError("Uploaded .eml file is empty")

    try:
        msg = message_from_bytes(raw_bytes)
    except Exception as exc:  # noqa: BLE001 - surfaced as a clean 400 upstream
        raise EmailParseError(f"Could not parse .eml file: {exc}") from exc

    subject = msg.get("Subject", "") or ""
    body = extract_text_body(msg)

    if not body.strip():
        raise EmailParseError("Parsed .eml file has no readable text content")

    return {"subject": subject, "body": body}
