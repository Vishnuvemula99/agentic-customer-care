import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)


class NotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, code="NOT_FOUND", status_code=404)


class LLMError(AppError):
    def __init__(self, message: str):
        super().__init__(message, code="LLM_ERROR", status_code=503)


def setup_error_handlers(app: FastAPI) -> None:
    """Register global error handlers for the FastAPI application."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(f"AppError: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "code": exc.code},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        logger.warning(f"ValueError: {exc}")
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "code": "VALIDATION_ERROR"},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred", "code": "INTERNAL_ERROR"},
        )
