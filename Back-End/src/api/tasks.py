from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Task, User
from ..schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskStatisticsResponse, BulkTaskIdsRequest, BulkOperationResponse
)
from ..dependencies import get_current_user_id, validate_user_id_match


router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: UUID,
    status_filter: str = Query(default="All", pattern="^(Pending|Completed|All)$"),
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List all tasks for the authenticated user, optionally filtered by status"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    # Query tasks for this user
    query = db.query(Task).filter(Task.user_id == user_id)

    # Apply status filter
    if status_filter == "Pending":
        query = query.filter(Task.status == "Pending")
    elif status_filter == "Completed":
        query = query.filter(Task.status == "Completed")

    # Order by created_at descending (newest first)
    tasks = query.order_by(Task.created_at.desc()).all()

    # Count statistics
    total = db.query(Task).filter(Task.user_id == user_id).count()
    pending_count = db.query(Task).filter(Task.user_id == user_id, Task.status == "Pending").count()
    completed_count = db.query(Task).filter(Task.user_id == user_id, Task.status == "Completed").count()

    return TaskListResponse(
        tasks=tasks,
        total=total,
        pending_count=pending_count,
        completed_count=completed_count
    )


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new task for the authenticated user"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    # Create new task
    new_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        status="Pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# ============ Advanced Features (Level 3) ============
# These routes must be defined BEFORE /{task_id} to avoid routing conflicts

@router.post("/{user_id}/tasks/bulk/complete", response_model=BulkOperationResponse)
async def bulk_complete_tasks(
    user_id: UUID,
    request: BulkTaskIdsRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark multiple tasks as completed"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    updated_count = 0
    now = datetime.utcnow()

    for task_id in request.task_ids:
        # Validate that task_id is a proper UUID
        try:
            validated_task_id = UUID(str(task_id))
        except ValueError:
            continue  # Skip invalid UUIDs

        task = db.query(Task).filter(Task.id == validated_task_id).first()
        if task and task.user_id == user_id and task.status != "Completed":
            task.status = "Completed"
            task.completed_at = now
            task.updated_at = now
            updated_count += 1

    db.commit()

    return BulkOperationResponse(
        message=f"{updated_count} tasks marked as completed",
        updated_count=updated_count
    )


@router.post("/{user_id}/tasks/bulk/delete", response_model=BulkOperationResponse)
async def bulk_delete_tasks(
    user_id: UUID,
    request: BulkTaskIdsRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete multiple tasks"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    deleted_count = 0

    for task_id in request.task_ids:
        # Validate that task_id is a proper UUID
        try:
            validated_task_id = UUID(str(task_id))
        except ValueError:
            continue  # Skip invalid UUIDs

        task = db.query(Task).filter(Task.id == validated_task_id).first()
        if task and task.user_id == user_id:
            db.delete(task)
            deleted_count += 1

    db.commit()

    return BulkOperationResponse(
        message=f"{deleted_count} tasks deleted",
        updated_count=0,
        deleted_count=deleted_count
    )


@router.get("/{user_id}/tasks/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get task statistics for the authenticated user"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    total = db.query(Task).filter(Task.user_id == user_id).count()
    pending = db.query(Task).filter(Task.user_id == user_id, Task.status == "Pending").count()
    completed = db.query(Task).filter(Task.user_id == user_id, Task.status == "Completed").count()

    return TaskStatisticsResponse(
        total=total,
        pending=pending,
        completed=completed
    )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: task belongs to another user"
        )

    return task


@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a task's title, description, and/or status"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: task belongs to another user"
        )

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status
        # Set or clear completed_at based on status
        if task_data.status == "Completed":
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a task (permanent deletion)"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: task belongs to another user"
        )

    # Delete task
    db.delete(task)
    db.commit()


@router.post("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete(
    user_id: UUID,
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark a task as completed"""

    # Validate user_id matches JWT
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id mismatch"
        )

    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: task belongs to another user"
        )

    # Mark as completed
    task.status = "Completed"
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return task
