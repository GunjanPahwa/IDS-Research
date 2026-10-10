"""Inference service managing model registry and prediction execution."""

import time
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd

from app.config import settings
from app.core.errors import BatchSizeExceededError, ModelNotLoadedError, UnknownDatasetError
from app.core.logging import logger
from app.schemas.predict import Features, PredictionResult
from src.preprocessing.artifacts import load_preprocessor

# Mapping of dataset aliases to canonical keys and artifact filenames
DATASET_REGISTRY: Dict[str, Dict[str, str]] = {
    "kdd99": {
        "preprocessor": "kdd99_common5_preprocessor.pkl",
        "model": "unified_singlestage_kdd99_common5.pkl",
    },
    "nsl_kdd": {
        "preprocessor": "nsl-kdd_common5_preprocessor.pkl",
        "model": "unified_singlestage_nsl-kdd_common5.pkl",
    },
    "unsw_nb15": {
        "preprocessor": "unsw-nb15_common5_preprocessor.pkl",
        "model": "unified_singlestage_unsw-nb15_common5.pkl",
    },
    "cic_ids2017": {
        "preprocessor": "cic-ids2017_common5_preprocessor.pkl",
        "model": "unified_singlestage_cic-ids2017_common5.pkl",
    },
    "cse_cic_ids2018": {
        "preprocessor": "cse-cic-ids2018_common5_preprocessor.pkl",
        "model": "unified_singlestage_cse-cic-ids2018_common5.pkl",
    },
    "uwf_zeekdata24": {
        "preprocessor": "uwf_zeekdata_common5_preprocessor.pkl",
        "model": "unified_singlestage_uwf_zeekdata_common5.pkl",
    },
}

# Alias lookup table for user request flexibility
DATASET_ALIASES: Dict[str, str] = {
    "kdd99": "kdd99",
    "nsl_kdd": "nsl_kdd",
    "nsl-kdd": "nsl_kdd",
    "unsw_nb15": "unsw_nb15",
    "unsw-nb15": "unsw_nb15",
    "cic_ids2017": "cic_ids2017",
    "cic-ids2017": "cic_ids2017",
    "cse_cic_ids2018": "cse_cic_ids2018",
    "cse-cic-ids2018": "cse_cic_ids2018",
    "uwf_zeekdata24": "uwf_zeekdata24",
    "uwf_zeekdata": "uwf_zeekdata24",
    "uwf-zeekdata24": "uwf_zeekdata24",
    "uwf-zeekdata": "uwf_zeekdata24",
}


class InferenceService:
    """Singleton service managing dataset preprocessors and XGBoost models."""

    def __init__(self) -> None:
        self._preprocessors: Dict[str, Any] = {}
        self._models: Dict[str, Any] = {}
        self._classes: Dict[str, list[str]] = {}

    def resolve_dataset(self, dataset_name: Optional[str]) -> str:
        """Resolve optional dataset string or default dataset into a canonical key."""
        target = dataset_name or settings.DEFAULT_DATASET
        target_norm = str(target).strip().lower()

        if target_norm in DATASET_ALIASES:
            return DATASET_ALIASES[target_norm]

        available = list(DATASET_REGISTRY.keys())
        raise UnknownDatasetError(dataset_name=str(target), available_datasets=available)

    def load_all_models(self) -> None:
        """Preload preprocessors and models for all registered datasets during startup lifespan."""
        logger.info("Initializing NIDS Inference Service model registry...")
        models_dir = settings.models_path
        preprocessors_dir = settings.preprocessors_path

        for ds_key, artifacts in DATASET_REGISTRY.items():
            pre_path = preprocessors_dir / artifacts["preprocessor"]
            model_path = models_dir / artifacts["model"]

            if not pre_path.exists():
                logger.error("Preprocessor artifact not found: %s", pre_path)
                continue
            if not model_path.exists():
                logger.error("Model artifact not found: %s", model_path)
                continue

            try:
                preprocessor = load_preprocessor(pre_path)
                model = joblib.load(model_path)
                classes = list(model.label_encoder.classes_)

                self._preprocessors[ds_key] = preprocessor
                self._models[ds_key] = model
                self._classes[ds_key] = classes
                logger.info("Loaded dataset model [%s]: %d target classes", ds_key, len(classes))
            except Exception as e:
                logger.error("Failed to load artifacts for dataset '%s': %s", ds_key, str(e))

        logger.info("Inference Service ready with %d loaded models.", len(self._models))

    def get_loaded_datasets(self) -> list[str]:
        """Get list of dataset keys currently loaded and ready."""
        return list(self._models.keys())

    def get_dataset_classes(self) -> Dict[str, list[str]]:
        """Get target classes dictionary per dataset."""
        return self._classes

    def is_dataset_loaded(self, ds_key: str) -> bool:
        """Check if dataset key is loaded."""
        return ds_key in self._models

    def predict_batch(
        self,
        dataset_name: Optional[str],
        flows: list[Features],
    ) -> list[PredictionResult]:
        """Perform vectorized batch inference across multiple flow feature objects."""
        if len(flows) > settings.MAX_BATCH_SIZE:
            raise BatchSizeExceededError(len(flows), settings.MAX_BATCH_SIZE)

        ds_key = self.resolve_dataset(dataset_name)

        if not self.is_dataset_loaded(ds_key):
            raise ModelNotLoadedError(ds_key, f"Model artifacts for '{ds_key}' were not loaded successfully.")

        t0 = time.perf_counter()

        preprocessor = self._preprocessors[ds_key]
        model = self._models[ds_key]
        classes = self._classes[ds_key]

        # Construct DataFrame matching training column names
        records = [
            {
                "duration": f.duration,
                "src_bytes": f.src_bytes,
                "dst_bytes": f.dst_bytes,
                "protocol": f.protocol.strip().lower(),
                "service": f.service.strip().lower(),
            }
            for f in flows
        ]
        df = pd.DataFrame(records)

        # Preprocess features using repo's fitted NIDSPreprocessor
        X, _, _ = preprocessor.transform(df)

        # Vectorized multi-class probability prediction
        probas = model.predict_proba(X)  # shape (N, n_classes)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        results: list[PredictionResult] = []
        for i in range(len(flows)):
            row_probas = probas[i]
            max_idx = int(np.argmax(row_probas))
            label = str(classes[max_idx])
            confidence = float(row_probas[max_idx])
            prob_dict = {str(c): float(p) for c, p in zip(classes, row_probas)}
            is_attack = bool(label != "BENIGN")
            attack_type = label if is_attack else None

            results.append(
                PredictionResult(
                    is_attack=is_attack,
                    label=label,
                    attack_type=attack_type,
                    confidence=round(confidence, 6),
                    probabilities={k: round(v, 6) for k, v in prob_dict.items()},
                    dataset=ds_key,
                    latency_ms=round(elapsed_ms, 3),
                )
            )

        return results

    def predict_single(
        self,
        dataset_name: Optional[str],
        features: Features,
    ) -> PredictionResult:
        """Perform single flow inference."""
        results = self.predict_batch(dataset_name, [features])
        return results[0]


inference_service = InferenceService()
