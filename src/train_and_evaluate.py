"""Comprehensive model training, evaluation, and cross-dataset generalization orchestrator.

Executes:
1. Stage 1 Binary Classifiers (All 6 datasets × Native, Common-5, Common-7).
2. Stage 2 Multi-Class Classifiers (Trained attack-only; evaluated Isolated vs Cascaded End-to-End).
3. Unified Single-Stage Multi-Class Baseline.
4. Cross-Dataset Generalization Matrices (Common-5 6x6 & Common-7 4x4).
5. Persistence of models to models/ and results to results/.
"""

from __future__ import annotations

import gc
import json
import pickle
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from src.data.registry import get_loader
from src.evaluation.cross_dataset import run_cross_dataset_matrix
from src.evaluation.metrics import compute_binary_metrics, compute_multiclass_metrics
from src.models.binary import Stage1BinaryClassifier
from src.models.multiclass import Stage2MultiClassClassifier, UnifiedSingleStageClassifier
from src.models.pipeline import TwoStageIDSPipeline
from src.preprocessing.pipeline import NIDSPreprocessor


PROCESSED_DIR = ROOT / "data" / "processed"
PREPROCESSORS_DIR = ROOT / "data" / "preprocessors"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

MODELS_DIR.mkdir(exist_ok=True, parents=True)
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

LABEL_MAPPING_CSV = str(ROOT / "data" / "label_mapping.csv")

DATASETS = ["cic-ids2017", "cse-cic-ids2018", "kdd99", "nsl-kdd", "unsw-nb15", "uwf_zeekdata"]
COMMON7_DATASETS = ["cic-ids2017", "cse-cic-ids2018", "unsw-nb15", "uwf_zeekdata"]


# Invisible Unicode characters that can appear in CSV headers (e.g. UTF-8 BOM
# written by Excel/pandas when encoding="utf-8-sig" is not used). These cause
# silent column-name mismatches that bypass leakage-column drop rules.
_BOM_STRIP_CHARS = "\ufeff\u00a0\u200b\u200c\u200d\u2060\ufffe"


def _sanitize_csv_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip BOM and other invisible Unicode characters from all column names."""
    df.columns = [str(c).strip(_BOM_STRIP_CHARS).strip() for c in df.columns]
    return df


def load_processed_csv(key: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load binary preprocessed train/test matrices.

    Applies BOM/invisible-char sanitization on column names before any
    column selection, so encoding artifacts in CSV headers cannot cause
    leakage columns to survive into the feature matrix.
    """
    train_path = PROCESSED_DIR / f"{key}_train.csv"
    test_path = PROCESSED_DIR / f"{key}_test.csv"

    train_df = _sanitize_csv_columns(pd.read_csv(train_path))
    test_df  = _sanitize_csv_columns(pd.read_csv(test_path))

    X_train = train_df.drop(columns=["label"]).values.astype(np.float32)
    y_train = train_df["label"].values.astype(np.int32)

    X_test = test_df.drop(columns=["label"]).values.astype(np.float32)
    y_test = test_df["label"].values.astype(np.int32)

    return X_train, y_train, X_test, y_test


def load_multiclass_data(dataset_name: str, feature_space: str = "Common-5") -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extract multiclass aligned matrices using NIDSPreprocessor on raw loaders."""
    print(f"  [Loader] Extracting multiclass targets for {dataset_name} ({feature_space})...")
    loader = get_loader(dataset_name)
    df_train_raw, df_test_raw = loader.load()

    mode = "within-dataset" if feature_space == "native" else "cross-dataset"
    pre = NIDSPreprocessor(
        dataset_name=dataset_name,
        preprocessing_mode=mode,
        feature_space=feature_space,
        label_mapping_csv=LABEL_MAPPING_CSV,
    )

    # Subsample train for fitting if > 200k rows
    sub_df = df_train_raw.sample(n=min(200000, len(df_train_raw)), random_state=42)
    pre.fit(sub_df)

    def _transform_chunked(df):
        X_parts, y_bin_parts, y_mul_parts = [], [], []
        chunk_size = 300000
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size]
            Xc, ybc, ymc = pre.transform(chunk)
            X_parts.append(Xc)
            y_bin_parts.append(ybc)
            y_mul_parts.append(ymc)
        return np.vstack(X_parts), np.concatenate(y_bin_parts), np.concatenate(y_mul_parts)

    X_train, y_bin_train, y_mul_train = _transform_chunked(df_train_raw)
    X_test, y_bin_test, y_mul_test = _transform_chunked(df_test_raw)

    del df_train_raw, df_test_raw
    gc.collect()

    return X_train, y_bin_train.astype(int), y_mul_train, X_test, y_bin_test.astype(int), y_mul_test


def save_model_artifact(model_obj: Any, name: str):
    path = MODELS_DIR / f"{name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(model_obj, f)
    print(f"    [Model Saved] {path}")


def run_stage1_binary_benchmarks() -> tuple[dict[str, Any], dict[str, Stage1BinaryClassifier]]:
    print("\n" + "=" * 80)
    print("STAGE 1: BINARY CLASSIFIER BENCHMARKS (ALL DATASETS x ALL FEATURE SPACES)")
    print("=" * 80)

    stage1_results: dict[str, dict] = {}
    fitted_common5_models: dict[str, Stage1BinaryClassifier] = {}

    runs = []
    for ds in DATASETS:
        runs.append((ds, "native", f"{ds}_native"))
        runs.append((ds, "Common-5", f"{ds}_common5"))
        if ds in COMMON7_DATASETS:
            runs.append((ds, "Common-7", f"{ds}_common7"))

    print(f"{'Dataset Key':<30} | {'Acc':>8} | {'Prec':>8} | {'Rec':>8} | {'F1':>8} | {'ROC-AUC':>8} | {'Time(s)':>7}")
    print("-" * 88)

    for ds_name, fs, key in runs:
        t0 = time.time()
        X_tr, y_tr, X_te, y_te = load_processed_csv(key)

        clf = Stage1BinaryClassifier(model_type="xgboost")
        clf.fit(X_tr, y_tr)

        y_pred = clf.predict(X_te)
        y_prob = clf.predict_proba(X_te)[:, 1] if hasattr(clf, "predict_proba") else None

        metrics = compute_binary_metrics(y_te, y_pred, y_prob)
        elapsed = round(time.time() - t0, 1)
        metrics["training_time_sec"] = elapsed

        stage1_results[key] = metrics
        save_model_artifact(clf, f"stage1_binary_{key}")

        if fs == "Common-5":
            fitted_common5_models[ds_name] = clf

        auc_str = f"{metrics['roc_auc']:.4f}" if metrics['roc_auc'] is not None else "N/A"
        print(f"{key:<30} | {metrics['accuracy']:>8.4f} | {metrics['precision']:>8.4f} | {metrics['recall']:>8.4f} | {metrics['f1']:>8.4f} | {auc_str:>8} | {elapsed:>7.1f}")

    return stage1_results, fitted_common5_models


def run_stage2_and_unified_benchmarks(fitted_stage1_common5: dict[str, Stage1BinaryClassifier]) -> dict[str, Any]:
    print("\n" + "=" * 80)
    print("STAGE 2 & UNIFIED BENCHMARKS (COMMON-5 FEATURE SPACE)")
    print("=" * 80)

    results: dict[str, dict] = {}

    print(f"{'Dataset':<16} | {'Two-Stage (Cascaded) Macro F1':>30} | {'Unified Single-Stage Macro F1':>30} | {'Stage 2 Isolated Macro F1':>26}")
    print("-" * 110)

    for ds in DATASETS:
        t0 = time.time()
        X_tr, y_bin_tr, y_mul_tr, X_te, y_bin_te, y_mul_te = load_multiclass_data(ds, "Common-5")

        # 1. Stage 2 Attack-Only Classifier (Trained exclusively on ground-truth attacks)
        attack_mask_tr = (y_mul_tr != "BENIGN")
        X_tr_atk = X_tr[attack_mask_tr]
        y_tr_atk = y_mul_tr[attack_mask_tr]

        stage2_clf = Stage2MultiClassClassifier(model_type="xgboost")
        stage2_clf.fit(X_tr_atk, y_tr_atk)
        save_model_artifact(stage2_clf, f"stage2_multiclass_{ds}_common5")

        # Approach (a) Isolated evaluation (on ground-truth test attacks)
        attack_mask_te = (y_mul_te != "BENIGN")
        X_te_atk = X_te[attack_mask_te]
        y_te_atk = y_mul_te[attack_mask_te]
        y_pred_isolated = stage2_clf.predict(X_te_atk)
        isolated_metrics = compute_multiclass_metrics(y_te_atk, y_pred_isolated)

        # Approach (b) Cascaded End-to-End Evaluation using TwoStageIDSPipeline
        stage1_clf = fitted_stage1_common5[ds]
        pipeline = TwoStageIDSPipeline(stage1_clf, stage2_clf)
        y_pred_cascaded = pipeline.predict(X_te)
        cascaded_metrics = compute_multiclass_metrics(y_mul_te, y_pred_cascaded)

        # 2. Unified Single-Stage Baseline Classifier (Trained on benign + all attack categories directly)
        unified_clf = UnifiedSingleStageClassifier(model_type="xgboost")
        unified_clf.fit(X_tr, y_mul_tr)
        save_model_artifact(unified_clf, f"unified_singlestage_{ds}_common5")

        y_pred_unified = unified_clf.predict(X_te)
        unified_metrics = compute_multiclass_metrics(y_mul_te, y_pred_unified)

        results[ds] = {
            "two_stage_cascaded": cascaded_metrics,
            "unified_single_stage": unified_metrics,
            "stage2_isolated_attack_only": isolated_metrics,
            "elapsed_sec": round(time.time() - t0, 1),
        }

        print(
            f"{ds:<16} | "
            f"{cascaded_metrics['macro_f1']:>30.4f} | "
            f"{unified_metrics['macro_f1']:>30.4f} | "
            f"{isolated_metrics['macro_f1']:>26.4f}"
        )

    return results


def run_cross_dataset_generalization_benchmarks() -> dict[str, Any]:
    print("\n" + "=" * 80)
    print("CROSS-DATASET GENERALIZATION BENCHMARKS")
    print("=" * 80)

    # 1. Common-5 Feature Space (6x6 matrix)
    print("\n--- Common-5 Feature Space (6x6 Generalization Matrix) ---")
    data_common5: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    models_common5: dict[str, Stage1BinaryClassifier] = {}

    for ds in DATASETS:
        X_tr, y_tr, X_te, y_te = load_processed_csv(f"{ds}_common5")
        clf = Stage1BinaryClassifier(model_type="xgboost")
        clf.fit(X_tr, y_tr)
        models_common5[ds] = clf
        data_common5[ds] = (X_te, y_te)

    res_common5 = run_cross_dataset_matrix(models_common5, data_common5)

    print("\nCommon-5 Binary F1-Score Matrix (Rows = Train Source, Cols = Test Target):")
    header = f"{'Source':<18}" + "".join(f"{d:>14}" for d in DATASETS)
    print(header)
    print("-" * len(header))
    for i, src in enumerate(DATASETS):
        row_str = f"{src:<18}"
        for j, tgt in enumerate(DATASETS):
            f1_val = res_common5["f1_matrix"][i][j]
            row_str += f"{f1_val:>14.4f}"
        print(row_str)

    # 2. Common-7 Feature Space (4x4 matrix)
    print("\n--- Common-7 Feature Space (4x4 Generalization Matrix) ---")
    data_common7: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    models_common7: dict[str, Stage1BinaryClassifier] = {}

    for ds in COMMON7_DATASETS:
        X_tr, y_tr, X_te, y_te = load_processed_csv(f"{ds}_common7")
        clf = Stage1BinaryClassifier(model_type="xgboost")
        clf.fit(X_tr, y_tr)
        models_common7[ds] = clf
        data_common7[ds] = (X_te, y_te)

    res_common7 = run_cross_dataset_matrix(models_common7, data_common7)

    print("\nCommon-7 Binary F1-Score Matrix (Rows = Train Source, Cols = Test Target):")
    header7 = f"{'Source':<18}" + "".join(f"{d:>14}" for d in COMMON7_DATASETS)
    print(header7)
    print("-" * len(header7))
    for i, src in enumerate(COMMON7_DATASETS):
        row_str = f"{src:<18}"
        for j, tgt in enumerate(COMMON7_DATASETS):
            f1_val = res_common7["f1_matrix"][i][j]
            row_str += f"{f1_val:>14.4f}"
        print(row_str)

    return {
        "common5_matrix": res_common5,
        "common7_matrix": res_common7,
    }


def main():
    print("================================================================================")
    print("STARTING FULL NIDS MODEL TRAINING & EVALUATION SUITE")
    print("================================================================================")
    start_total_time = time.time()

    # Step 1: Stage 1 Binary Classifiers
    stage1_results, common5_models = run_stage1_binary_benchmarks()

    # Step 2 & 3: Stage 2 Multi-Class & Unified Single-Stage Classifiers
    multiclass_results = run_stage2_and_unified_benchmarks(common5_models)

    # Step 4: Cross-Dataset Generalization
    cross_dataset_results = run_cross_dataset_generalization_benchmarks()

    # Save full consolidated results to JSON
    total_elapsed = round(time.time() - start_total_time, 1)
    full_output = {
        "meta": {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_execution_time_sec": total_elapsed,
        },
        "stage1_binary": stage1_results,
        "stage2_multiclass_and_unified": multiclass_results,
        "cross_dataset_generalization": cross_dataset_results,
    }

    results_json = RESULTS_DIR / "model_benchmarks.json"
    results_json.write_text(json.dumps(full_output, indent=2))
    print("\n" + "=" * 80)
    print(f"[✓] ALL EXPERIMENTS COMPLETE. Results saved to {results_json}")
    print(f"Total time elapsed: {total_elapsed}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
