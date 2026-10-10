"""Prediction endpoints for single flow and batch network traffic inference."""

from fastapi import APIRouter
from app.schemas.predict import BatchPredictRequest, PredictRequest, PredictionResult
from app.services.inference import inference_service

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("", response_model=PredictionResult, summary="Single Network Flow Prediction")
def predict_single_flow(request: PredictRequest) -> PredictionResult:
    """Classify a single network traffic flow as BENIGN or ATTACK category.

    Runs inference using the Unified Single-Stage multi-class model on Common-5 feature space.
    """
    return inference_service.predict_single(
        dataset_name=request.dataset,
        features=request.features,
    )


@router.post("/batch", response_model=list[PredictionResult], summary="Batch Network Flows Prediction")
def predict_batch_flows(request: BatchPredictRequest) -> list[PredictionResult]:
    """Classify a batch of network traffic flows using vectorized model evaluation.

    Returns list of prediction results in the exact input order of flows.
    """
    return inference_service.predict_batch(
        dataset_name=request.dataset,
        flows=request.flows,
    )
