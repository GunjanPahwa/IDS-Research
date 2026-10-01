"""Model information and metadata schema endpoint."""

from fastapi import APIRouter
from app.config import settings
from app.schemas.model_info import DatasetModelDetails, FeaturePropertySchema, ModelInfoResponse
from app.services.inference import DATASET_REGISTRY, inference_service

router = APIRouter(prefix="/model", tags=["Model Metadata"])


VERIFIED_DATASETS = {"unsw_nb15", "kdd99", "nsl_kdd"}


@router.get("/info", response_model=ModelInfoResponse, summary="Model Metadata & Feature Schemas")
def get_model_info() -> ModelInfoResponse:
    """Get metadata about available dataset models, feature definitions, and target attack labels."""
    available = list(DATASET_REGISTRY.keys())
    loaded = inference_service.get_loaded_datasets()
    classes_map = inference_service.get_dataset_classes()

    datasets_info = {}
    for ds in available:
        is_loaded = ds in loaded
        classes = classes_map.get(ds, [])
        datasets_info[ds] = DatasetModelDetails(
            dataset=ds,
            is_loaded=is_loaded,
            classes=classes,
            verified=ds in VERIFIED_DATASETS,
        )

    features_schema = [
        FeaturePropertySchema(
            name="duration",
            type="float",
            description="Connection flow duration in seconds (>= 0.0)",
        ),
        FeaturePropertySchema(
            name="src_bytes",
            type="integer",
            description="Source to destination payload bytes (>= 0)",
        ),
        FeaturePropertySchema(
            name="dst_bytes",
            type="integer",
            description="Destination to source payload bytes (>= 0)",
        ),
        FeaturePropertySchema(
            name="protocol",
            type="string",
            description="Protocol identifier (e.g. 'tcp', 'udp', 'icmp')",
        ),
        FeaturePropertySchema(
            name="service",
            type="string",
            description="Network service identifier (e.g. 'http', 'dns', 'ftp', or '-')",
        ),
    ]

    return ModelInfoResponse(
        available_datasets=available,
        default_dataset=settings.DEFAULT_DATASET,
        feature_space="Common-5",
        features_schema=features_schema,
        datasets_info=datasets_info,
    )
