from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

NoteStatus = Literal["active", "blocked", "archived"]
NoteSort = Literal[
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "title",
    "-title",
    "status",
    "-status",
]


class NoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=120)
    content: str = Field(min_length=10, max_length=5000)
    status: NoteStatus = "active"


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    status: NoteStatus
    created_at: datetime
    updated_at: datetime


class NotePatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=3, max_length=120)
    content: str | None = Field(default=None, min_length=10, max_length=5000)
    status: NoteStatus | None = None
