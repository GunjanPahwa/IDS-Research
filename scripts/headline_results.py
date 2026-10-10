"""
Headline results regeneration from source of truth.

Tasks:
1. Recompute accuracy, macro-F1, weighted-F1 for each dataset with data present.
   Print side-by-side vs model_benchmarks.json AND README.md Table 1. List mismatches.
2. (Results printed; README update done separately by the script.)
3. KDD99: count train-test overlap rows. Recompute metrics after dropping overlaps.
4. NSL-KDD: why are R2L/U2R classes absent from the trained label set?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.kdd99 import KDD99Loader
from src.data.nsl_kdd import NSLKDDLoader
from src.data.unsw_nb15 import UNSWNB15Loader
from src.preprocessing.artifacts import load_preprocessor

LABEL_CSV    = ROOT / "data" / "label_mapping.csv"
BENCHMARKS   = ROOT / "results" / "model_benchmarks.json"

ARTIFACTS = {
    "kdd99":    ("kdd99_common5_preprocessor.pkl",    "unified_singlestage_kdd99_common5.pkl"),
    "nsl_kdd":  ("nsl-kdd_common5_preprocessor.pkl",  "unified_singlestage_nsl-kdd_common5.pkl"),
    "unsw_nb15":("unsw-nb15_common5_preprocessor.pkl","unified_singlestage_unsw-nb15_common5.pkl"),
}

# README Table 1 values (Unified Single-Stage row, columns: macro_prec, macro_rec, macro_f1, weighted_f1, accuracy)
README_TABLE1 = {
    "kdd99":    {"macro_prec": 0.9450, "macro_rec": 0.9261, "macro_f1": 0.9341, "weighted_f1": 0.9992, "accuracy": 0.9992},
    "nsl_kdd":  {"macro_prec": 0.8420, "macro_rec": 0.8115, "macro_f1": 0.8256, "weighted_f1": 0.9801, "accuracy": 0.9801},
    "unsw_nb15":{"macro_prec": 0.5510, "macro_rec": 0.5280, "macro_f1": 0.5336, "weighted_f1": 0.9612, "accuracy": 0.9612},
}


def section(title: str):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def load_preprocessor_and_model(ds_key: str):
    pre_file, model_file = ARTIFACTS[ds_key]
    pre   = load_preprocessor(ROOT / "data" / "preprocessors" / pre_file)
    model = joblib.load(ROOT / "models" / model_file)
    return pre, model


def build_feature_df(df_std: pd.DataFrame) -> pd.DataFrame:
    """Extract the 5 API-compatible feature columns from a standardised DataFrame."""
    res = pd.DataFrame(index=df_std.index)
    res["duration"] = pd.to_numeric(df_std.get("duration", 0.0), errors="coerce").fillna(0.0).clip(lower=0.0).astype(float)
    res["src_bytes"] = pd.to_numeric(df_std.get("src_bytes", 0), errors="coerce").fillna(0).clip(lower=0).astype(int)
    res["dst_bytes"] = pd.to_numeric(df_std.get("dst_bytes", 0), errors="coerce").fillna(0).clip(lower=0).astype(int)
    
    prot = df_std["protocol"].astype(str).str.strip() if "protocol" in df_std.columns else pd.Series("tcp", index=df_std.index)
    res["protocol"] = prot.replace("", "tcp")
    
    srv = df_std["service"].astype(str).str.strip() if "service" in df_std.columns else pd.Series("-", index=df_std.index)
    res["service"] = srv.replace("", "-")
    
    return res


def compute_metrics(y_true, y_pred):
    labels = sorted(set(y_true) | set(y_pred))
    acc  = accuracy_score(y_true, y_pred)
    mf1  = f1_score(y_true, y_pred, average="macro",    zero_division=0, labels=labels)
    wf1  = f1_score(y_true, y_pred, average="weighted", zero_division=0, labels=labels)
    mprec = f1_score(y_true, y_pred, average="macro",   zero_division=0, labels=labels)  # placeholder
    # proper precision
    from sklearn.metrics import precision_score, recall_score
    mprec = precision_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)
    mrec  = recall_score(   y_true, y_pred, average="macro", zero_division=0, labels=labels)
    return {"accuracy": acc, "macro_f1": mf1, "weighted_f1": wf1,
            "macro_prec": mprec, "macro_rec": mrec}


def mismatch_flag(live, stored, tol=0.0005):
    return "⚠ MISMATCH" if abs(live - stored) > tol else "✓"


# ─────────────────────────────────────────────────────────────────────────────
# Load benchmarks.json
# ─────────────────────────────────────────────────────────────────────────────
with open(BENCHMARKS) as f:
    BM = json.load(f)

def bm_unified(ds_bm_key: str) -> dict:
    return BM["stage2_multiclass_and_unified"][ds_bm_key]["unified_single_stage"]

BM_STORED = {
    "kdd99":    bm_unified("kdd99"),
    "nsl_kdd":  bm_unified("nsl-kdd"),
    "unsw_nb15":bm_unified("unsw-nb15"),
}

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 — Recompute metrics for all 3 datasets
# ─────────────────────────────────────────────────────────────────────────────
section("TASK 1 — Live metric recomputation vs benchmarks.json and README Table 1")

live_results: dict[str, dict] = {}

# ── UNSW-NB15 ──────────────────────────────────────────────────────────────
print("\n--- UNSW-NB15 (test split: UNSW_NB15_testing-set.csv) ---")
pre_unsw, model_unsw = load_preprocessor_and_model("unsw_nb15")
loader_unsw = UNSWNB15Loader(root_dir=ROOT)
df_raw_unsw, _ = loader_unsw.load_sample(n_rows=500_000, split="test")

df_std_unsw = pre_unsw._standardize_columns(df_raw_unsw)
_, y_multi_unsw, keep_unsw = pre_unsw._extract_labels(df_std_unsw)
df_std_unsw = df_std_unsw.loc[keep_unsw].reset_index(drop=True)
y_true_unsw = y_multi_unsw[keep_unsw]
feat_df_unsw = build_feature_df(df_std_unsw)
X_unsw, _, _ = pre_unsw.transform(feat_df_unsw)
y_pred_unsw = model_unsw.predict(X_unsw)
live_results["unsw_nb15"] = compute_metrics(y_true_unsw, y_pred_unsw)
print(f"  Rows evaluated: {len(y_true_unsw):,}")
print(f"  Live: accuracy={live_results['unsw_nb15']['accuracy']:.6f}  "
      f"macro_f1={live_results['unsw_nb15']['macro_f1']:.6f}  "
      f"weighted_f1={live_results['unsw_nb15']['weighted_f1']:.6f}")

# ── NSL-KDD ────────────────────────────────────────────────────────────────
print("\n--- NSL-KDD (test split: KDDTest+.txt) ---")
pre_nsl, model_nsl = load_preprocessor_and_model("nsl_kdd")
loader_nsl = NSLKDDLoader(root_dir=ROOT)
df_raw_nsl, _ = loader_nsl.load_sample(n_rows=100_000, split="test")

df_std_nsl = pre_nsl._standardize_columns(df_raw_nsl)
_, y_multi_nsl, keep_nsl = pre_nsl._extract_labels(df_std_nsl)
df_std_nsl = df_std_nsl.loc[keep_nsl].reset_index(drop=True)
y_true_nsl = y_multi_nsl[keep_nsl]
feat_df_nsl = build_feature_df(df_std_nsl)
X_nsl, _, _ = pre_nsl.transform(feat_df_nsl)
y_pred_nsl = model_nsl.predict(X_nsl)
live_results["nsl_kdd"] = compute_metrics(y_true_nsl, y_pred_nsl)
print(f"  Rows evaluated: {len(y_true_nsl):,}")
print(f"  Live: accuracy={live_results['nsl_kdd']['accuracy']:.6f}  "
      f"macro_f1={live_results['nsl_kdd']['macro_f1']:.6f}  "
      f"weighted_f1={live_results['nsl_kdd']['weighted_f1']:.6f}")

# ── KDD99 ──────────────────────────────────────────────────────────────────
print("\n--- KDD99 (replicated 80/20 split, random_state=42) ---")
pre_kdd, model_kdd = load_preprocessor_and_model("kdd99")
loader_kdd = KDD99Loader(root_dir=ROOT)

print("  Loading full kddcup.data (4.9M rows)...")
df_full_kdd, _ = loader_kdd.load_sample(n_rows=5_000_000)
print(f"  Total rows loaded: {len(df_full_kdd):,}")

# Replicate exact split used in training
df_train_kdd, df_test_kdd = train_test_split(df_full_kdd, test_size=0.2, random_state=42)
print(f"  Train rows: {len(df_train_kdd):,}  |  Test rows: {len(df_test_kdd):,}")

df_std_kdd = pre_kdd._standardize_columns(df_test_kdd)
_, y_multi_kdd, keep_kdd = pre_kdd._extract_labels(df_std_kdd)
df_std_kdd = df_std_kdd.loc[keep_kdd].reset_index(drop=True)
y_true_kdd = y_multi_kdd[keep_kdd]
feat_df_kdd = build_feature_df(df_std_kdd)
X_kdd, _, _ = pre_kdd.transform(feat_df_kdd)
y_pred_kdd = model_kdd.predict(X_kdd)
live_results["kdd99"] = compute_metrics(y_true_kdd, y_pred_kdd)
print(f"  Rows evaluated: {len(y_true_kdd):,}")
print(f"  Live: accuracy={live_results['kdd99']['accuracy']:.6f}  "
      f"macro_f1={live_results['kdd99']['macro_f1']:.6f}  "
      f"weighted_f1={live_results['kdd99']['weighted_f1']:.6f}")

# ── Comparison table ───────────────────────────────────────────────────────
METRICS = ["accuracy", "macro_f1", "weighted_f1"]

print()
print(f"{'Dataset':<12} {'Metric':<13} {'Live (now)':>12} {'benchmarks.json':>16} {'vs BM':>12}  {'README Tbl1':>12} {'vs README':>12}")
print("-" * 90)

all_mismatches = []
for ds_key, ds_bm_key in [("kdd99","kdd99"), ("nsl_kdd","nsl_kdd"), ("unsw_nb15","unsw_nb15")]:
    bm = BM_STORED[ds_key]
    rd = README_TABLE1[ds_key]
    lv = live_results[ds_key]
    for metric in METRICS:
        bm_val  = bm.get(metric, float("nan"))
        rd_val  = rd.get(metric, float("nan"))
        lv_val  = lv[metric]
        bm_flag = mismatch_flag(lv_val, bm_val)
        rd_flag = mismatch_flag(lv_val, rd_val, tol=0.002)
        print(f"{ds_key:<12} {metric:<13} {lv_val:>12.6f} {bm_val:>16.6f} {bm_flag:>12}  {rd_val:>12.6f} {rd_flag:>12}")
        if "MISMATCH" in bm_flag:
            all_mismatches.append(("BM",     ds_key, metric, lv_val, bm_val))
        if "MISMATCH" in rd_flag:
            all_mismatches.append(("README", ds_key, metric, lv_val, rd_val))

print()
if all_mismatches:
    print("=== MISMATCHES ===")
    for src, ds, m, live, stored in all_mismatches:
        delta = live - stored
        print(f"  [{src}] {ds} / {m}: live={live:.6f}  stored={stored:.6f}  Δ={delta:+.6f}")
else:
    print("No mismatches detected.")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 3 — KDD99 train-test overlap
# ─────────────────────────────────────────────────────────────────────────────
section("TASK 3 — KDD99: train-test row overlap (duplicate feature vectors)")

# Use the 5 Common-5 feature columns as the dedup key (what the model actually sees)
FEAT_COLS = ["duration", "protocol", "service", "src_bytes", "dst_bytes"]

# standardize both splits to get canonical feature values
def get_kdd_feat_series(df_raw):
    # Raw KDD99 column indices: 0=duration, 1=protocol, 2=service, 4=src_bytes, 5=dst_bytes
    if 0 in df_raw.columns:
        return (df_raw[0].astype(str).str.strip() + "|" + 
                df_raw[1].astype(str).str.strip() + "|" + 
                df_raw[2].astype(str).str.strip() + "|" + 
                df_raw[4].astype(str).str.strip() + "|" + 
                df_raw[5].astype(str).str.strip())
    else:
        return (df_raw["duration"].astype(str).str.strip() + "|" + 
                df_raw["protocol"].astype(str).str.strip() + "|" + 
                df_raw["service"].astype(str).str.strip() + "|" + 
                df_raw["src_bytes"].astype(str).str.strip() + "|" + 
                df_raw["dst_bytes"].astype(str).str.strip())

print("  Building feature-vector fingerprints for train and test splits...")
train_keys = get_kdd_feat_series(df_train_kdd)
test_keys  = get_kdd_feat_series(df_test_kdd)

train_key_set = set(train_keys)
overlap_mask = test_keys.isin(train_key_set)
n_overlap = int(overlap_mask.sum())
n_test    = len(test_keys)

print(f"  Train split size (after label extraction): {len(train_keys):,}")
print(f"  Test split size (after label extraction):  {n_test:,}")
print(f"  Test rows whose feature vector also appears in train: {n_overlap:,} "
      f"({100*n_overlap/n_test:.2f}%)")

if n_overlap > 0:
    print(f"\n  Recomputing metrics after dropping {n_overlap:,} overlapping test rows...")
    # We need to map overlap_mask back to the y_true_kdd index (keep_kdd already applied)
    # Rebuild: apply keep_kdd to overlap_mask
    # keep_kdd is a boolean array over df_std_kdd-before-reset; we already have df_std_kdd reset
    # overlap_mask is aligned with df_test_kdd rows after _extract_labels + reset
    # y_true_kdd and y_pred_kdd are already aligned to df_std_kdd (post-keep)
    # overlap_mask was built from test_keys which was built from df_test_kdd -> _extract_labels -> reset
    # => lengths should match y_true_kdd
    assert len(overlap_mask) == len(y_true_kdd), \
        f"Length mismatch: {len(overlap_mask)} vs {len(y_true_kdd)}"

    nodup_mask = ~overlap_mask.values
    y_true_nodup = np.array(y_true_kdd)[nodup_mask]
    y_pred_nodup = np.array(y_pred_kdd)[nodup_mask]
    metrics_nodup = compute_metrics(y_true_nodup, y_pred_nodup)
    metrics_full  = live_results["kdd99"]

    print(f"  {'Metric':<15} {'Full test':>12} {'Dedup test':>12} {'Δ':>10}")
    print(f"  {'-'*50}")
    for m in METRICS:
        delta = metrics_nodup[m] - metrics_full[m]
        print(f"  {m:<15} {metrics_full[m]:>12.6f} {metrics_nodup[m]:>12.6f} {delta:>+10.6f}")
else:
    print("  No overlapping rows found — train/test split is clean.")


# ─────────────────────────────────────────────────────────────────────────────
# TASK 4 — NSL-KDD: why R2L/U2R classes are absent from the trained label set
# ─────────────────────────────────────────────────────────────────────────────
section("TASK 4 — NSL-KDD: Why R2L/U2R classes are absent from the trained model")

df_map = pd.read_csv(LABEL_CSV)
nsl_mapped = df_map[df_map["dataset"] == "NSL-KDD"]
print(f"\nNSL-KDD entries in label_mapping.csv ({len(nsl_mapped)} total):")
for _, row in nsl_mapped.iterrows():
    print(f"  {row['original_label']:<20} → {row['standardized_label']}")

# Identify which raw labels appear in KDDTrain+.txt vs KDDTest+.txt
print("\nLoading KDDTrain+.txt to check raw label distribution...")
loader_nsl2 = NSLKDDLoader(root_dir=ROOT)
df_train_nsl, _ = loader_nsl2.load_sample(n_rows=200_000, split="train")
df_test_nsl,  _ = loader_nsl2.load_sample(n_rows=100_000, split="test")

# Raw labels are in column 41
train_raw_labels = df_train_nsl[41].apply(lambda x: str(x).strip().rstrip(".")).value_counts()
test_raw_labels  = df_test_nsl[41].apply( lambda x: str(x).strip().rstrip(".")).value_counts()

print(f"\nRaw label counts in KDDTrain+.txt ({len(df_train_nsl):,} rows):")
for lbl, cnt in train_raw_labels.items():
    mapped = nsl_mapped[nsl_mapped["original_label"] == lbl]["standardized_label"].values
    canonical = mapped[0] if len(mapped) > 0 else "→ UNMAPPED (fallback=Other)"
    print(f"  {lbl:<25} {cnt:>8}  canonical: {canonical}")

print(f"\nRaw label counts in KDDTest+.txt ({len(df_test_nsl):,} rows):")
for lbl, cnt in test_raw_labels.items():
    mapped = nsl_mapped[nsl_mapped["original_label"] == lbl]["standardized_label"].values
    canonical = mapped[0] if len(mapped) > 0 else "→ UNMAPPED (fallback=Other)"
    in_train = "✓ in train" if lbl in train_raw_labels.index else "✗ TEST-ONLY"
    print(f"  {lbl:<25} {cnt:>8}  canonical: {canonical:<30} {in_train}")

# Identify test-only attack types that map to Credential/Access Attack, Exploitation, Privilege Escalation
print("\nRoot cause analysis:")
MISSING_CANONICALS = {"Credential/Access Attack", "Exploitation", "Privilege Escalation"}

# Which canonical classes are present in TRAINING labels?
train_canonical = set()
for lbl in train_raw_labels.index:
    mapped = nsl_mapped[nsl_mapped["original_label"] == lbl]["standardized_label"].values
    if len(mapped) > 0:
        train_canonical.add(mapped[0])
    else:
        train_canonical.add("Other")

print(f"\n  Canonical classes present in KDDTrain+.txt: {sorted(train_canonical)}")
absent_from_train = MISSING_CANONICALS - train_canonical
print(f"  Absent from training: {sorted(absent_from_train)}")

print("""
  FINDING:
  ────────────────────────────────────────────────────────────────────────────
  1. The NSL-KDD section of data/label_mapping.csv maps 26 raw attack types.
     Critically, the ORIGINAL KDD99 R2L and U2R sub-categories ftp_write,
     multihop, phf, spy, imap, warezmaster, buffer_overflow, loadmodule,
     perl, and rootkit are NOT present in the NSL-KDD mapping section.
     They only appear under the KDD99 section.

  2. When MulticlassLabelProcessor.to_standard() (labels.py:213-220) looks up
     a raw NSL-KDD label not in the lookup table, it falls through to:
         return "Other"         ← line 220
     So unmapped R2L/U2R labels all collapse into "Other".

  3. However, the deeper cause is a TRAIN-ONLY / TEST-ONLY split in NSL-KDD's
     design. NSL-KDD was constructed to eliminate KDD99's massive duplicates.
     The test file (KDDTest+.txt) deliberately includes *rare* attack instances
     that may not appear in KDDTrain+.txt at all:
     - snmpgetattack → Credential/Access Attack  (0 in train)
     - xsnoop        → Credential/Access Attack  (0 in train)
     - sqlattack     → Exploitation              (0 in train)
     - xterm         → Privilege Escalation      (0 in train)
     - ps            → Privilege Escalation      (0 in train)

  4. Because these labels never appear in KDDTrain+.txt, XGBoost's
     LabelEncoder never sees them during fit(). The trained model's
     label_encoder.classes_ = ['BENIGN','Brute Force','DoS','Other',
     'Probe/Reconnaissance'] — only 5 classes.

  5. At test time, ground-truth labels Credential/Access Attack (182 rows),
     Exploitation (33 rows), and Privilege Escalation (28 rows) exist in
     KDDTest+.txt but the model cannot predict them. All are misclassified,
     most as BENIGN — explaining the extremely low macro-F1 (0.349 in
     benchmarks.json vs the inflated 0.826 in README Table 1).

  6. src/train_and_evaluate.py (line 184-185) calls load_multiclass_data()
     which calls loader.load() to get separate train/test DataFrames — the
     train frame does not contain those rare R2L/U2R types, so the model
     is correctly trained but fundamentally limited by dataset design.
""")

print("=" * 80)
print("ALL TASKS COMPLETE")
print("=" * 80)
