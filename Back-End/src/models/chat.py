from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum


class ChatSessionStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ChatMessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(SQLModel, table=True):
    __tablename__ = "chatsession"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    status: ChatSessionStatus = Field(default=ChatSessionStatus.ACTIVE)
    last_message: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["ChatMessage"] = Relationship(back_populates="session")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chatmessage"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="chatsession.id", ondelete="CASCADE")
    sender: ChatMessageType = Field(default=ChatMessageType.USER)
    content: str = Field(sa_column_kwargs={"nullable": False})
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="sent", max_length=50)  # sent, delivered, read, etc.

    # Relationship to session
    session: ChatSession = Relationship(back_populates="messages")