"""
MCP Routes for Todo App Natural Language Commands

This module implements the API routes for the Model Context Protocol (MCP)
server that handles natural language commands for todo operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from pydantic import BaseModel
from datetime import datetime
import logging

from ..database import get_db
from ..auth.jwt import get_user_id_from_token
from ..models.nlp_command import NaturalLanguageCommand
from ..models.parsed_command import ParsedCommand
from ..models.task import Task
from ..services.command_processor import get_command_processor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/mcp", tags=["mcp"])

# Security scheme
security = HTTPBearer()


class NaturalLanguageCommandRequest(BaseModel):
    """
    Request model for natural language commands
    """
    command: str
    user_id: str
    session_context: Optional[dict] = None


class CommandResponse(BaseModel):
    """
    Response model for command processing
    """
    success: bool
    operation_performed: str
    message: str
    parsed_command: Optional[Dict] = None
    affected_task: Optional[Dict] = None
    task_list: Optional[list] = []
    suggested_next_steps: Optional[list] = []


class ErrorResponse(BaseModel):
    """
    Error response model
    """
    error: str
    message: str
    suggestions: Optional[list] = []


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
    """
    Verify JWT token and return user data
    """
    try:
        # Extract token from the Authorization header
        token_string = credentials.credentials

        # Get user ID from token
        user_id = get_user_id_from_token(token_string)

        # Return user data
        return {"user_id": str(user_id)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/todo/command", response_model=CommandResponse)
async def process_natural_language_command(
    request: NaturalLanguageCommandRequest,
    token_data: dict = Depends(verify_jwt),
    db: Session = Depends(get_db)
) -> CommandResponse:
    """
    Process natural language command for todo operations

    This endpoint interprets natural language commands and executes appropriate todo operations.

    Args:
        request: Natural language command with user context
        token_data: JWT token data for authentication
        db: Database session

    Returns:
        CommandResponse with operation results
    """
    try:
        # Verify that the user in the token matches the user in the request
        token_user_id = token_data.get("user_id")  # Assuming JWT contains user_id
        request_user_id = request.user_id

        # Convert to UUID for comparison if needed
        try:
            token_user_id_uuid = UUID(token_user_id) if isinstance(token_user_id, str) else token_user_id
            request_user_id_uuid = UUID(request_user_id) if isinstance(request_user_id, str) else request_user_id
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        if token_user_id_uuid != request_user_id_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: user ID mismatch"
            )

        # Log the incoming command
        logger.info(f"Processing command for user {request_user_id}: {request.command}")

        # Create NaturalLanguageCommand object
        nlp_command = NaturalLanguageCommand(
            raw_input=request.command,
            user_id=request_user_id,
            session_context=request.session_context or {},
            timestamp=datetime.utcnow()
        )

        # Get command processor instance
        command_processor = get_command_processor(db, request.user_id)

        # Process the command
        result = command_processor.process_command(nlp_command)

        # Log successful processing
        logger.info(f"Command processed successfully for user {request_user_id}")

        return CommandResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Error processing command for user {request.user_id}: {str(e)}")

        # Return error response
        error_response = {
            'success': False,
            'operation_performed': 'ERROR',
            'message': f'Error processing command: {str(e)}',
            'suggestions': ['Please try rephrasing your command', 'Check your command syntax']
        }

        return CommandResponse(**error_response)


# Additional utility endpoints

@router.get("/todo/status")
async def get_mcp_server_status():
    """
    Get the status of the MCP server

    Returns:
        Server status information
    """
    return {
        "status": "healthy",
        "service": "Todo MCP Server",
        "message": "Natural language command processing is operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/todo/help")
async def get_command_help():
    """
    Get help information about supported commands

    Returns:
        Help information with examples of supported commands
    """
    return {
        "supported_commands": [
            {
                "add": {
                    "examples": [
                        "add a todo to buy groceries",
                        "create a task to finish project report",
                        "add task to schedule meeting"
                    ],
                    "description": "Add a new task to your todo list"
                }
            },
            {
                "delete": {
                    "examples": [
                        "delete the meeting task",
                        "remove the grocery list",
                        "delete task with title 'finish proposal'"
                    ],
                    "description": "Remove a task from your todo list"
                }
            },
            {
                "complete": {
                    "examples": [
                        "mark my workout task as complete",
                        "complete the homework task",
                        "finish the 'read book' task"
                    ],
                    "description": "Mark a task as completed"
                }
            },
            {
                "list": {
                    "examples": [
                        "show my pending tasks",
                        "list all my tasks",
                        "what tasks do I have?"
                    ],
                    "description": "List your tasks with optional filters"
                }
            }
        ],
        "multilingual_support": {
            "description": "Support for mixed English-Urdu/Hindi expressions",
            "examples": [
                "add todo title them new todo description",
                "remove ya delete",
                "jis mai todo ke task krne ka ho"
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Register the router
mcp_router = router