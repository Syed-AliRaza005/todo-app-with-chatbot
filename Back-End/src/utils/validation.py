"""
Validation Utilities for Todo App MCP Server

This module provides shared validation functions for various components
of the Todo App MCP Server.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import UUID


def validate_user_id(user_id: str) -> bool:
    """
    Validate that the user ID is a valid UUID string.

    Args:
        user_id: The user ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        UUID(user_id)
        return True
    except (TypeError, ValueError):
        return False


def validate_task_title(title: str) -> tuple[bool, Optional[str]]:
    """
    Validate a task title.

    Args:
        title: The title to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Task title cannot be empty"

    if len(title.strip()) > 500:
        return False, "Task title cannot exceed 500 characters"

    return True, None


def validate_task_description(description: str) -> tuple[bool, Optional[str]]:
    """
    Validate a task description.

    Args:
        description: The description to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if description and len(description) > 10000:
        return False, "Task description cannot exceed 10,000 characters"

    return True, None


def validate_command_text(command_text: str) -> tuple[bool, Optional[str]]:
    """
    Validate a natural language command text.

    Args:
        command_text: The command text to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not command_text or not command_text.strip():
        return False, "Command text cannot be empty"

    if len(command_text.strip()) > 1000:
        return False, "Command text cannot exceed 1,000 characters"

    return True, None


def validate_language_code(language_code: str) -> tuple[bool, Optional[str]]:
    """
    Validate a language code.

    Args:
        language_code: The language code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_codes = {"en", "ur", "hi", "mixed"}

    if not language_code:
        return False, "Language code cannot be empty"

    if language_code not in valid_codes:
        return False, f"Invalid language code: {language_code}. Valid codes are: {', '.join(valid_codes)}"

    return True, None


def validate_confidence_score(confidence: float) -> tuple[bool, Optional[str]]:
    """
    Validate a confidence score.

    Args:
        confidence: The confidence score to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if confidence is None:
        return False, "Confidence score cannot be None"

    if not isinstance(confidence, (int, float)):
        return False, "Confidence score must be a number"

    if not 0.0 <= confidence <= 1.0:
        return False, "Confidence score must be between 0.0 and 1.0"

    return True, None


def validate_entities(entities: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    """
    Validate a list of entities.

    Args:
        entities: The list of entities to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(entities, list):
        return False, "Entities must be a list"

    for i, entity in enumerate(entities):
        if not isinstance(entity, dict):
            return False, f"Entity at index {i} must be a dictionary"

        if "type" not in entity:
            return False, f"Entity at index {i} must have a 'type' field"

        if "value" not in entity:
            return False, f"Entity at index {i} must have a 'value' field"

        if not isinstance(entity["type"], str):
            return False, f"Entity type at index {i} must be a string"

        if not isinstance(entity["value"], str):
            return False, f"Entity value at index {i} must be a string"

    return True, None


def validate_timestamp(timestamp: datetime) -> tuple[bool, Optional[str]]:
    """
    Validate a timestamp.

    Args:
        timestamp: The timestamp to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if timestamp is None:
        return False, "Timestamp cannot be None"

    if not isinstance(timestamp, datetime):
        return False, "Timestamp must be a datetime object"

    # Check that the timestamp is not in the future (with some tolerance for clock differences)
    if timestamp > datetime.utcnow().replace(microsecond=0) + timedelta(minutes=5):
        return False, "Timestamp cannot be in the future"

    return True, None


def validate_parsed_command_structure(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the structure of a parsed command dictionary.

    Args:
        data: The parsed command data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["intent", "entities", "confidence", "resolved_action", "raw_input"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate specific fields
    if data["intent"] is not None and not isinstance(data["intent"], str):
        return False, "Intent must be a string or None"

    entities_valid, entities_error = validate_entities(data["entities"])
    if not entities_valid:
        return False, f"Invalid entities: {entities_error}"

    confidence_valid, confidence_error = validate_confidence_score(data["confidence"])
    if not confidence_valid:
        return False, confidence_error

    if not isinstance(data["resolved_action"], str):
        return False, "Resolved action must be a string"

    if not isinstance(data["raw_input"], str):
        return False, "Raw input must be a string"

    return True, None


def validate_natural_language_command_structure(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the structure of a natural language command dictionary.

    Args:
        data: The command data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["raw_input", "user_id"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    command_valid, command_error = validate_command_text(data["raw_input"])
    if not command_valid:
        return False, command_error

    user_id_valid, user_id_error = validate_user_id(data["user_id"])
    if not user_id_valid:
        return False, user_id_error

    return True, None


def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing potentially harmful content.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return text

    # Remove potentially harmful characters or patterns
    # This is a basic example - more sophisticated sanitization might be needed
    sanitized = text.replace("\0", "")  # Remove null bytes
    return sanitized


