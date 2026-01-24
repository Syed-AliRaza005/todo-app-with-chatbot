"""
Console Todo Application - Command Implementations

This module contains command functions for all CLI operations.
"""

import sys
from src.storage import load_collection, save_collection
from src.models import TodoError, ValidationError, TaskNotFoundError, StorageError
from src.ui import render_all_tasks, render_success, render_error, render_task_detail


# ============================================================================
# Phase 6 & 7: MVP Commands (T022-T029)
# ============================================================================

def cmd_add(title: str, description: str) -> None:
    """
    Add a new task.

    Args:
        title: Task title
        description: Task description
    """
    try:
        # Load collection
        collection = load_collection()

        # Add task
        collection = collection.add_task(title, description)

        # Save collection
        save_collection(collection)

        # Get the newly added task
        new_task = collection.tasks[-1]

        # Render success with task details
        render_success("Task added successfully!")
        render_task_detail(new_task)

    except ValidationError as e:
        render_error(f"{e}")
        sys.exit(1)
    except StorageError as e:
        render_error(f"{e}")
        sys.exit(2)
    except Exception as e:
        render_error(f"Unexpected error: {e}")
        sys.exit(2)


def cmd_list() -> None:
    """
    List all tasks in categorized sections.
    """
    try:
        # Load collection
        collection = load_collection()

        # Render all tasks
        render_all_tasks(collection)

    except StorageError as e:
        render_error(f"{e}")
        sys.exit(2)
    except Exception as e:
        render_error(f"Unexpected error: {e}")
        sys.exit(2)


def cmd_done(task_id: int) -> None:
    """
    Mark a task as completed.

    Args:
        task_id: ID of task to mark done
    """
    try:
        # Load collection
        collection = load_collection()

        # Mark done
        collection = collection.mark_done(task_id)

        # Save collection
        save_collection(collection)

        # Get updated task
        updated_task = collection.get_task(task_id)

        # Render success
        render_success(f"Task #{task_id} marked as completed!")
        if updated_task:
            render_task_detail(updated_task)

    except TaskNotFoundError as e:
        render_error(f"{e}")
        sys.exit(1)
    except StorageError as e:
        render_error(f"{e}")
        sys.exit(2)
    except Exception as e:
        render_error(f"Unexpected error: {e}")
        sys.exit(2)


# ============================================================================
# Phase 9: Task Update (T036-T037)
# ============================================================================

def cmd_update(task_id: int, title: str, description: str) -> None:
    """
    Update task title and description.

    Args:
        task_id: ID of task to update
        title: New title
        description: New description
    """
    try:
        # Load collection
        collection = load_collection()

        # Update task
        collection = collection.update_task(task_id, title, description)

        # Save collection
        save_collection(collection)

        # Get updated task
        updated_task = collection.get_task(task_id)

        # Render success
        render_success(f"Task #{task_id} updated successfully!")
        if updated_task:
            render_task_detail(updated_task)

    except TaskNotFoundError as e:
        render_error(f"{e}")
        sys.exit(1)
    except ValidationError as e:
        render_error(f"{e}")
        sys.exit(1)
    except StorageError as e:
        render_error(f"{e}")
        sys.exit(2)
    except Exception as e:
        render_error(f"Unexpected error: {e}")
        sys.exit(2)


# ============================================================================
# Phase 10: Task Deletion (T040-T041)
# ============================================================================

def cmd_delete(task_id: int) -> None:
    """
    Delete a task by ID.

    Args:
        task_id: ID of task to delete
    """
    try:
        # Load collection
        collection = load_collection()

        # Get task before deleting (for display)
        task_to_delete = collection.get_task(task_id)

        # Delete task
        collection = collection.delete_task(task_id)

        # Save collection
        save_collection(collection)

        # Render success
        if task_to_delete:
            render_success(f"Task #{task_id} deleted successfully!")
            print(f"  Deleted: \"{task_to_delete.title}\"")
            print(f"  Note: Other task IDs remain unchanged")
        else:
            render_success(f"Task #{task_id} deleted!")

    except TaskNotFoundError as e:
        render_error(f"{e}")
        sys.exit(1)
    except StorageError as e:
        render_error(f"{e}")
        sys.exit(2)
    except Exception as e:
        render_error(f"Unexpected error: {e}")
        sys.exit(2)


# ============================================================================
# Phase 11: Clear All Tasks (T044)
# ============================================================================

def cmd_clear() -> None:
    """
    Clear all tasks and reset ID counter.
    """
    try:
        # Load collection to count tasks
        old_collection = load_collection()
        task_count = len(old_collection.tasks)

        # Create empty collection
        collection = old_collection.clear()

        # Save collection
        save_collection(collection)

        # Render success
        render_success("All tasks cleared!")
        print(f"  Deleted: {task_count} task(s)")
        print(f"  ID counter reset to 1")

    except StorageError as e:
        render_error(f"{e}")
        sys.exit(2)
    except Exception as e:
        render_error(f"Unexpected error: {e}")
        sys.exit(2)
