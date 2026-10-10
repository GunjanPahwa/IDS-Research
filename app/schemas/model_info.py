"""Model metadata and schema endpoint response models."""

from typing import Dict
from pydantic import BaseModel, ConfigDict, Field


class FeaturePropertySchema(BaseModel):
    """Schema descriptor for an individual input feature."""

    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    description: str


class DatasetModelDetails(BaseModel):
    """Model status details for a dataset."""

    model_config = ConfigDict(extra="forbid")

    dataset: str
    is_loaded: bool
    classes: list[str]
    verified: bool = Field(False, description="Whether dataset test split is verified in local repository")


class ModelInfoResponse(BaseModel):
    """Response schema for GET /api/v1/model/info."""

    model_config = ConfigDict(extra="forbid")

    available_datasets: list[str] = Field(..., description="List of supported dataset model keys")
    default_dataset: str = Field(..., description="Currently configured default dataset")
    feature_space: str = Field(..., description="Canonical feature space used by models ('Common-5')")
    features_schema: list[FeaturePropertySchema] = Field(..., description="List of required input features")
    datasets_info: Dict[str, DatasetModelDetails] = Field(
        ..., description="Map of dataset keys to model details and target classes"
    )
