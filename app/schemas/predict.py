"""Pydantic v2 request/response schemas for prediction endpoints."""

import math
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Features(BaseModel):
    """Network flow input features (Common-5 feature space)."""

    model_config = ConfigDict(extra="forbid")

    duration: float = Field(..., ge=0.0, description="Connection duration in seconds (>= 0.0)")
    src_bytes: int = Field(..., ge=0, description="Source-to-destination payload bytes (>= 0)")
    dst_bytes: int = Field(..., ge=0, description="Destination-to-source payload bytes (>= 0)")
    protocol: str = Field(..., min_length=1, description="Network protocol (e.g. tcp, udp, icmp)")
    service: str = Field(..., min_length=1, description="Network service (e.g. http, dns, ftp, or '-')")

    @field_validator("duration")
    @classmethod
    def validate_duration_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("duration must be a finite non-negative number")
        return v

    @field_validator("protocol", "service")
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        s = v.strip().lower()
        if not s:
            raise ValueError("String fields cannot be blank or whitespace-only")
        return s


class PredictRequest(BaseModel):
    """Single flow prediction request schema."""

    model_config = ConfigDict(extra="forbid")

    dataset: Optional[str] = Field(
        None,
        description="Dataset model target: kdd99 | nsl_kdd | unsw_nb15 | cic_ids2017 | cse_cic_ids2018 | uwf_zeekdata24",
    )
    features: Features


class BatchPredictRequest(BaseModel):
    """Batch flows prediction request schema."""

    model_config = ConfigDict(extra="forbid")

    dataset: Optional[str] = Field(
        None,
        description="Dataset model target: kdd99 | nsl_kdd | unsw_nb15 | cic_ids2017 | cse_cic_ids2018 | uwf_zeekdata24",
    )
    flows: list[Features] = Field(..., min_length=1, description="List of network flows (max batch size applies)")


class PredictionResult(BaseModel):
    """Prediction result output schema."""

    model_config = ConfigDict(extra="forbid")

    is_attack: bool = Field(..., description="True if predicted flow is an attack; False if BENIGN")
    label: str = Field(..., description="Predicted class label (BENIGN or attack category)")
    attack_type: Optional[str] = Field(..., description="Attack category name if attack, null if BENIGN")
    confidence: float = Field(..., description="Model prediction confidence score [0.0 - 1.0]")
    probabilities: Dict[str, float] = Field(..., description="Probability distribution across all target classes")
    dataset: str = Field(..., description="Dataset model used for prediction")
    latency_ms: float = Field(..., description="Inference execution latency in milliseconds")
