"""
Todo Operation Model for Todo App MCP Server

This module defines the data model for representing an action to be taken on a todo task.
"""

from sqlmodel import SQLModel
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import UUID


class OperationType(str, Enum):
    """
    Types of operations that can be performed on todo tasks
    """
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    COMPLETE = "COMPLETE"
    MARK_INCOMPLETE = "MARK_INCOMPLETE"


class TodoOperation(SQLModel, table=False):
    """
    Represents the action to be taken on a todo task
    """

    # Type of operation to perform
    operation_type: OperationType

    # Target task to operate on (optional, as some operations don't require a specific task)
    target_task_id: Optional[UUID] = None

    # Additional parameters for the operation
    parameters: Optional[Dict[str, Any]] = {}

    # User context for the operation
    user_context: Optional[Dict[str, Any]] = {}

    # Timestamp when the operation was created
    timestamp: datetime

    # ID for database storage (if needed for history)
    id: Optional[UUID] = None

    def __init__(self, operation_type: OperationType, target_task_id: Optional[UUID] = None,
                 parameters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize a TodoOperation

        Args:
            operation_type: The type of operation to perform
            target_task_id: The ID of the target task (if applicable)
            parameters: Additional parameters for the operation
            user_context: Information about the current user session
        """
        super().__init__(
            operation_type=operation_type,
            target_task_id=target_task_id,
            parameters=parameters or {},
            user_context=user_context or {},
            timestamp=datetime.utcnow(),
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the operation to a dictionary representation

        Returns:
            Dictionary representation of the operation
        """
        return {
            "operation_type": self.operation_type.value if isinstance(self.operation_type, Enum) else self.operation_type,
            "target_task_id": str(self.target_task_id) if self.target_task_id else None,
            "parameters": self.parameters,
            "user_context": self.user_context,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "id": str(self.id) if self.id else None
        }

    def __repr__(self):
        """
        String representation of the operation
        """
        return f"TodoOperation(type='{self.operation_type}', target_task_id='{self.target_task_id}')"