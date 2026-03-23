from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


# AI-generated (TODO3): centralized app configuration model + loader.
@dataclass(frozen=True)
class Settings:
    app_title: str
    frontend_dir: Path


def get_settings() -> Settings:
    # AI-generated (TODO3): resolve project paths and env-based app title in one place.
    base_dir = Path(__file__).resolve().parents[1]
    frontend_dir = base_dir / "frontend"
    app_title = os.getenv("APP_TITLE", "Action Item Extractor")
    return Settings(app_title=app_title, frontend_dir=frontend_dir)
