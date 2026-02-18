from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schema.tasks import PaginatedTasks, TaskCreate, TaskRead, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "Not Found", "details": {"id": f"Task {task_id} not found"}},
    )


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskRead:
    task = task_service.create_task(db, payload)
    # Pydantic's orm_mode will handle SQLAlchemy model → schema conversion.
    return TaskRead.from_orm(task)


@router.get(
    "",
    response_model=PaginatedTasks,
    summary="List tasks with filtering and pagination",
)
def list_tasks(
    completed: Optional[bool] = Query(
        None,
        description="Filter by completion state",
    ),
    priority: Optional[int] = Query(
        None,
        ge=1,
        le=5,
        description="Filter by priority level (1–5)",
    ),
    tags: Optional[str] = Query(
        None,
        description="CSV list of tags, e.g. ?tags=work,urgent",
    ),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedTasks:
    tag_list = (
        [t.strip() for t in tags.split(",") if t.strip()]
        if tags
        else None
    )
    tasks, total = task_service.list_tasks(
        db,
        completed=completed,
        priority=priority,
        tags=tag_list,
        limit=limit,
        offset=offset,
    )
    items = [TaskRead.from_orm(t) for t in tasks]
    return PaginatedTasks(total=total, items=items, limit=limit, offset=offset)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a single task by ID",
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> TaskRead:
    task = task_service.get_task(db, task_id)
    if not task:
        raise _not_found(task_id)
    return TaskRead.from_orm(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Partially update a task",
)
def patch_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskRead:
    task = task_service.get_task(db, task_id)
    if not task:
        raise _not_found(task_id)
    updated = task_service.update_task(db, task, payload)
    return TaskRead.from_orm(updated)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task (soft delete)",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> None:
    task = task_service.get_task(db, task_id)
    if not task:
        raise _not_found(task_id)
    task_service.soft_delete_task(db, task)
