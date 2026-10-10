"""Health check endpoint."""

from fastapi import APIRouter
from app.config import settings
from app.schemas.health import HealthResponse
from app.services.inference import inference_service

router = APIRouter(prefix="/health", tags=["System"])


@router.get("", response_model=HealthResponse, summary="Application Health Check")
def get_health() -> HealthResponse:
    """Get application operational status and list of loaded dataset models."""
    loaded = inference_service.get_loaded_datasets()
    status = "ok" if loaded else "degraded"
    return HealthResponse(
        status=status,
        loaded_models=loaded,
        default_dataset=settings.DEFAULT_DATASET,
    )
