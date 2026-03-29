from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..api_utils import apply_sort, get_or_404
from ..db import get_db
from ..models import ActionItem, Project
from ..schemas import ActionItemCreate, ActionItemPatch, ActionItemRead, ActionItemSort

router = APIRouter(prefix="/action-items", tags=["action_items"])

PaginationSkip = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=200)]


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    db: Session = Depends(get_db),
    completed: bool | None = None,
    project_id: int | None = None,
    skip: PaginationSkip = 0,
    limit: PaginationLimit = 50,
    sort: ActionItemSort = "-created_at",
) -> list[ActionItemRead]:
    stmt = select(ActionItem).options(selectinload(ActionItem.project))
    if completed is not None:
        stmt = stmt.where(ActionItem.completed.is_(completed))
    if project_id is not None:
        stmt = stmt.where(ActionItem.project_id == project_id)

    stmt = apply_sort(stmt, ActionItem, sort)
    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [ActionItemRead.model_validate(row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    if payload.project_id is not None:
        get_or_404(db, Project, payload.project_id, "Project not found")

    item = ActionItem(
        description=payload.description,
        completed=False,
        project_id=payload.project_id,
    )
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = get_or_404(db, ActionItem, item_id, "Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ActionItemRead)
def patch_item(
    item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)
) -> ActionItemRead:
    item = get_or_404(db, ActionItem, item_id, "Action item not found")
    if payload.description is not None:
        item.description = payload.description
    if payload.completed is not None:
        item.completed = payload.completed
    if "project_id" in payload.model_fields_set:
        if payload.project_id is not None:
            get_or_404(db, Project, payload.project_id, "Project not found")
        item.project_id = payload.project_id
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.get("/{item_id}", response_model=ActionItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    stmt = select(ActionItem).where(ActionItem.id == item_id).options(selectinload(ActionItem.project))
    item = db.execute(stmt).scalar_one_or_none()
    if item is None:
        return get_or_404(db, ActionItem, item_id, "Action item not found")
    return ActionItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    item = get_or_404(db, ActionItem, item_id, "Action item not found")
    db.delete(item)
    db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
