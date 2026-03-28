from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=5)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    content: Optional[str] = Field(default=None, min_length=5)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class ActionItemCreate(BaseModel):
    description: str = Field(min_length=3)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    model_config = ConfigDict(from_attributes=True)
