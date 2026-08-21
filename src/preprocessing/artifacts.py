"""Persist and load fitted preprocessing artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import joblib


def save_preprocessor(preprocessor, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "dataset_name": preprocessor.dataset_name,
        "preprocessing_mode": preprocessor.preprocessing_mode,
        "feature_space": preprocessor.feature_space,
        "duplicate_policy": getattr(preprocessor.duplicate_policy, "value", None),
    }
    joblib.dump(preprocessor, path)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def load_preprocessor(path: Path):
    return joblib.load(path)
