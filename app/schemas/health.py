"""Health check response schema."""

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Health check endpoint response schema."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Application operational status e.g. 'ok'")
    loaded_models: list[str] = Field(..., description="List of currently loaded dataset model identifiers")
    default_dataset: str = Field(..., description="Default dataset configured for inference requests")
