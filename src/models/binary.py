"""Stage 1: Binary attack/benign classifier module with class-imbalance weighting."""

from __future__ import annotations

import time
from typing import Any, Optional

import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


class Stage1BinaryClassifier:
    """Stage 1 Binary Classifier (0 = BENIGN, 1 = ATTACK).
    
    Supports loss-gradient class weighting (scale_pos_weight) for XGBoost to handle class imbalance.
    """

    def __init__(self, model_type: str = "xgboost", params: Optional[dict[str, Any]] = None):
        self.model_type = model_type.lower()
        self.params = params or {}
        self.model: Any = None
        self.is_fitted = False

    def _init_model(self, y_train: np.ndarray):
        n_neg = int((y_train == 0).sum())
        n_pos = int((y_train == 1).sum())
        spw = round(n_neg / n_pos, 4) if n_pos > 0 else 1.0

        if self.model_type == "xgboost":
            default_params = dict(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                tree_method="hist",
                n_jobs=-1,
                random_state=42,
                eval_metric="logloss",
                verbosity=0,
                scale_pos_weight=spw,
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
        elif self.model_type == "logistic_regression":
            default_params = dict(
                max_iter=500,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
            default_params.update(self.params)
            self.model = LogisticRegression(**default_params)
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}")

    def fit(self, X: np.ndarray, y: np.ndarray) -> Stage1BinaryClassifier:
        self._init_model(y)
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call fit() first.")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call fit() first.")
        return self.model.predict_proba(X)
