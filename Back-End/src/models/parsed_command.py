"""
Parsed Command Model for Todo App MCP Server

This module defines the data model for containing extracted intent and parameters
from natural language input.
"""

from sqlmodel import SQLModel
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
from .todo_reference import TodoReference


class IntentType(str, Enum):
    """
    Types of intents that can be identified from natural language commands
    """
    ADD_TODO = "ADD_TODO"
    DELETE_TODO = "DELETE_TODO"
    UPDATE_TODO = "UPDATE_TODO"
    COMPLETE_TODO = "COMPLETE_TODO"
    LIST_TODOS = "LIST_TODOS"


class ParsedCommand(SQLModel, table=False):
    """
    Contains extracted intent and parameters from natural language input
    """

    # The identified intent
    intent: Optional[IntentType] = None

    # Identified entities in the command
    entities: List[Dict[str, Any]]

    # Confidence level of the parsing
    confidence: float

    # The specific action to take based on intent and entities
    resolved_action: str

    # Raw input that was parsed
    raw_input: str

    # Detected language of the input
    language_code: str

    # Timestamp when the command was parsed
    timestamp: datetime

    # Context reference (for "that one", "the last one", etc.)
    context_reference: Optional[TodoReference] = None

    # ID for database storage (if needed for history)
    id: Optional[str] = None

    def __init__(self, intent: Optional[IntentType] = None, entities: Optional[List[Dict[str, Any]]] = None,
                 confidence: float = 0.0, resolved_action: str = "", raw_input: str = "",
                 language_code: str = "en", **kwargs):
        """
        Initialize a ParsedCommand

        Args:
            intent: The identified intent
            entities: Identified entities in the command
            confidence: Confidence level of the parsing
            resolved_action: The specific action to take based on intent and entities
            raw_input: The raw input that was parsed
            language_code: Detected language of the input
        """
        # Handle timestamp assignment carefully to avoid conflicts
        timestamp_val = datetime.utcnow()

        super().__init__(
            intent=intent,
            entities=entities or [],
            confidence=confidence,
            resolved_action=resolved_action,
            raw_input=raw_input,
            language_code=language_code,
            timestamp=timestamp_val,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the parsed command to a dictionary representation

        Returns:
            Dictionary representation of the parsed command
        """
        return {
            "intent": self.intent.value if self.intent and isinstance(self.intent, Enum) else self.intent,
            "entities": self.entities,
            "confidence": self.confidence,
            "resolved_action": self.resolved_action,
            "raw_input": self.raw_input,
            "language_code": self.language_code,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "context_reference": self.context_reference.to_dict() if self.context_reference else None,
            "id": self.id
        }

    def __repr__(self):
        """
        String representation of the parsed command
        """
        return f"ParsedCommand(intent='{self.intent}', confidence={self.confidence:.2f}, raw_input='{self.raw_input[:50]}...')"