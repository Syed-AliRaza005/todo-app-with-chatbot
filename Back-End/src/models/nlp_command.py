"""
Natural Language Command Model for Todo App MCP Server

This module defines the data model for representing a user's natural language command
that needs to be parsed for todo operations.
"""

from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4


class NaturalLanguageCommand(SQLModel, table=False):
    """
    Represents a user's spoken or typed command that needs to be parsed for todo operations
    """

    # Raw input from the user
    raw_input: str

    # User ID of the person issuing the command
    user_id: str

    # Parsed intent (will be populated after processing)
    parsed_intent: Optional[str] = None

    # Extracted parameters from the command
    extracted_parameters: Optional[Dict[str, Any]] = {}

    # Detected language of the input
    language_code: Optional[str] = "en"

    # Confidence score of the intent classification
    confidence_score: Optional[float] = 0.0

    # Timestamp when the command was received
    timestamp: datetime

    # Session context for the command
    session_context: Optional[Dict[str, Any]] = {}

    # ID for database storage (if needed for history)
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    def __init__(self, raw_input: str, user_id: str, session_context: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize a NaturalLanguageCommand

        Args:
            raw_input: The original user input
            user_id: ID of the user issuing the command
            session_context: Additional context from the current session
        """
        super().__init__(
            raw_input=raw_input,
            user_id=user_id,
            session_context=session_context or {},
            timestamp=datetime.utcnow(),
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the command to a dictionary representation

        Returns:
            Dictionary representation of the command
        """
        return {
            "raw_input": self.raw_input,
            "user_id": self.user_id,
            "parsed_intent": self.parsed_intent,
            "extracted_parameters": self.extracted_parameters,
            "language_code": self.language_code,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "session_context": self.session_context,
            "id": str(self.id) if self.id else None
        }

    def __repr__(self):
        """
        String representation of the command
        """
        return f"NaturalLanguageCommand(raw_input='{self.raw_input[:50]}...', user_id='{self.user_id}')"