from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "llm_primary": settings.primary_llm,
        "llm_fallback": settings.fallback_llm,
    }
