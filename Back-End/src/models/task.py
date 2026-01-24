from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid


class Task(SQLModel, table=True):
    """Task model for todo items owned by users"""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False
    )
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="Pending", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship - Task belongs to one user
    user: "User" = Relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
