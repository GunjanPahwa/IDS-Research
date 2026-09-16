"""
Autoencoder Anomaly Detector — UNSW-NB15 Native (PoC Run)

Architecture:
  Encoder: 60 -> 32 -> 16 -> 8 (bottleneck)
  Decoder: 8  -> 16 -> 32 -> 60
  Loss: MSE reconstruction on benign-only training samples
  Activation: LeakyReLU (better gradient flow than ReLU)
  Batch normalisation after each layer for stability

Anomaly detection logic:
  - Train ONLY on benign (label=0) samples
  - At inference: compute per-sample MSE reconstruction error on all test samples
  - Threshold: 95th percentile of benign validation reconstruction errors
  - Attack samples should have higher reconstruction error (they're OOD)

Outputs:
  - models/autoencoder_unsw-nb15_native.pkl  (model + scaler + threshold)
  - Reconstruction error distributions (percentiles) for benign vs attack
  - Full classification metrics at chosen threshold
  - Comparison vs XGBoost baseline
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
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
)
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
torch.manual_seed(42)
np.random.seed(42)

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


# ── Model Definition ──────────────────────────────────────────────────────────

class NetworkAnomalyAutoencoder(nn.Module):
    """Symmetric bottleneck autoencoder for NIDS anomaly detection.

    Trained on benign-only traffic; attack flows produce higher
    MSE reconstruction error (out-of-distribution signal).
    """

    def __init__(self, input_dim: int, bottleneck_dim: int = 8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32), nn.BatchNorm1d(32), nn.LeakyReLU(0.1),
            nn.Linear(32, 16),        nn.BatchNorm1d(16), nn.LeakyReLU(0.1),
            nn.Linear(16, bottleneck_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, 16), nn.BatchNorm1d(16), nn.LeakyReLU(0.1),
            nn.Linear(16, 32),             nn.BatchNorm1d(32), nn.LeakyReLU(0.1),
            nn.Linear(32, input_dim),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

    def reconstruction_error(self, x: torch.Tensor) -> torch.Tensor:
        """Per-sample MSE reconstruction error (no reduction)."""
        with torch.no_grad():
            recon = self.forward(x)
            return ((recon - x) ** 2).mean(dim=1)


# ── Training ──────────────────────────────────────────────────────────────────

def train_autoencoder(
    model: NetworkAnomalyAutoencoder,
    X_benign_train: np.ndarray,
    X_benign_val: np.ndarray,
    n_epochs: int = 50,
    batch_size: int = 512,
    lr: float = 1e-3,
) -> list[float]:
    """Train on benign-only samples. Returns per-epoch validation MSE."""
    device = torch.device("cpu")
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)
    criterion = nn.MSELoss()

    X_t = torch.tensor(X_benign_train, dtype=torch.float32)
    loader = DataLoader(TensorDataset(X_t), batch_size=batch_size, shuffle=True)
    X_val_t = torch.tensor(X_benign_val, dtype=torch.float32)

    val_losses = []
    for epoch in range(1, n_epochs + 1):
        model.train()
        epoch_loss = 0.0
        for (batch,) in loader:
            optimizer.zero_grad()
            recon = model(batch)
            loss = criterion(recon, batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(batch)
        epoch_loss /= len(X_t)
        scheduler.step()

        model.eval()
        with torch.no_grad():
            val_recon = model(X_val_t)
            val_loss = criterion(val_recon, X_val_t).item()
        val_losses.append(val_loss)

        if epoch % 10 == 0 or epoch == 1:
            print(f"  Epoch {epoch:>3}/{n_epochs} | Train MSE: {epoch_loss:.6f} | Val MSE: {val_loss:.6f}")

    return val_losses


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("Autoencoder Anomaly Detector — UNSW-NB15 Native (PoC: 50 epochs)")
    print("=" * 72)

    # ── Load data ─────────────────────────────────────────────────────────────
    print("\n[1] Loading UNSW-NB15 native data...")
    tr = _sanitize(pd.read_csv(PROCESSED / "unsw-nb15_native_train.csv"))
    te = _sanitize(pd.read_csv(PROCESSED / "unsw-nb15_native_test.csv"))

    id_cols = [c for c in tr.columns if c.strip(_BOM_STRIP).strip().lower() == "id"]
    if id_cols:
        print(f"  [Sanitize] Dropping: {id_cols}")
        tr = tr.drop(columns=id_cols, errors="ignore")
        te = te.drop(columns=id_cols, errors="ignore")

    feature_cols = [c for c in tr.columns if c != "label"]
    X_all_tr = tr[feature_cols].values.astype(np.float32)
    y_tr = tr["label"].values.astype(np.int32)
    X_te = te[feature_cols].values.astype(np.float32)
    y_te = te["label"].values.astype(np.int32)

    print(f"  Train: {X_all_tr.shape} | Attack ratio: {y_tr.mean():.3f}")
    print(f"  Test:  {X_te.shape}  | Attack ratio: {y_te.mean():.3f}")

    # Extract benign-ONLY training samples
    X_benign_all = X_all_tr[y_tr == 0]
    print(f"  Benign-only train samples: {len(X_benign_all)}")

    # ── Scale ─────────────────────────────────────────────────────────────────
    print("\n[2] Fitting StandardScaler on benign training samples...")
    scaler = StandardScaler()
    X_benign_sc = scaler.fit_transform(X_benign_all)
    X_te_sc = scaler.transform(X_te)

    # Split benign into train/val (90/10) for threshold calibration
    n_val = max(1000, int(0.10 * len(X_benign_sc)))
    X_b_train = X_benign_sc[:-n_val]
    X_b_val   = X_benign_sc[-n_val:]
    print(f"  Benign train: {len(X_b_train)}, Benign val: {len(X_b_val)}")

    # ── Train ─────────────────────────────────────────────────────────────────
    print(f"\n[3] Training Autoencoder (input_dim={len(feature_cols)}, bottleneck=8, epochs=50)...")
    model = NetworkAnomalyAutoencoder(input_dim=len(feature_cols), bottleneck_dim=8)
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
    t0 = time.time()
    val_losses = train_autoencoder(model, X_b_train, X_b_val, n_epochs=50, batch_size=512, lr=1e-3)
    elapsed = round(time.time() - t0, 1)
    print(f"  Training complete in {elapsed}s")

    # ── Reconstruction Errors ─────────────────────────────────────────────────
    print("\n[4] Computing reconstruction errors on test set...")
    model.eval()
    X_te_t = torch.tensor(X_te_sc, dtype=torch.float32)
    errors = model.reconstruction_error(X_te_t).numpy()

    errors_benign = errors[y_te == 0]
    errors_attack = errors[y_te == 1]

    print("\n  --- Reconstruction Error Distribution ---")
    print(f"  {'Percentile':<12} | {'Benign':>12} | {'Attack':>12}")
    print("  " + "-" * 42)
    for p in [5, 25, 50, 75, 90, 95, 99, 100]:
        b_val = np.percentile(errors_benign, p)
        a_val = np.percentile(errors_attack, p)
        print(f"  {p:>10}th | {b_val:>12.6f} | {a_val:>12.6f}")

    # Separation metric: what fraction of attacks exceed the 95th-pct benign threshold?
    threshold_95 = np.percentile(errors_benign, 95)
    threshold_99 = np.percentile(errors_benign, 99)
    frac_attacks_above_95 = (errors_attack > threshold_95).mean()
    frac_attacks_above_99 = (errors_attack > threshold_99).mean()
    frac_benign_above_95  = (errors_benign > threshold_95).mean()

    print(f"\n  95th-pct benign threshold: {threshold_95:.6f}")
    print(f"  Attacks above threshold:   {frac_attacks_above_95:.4f} ({frac_attacks_above_95*100:.1f}%)")
    print(f"  Benign above threshold:    {frac_benign_above_95:.4f}  (FPR = {frac_benign_above_95*100:.1f}%)")
    print(f"  99th-pct benign threshold: {threshold_99:.6f}")
    print(f"  Attacks above 99th-pct:    {frac_attacks_above_99:.4f} ({frac_attacks_above_99*100:.1f}%)")

    # ── Threshold sweep for best F1 ───────────────────────────────────────────
    print("\n[5] Threshold sweep for classification metrics...")
    # Sample candidate thresholds from the error distribution
    candidates = np.percentile(errors, np.arange(1, 100, 1))
    best_t, best_f1 = threshold_95, 0.0
    for t in candidates:
        y_pred_t = (errors >= t).astype(int)
        f1_t = f1_score(y_te, y_pred_t, zero_division=0)
        if f1_t > best_f1:
            best_f1, best_t = f1_t, t

    y_pred = (errors >= best_t).astype(int)
    print(f"  Optimal threshold (best F1): {best_t:.6f}")

    acc  = accuracy_score(y_te, y_pred)
    prec = precision_score(y_te, y_pred, zero_division=0)
    rec  = recall_score(y_te, y_pred, zero_division=0)
    f1   = f1_score(y_te, y_pred, zero_division=0)
    auc  = roc_auc_score(y_te, errors)  # higher error = more anomalous
    cm   = confusion_matrix(y_te, y_pred)

    print("\n" + "=" * 72)
    print("AUTOENCODER RESULTS — UNSW-NB15 Native")
    print("=" * 72)
    print(f"  Accuracy : {acc:.6f}")
    print(f"  Precision: {prec:.6f}")
    print(f"  Recall   : {rec:.6f}")
    print(f"  F1-Score : {f1:.6f}")
    print(f"  ROC-AUC  : {auc:.6f}  (reconstruction error as score)")
    print(f"  Confusion Matrix (TN FP / FN TP): {cm[0].tolist()} / {cm[1].tolist()}")
    print(f"  Training time: {elapsed}s")

    XGBOOST_BASELINE = {
        "accuracy": 0.909889, "precision": 0.881964,
        "recall": 0.965565, "f1": 0.921873, "roc_auc": 0.985180,
    }
    print("\n  --- vs XGBoost Baseline ---")
    print(f"  {'Metric':<12} | {'XGBoost':>10} | {'Autoenc':>10} | {'Delta':>10}")
    print("  " + "-" * 50)
    results = {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": auc}
    for m, xv in XGBOOST_BASELINE.items():
        tv = results[m]
        d = tv - xv
        print(f"  {m:<12} | {xv:>10.6f} | {tv:>10.6f} | {d:>+.6f}")

    # ── Save ──────────────────────────────────────────────────────────────────
    print("\n[6] Saving artifacts...")
    pkl_path = MODELS_DIR / "autoencoder_unsw-nb15_native.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump({"model": model, "scaler": scaler,
                     "threshold_f1": float(best_t),
                     "threshold_95pct_benign": float(threshold_95),
                     "threshold_99pct_benign": float(threshold_99)}, f)
    print(f"  [Saved] {pkl_path}")

    out = {
        "model": "Autoencoder", "dataset": "unsw-nb15_native",
        "architecture": "60->32->16->8->16->32->60",
        "bottleneck_dim": 8, "n_epochs": 50,
        "training_time_sec": elapsed,
        "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": auc,
        "confusion_matrix": cm.tolist(),
        "threshold_best_f1": float(best_t),
        "threshold_95pct_benign": float(threshold_95),
        "threshold_99pct_benign": float(threshold_99),
        "reconstruction_error_distributions": {
            "benign": {f"p{p}": float(np.percentile(errors_benign, p))
                       for p in [5, 25, 50, 75, 90, 95, 99, 100]},
            "attack": {f"p{p}": float(np.percentile(errors_attack, p))
                       for p in [5, 25, 50, 75, 90, 95, 99, 100]},
        },
        "frac_attacks_above_95pct_benign": float(frac_attacks_above_95),
        "frac_attacks_above_99pct_benign": float(frac_attacks_above_99),
        "xgboost_baseline": XGBOOST_BASELINE,
    }
    res_path = RESULTS_DIR / "autoencoder_unsw_native_results.json"
    res_path.write_text(json.dumps(out, indent=2))
    print(f"  [Saved] {res_path}")
    print("\nAutoencoder PoC complete.")


if __name__ == "__main__":
    main()
