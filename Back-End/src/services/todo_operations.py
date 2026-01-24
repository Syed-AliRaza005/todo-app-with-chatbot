"""
Todo Operations Service for Todo App MCP Server

This module provides the core functionality for todo operations including
creating, reading, updating, and deleting tasks with proper user isolation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from uuid import UUID
from ..models.task import Task
from ..models.user import User


class TodoOperationsService:
    """
    Service class for todo operations with proper user isolation
    """

    def __init__(self, db_session: Session, user_id: str):
        self.db_session = db_session
        self.user_id = UUID(user_id) if isinstance(user_id, str) else user_id

    def create_task(self, title: str, description: str = "") -> Task:
        """
        Create a new task for the user

        Args:
            title: Title of the task
            description: Description of the task (optional)

        Returns:
            Created Task object
        """
        new_task = Task(
            user_id=self.user_id,
            title=title,
            description=description,
            status="Pending"
        )

        self.db_session.add(new_task)
        self.db_session.commit()
        self.db_session.refresh(new_task)

        return new_task

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """
        Get a specific task by ID for the user

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == self.user_id)
        task = self.db_session.exec(statement).first()
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """
        List all tasks for the user, optionally filtered by status

        Args:
            status: Optional status filter (Pending, Completed, etc.)

        Returns:
            List of Task objects
        """
        query = select(Task).where(Task.user_id == self.user_id)

        if status:
            query = query.where(Task.status == status)

        query = query.order_by(Task.created_at.desc())

        tasks = self.db_session.exec(query).all()
        return tasks

    def update_task(self, task_id: UUID, title: Optional[str] = None,
                    description: Optional[str] = None, status: Optional[str] = None) -> Optional[Task]:
        """
        Update a task for the user

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)

        Returns:
            Updated Task object if successful, None otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
            if status == "Completed" and task.completed_at is None:
                task.completed_at = datetime.utcnow()
            elif status == "Pending":
                task.completed_at = None

        task.updated_at = datetime.utcnow()

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        return task

    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task for the user

        Args:
            task_id: ID of the task to delete

        Returns:
            True if successful, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return False

        self.db_session.delete(task)
        self.db_session.commit()
        return True

    def find_task_by_identifier(self, identifier: str, user_id: str) -> Optional[Task]:
        """
        Find a task by an identifier string (title, partial title, etc.)

        Args:
            identifier: String to match against task titles
            user_id: User ID to scope the search

        Returns:
            Task object if found, None otherwise
        """
        # Search for tasks with titles containing the identifier
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

        # First try exact match
        statement = select(Task).where(
            Task.user_id == user_uuid,
            Task.title.ilike(f"%{identifier}%")
        ).order_by(Task.created_at.desc())

        tasks = self.db_session.exec(statement).all()

        # If we have multiple matches, return the most recent one
        if tasks:
            return tasks[0]

        return None

    def find_task_by_reference(self, context_reference) -> Optional[Task]:
        """
        Find a task based on a context reference (like "that one", "the last one")

        Args:
            context_reference: TodoReference object with context information

        Returns:
            Task object if found, None otherwise
        """
        from ..models.todo_reference import IdentifierType

        if context_reference.identifier_type == IdentifierType.CONTEXT_REFERENCE:
            if context_reference.value in ["that one", "that", "that task", "that item"]:
                # Return the most recently created task
                statement = select(Task).where(
                    Task.user_id == self.user_id
                ).order_by(Task.created_at.desc()).limit(1)

                return self.db_session.exec(statement).first()

            elif context_reference.value in ["the last one", "last task", "recent task", "previous task"]:
                # Return the most recently created task
                statement = select(Task).where(
                    Task.user_id == self.user_id
                ).order_by(Task.created_at.desc()).limit(1)

                return self.db_session.exec(statement).first()

        elif context_reference.identifier_type == IdentifierType.POSITION:
            # Handle position-based references (first, second, etc.)
            position = int(context_reference.value) if context_reference.value.isdigit() else 1

            # Get all tasks ordered by creation date (most recent first)
            statement = select(Task).where(
                Task.user_id == self.user_id
            ).order_by(Task.created_at.desc())

            tasks = self.db_session.exec(statement).all()

            # Position is 1-indexed, so subtract 1 to get the correct index
            if 1 <= position <= len(tasks):
                return tasks[position - 1]

        return None

    def get_user_tasks_summary(self) -> Dict[str, Any]:
        """
        Get a summary of user's tasks

        Returns:
            Dictionary with task statistics
        """
        all_tasks = self.list_tasks()
        completed_tasks = self.list_tasks(status="Completed")
        pending_tasks = self.list_tasks(status="Pending")

        return {
            "total": len(all_tasks),
            "completed": len(completed_tasks),
            "pending": len(pending_tasks)
        }

    def bulk_update_tasks(self, task_ids: List[UUID], updates: Dict[str, Any]) -> int:
        """
        Bulk update multiple tasks

        Args:
            task_ids: List of task IDs to update
            updates: Dictionary of field-value pairs to update

        Returns:
            Number of tasks successfully updated
        """
        updated_count = 0

        for task_id in task_ids:
            task = self.get_task(task_id)
            if task:
                for field, value in updates.items():
                    if hasattr(task, field):
                        setattr(task, field, value)

                task.updated_at = datetime.utcnow()
                self.db_session.add(task)
                updated_count += 1

        if updated_count > 0:
            self.db_session.commit()

        return updated_count

    def mark_all_tasks_completed(self) -> int:
        """
        Mark all user's pending tasks as completed

        Returns:
            Number of tasks updated
        """
        pending_tasks = self.list_tasks(status="Pending")

        updated_count = 0
        for task in pending_tasks:
            if task.status != "Completed":
                task.status = "Completed"
                task.completed_at = datetime.utcnow()
                task.updated_at = datetime.utcnow()
                self.db_session.add(task)
                updated_count += 1

        if updated_count > 0:
            self.db_session.commit()

        return updated_count

    def clear_all_tasks(self) -> int:
        """
        Delete all tasks for the user

        Returns:
            Number of tasks deleted
        """
        all_tasks = self.list_tasks()
        deleted_count = len(all_tasks)

        for task in all_tasks:
            self.db_session.delete(task)

        if deleted_count > 0:
            self.db_session.commit()

        return deleted_count