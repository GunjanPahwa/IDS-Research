"""Stage 2: Multi-class attack-type classifier and Unified single-stage baseline module."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier


class Stage2MultiClassClassifier:
    """Stage 2 Multi-class Attack-Type Classifier.
    
    Trained EXCLUSIVELY on ground-truth attack rows (benign rows excluded during training).
    Maps multi-class string attack labels to integer codes using LabelEncoder.
    """

    def __init__(self, model_type: str = "xgboost", params: Optional[dict[str, Any]] = None):
        self.model_type = model_type.lower()
        self.params = params or {}
        self.label_encoder = LabelEncoder()
        self.model: Any = None
        self.is_fitted = False

    def fit(self, X_attack: np.ndarray, y_attack_labels: np.ndarray) -> Stage2MultiClassClassifier:
        y_encoded = self.label_encoder.fit_transform(y_attack_labels)
        n_classes = len(self.label_encoder.classes_)

        if self.model_type == "xgboost":
            default_params = dict(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                tree_method="hist",
                n_jobs=-1,
                random_state=42,
                verbosity=0,
                objective="multi:softprob" if n_classes > 2 else "binary:logistic",
            )
            default_params.update(self.params)
            self.model = XGBClassifier(**default_params)
        elif self.model_type == "random_forest":
            default_params = dict(
                n_estimators=100,
                max_depth=15,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            )
            default_params.update(self.params)
            self.model = RandomForestClassifier(**default_params)
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}")

        self.model.fit(X_attack, y_encoded)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call fit() first.")
        y_encoded_pred = self.model.predict(X)
        return self.label_encoder.inverse_transform(y_encoded_pred)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call fit() first.")
        return self.model.predict_proba(X)


class UnifiedSingleStageClassifier:
    """Unified Single-Stage Baseline Classifier.
    
    Classifies 'BENIGN' + all specific attack categories in a single model pass.
    """

    def __init__(self, model_type: str = "xgboost", params: Optional[dict[str, Any]] = None):
        self.model_type = model_type.lower()
        self.params = params or {}
        self.label_encoder = LabelEncoder()
        self.model: Any = None
        self.is_fitted = False

    def fit(self, X: np.ndarray, y_labels: np.ndarray) -> UnifiedSingleStageClassifier:
        y_encoded = self.label_encoder.fit_transform(y_labels)
        n_classes = len(self.label_encoder.classes_)

        if self.model_type == "xgboost":
            default_params = dict(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                tree_method="hist",
                n_jobs=-1,
                random_state=42,
                verbosity=0,
                objective="multi:softprob" if n_classes > 2 else "binary:logistic",
            )
            default_params.update(self.params)
            self.model = XGBClassifier(**default_params)
        elif self.model_type == "random_forest":
            default_params = dict(
                n_estimators=100,
                max_depth=15,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            )
            default_params.update(self.params)
            self.model = RandomForestClassifier(**default_params)
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}")

        self.model.fit(X, y_encoded)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call fit() first.")
        y_encoded_pred = self.model.predict(X)
        return self.label_encoder.inverse_transform(y_encoded_pred)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call fit() first.")
        return self.model.predict_proba(X)
