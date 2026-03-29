from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_utils import apply_sort, get_or_404
from ..db import get_db
from ..models import Note
from ..schemas import (
    ExtractedActionItemRead,
    ExtractedActionItemsRead,
    NoteCreate,
    NotePatch,
    NoteRead,
    NoteSort,
)
from ..services.extract import analyze_action_items

router = APIRouter(prefix="/notes", tags=["notes"])

PaginationSkip = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=200)]


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    skip: PaginationSkip = 0,
    limit: PaginationLimit = 50,
    sort: NoteSort = "-created_at",
) -> list[NoteRead]:
    stmt = select(Note)
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))

    stmt = apply_sort(stmt, Note, sort)
    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = get_or_404(db, Note, note_id, "Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = get_or_404(db, Note, note_id, "Note not found")
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = get_or_404(db, Note, note_id, "Note not found")
    db.delete(note)
    db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{note_id}/extract-action-items", response_model=ExtractedActionItemsRead)
def extract_note_action_items(
    note_id: int, db: Session = Depends(get_db)
) -> ExtractedActionItemsRead:
    note = get_or_404(db, Note, note_id, "Note not found")
    analyzed_items = analyze_action_items(note.content)
    items = [ExtractedActionItemRead.model_validate(item) for item in analyzed_items]
    return ExtractedActionItemsRead(
        note_id=note.id,
        count=len(items),
        items=items,
    )
