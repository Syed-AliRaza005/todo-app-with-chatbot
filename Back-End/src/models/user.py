from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid


class User(SQLModel, table=True):
    """User model for authentication and task ownership"""

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    email: str = Field(unique=True, max_length=255, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    name: Optional[str] = Field(max_length=255, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship - User can have many tasks
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete="all")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
