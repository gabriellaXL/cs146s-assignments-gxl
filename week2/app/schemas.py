from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# AI-generated (TODO3): explicit API contracts for request/response validation.
class NoteCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


class ActionItemExtractRequest(BaseModel):
    text: str = Field(min_length=1)
    save_note: bool = False


class ExtractedActionItem(BaseModel):
    id: int
    text: str


class ActionItemExtractResponse(BaseModel):
    note_id: Optional[int]
    items: list[ExtractedActionItem]


class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
