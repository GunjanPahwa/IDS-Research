"""Stage 1: Binary attack/benign classifier using XGBoost on common7 feature space.

Trains 4 per-dataset models + 1 pooled model and evaluates cross-dataset generalization.
Produces a 4×4 accuracy/F1 matrix (rows=train source, cols=eval dataset).
Saves all results to results/stage1_binary_results.json.
"""
from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    roc_auc_score,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_FILE = RESULTS_DIR / "stage1_binary_results.json"

# KDD99 and NSL-KDD excluded: incompatible with common7
DATASETS = [
    "cic-ids2017",
    "cse-cic-ids2018",
    "unsw-nb15",
    "uwf_zeekdata",
]
FEATURE_SPACE = "common7"
LABEL_COL = "label"

# XGBoost hyperparameters (hist method = fast for large datasets)
XGB_BASE_PARAMS = dict(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    tree_method="hist",
    n_jobs=-1,
    random_state=42,
    eval_metric="logloss",
    verbosity=0,
)


# ─── Data Loading ──────────────────────────────────────────────────────────────

def load_dataset(key: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(PROCESSED / f"{key}_{FEATURE_SPACE}_train.csv")
    test  = pd.read_csv(PROCESSED / f"{key}_{FEATURE_SPACE}_test.csv")
    return train, test


def split_xy(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    X = df.drop(columns=[LABEL_COL]).values.astype(np.float32)
    y = df[LABEL_COL].values.astype(np.int32)
    return X, y


# ─── Sanity Checks ─────────────────────────────────────────────────────────────

def check_class_balance(key: str, y: np.ndarray, split: str) -> dict:
    n = len(y)
    n_pos = int(y.sum())
    n_neg = n - n_pos
    ratio = n_pos / n if n > 0 else 0.0
    flag = ""
    if ratio < 0.05 or ratio > 0.95:
        flag = "SEVERE_IMBALANCE"
    elif ratio < 0.15 or ratio > 0.85:
        flag = "IMBALANCED"
    print(f"  [{split}] {key}: n={n:,}  benign={n_neg:,} ({100*(1-ratio):.1f}%)  attack={n_pos:,} ({100*ratio:.1f}%)  {flag}")
    return {"n": n, "n_benign": n_neg, "n_attack": n_pos, "attack_ratio": round(ratio, 4), "flag": flag}


# ─── Metrics ───────────────────────────────────────────────────────────────────

def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray | None = None) -> dict:
    cm = confusion_matrix(y_true, y_pred).tolist()
    metrics = {
        "accuracy":  round(float(accuracy_score(y_true, y_pred)), 6),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 6),
        "recall":    round(float(recall_score(y_true, y_pred, zero_division=0)), 6),
        "f1":        round(float(f1_score(y_true, y_pred, zero_division=0)), 6),
        "confusion_matrix": cm,
    }
    if y_prob is not None:
        try:
            metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_prob)), 6)
        except ValueError:
            metrics["roc_auc"] = None
    return metrics


def flag_suspicious(train_key: str, eval_key: str, metrics: dict) -> str:
    acc = metrics["accuracy"]
    f1  = metrics["f1"]
    if train_key != eval_key:
        if acc > 0.97:
            return "SUSPICIOUSLY_HIGH (>97% cross-dataset — check feature scaling)"
        if f1 < 0.55:
            return "SUSPICIOUSLY_LOW (F1<0.55 cross-dataset — near random)"
    return ""


# ─── Training ──────────────────────────────────────────────────────────────────

def train_model(X_train: np.ndarray, y_train: np.ndarray, label: str) -> XGBClassifier:
    n_neg = int((y_train == 0).sum())
    n_pos = int((y_train == 1).sum())
    # Weight to handle class imbalance
    spw = round(n_neg / n_pos, 4) if n_pos > 0 else 1.0
    print(f"  Training {label}  n={len(y_train):,}  scale_pos_weight={spw}")
    t0 = time.time()
    clf = XGBClassifier(**XGB_BASE_PARAMS, scale_pos_weight=spw)
    clf.fit(X_train, y_train)
    print(f"  Done in {time.time()-t0:.1f}s")
    return clf


def eval_model(clf: XGBClassifier, X: np.ndarray, y: np.ndarray) -> dict:
    y_pred = clf.predict(X)
    y_prob = clf.predict_proba(X)[:, 1]
    return compute_metrics(y, y_pred, y_prob)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Stage 1: Binary Classifier — Common-7 Feature Space")
    print("=" * 60)

    # ── Load all data ──────────────────────────────────────────────
    print("\n[1] Loading datasets...")
    data: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    balance_info: dict[str, dict] = {}

    for ds in DATASETS:
        print(f"\n  {ds}")
        train_df, test_df = load_dataset(ds)
        X_tr, y_tr = split_xy(train_df)
        X_te, y_te = split_xy(test_df)
        data[ds] = (X_tr, y_tr, X_te, y_te)
        balance_info[ds] = {
            "train": check_class_balance(ds, y_tr, "train"),
            "test":  check_class_balance(ds, y_te, "test"),
        }

    # ── Per-dataset models ─────────────────────────────────────────
    print("\n[2] Training per-dataset models...")
    per_dataset_results: dict[str, dict] = {}
    models: dict[str, XGBClassifier] = {}

    for train_ds in DATASETS:
        X_tr, y_tr, _, _ = data[train_ds]
        print(f"\n  Model: trained on {train_ds}")
        clf = train_model(X_tr, y_tr, train_ds)
        models[train_ds] = clf

        eval_row: dict[str, dict] = {}
        for eval_ds in DATASETS:
            _, _, X_te, y_te = data[eval_ds]
            m = eval_model(clf, X_te, y_te)
            flag = flag_suspicious(train_ds, eval_ds, m)
            if flag:
                print(f"    ⚠ {train_ds} → {eval_ds}: {flag}")
            eval_row[eval_ds] = {**m, "flag": flag}

        per_dataset_results[train_ds] = eval_row

    # ── Pooled model ───────────────────────────────────────────────
    print("\n[3] Training pooled model (all 4 datasets combined)...")
    X_pool = np.concatenate([data[ds][0] for ds in DATASETS], axis=0)
    y_pool = np.concatenate([data[ds][1] for ds in DATASETS], axis=0)
    pooled_clf = train_model(X_pool, y_pool, "POOLED")

    pooled_results: dict[str, dict] = {}
    for eval_ds in DATASETS:
        _, _, X_te, y_te = data[eval_ds]
        m = eval_model(pooled_clf, X_te, y_te)
        flag = flag_suspicious("pooled", eval_ds, m)
        if flag:
            print(f"  ⚠ pooled → {eval_ds}: {flag}")
        pooled_results[eval_ds] = {**m, "flag": flag}

    # Combined test set eval
    X_test_all = np.concatenate([data[ds][2] for ds in DATASETS], axis=0)
    y_test_all = np.concatenate([data[ds][3] for ds in DATASETS], axis=0)
    pooled_results["combined"] = eval_model(pooled_clf, X_test_all, y_test_all)

    # ── Print 4×4 matrix ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("4×4 ACCURACY MATRIX (row=train source, col=eval dataset)")
    print("=" * 60)
    header = f"{'':22s}" + "".join(f"{ds[:14]:>16s}" for ds in DATASETS)
    print(header)
    for train_ds in DATASETS:
        row = f"{train_ds[:22]:22s}"
        for eval_ds in DATASETS:
            acc = per_dataset_results[train_ds][eval_ds]["accuracy"]
            row += f"{acc:>16.4f}"
        print(row)
    print(f"\n{'pooled':22s}" + "".join(
        f"{pooled_results[ds]['accuracy']:>16.4f}" for ds in DATASETS
    ))

    print("\n4×4 F1 MATRIX")
    print(header)
    for train_ds in DATASETS:
        row = f"{train_ds[:22]:22s}"
        for eval_ds in DATASETS:
            f1 = per_dataset_results[train_ds][eval_ds]["f1"]
            row += f"{f1:>16.4f}"
        print(row)
    print(f"\n{'pooled':22s}" + "".join(
        f"{pooled_results[ds]['f1']:>16.4f}" for ds in DATASETS
    ))

    # ── Save results ───────────────────────────────────────────────
    output = {
        "meta": {
            "feature_space": FEATURE_SPACE,
            "datasets": DATASETS,
            "model": "XGBClassifier",
            "xgb_params": XGB_BASE_PARAMS,
            "date": time.strftime("%Y-%m-%d"),
        },
        "class_balance": balance_info,
        "per_dataset_models": per_dataset_results,
        "pooled_model": pooled_results,
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2))
    print(f"\n[✓] Results saved to {RESULTS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
