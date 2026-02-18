from datetime import date
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.tags import Tag
from app.schema.tasks import TaskCreate, TaskUpdate


def _get_or_create_tags(db: Session, tag_names: Iterable[str]) -> List[Tag]:
    """Fetch existing tags by name or create them if they don't exist."""
    cleaned = {name.strip().lower() for name in tag_names if name.strip()}
    if not cleaned:
        return []

    existing = (
        db.query(Tag)
        .filter(func.lower(Tag.name).in_(list(cleaned)))
        .all()
    )
    existing_by_name = {t.name.lower(): t for t in existing}

    tags: List[Tag] = []
    for name in cleaned:
        found = existing_by_name.get(name)
        if found:
            tags.append(found)
        else:
            tag = Tag(name=name)
            db.add(tag)
            tags.append(tag)

    return tags


def create_task(db: Session, data: TaskCreate) -> Task:
    tags = _get_or_create_tags(db, data.tags)
    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        tags=tags,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    *,
    completed: Optional[bool],
    priority: Optional[int],
    tags: Optional[List[str]],
    limit: int,
    offset: int,
) -> Tuple[List[Task], int]:
    query = db.query(Task).filter(Task.is_deleted.is_(False))

    if completed is not None:
        query = query.filter(Task.completed.is_(completed))

    if priority is not None:
        query = query.filter(Task.priority == priority)

    if tags:
        cleaned = [t.strip().lower() for t in tags if t.strip()]
        if cleaned:
            query = query.join(Task.tags).filter(func.lower(Tag.name).in_(cleaned))

    total = query.distinct().count()

    tasks = (
        query.order_by(Task.due_date.asc(), Task.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return tasks, total


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.is_deleted.is_(False))
        .first()
    )


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    payload = data.dict(exclude_unset=True)

    if "tags" in payload:
        tag_names = payload.pop("tags") or []
        task.tags = _get_or_create_tags(db, tag_names)

    for field, value in payload.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def soft_delete_task(db: Session, task: Task) -> None:
    task.is_deleted = True
    db.add(task)
    db.commit()
