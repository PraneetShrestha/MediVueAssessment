from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, validator, ConfigDict

class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: int = Field(..., ge=1, le=5, description="1–5, where 5 is highest")
    due_date: date
    tags: List[str] = Field(default_factory=list)

    @validator("due_date")
    def due_date_not_in_past(cls, v: date) -> date:
        today = date.today()
        if v < today:
            raise ValueError("due_date cannot be in the past")
        return v


class TaskCreate(TaskBase):
    pass
    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)

    @validator("due_date")
    def update_due_date_not_in_past(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        today = date.today()
        if v < today:
            raise ValueError("due_date cannot be in the past")
        return v


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    due_date: date
    completed: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def tags_to_strings(cls, v: object) -> List[str]:
        """Convert ORM Tag objects to tag name strings when building from a Task."""
        if not isinstance(v, list):
            return []
        return [x.name if hasattr(x, "name") else str(x) for x in v]


class PaginatedTasks(BaseModel):
    total: int
    items: List[TaskRead]
    limit: int
    offset: int
    
    model_config = ConfigDict(from_attributes=True)
