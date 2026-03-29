from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

ModelT = TypeVar("ModelT")


def get_or_404(db: Session, model: type[ModelT], object_id: int, detail: str) -> ModelT:
    instance = db.get(model, object_id)
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return instance


def apply_sort(stmt: Select, model: type[ModelT], sort: str) -> Select:
    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    return stmt.order_by(order_fn(getattr(model, sort_field)))
