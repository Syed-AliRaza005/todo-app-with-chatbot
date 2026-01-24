from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# ====================
# Task Schemas
# ====================

class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    status: Optional[str] = Field(None, pattern="^(Pending|Completed)$")


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks with statistics"""
    tasks: List[TaskResponse]
    total: int
    pending_count: int
    completed_count: int


class TaskStatisticsResponse(BaseModel):
    """Schema for task statistics"""
    total: int
    pending: int
    completed: int


# ====================
# Bulk Operation Schemas
# ====================

class BulkTaskIdsRequest(BaseModel):
    """Schema for bulk operation requests"""
    task_ids: List[UUID] = Field(..., min_length=1)


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation response"""
    message: str
    updated_count: int
    deleted_count: int = 0
