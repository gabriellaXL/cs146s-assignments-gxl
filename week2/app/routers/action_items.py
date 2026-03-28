from __future__ import annotations

from typing import Callable, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemExtractRequest,
    ActionItemExtractResponse,
    ActionItemResponse,
    ExtractedActionItem,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


def _extract_with(
    payload: ActionItemExtractRequest,
    extractor: Callable[[str], list[str]],
) -> ActionItemExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extractor(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ActionItemExtractResponse(
        note_id=note_id,
        items=[ExtractedActionItem(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract", response_model=ActionItemExtractResponse)
def extract(payload: ActionItemExtractRequest) -> ActionItemExtractResponse:
    # AI-generated (TODO3): schema-driven extraction API contract.
    return _extract_with(payload, extract_action_items)


@router.post("/extract-llm", response_model=ActionItemExtractResponse)
def extract_llm(payload: ActionItemExtractRequest) -> ActionItemExtractResponse:
    # AI-generated (TODO4): LLM extraction endpoint used by frontend "Extract LLM" button.
    return _extract_with(payload, extract_action_items_llm)


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: Optional[int] = None) -> list[ActionItemResponse]:
    # AI-generated (TODO3): typed list response for stable client contract.
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    # AI-generated (TODO3): return 404 when target action item does not exist.
    updated = db.mark_action_item_done(action_item_id, payload.done)
    if not updated:
        raise HTTPException(status_code=404, detail="action item not found")
    return MarkDoneResponse(id=action_item_id, done=payload.done)
