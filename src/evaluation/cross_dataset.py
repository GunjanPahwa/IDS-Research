"""Cross-dataset generalization testing engine."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.evaluation.metrics import compute_binary_metrics


def run_cross_dataset_matrix(
    models_dict: dict[str, Any],
    datasets_data: dict[str, tuple[np.ndarray, np.ndarray]],
) -> dict[str, Any]:
    """Evaluate trained models across all test datasets in a specified feature space.
    
    Args:
        models_dict: dict mapping dataset_name -> trained Stage1BinaryClassifier
        datasets_data: dict mapping dataset_name -> (X_test, y_test)
        
    Returns:
        Dict containing accuracy_matrix, f1_matrix, and full per-pair detailed metrics.
    """
    dataset_names = sorted(list(models_dict.keys()))
    n = len(dataset_names)

    acc_matrix = np.zeros((n, n), dtype=float)
    f1_matrix = np.zeros((n, n), dtype=float)
    pair_details: dict[str, dict[str, dict[str, Any]]] = {}

    for i, train_ds in enumerate(dataset_names):
        clf = models_dict[train_ds]
        pair_details[train_ds] = {}

        for j, eval_ds in enumerate(dataset_names):
            X_test, y_test = datasets_data[eval_ds]
            y_pred = clf.predict(X_test)
            metrics = compute_binary_metrics(y_test, y_pred)

            acc_matrix[i, j] = metrics["accuracy"]
            f1_matrix[i, j] = metrics["f1"]
            pair_details[train_ds][eval_ds] = metrics

    return {
        "datasets": dataset_names,
        "accuracy_matrix": acc_matrix.tolist(),
        "f1_matrix": f1_matrix.tolist(),
        "pair_details": pair_details,
    }
