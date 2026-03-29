from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_schema_updates, apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router
from .routers import projects as projects_router

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    apply_schema_updates()
    apply_seed_if_needed()
    yield


app = FastAPI(title="Modern Software Dev Starter (Week 7)", version="0.1.0", lifespan=lifespan)

# Mount static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("frontend/index.html")


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
app.include_router(projects_router.router)
