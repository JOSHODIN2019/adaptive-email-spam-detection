import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import adaptive, drift, events, evaluation, feedback, health, predict
from app.core.state import build_app_state
from app.ml.preprocessing import ensure_nltk_data
from app.schemas.common import error

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
logger = logging.getLogger("spam_detection")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_nltk_data()
    app.state.app_state = build_app_state()
    yield


app = FastAPI(title="Adaptive Email Spam Detection System", lifespan=lifespan)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(feedback.router)
app.include_router(adaptive.router)
app.include_router(drift.router)
app.include_router(events.router)
app.include_router(evaluation.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    message = first.get("msg", "Invalid request")
    return JSONResponse(status_code=422, content=error("VALIDATION_ERROR", message))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=error("INTERNAL_ERROR", "An unexpected error occurred. See server logs for details."),
    )


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")


@app.get("/")
def serve_index():
    return FileResponse(str(FRONTEND_DIR / "templates" / "index.html"))
