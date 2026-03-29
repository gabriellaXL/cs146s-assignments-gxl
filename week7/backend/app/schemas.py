from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

NoteSort = Literal[
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "title",
    "-title",
]
ActionItemSort = Literal[
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "description",
    "-description",
    "completed",
    "-completed",
]
ProjectSort = Literal[
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "name",
    "-name",
]
ExtractionTrigger = Literal["tagged", "checkbox", "commitment", "imperative"]
ExtractionConfidence = Literal["high", "medium"]


class NoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class NotePatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=5000)


class ProjectReferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ActionItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str = Field(min_length=1, max_length=5000)
    project_id: int | None = None


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool
    project_id: int | None = None
    project: ProjectReferenceRead | None = None
    created_at: datetime
    updated_at: datetime


class ActionItemPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str | None = Field(default=None, min_length=1, max_length=5000)
    completed: bool | None = None
    project_id: int | None = None


class ProjectActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool
    project_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ProjectPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    action_item_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProjectDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    action_items: list[ProjectActionItemRead]
    created_at: datetime
    updated_at: datetime


class ExtractedActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str
    source_line: int
    trigger: ExtractionTrigger
    confidence: ExtractionConfidence
    due_hint: str | None = None
    assignee_hint: str | None = None


class ExtractedActionItemsRead(BaseModel):
    note_id: int
    count: int
    items: list[ExtractedActionItemRead]
