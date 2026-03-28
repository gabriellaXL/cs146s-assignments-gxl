from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

# Reusable constrained string types (Pydantic v2 pattern).
# strip_whitespace trims surrounding whitespace before validation,
# so "   " becomes "" and fails min_length=1 with a clear 422.
TitleStr = Annotated[str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)]
ContentStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
DescStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


class NoteCreate(BaseModel):
    title: TitleStr
    content: ContentStr


class NoteUpdate(BaseModel):
    """Full replacement payload for PUT /notes/{id}."""

    title: TitleStr
    content: ContentStr


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    model_config = {"from_attributes": True}


class ActionItemCreate(BaseModel):
    description: DescStr


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    model_config = {"from_attributes": True}


class BulkCompleteRequest(BaseModel):
    """Request body for bulk-completing action items by ID."""

    ids: list[int] = Field(
        ..., min_length=1, description="Non-empty list of action item IDs to mark complete"
    )


class BulkCompleteResponse(BaseModel):
    """Result of a bulk-complete operation."""

    updated: int = Field(..., description="Number of items that were updated")
    ids: list[int] = Field(..., description="IDs of items that were marked complete")
