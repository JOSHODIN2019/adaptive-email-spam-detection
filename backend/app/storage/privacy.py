"""Stage 43 — Privacy helpers. Human-readable event logs (predictions.jsonl,
feedback.jsonl) must not contain full email bodies by default
(PROJECT_MEMORY.md §14), so every event writer routes text through here."""

import hashlib

PREVIEW_LENGTH = 120


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def safe_preview(text: str, log_full_body: bool) -> dict:
    if log_full_body:
        return {"body_preview": text, "content_hash": content_hash(text), "full_body_logged": True}
    trimmed = text.strip().replace("\n", " ")
    preview = trimmed[:PREVIEW_LENGTH] + ("..." if len(trimmed) > PREVIEW_LENGTH else "")
    return {"body_preview": preview, "content_hash": content_hash(text), "full_body_logged": False}
