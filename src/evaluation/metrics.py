"""Evaluation metrics calculation module for binary, multiclass, and cascaded models."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_binary_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None
) -> dict[str, Any]:
    """Compute binary classification metrics."""
    cm = confusion_matrix(y_true, y_pred).tolist()
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    metrics = {
        "accuracy": round(acc, 6),
        "precision": round(prec, 6),
        "recall": round(rec, 6),
        "f1": round(f1, 6),
        "confusion_matrix": cm,
    }

    if y_prob is not None:
        try:
            auc = float(roc_auc_score(y_true, y_prob))
            metrics["roc_auc"] = round(auc, 6)
        except ValueError:
            metrics["roc_auc"] = None

    return metrics


def compute_multiclass_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, labels: Optional[list[str]] = None
) -> dict[str, Any]:
    """Compute multi-class classification metrics."""
    if labels is None:
        unique_labels = sorted(list(set(y_true) | set(y_pred)))
    else:
        unique_labels = labels

    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, labels=unique_labels, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, labels=unique_labels, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, labels=unique_labels, average="macro", zero_division=0))

    prec_weighted = float(precision_score(y_true, y_pred, labels=unique_labels, average="weighted", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, labels=unique_labels, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, labels=unique_labels, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=unique_labels).tolist()

    return {
        "accuracy": round(acc, 6),
        "macro_precision": round(prec_macro, 6),
        "macro_recall": round(rec_macro, 6),
        "macro_f1": round(f1_macro, 6),
        "weighted_precision": round(prec_weighted, 6),
        "weighted_recall": round(rec_weighted, 6),
        "weighted_f1": round(f1_weighted, 6),
        "labels": unique_labels,
        "confusion_matrix": cm,
    }
