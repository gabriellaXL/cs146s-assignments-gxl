from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True


class BulkCompleteRequest(BaseModel):
    """Request body for bulk-completing action items by ID."""

    ids: list[int] = Field(
        ..., min_length=1, description="Non-empty list of action item IDs to mark complete"
    )


class BulkCompleteResponse(BaseModel):
    """Result of a bulk-complete operation."""

    updated: int = Field(..., description="Number of items that were updated")
    ids: list[int] = Field(..., description="IDs of items that were marked complete")
