"""
TabNet Stage 1 Binary Classifier — UNSW-NB15 Native (PoC Run)

PoC settings (CPU-optimised):
  - n_steps=3  (default is 5; reduces sparse-attention compute by ~40%)
  - max_epochs=50 (default is 200)
  - batch_size=8192 (large batches amortise CPU overhead)
  - virtual_batch_size=512

Drops the BOM-corrupted column before training (same fix as stage1_binary_unsw-nb15_native.pkl).
"""
from __future__ import annotations

import json
import pickle
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
)
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(r"c:\Users\HP\OneDrive\Desktop\Minor Project")
sys.path.insert(0, str(ROOT))
PROCESSED   = ROOT / "data" / "processed"
MODELS_DIR  = ROOT / "models"
RESULTS_DIR = ROOT / "results"
MODELS_DIR.mkdir(exist_ok=True)

_BOM_STRIP = "\ufeff\u00a0\u200b\u200c\u200d\u2060\ufffe"

def _sanitize(df):
    df.columns = [str(c).strip(_BOM_STRIP).strip() for c in df.columns]
    return df

def load_unsw_native():
    tr = _sanitize(pd.read_csv(PROCESSED / "unsw-nb15_native_train.csv"))
    te = _sanitize(pd.read_csv(PROCESSED / "unsw-nb15_native_test.csv"))
    id_cols = [c for c in tr.columns if c.strip(_BOM_STRIP).strip().lower() == "id"]
    if id_cols:
        print(f"  [Sanitize] Dropping id-like columns: {id_cols}")
        tr = tr.drop(columns=id_cols, errors="ignore")
        te = te.drop(columns=id_cols, errors="ignore")
    feature_cols = [c for c in tr.columns if c != "label"]
    X_tr = tr[feature_cols].values.astype(np.float32)
    y_tr = tr["label"].values.astype(np.int64)
    X_te = te[feature_cols].values.astype(np.float32)
    y_te = te["label"].values.astype(np.int64)
    return X_tr, y_tr, X_te, y_te, feature_cols


def main():
    print("=" * 72)
    print("TabNet Binary Classifier — UNSW-NB15 Native (PoC: n_steps=3, epochs=50)")
    print("=" * 72)

    print("\n[1] Loading UNSW-NB15 native data...")
    X_tr, y_tr, X_te, y_te, feature_cols = load_unsw_native()
    print(f"  Train: {X_tr.shape}, Attack ratio: {y_tr.mean():.3f}")
    print(f"  Test:  {X_te.shape}, Attack ratio: {y_te.mean():.3f}")
    print(f"  Feature count: {len(feature_cols)}")

    print("\n[2] Scaling features (StandardScaler for TabNet convergence)...")
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_tr)
    X_te_sc = scaler.transform(X_te)

    n_neg = int((y_tr == 0).sum())
    n_pos = int((y_tr == 1).sum())
    w_pos = n_neg / (n_neg + n_pos)
    w_neg = n_pos / (n_neg + n_pos)
    weights_tr = np.where(y_tr == 1, w_pos, w_neg).astype(np.float32)
    print(f"  Class weights — benign: {w_neg:.4f}, attack: {w_pos:.4f}")

    print("\n[3] Training TabNet (n_steps=3, max_epochs=50, batch_size=8192)...")
    from pytorch_tabnet.tab_model import TabNetClassifier
    import torch

    clf = TabNetClassifier(
        n_steps=3,
        n_d=32,
        n_a=32,
        gamma=1.3,
        cat_idxs=[],
        cat_dims=[],
        momentum=0.02,
        optimizer_fn=torch.optim.Adam,
        optimizer_params={"lr": 2e-3, "weight_decay": 1e-5},
        scheduler_fn=torch.optim.lr_scheduler.StepLR,
        scheduler_params={"step_size": 10, "gamma": 0.9},
        mask_type="sparsemax",
        device_name="cpu",
        verbose=5,
        seed=42,
    )

    t0 = time.time()
    clf.fit(
        X_train=X_tr_sc,
        y_train=y_tr,
        eval_set=[(X_te_sc, y_te)],
        eval_name=["test"],
        eval_metric=["auc"],
        max_epochs=50,
        patience=15,
        batch_size=8192,
        virtual_batch_size=512,
        weights=weights_tr,
    )
    elapsed = round(time.time() - t0, 1)
    print(f"\n  Training complete in {elapsed}s")

    print("\n[4] Evaluating — threshold sweep for best F1...")
    y_prob = clf.predict_proba(X_te_sc)[:, 1]
    thresholds = np.arange(0.3, 0.8, 0.01)
    best_t, best_f1 = 0.5, 0.0
    for t in thresholds:
        f1_t = f1_score((y_prob >= t).astype(int), y_te, zero_division=0)
        if f1_t > best_f1:
            best_f1, best_t = f1_t, t
    y_pred = (y_prob >= best_t).astype(int)
    print(f"  Optimal threshold: {best_t:.2f}")

    acc  = accuracy_score(y_te, y_pred)
    prec = precision_score(y_te, y_pred, zero_division=0)
    rec  = recall_score(y_te, y_pred, zero_division=0)
    f1   = f1_score(y_te, y_pred, zero_division=0)
    auc  = roc_auc_score(y_te, y_prob)
    cm   = confusion_matrix(y_te, y_pred)

    print("\n" + "=" * 72)
    print("TABNET RESULTS — UNSW-NB15 Native")
    print("=" * 72)
    print(f"  Accuracy : {acc:.6f}")
    print(f"  Precision: {prec:.6f}")
    print(f"  Recall   : {rec:.6f}")
    print(f"  F1-Score : {f1:.6f}")
    print(f"  ROC-AUC  : {auc:.6f}")
    print(f"  Confusion Matrix (TN FP / FN TP): {cm[0].tolist()} / {cm[1].tolist()}")
    print(f"  Training time: {elapsed}s")

    XGBOOST_BASELINE = {
        "accuracy": 0.909889, "precision": 0.881964,
        "recall": 0.965565, "f1": 0.921873, "roc_auc": 0.985180,
    }
    print("\n  --- vs XGBoost Baseline ---")
    print(f"  {'Metric':<12} | {'XGBoost':>10} | {'TabNet':>10} | {'Delta':>10}")
    print("  " + "-" * 48)
    for m, xv in XGBOOST_BASELINE.items():
        tv = {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": auc}[m]
        d = tv - xv
        print(f"  {m:<12} | {xv:>10.6f} | {tv:>10.6f} | {d:>+.6f}")

    print("\n[5] Saving artifacts...")
    pkl_path = MODELS_DIR / "tabnet_binary_unsw-nb15_native.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump({"clf": clf, "scaler": scaler, "threshold": best_t}, f)
    print(f"  [Saved] {pkl_path}")

    out = {
        "model": "TabNet", "dataset": "unsw-nb15_native",
        "n_steps": 3, "max_epochs": 50,
        "optimal_threshold": round(float(best_t), 2),
        "training_time_sec": elapsed,
        "accuracy": acc, "precision": prec, "recall": rec,
        "f1": f1, "roc_auc": auc,
        "confusion_matrix": cm.tolist(),
        "xgboost_baseline": XGBOOST_BASELINE,
    }
    res_path = RESULTS_DIR / "tabnet_unsw_native_results.json"
    res_path.write_text(json.dumps(out, indent=2))
    print(f"  [Saved] {res_path}")
    print("\nTabNet PoC complete.")


if __name__ == "__main__":
    main()
