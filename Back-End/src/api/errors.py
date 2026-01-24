from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str
    message: str
    details: Optional[dict] = None


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": get_error_code(exc.status_code),
            "message": exc.detail,
            "details": None
        },
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc):
    """Handle validation errors with detailed field errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"fields": errors}
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": None
        }
    )


def get_error_code(status_code: int) -> str:
    """Map HTTP status code to error code"""
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
    }
    return error_codes.get(status_code, "UNKNOWN_ERROR")
