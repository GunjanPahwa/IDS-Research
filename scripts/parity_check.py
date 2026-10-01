"""Parity check script verifying backend API predictions against offline model predictions.

Loads real TEST-split data for each dataset through the existing loaders in src/data/.
No synthetic fallback — raises an error if any dataset cannot be loaded.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app
from app.services.inference import DATASET_REGISTRY
from src.data.registry import get_loader
from src.preprocessing.artifacts import load_preprocessor

# Map API dataset keys → (loader_name, split_arg)
# split_arg=None means load all available data (no named split)
LOADER_MAP: Dict[str, Tuple[str, Optional[str]]] = {
    "kdd99":          ("KDD99",           None),       # single file, no split
    "nsl_kdd":        ("NSL-KDD",         "test"),     # KDDTest+.txt
    "unsw_nb15":      ("UNSW-NB15",       "test"),     # UNSW_NB15_testing-set.csv
    "cic_ids2017":    ("CIC-IDS2017",     None),       # all day CSVs
    "cse_cic_ids2018":("CSE-CIC-IDS2018", None),       # all parquets
    "uwf_zeekdata24": ("UWF ZeekData",    None),       # all parquets
}

# Paths that must exist (file or directory) for a dataset to be considered available.
# If the path is absent we skip (data not mirrored); if it exists but loading fails
# we treat it as a hard error and stop.
DATA_AVAILABILITY: Dict[str, Path] = {
    "kdd99":          ROOT / "KDD99" / "kddcup.data",
    "nsl_kdd":        ROOT / "NSL KDD" / "KDDTest+.txt",
    "unsw_nb15":      ROOT / "NB15" / "UNSW_NB15_testing-set.csv",
    "cic_ids2017":    ROOT / "CIC2017" / "MachineLearningCVE",
    "cse_cic_ids2018":ROOT / "CIC2018",
    "uwf_zeekdata24": ROOT / "UWF ZeekData",
}

ROWS_PER_CLASS = 40
RANDOM_SEED = 42


def load_raw_for_dataset(
    ds_key: str,
    pre,
    max_load: int = 100_000,
) -> pd.DataFrame:
    """
    Load raw rows from the real data source and apply standardize + extract_labels
    (but NOT _clean_features), then attach ground-truth multiclass labels.

    Returns a DataFrame with raw feature columns + '_label' (ground-truth multiclass).
    Raises if data cannot be loaded.
    """
    loader_name, split_arg = LOADER_MAP[ds_key]
    loader = get_loader(loader_name, ROOT)

    # Load enough rows to get good class coverage
    kwargs: Dict[str, Any] = {"n_rows": max_load}
    if split_arg is not None:
        kwargs["split"] = split_arg
    df_raw, _ = loader.load_sample(**kwargs)

    if df_raw is None or len(df_raw) == 0:
        raise ValueError(f"Loader returned no data for {ds_key}")

    # Standardize column names (rename to canonical)
    df_std = pre._standardize_columns(df_raw)

    # Extract ground-truth labels and the keep mask
    y_binary, y_multi, keep_mask = pre._extract_labels(df_std)
    if y_multi is None:
        raise ValueError(f"No multiclass label found for {ds_key} after standardizing columns")

    df_std = df_std.loc[keep_mask].reset_index(drop=True)
    y_multi = y_multi[keep_mask]

    # Attach label; we will extract raw feature values here, BEFORE _clean_features,
    # so that the API receives the same raw values that would normally be passed
    # to preprocessor.transform() — which internally calls _clean_features.
    df_std["_label"] = y_multi
    return df_std


def stratified_sample(df: pd.DataFrame, rows_per_class: int, seed: int) -> pd.DataFrame:
    """Sample up to `rows_per_class` rows per unique '_label' class. Fixed seed."""
    parts = []
    for label, grp in df.groupby("_label"):
        n_take = min(len(grp), rows_per_class)
        parts.append(grp.sample(n=n_take, random_state=seed))
    if not parts:
        raise ValueError("No data after grouping by label")
    return pd.concat(parts, ignore_index=True)


def extract_api_features(row: pd.Series) -> Dict[str, Any]:
    """
    Extract the 5 API feature fields from a raw (pre-_clean_features) row.
    We pass values verbatim so that the API's internal preprocessor.transform()
    applies the same _clean_features logic as the offline path.
    """
    def safe_float(v, default=0.0) -> float:
        try:
            f = float(v)
            return f if np.isfinite(f) and f >= 0 else default
        except (TypeError, ValueError):
            return default

    def safe_int(v, default=0) -> int:
        try:
            i = int(float(v))
            return max(0, i)
        except (TypeError, ValueError):
            return default

    duration = safe_float(row.get("duration", 0.0))
    src_bytes = safe_int(row.get("src_bytes", 0))
    dst_bytes = safe_int(row.get("dst_bytes", 0))
    protocol = str(row.get("protocol", "tcp")).strip() or "tcp"
    service = str(row.get("service", "-")).strip() or "-"

    return {
        "duration": duration,
        "src_bytes": src_bytes,
        "dst_bytes": dst_bytes,
        "protocol": protocol,
        "service": service,
    }


def compute_confusion(
    gt_labels: List[str],
    pred_labels: List[str],
) -> str:
    """Return a compact confusion matrix string (GT rows × Pred cols)."""
    all_labels = sorted(set(gt_labels) | set(pred_labels))
    gt_arr = np.array(gt_labels)
    pred_arr = np.array(pred_labels)
    lines = []
    header = f"{'GT \\ PRED':<30}" + "".join(f"{l:<25}" for l in all_labels)
    lines.append(header)
    lines.append("-" * len(header))
    for gt_cls in all_labels:
        mask = gt_arr == gt_cls
        row_str = f"{gt_cls:<30}"
        for pred_cls in all_labels:
            count = int(np.sum(pred_arr[mask] == pred_cls))
            row_str += f"{count:<25}"
        lines.append(row_str)
    return "\n".join(lines)


def compute_per_class_recall(
    ds_key: str,
    pre,
    model,
    classes: List[str],
    max_load: int = 200_000,
) -> Dict[str, float]:
    """
    Compute per-class recall on the full test split using the offline model.
    Loads up to max_load rows; for KDD99 (no split), loads from the full file.
    """
    print(f"  Computing per-class recall on full test split (up to {max_load:,} rows)...")
    loader_name, split_arg = LOADER_MAP[ds_key]
    loader = get_loader(loader_name, ROOT)

    kwargs: Dict[str, Any] = {"n_rows": max_load}
    if split_arg is not None:
        kwargs["split"] = split_arg
    df_raw, _ = loader.load_sample(**kwargs)

    df_std = pre._standardize_columns(df_raw)
    _, y_multi, keep_mask = pre._extract_labels(df_std)
    if y_multi is None:
        print("    [WARN] No multiclass labels found — skipping recall computation")
        return {}

    df_std_keep = df_std.loc[keep_mask].reset_index(drop=True)
    y_true = y_multi[keep_mask]

    # Build feature DataFrame for offline prediction (raw, pre-clean)
    feature_df = _build_feature_df(df_std_keep)
    X, _, _ = pre.transform(feature_df)
    y_pred = model.predict(X)

    recall_per_class: Dict[str, float] = {}
    for cls in classes:
        mask = y_true == cls
        if not np.any(mask):
            continue
        correct = np.sum(y_pred[mask] == cls)
        recall_per_class[cls] = round(float(correct) / float(np.sum(mask)), 4)

    return recall_per_class


def _build_feature_df(df_std: pd.DataFrame) -> pd.DataFrame:
    """
    Build a 5-column DataFrame from a standardized (pre-_clean_features) DataFrame.
    Keeps only the columns the API uses; missing columns default to safe values.
    """
    records = []
    for _, row in df_std.iterrows():
        records.append(extract_api_features(row))
    return pd.DataFrame(records)


def run_parity_check(api_url: str | None = None, allow_skip: bool = False) -> int:
    print("=" * 80)
    print("NIDS BACKEND API PARITY CHECK — REAL DATA ONLY")
    print("=" * 80)

    overall_passed = True
    skipped_datasets: List[str] = []
    verified_datasets: List[str] = []
    test_client = None if api_url else TestClient(app)

    if test_client:
        test_client.__enter__()

    try:
        for ds_key, artifacts in DATASET_REGISTRY.items():
            print(f"\n{'='*60}")
            print(f"Dataset: {ds_key}")
            print(f"{'='*60}")

            pre_path = ROOT / "data" / "preprocessors" / artifacts["preprocessor"]
            model_path = ROOT / "models" / artifacts["model"]

            # ── Load preprocessor & model ──────────────────────────────────
            pre = load_preprocessor(pre_path)
            model = joblib.load(model_path)
            classes: List[str] = list(model.label_encoder.classes_)
            print(f"Model classes ({len(classes)}): {classes}")

            # ── Check data availability (skip if files not mirrored here) ───
            avail_path = DATA_AVAILABILITY[ds_key]
            if not avail_path.exists():
                print(f"  [SKIP] Data not available on this machine: {avail_path}")
                print(f"         Download {ds_key} dataset to run this check.")
                skipped_datasets.append(ds_key)
                continue

            # ── Load REAL data — hard error if files exist but load fails ────
            try:
                df_all = load_raw_for_dataset(ds_key, pre, max_load=80_000)
            except Exception as e:
                print(f"  [ERROR] Data files found but loading failed for {ds_key}: {e}")
                overall_passed = False
                sys.exit(1)

            gt_total_counts = df_all["_label"].value_counts().to_dict()
            print(f"  Total rows loaded: {len(df_all)}")
            print(f"  Ground-truth label distribution (full load): {gt_total_counts}")

            # ── Stratified sample ─────────────────────────────────────────
            df_sample = stratified_sample(df_all, ROWS_PER_CLASS, RANDOM_SEED)
            print(f"  Sample size: {len(df_sample)} rows "
                  f"({ROWS_PER_CLASS} per class, {df_sample['_label'].nunique()} classes)")

            gt_sample_counts = df_sample["_label"].value_counts().to_dict()
            print(f"  Ground-truth class counts in sample: {gt_sample_counts}")

            # ── Build feature rows (raw, pre-_clean_features) ─────────────
            feature_rows: List[Dict[str, Any]] = []
            gt_labels: List[str] = []
            for _, row in df_sample.iterrows():
                feature_rows.append(extract_api_features(row))
                gt_labels.append(str(row["_label"]))

            print(f"\n  First 5 sampled rows (raw API features):")
            for i, fr in enumerate(feature_rows[:5]):
                print(f"    [{i}] gt={gt_labels[i]!r}  feats={fr}")

            # ── Offline prediction ────────────────────────────────────────
            df_for_offline = pd.DataFrame(feature_rows)
            X_offline, _, _ = pre.transform(df_for_offline)
            offline_preds: List[str] = list(model.predict(X_offline))

            # ── API prediction ────────────────────────────────────────────
            payload = {"dataset": ds_key, "flows": feature_rows}
            if api_url:
                import httpx
                resp = httpx.post(
                    f"{api_url.rstrip('/')}/api/v1/predict/batch",
                    json=payload,
                    timeout=60.0,
                )
                assert resp.status_code == 200, f"API HTTP Error {resp.status_code}: {resp.text}"
                api_results = resp.json()
            else:
                resp = test_client.post("/api/v1/predict/batch", json=payload)
                assert resp.status_code == 200, f"TestClient Error {resp.status_code}: {resp.text}"
                api_results = resp.json()

            api_preds: List[str] = [item["label"] for item in api_results]

            # ── Match analysis ────────────────────────────────────────────
            pred_counts = pd.Series(api_preds).value_counts().to_dict()
            print(f"\n  API predicted class counts: {pred_counts}")

            mismatches = []
            attack_example = None
            for i, (off_pred, api_res) in enumerate(zip(offline_preds, api_results)):
                api_pred = api_res["label"]
                if off_pred != api_pred:
                    mismatches.append((i, gt_labels[i], off_pred, api_pred))
                if api_res["is_attack"] and attack_example is None:
                    attack_example = (i, api_res["label"], api_res["attack_type"], feature_rows[i])

            match_count = len(df_sample) - len(mismatches)
            match_rate = (match_count / len(df_sample)) * 100.0

            # ── Confusion matrix ──────────────────────────────────────────
            print(f"\n  Confusion Matrix (GT rows × API Pred cols):")
            print(compute_confusion(gt_labels, api_preds))

            # ── Offline-vs-API match ──────────────────────────────────────
            print(f"\n  Offline-vs-API Match Rate: {match_rate:.2f}% ({match_count}/{len(df_sample)})")

            if mismatches:
                overall_passed = False
                print(f"  [MISMATCHES: {len(mismatches)}]")
                for idx, gt_l, off_l, api_l in mismatches[:10]:
                    print(f"    Row {idx}: GT={gt_l!r}  Offline={off_l!r}  API={api_l!r}  feats={feature_rows[idx]}")
            else:
                print("  [OK] 100% offline-vs-API match")

            if attack_example:
                idx, label, atk_type, feats = attack_example
                print(f"\n  [ATTACK EXAMPLE] Row {idx}: attack_type={atk_type!r} | features={feats}")
            else:
                print("\n  [NOTICE] No attack classified by API in sample batch.")
                all_benign = all(p == "BENIGN" for p in api_preds)
                if all_benign:
                    print("  [WARN] Model predicts BENIGN for every row in the sample.")
                    offline_attack_count = sum(1 for p in offline_preds if p != "BENIGN")
                    print(f"         Offline model found {offline_attack_count} attack(s) in the same rows.")

            # ── Per-class recall on FULL test split ───────────────────────
            try:
                recall = compute_per_class_recall(ds_key, pre, model, classes)
                print(f"\n  Per-class recall on full test split:")
                for cls in classes:
                    r = recall.get(cls)
                    if r is not None:
                        bar = "█" * int(r * 20)
                        print(f"    {cls:<35} {r:.4f}  {bar}")
                    else:
                        print(f"    {cls:<35} (no samples in test split)")
            except Exception as e:
                print(f"\n  [WARN] Could not compute full-split recall for {ds_key}: {e}")

            verified_datasets.append(ds_key)

    finally:
        if test_client:
            test_client.__exit__(None, None, None)

    total = len(DATASET_REGISTRY)
    n_verified = len(verified_datasets)
    n_skipped = len(skipped_datasets)

    print("\n" + "=" * 80)
    print(f"SUMMARY: Verified {n_verified}/{total} datasets" +
          (f", skipped: {skipped_datasets}" if skipped_datasets else "") + ".")

    if skipped_datasets and not allow_skip:
        print(f"[FAIL] {n_skipped} dataset(s) skipped. Pass --allow-skip to suppress this failure.")
        overall_passed = False

    if overall_passed:
        print("ALL CHECKED DATASETS PASSED PARITY CHECK (100% OFFLINE-VS-API MATCH).")
        return 0
    else:
        print("PARITY CHECK FAILED: mismatches or unskipped skips detected.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run NIDS API Parity Check — real data only")
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Optional external API base URL (e.g. http://localhost:8000). "
             "Omit to use FastAPI TestClient.",
    )
    parser.add_argument(
        "--allow-skip",
        action="store_true",
        default=False,
        help="Do not exit non-zero when datasets are skipped due to missing data files.",
    )
    args = parser.parse_args()
    sys.exit(run_parity_check(args.url, allow_skip=args.allow_skip))
