"""
Console Todo Application - Data Models

This module contains the core data structures, validation logic,
and business logic for the todo application.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, ClassVar


# ============================================================================
# Custom Exceptions (T005)
# ============================================================================

class TodoError(Exception):
    """Base exception for all todo application errors."""
    pass


class ValidationError(TodoError):
    """Raised when data validation fails."""
    pass


class TaskNotFoundError(TodoError):
    """Raised when a task ID doesn't exist."""
    pass


class StorageError(TodoError):
    """Raised when file I/O operations fail."""
    pass


# ============================================================================
# Task Status Enum (T006)
# ============================================================================

class TaskStatus(str, Enum):
    """Enumeration of possible task statuses."""
    PENDING = "Pending"
    COMPLETED = "Completed"


# ============================================================================
# Validation Functions (T007)
# ============================================================================

def validate_title(title: str) -> str:
    """
    Validates and normalizes task title.

    Rules:
    - Must not be empty after stripping whitespace
    - Length: 1-1000 characters after stripping
    - Leading/trailing whitespace is removed

    Args:
        title: Task title to validate

    Returns:
        Cleaned and validated title

    Raises:
        ValidationError: If title is empty or too long
    """
    cleaned = title.strip()
    if not cleaned:
        raise ValidationError("Title cannot be empty")
    if len(cleaned) > 1000:
        raise ValidationError("Title cannot exceed 1000 characters")
    return cleaned


def validate_description(description: str) -> str:
    """
    Validates and normalizes task description.

    Rules:
    - Length: 0-1000 characters after stripping
    - Leading/trailing whitespace is removed
    - Empty descriptions are allowed

    Args:
        description: Task description to validate

    Returns:
        Cleaned and validated description

    Raises:
        ValidationError: If description is too long
    """
    cleaned = description.strip()
    if len(cleaned) > 1000:
        raise ValidationError("Description cannot exceed 1000 characters")
    return cleaned


def validate_status(status: str) -> TaskStatus:
    """
    Validates task status.

    Rules:
    - Must be exactly "Pending" or "Completed" (case-sensitive)

    Args:
        status: Status string to validate

    Returns:
        TaskStatus enum value

    Raises:
        ValidationError: If status is invalid
    """
    try:
        return TaskStatus(status)
    except ValueError:
        raise ValidationError(f"Status must be 'Pending' or 'Completed', got: {status}")


def validate_timestamp(timestamp: str) -> str:
    """
    Validates timestamp format.

    Rules:
    - Format: YYYY-MM-DD HH:MM:SS
    - Must be parseable as datetime
    - No timezone component

    Args:
        timestamp: Timestamp string to validate

    Returns:
        Valid timestamp string

    Raises:
        ValidationError: If timestamp format is invalid
    """
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    try:
        datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        return timestamp
    except ValueError:
        raise ValidationError(f"Invalid timestamp format. Expected: YYYY-MM-DD HH:MM:SS")


# ============================================================================
# Task Entity (T008-T010)
# ============================================================================

@dataclass
class Task:
    """
    Represents a single todo item.

    Attributes:
        id: Unique task identifier (immutable)
        title: Task title (1-1000 chars)
        description: Task description (0-1000 chars)
        status: Task status (Pending or Completed)
        created_at: Creation timestamp (immutable, YYYY-MM-DD HH:MM:SS)
    """
    id: int
    title: str
    description: str
    status: str
    created_at: str

    # Class constant for timestamp formatting
    TIMESTAMP_FORMAT: ClassVar[str] = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def create(cls, id: int, title: str, description: str) -> 'Task':
        """
        Factory method for creating new tasks with validation.

        Args:
            id: Unique task identifier (from counter)
            title: Task title (will be validated and normalized)
            description: Task description (will be validated and normalized)

        Returns:
            Task instance with status="Pending" and current timestamp

        Raises:
            ValidationError: If validation fails
        """
        return cls(
            id=id,
            title=validate_title(title),
            description=validate_description(description),
            status=TaskStatus.PENDING.value,
            created_at=datetime.now().strftime(cls.TIMESTAMP_FORMAT)
        )

    def mark_completed(self) -> 'Task':
        """
        Creates a new Task instance with Completed status.

        Returns:
            New Task instance (immutable update pattern)
        """
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            status=TaskStatus.COMPLETED.value,
            created_at=self.created_at
        )

    def update_details(self, title: str, description: str) -> 'Task':
        """
        Creates a new Task instance with updated title/description.

        Args:
            title: New title (will be validated)
            description: New description (will be validated)

        Returns:
            New Task instance with updated fields

        Raises:
            ValidationError: If validation fails
        """
        return Task(
            id=self.id,
            title=validate_title(title),
            description=validate_description(description),
            status=self.status,
            created_at=self.created_at
        )

    def to_dict(self) -> dict:
        """Serializes task to dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """
        Deserializes task from dictionary (from JSON storage).

        Args:
            data: Dictionary with task fields

        Returns:
            Task instance

        Raises:
            ValidationError: If data is invalid
        """
        # Validate stored data
        validate_timestamp(data["created_at"])
        validate_status(data["status"])

        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=data["status"],
            created_at=data["created_at"]
        )


# ============================================================================
# TaskCollection Entity (T011-T013)
# ============================================================================

@dataclass
class TaskCollection:
    """
    Manages task collection and ID counter.

    Ensures ID stability and validates invariants.

    Attributes:
        next_id: Counter for next task ID (never decrements except on clear)
        tasks: List of all tasks (may have gaps in IDs)
    """
    next_id: int
    tasks: List[Task]

    def __post_init__(self):
        """Validates invariants after initialization."""
        # Validate next_id
        if self.next_id < 1:
            raise ValidationError("next_id must be at least 1")

        # Validate next_id is greater than max task ID
        if self.tasks:
            max_id = max(task.id for task in self.tasks)
            if self.next_id <= max_id:
                raise ValidationError(
                    f"next_id ({self.next_id}) must be greater than max task ID ({max_id})"
                )

        # Check ID uniqueness
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValidationError("Duplicate task IDs detected")

    def add_task(self, title: str, description: str) -> 'TaskCollection':
        """
        Creates new collection with added task.

        Args:
            title: Task title
            description: Task description

        Returns:
            New TaskCollection with incremented next_id
        """
        new_task = Task.create(self.next_id, title, description)
        return TaskCollection(
            next_id=self.next_id + 1,
            tasks=self.tasks + [new_task]
        )

    def get_task(self, task_id: int) -> Optional[Task]:
        """Finds task by ID or returns None."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: str, description: str) -> 'TaskCollection':
        """
        Creates new collection with updated task.

        Args:
            task_id: ID of task to update
            title: New title
            description: New description

        Returns:
            New TaskCollection with updated task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        updated_tasks = []
        found = False

        for task in self.tasks:
            if task.id == task_id:
                updated_tasks.append(task.update_details(title, description))
                found = True
            else:
                updated_tasks.append(task)

        if not found:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        return TaskCollection(next_id=self.next_id, tasks=updated_tasks)

    def mark_done(self, task_id: int) -> 'TaskCollection':
        """
        Creates new collection with task marked as completed.

        Args:
            task_id: ID of task to mark done

        Returns:
            New TaskCollection with completed task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        updated_tasks = []
        found = False

        for task in self.tasks:
            if task.id == task_id:
                updated_tasks.append(task.mark_completed())
                found = True
            else:
                updated_tasks.append(task)

        if not found:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        return TaskCollection(next_id=self.next_id, tasks=updated_tasks)

    def delete_task(self, task_id: int) -> 'TaskCollection':
        """
        Creates new collection without specified task.
        Note: next_id is NOT decremented (ID stability).

        Args:
            task_id: ID of task to delete

        Returns:
            New TaskCollection without deleted task

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        new_tasks = [task for task in self.tasks if task.id != task_id]

        if len(new_tasks) == len(self.tasks):
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        return TaskCollection(next_id=self.next_id, tasks=new_tasks)

    @staticmethod
    def clear() -> 'TaskCollection':
        """Creates new empty collection with next_id reset to 1."""
        return TaskCollection(next_id=1, tasks=[])

    def to_dict(self) -> dict:
        """Serializes collection to dictionary for JSON storage."""
        return {
            "next_id": self.next_id,
            "tasks": [task.to_dict() for task in self.tasks]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TaskCollection':
        """
        Deserializes collection from dictionary.

        Handles missing fields and validates structure.

        Args:
            data: Dictionary with collection fields

        Returns:
            TaskCollection instance
        """
        next_id = data.get("next_id", 1)
        task_dicts = data.get("tasks", [])
        tasks = [Task.from_dict(td) for td in task_dicts]
        return cls(next_id=next_id, tasks=tasks)
