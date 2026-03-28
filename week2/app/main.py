from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import DatabaseError, init_db
from .routers import action_items, notes

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # AI-generated (TODO3): move DB initialization into app lifecycle (no import-time side effects).
    init_db()
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)


@app.exception_handler(DatabaseError)
async def handle_database_error(_: Request, exc: DatabaseError) -> JSONResponse:
    # AI-generated (TODO3): global DB error handler for consistent 500 responses.
    logger.exception("database request failed: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "database operation failed"},
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html_path = settings.frontend_dir / "index.html"
    return html_path.read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)


static_dir = settings.frontend_dir
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
