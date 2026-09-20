"""Vercel serverless entrypoint. Exposes the existing FastAPI app as an
ASGI callable Vercel's Python runtime can serve, without restructuring
the backend/app package layout used by every other deployment target
(local dev, Render).

Known limitation (see PROJECT_MEMORY.md §24): Vercel serverless
functions have no persistent filesystem across invocations, so
feedback-driven adaptive-model updates will not persist between
requests here the way they do locally or on Render.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402
