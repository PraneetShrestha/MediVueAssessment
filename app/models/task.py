from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.db import Base


task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        # Frequently used in filtering; add a composite index.
        Index("ix_tasks_priority_completed", "priority", "completed"),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, nullable=False, index=True)
    due_date = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=False, default=False, index=True)

    # Soft-delete flag so we can keep history while hiding from API queries.
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    tags = relationship(
        "Tag",
        secondary=task_tags,
        back_populates="tasks",
        lazy="joined",
    )
