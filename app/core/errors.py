"""Centralized exception handling and custom exception definitions."""

from typing import Any, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger


class NIDSException(Exception):
    """Base exception for NIDS API domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class UnknownDatasetError(NIDSException):
    """Raised when an requested dataset name is invalid or unknown."""

    def __init__(self, dataset_name: str, available_datasets: list[str]):
        super().__init__(
            message=f"Dataset '{dataset_name}' is unknown or not supported.",
            code="UNKNOWN_DATASET",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"requested": dataset_name, "available": available_datasets},
        )


class ModelNotLoadedError(NIDSException):
    """Raised when a dataset's model or preprocessor is unavailable/failed to load."""

    def __init__(self, dataset_name: str, reason: str = "Artifacts not found or corrupted."):
        super().__init__(
            message=f"Model for dataset '{dataset_name}' is unavailable: {reason}",
            code="MODEL_NOT_LOADED",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"dataset": dataset_name, "reason": reason},
        )


class BatchSizeExceededError(NIDSException):
    """Raised when a batch prediction request exceeds the maximum allowed flows."""

    def __init__(self, requested_count: int, max_batch_size: int):
        super().__init__(
            message=f"Batch size {requested_count} exceeds maximum allowed limit of {max_batch_size}.",
            code="BATCH_SIZE_EXCEEDED",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"requested_size": requested_count, "max_batch_size": max_batch_size},
        )


def make_error_response(
    code: str,
    message: str,
    status_code: int,
    details: Optional[Any] = None,
) -> JSONResponse:
    """Utility to build standardized error JSON responses."""
    content: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details is not None:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


async def nids_exception_handler(request: Request, exc: NIDSException) -> JSONResponse:
    """Handler for custom NIDSException instances."""
    logger.warning("NIDSException [%s]: %s (path: %s)", exc.code, exc.message, request.url.path)
    return make_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic/FastAPI validation errors (422)."""
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    # Format details into readable structure
    errors_list = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors_list.append({
            "field": loc,
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        })

    return make_error_response(
        code="VALIDATION_ERROR",
        message="Request payload validation failed.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=errors_list,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for standard Starlette/FastAPI HTTPExceptions."""
    code_map = {
        400: "BAD_REQUEST",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    msg = str(exc.detail) if exc.detail else "HTTP Error occurred"
    return make_error_response(
        code=code,
        message=msg,
        status_code=exc.status_code,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all unhandled exception handler."""
    logger.error("Unhandled server error: %s", str(exc), exc_info=True)
    return make_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
