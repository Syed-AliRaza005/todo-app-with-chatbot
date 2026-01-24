"""
Todo Reference Model for Todo App MCP Server

This module defines the data model for identifying specific tasks using natural language descriptors.
"""

from sqlmodel import SQLModel
from typing import Optional, Any, Dict
from enum import Enum
from datetime import datetime


class IdentifierType(str, Enum):
    """
    Types of ways to identify a task
    """
    TITLE_KEYWORD = "TITLE_KEYWORD"
    POSITION = "POSITION"
    CONTEXT_REFERENCE = "CONTEXT_REFERENCE"
    EXACT_ID = "EXACT_ID"


class TodoReference(SQLModel, table=False):
    """
    Identifies specific tasks using natural language descriptors (title keywords, position, context)
    """

    # How the task is identified
    identifier_type: IdentifierType

    # The identifying value (keyword, position number, context reference, UUID)
    value: str

    # Confidence level of the identification
    confidence: float

    # The actual task that was matched (when resolved)
    matched_task: Optional[Dict[str, Any]] = None

    # Timestamp when the reference was created
    timestamp: datetime

    # ID for database storage (if needed for history)
    id: Optional[str] = None

    def __init__(self, identifier_type: IdentifierType, value: str, confidence: float = 0.0,
                 matched_task: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize a TodoReference

        Args:
            identifier_type: How the task is identified
            value: The identifying value
            confidence: Confidence level of the identification
            matched_task: The actual task that was matched (when resolved)
        """
        super().__init__(
            identifier_type=identifier_type,
            value=value,
            confidence=confidence,
            matched_task=matched_task,
            timestamp=datetime.utcnow(),
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the todo reference to a dictionary representation

        Returns:
            Dictionary representation of the todo reference
        """
        return {
            "identifier_type": self.identifier_type.value if isinstance(self.identifier_type, Enum) else self.identifier_type,
            "value": self.value,
            "confidence": self.confidence,
            "matched_task": self.matched_task,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "id": self.id
        }

    def __repr__(self):
        """
        String representation of the todo reference
        """
        return f"TodoReference(type='{self.identifier_type}', value='{self.value}', confidence={self.confidence:.2f})"