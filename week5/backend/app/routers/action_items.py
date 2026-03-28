
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import ActionItemCreate, ActionItemRead, BulkCompleteRequest, BulkCompleteResponse

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    completed: bool | None = None,
    db: Session = Depends(get_db),
) -> list[ActionItemRead]:
    """Return all action items, optionally filtered by completion status."""
    stmt = select(ActionItem)
    if completed is not None:
        stmt = stmt.where(ActionItem.completed == completed)
    rows = db.execute(stmt).scalars().all()
    return [ActionItemRead.model_validate(row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    """Create a new action item."""
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.post("/bulk-complete", response_model=BulkCompleteResponse)
def bulk_complete(
    payload: BulkCompleteRequest,
    db: Session = Depends(get_db),
) -> BulkCompleteResponse:
    """Mark a list of action items as completed in a single transaction.

    Raises 404 if *any* supplied ID does not exist, rolling back the entire
    operation so the caller receives an atomic all-or-nothing guarantee.
    """
    unique_ids = list(dict.fromkeys(payload.ids))  # deduplicate, preserve order

    rows = db.execute(select(ActionItem).where(ActionItem.id.in_(unique_ids))).scalars().all()

    found_ids = {row.id for row in rows}
    missing = sorted(set(unique_ids) - found_ids)
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Action items not found: {missing}",
        )

    for item in rows:
        item.completed = True

    db.flush()

    completed_ids = sorted(found_ids)
    return BulkCompleteResponse(updated=len(rows), ids=completed_ids)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    """Mark a single action item as completed."""
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)
