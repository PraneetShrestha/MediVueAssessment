from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    # many-to-many backref; defined in app.models.task
    tasks = relationship(
        "Task",
        secondary="task_tags",
        back_populates="tags",
        lazy="joined",
    )
