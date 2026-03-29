from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..api_utils import apply_sort, get_or_404
from ..db import get_db
from ..models import ActionItem, Project
from ..schemas import ProjectCreate, ProjectDetailRead, ProjectPatch, ProjectRead, ProjectSort

router = APIRouter(prefix="/projects", tags=["projects"])

PaginationSkip = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=200)]


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    q: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    skip: PaginationSkip = 0,
    limit: PaginationLimit = 50,
    sort: ProjectSort = "name",
) -> list[ProjectRead]:
    stmt = select(Project)
    if q:
        stmt = stmt.where(Project.name.contains(q))

    stmt = apply_sort(stmt, Project, sort)
    projects = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [_serialize_project_summary(db, project) for project in projects]


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    existing = db.execute(select(Project).where(Project.name == payload.name)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name already exists",
        )

    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.flush()
    db.refresh(project)
    return _serialize_project_summary(db, project)


@router.get("/{project_id}", response_model=ProjectDetailRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectDetailRead:
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.action_items))
    )
    project = db.execute(stmt).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectDetailRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def patch_project(
    project_id: int, payload: ProjectPatch, db: Session = Depends(get_db)
) -> ProjectRead:
    project = get_or_404(db, Project, project_id, "Project not found")
    if payload.name is not None and payload.name != project.name:
        existing = db.execute(select(Project).where(Project.name == payload.name)).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project name already exists",
            )
        project.name = payload.name
    if "description" in payload.model_fields_set:
        project.description = payload.description

    db.add(project)
    db.flush()
    db.refresh(project)
    return _serialize_project_summary(db, project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> Response:
    project = get_or_404(db, Project, project_id, "Project not found")
    for action_item in project.action_items:
        action_item.project_id = None
        db.add(action_item)

    db.delete(project)
    db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _serialize_project_summary(db: Session, project: Project) -> ProjectRead:
    action_item_count = db.execute(
        select(func.count(ActionItem.id)).where(ActionItem.project_id == project.id)
    ).scalar_one()
    return ProjectRead(
        id=project.id,
        name=project.name,
        description=project.description,
        action_item_count=action_item_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
