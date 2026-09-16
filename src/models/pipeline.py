"""Two-Stage cascaded IDS pipeline wrapper."""

from __future__ import annotations

import numpy as np

from src.models.binary import Stage1BinaryClassifier
from src.models.multiclass import Stage2MultiClassClassifier


class TwoStageIDSPipeline:
    """Cascaded two-stage NIDS pipeline.
    
    Stage 1: Binary Classifier (BENIGN vs ATTACK).
    Stage 2: Multi-class Classifier (predicts attack category for rows flagged as ATTACK by Stage 1).
    """

    def __init__(self, stage1_model: Stage1BinaryClassifier, stage2_model: Stage2MultiClassClassifier):
        self.stage1_model = stage1_model
        self.stage2_model = stage2_model

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Run cascaded prediction.
        
        Rows predicted as 0 (BENIGN) by Stage 1 are assigned label 'BENIGN'.
        Rows predicted as 1 (ATTACK) by Stage 1 are passed to Stage 2 for attack classification.
        """
        y_stage1 = self.stage1_model.predict(X)
        final_preds = np.full(len(X), "BENIGN", dtype=object)

        attack_indices = np.where(y_stage1 == 1)[0]
        if len(attack_indices) > 0:
            X_attack = X[attack_indices]
            y_stage2_preds = self.stage2_model.predict(X_attack)
            final_preds[attack_indices] = y_stage2_preds

        return final_preds
