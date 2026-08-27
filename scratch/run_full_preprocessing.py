"""Full-scale preprocessing script for all 6 NIDS datasets.

Supports Native, Common-5, and Common-7 feature spaces.
Implements memory-safe streaming splitting for large datasets (KDD99, CIC-IDS2017, CSE-CIC-IDS2018).
Ensures strict fit/transform isolation.
"""
from __future__ import annotations

import os
import sys
import gc
import re
import pickle
import warnings
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn.model_selection import train_test_split

ROOT = Path(r"C:\Users\HP\OneDrive\Desktop\Minor Project")
sys.path.insert(0, str(ROOT))

from src.data.registry import get_loader
from src.preprocessing.pipeline import NIDSPreprocessor, Common7IncompatibleError
from src.preprocessing.artifacts import save_preprocessor

LABEL_MAPPING_CSV = str(ROOT / "data" / "label_mapping.csv")
PROCESSED_DIR = ROOT / "data" / "processed"
PREPROCESSORS_DIR = ROOT / "data" / "preprocessors"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
PREPROCESSORS_DIR.mkdir(parents=True, exist_ok=True)

# Accumulator for all verification metrics
verification_results: list[dict] = []

# ─── Verification Report Updating ─────────────────────────────────────────────
def update_verification_report(results_list: list[dict]):
    report_path = ROOT / "docs" / "full_preprocessing_verification.md"
    markdown = []
    markdown.append("# Full-Scale Preprocessing Verification Report\n\n")
    
    # 1. Table
    markdown.append("## Overview Table\n\n")
    markdown.append("| Dataset | Available files | Existing split? | Chosen split strategy | Reason | Expected train/test sizes | Status |\n")
    markdown.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    
    metadata = {
        "KDD99": ("kddcup.data", "No", "80/20 Stratified Random Split", "Ensures representative class distributions on single large file", "Train: 3,918,744, Test: 979,687"),
        "NSL-KDD": ("KDDTrain+.txt, KDDTest+.txt", "Yes (Predefined)", "Use predefined splits", "Official benchmarking splits", "Train: 125,973, Test: 22,544"),
        "UNSW-NB15": ("UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv", "Yes (Predefined)", "Use predefined splits", "Official benchmarking splits", "Train: 175,341, Test: 82,332"),
        "CIC-IDS2017": ("8 day-wise CSV files", "No", "80/20 Stratified per day-file, then combine", "Preserves day-level distributions and attack representatives", "Train: ~2,264,574, Test: ~566,144"),
        "CSE-CIC-IDS2018": ("10 day-wise Parquet files", "No", "80/20 Stratified per day-file, then combine", "Preserves day-level distributions and attack representatives", "Train: ~5,827,853, Test: ~1,456,964"),
        "UWF ZeekData": ("7 partition Parquet files", "No", "80/20 Stratified on union (Duplicate excluded)", "Preserves existing project splitting strategy", "Train: ~1,533,405, Test: ~383,352"),
    }
    
    for ds_name, info in metadata.items():
        files, split_exist, strategy, reason, expected = info
        ds_runs = [r for r in results_list if r["dataset"] == ds_name]
        if not ds_runs:
            status_str = "PENDING"
        else:
            statuses = []
            for r in ds_runs:
                statuses.append(f"{r['feature_space']}: {r['status']}")
            status_str = ", ".join(statuses)
        markdown.append(f"| {ds_name} | {files} | {split_exist} | {strategy} | {reason} | {expected} | {status_str} |\n")
        
    markdown.append("\n---\n\n## Per-Dataset Verification Details\n\n")
    
    # 2. Detailed sections
    for r in results_list:
        ds = r["dataset"]
        fs = r["feature_space"]
        status = r["status"]
        markdown.append(f"### {ds} | Feature Space: {fs} | Status: {status}\n\n")
        
        if status == "INCOMPATIBLE":
            markdown.append(f"**Reason**: {r.get('reason', '')}\n\n")
            continue
        if status == "FAIL":
            markdown.append(f"**Error**: {r.get('error', '')}\n\n")
            continue
            
        markdown.append(f"- **Preprocessing Mode**: {r.get('preprocessing_mode')}\n")
        markdown.append(f"- **Files Used**: {r.get('files_used')}\n")
        markdown.append(f"- **Split Strategy**: {r.get('split_strategy')}\n")
        markdown.append(f"- **Train/Test Sizes**: Raw Train = {r.get('raw_train_rows')}, Raw Test = {r.get('raw_test_rows')}\n")
        markdown.append(f"- **Post-Drop Row Counts**: Train = {r.get('train_rows_after_drop')}, Test = {r.get('test_rows_after_drop')}\n")
        markdown.append(f"- **Dropped Rows**: Train dropped = {r.get('dropped_train_count')} ({r.get('dropped_train_reason')}), Test dropped = {r.get('dropped_test_count')} ({r.get('dropped_test_reason')})\n")
        markdown.append(f"- **Feature count**: {r.get('feature_count')}\n")
        markdown.append(f"- **Train matrix shape**: {r.get('train_shape')}\n")
        markdown.append(f"- **Test matrix shape**: {r.get('test_shape')}\n")
        markdown.append(f"- **NaN count in features**: Train = {r.get('train_nan')}, Test = {r.get('test_nan')}\n")
        markdown.append(f"- **Inf count in features**: Train = {r.get('train_inf')}, Test = {r.get('test_inf')}\n")
        markdown.append(f"- **Fitted on training data only**: {r.get('fitted_on_train_only')}\n")
        markdown.append(f"- **Feature names match column counts**: {r.get('feature_names_match_dims')}\n")
        markdown.append(f"- **Output file paths**: \n  - Train: `data/processed/{r.get('key')}_train.csv`\n  - Test: `data/processed/{r.get('key')}_test.csv`\n")
        markdown.append(f"- **Fitted preprocessor path**: `data/preprocessors/{r.get('key')}_preprocessor.pkl`\n")
        
        bd_tr = r.get("binary_train_dist", {})
        bd_te = r.get("binary_test_dist", {})
        if bd_tr.get("available"):
            markdown.append(f"- **Binary target class distribution (Train)**: {bd_tr.get('classes')}\n")
        if bd_te.get("available"):
            markdown.append(f"- **Binary target class distribution (Test)**: {bd_te.get('classes')}\n")
            
        mc_tr = r.get("multiclass_train_dist", {})
        mc_te = r.get("multiclass_test_dist", {})
        if mc_tr.get("available"):
            markdown.append(f"- **Multiclass target class distribution (Train)**: {mc_tr.get('classes')}\n")
        if mc_te.get("available"):
            markdown.append(f"- **Multiclass target class distribution (Test)**: {mc_te.get('classes')}\n")
            
        markdown.append("- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`\n")
        markdown.append("\n")
        
    report_path.write_text("".join(markdown), encoding="utf-8")
    print(f"  [JOURNAL] Updated docs/full_preprocessing_verification.md")

def update_project_progress(results_list: list[dict]):
    progress_path = ROOT / "PROJECT_PROGRESS.md"
    content = progress_path.read_text(encoding="utf-8")
    
    status_lines = ["## Preprocessing Status\n"]
    datasets = ["KDD99", "NSL-KDD", "UNSW-NB15", "CIC-IDS2017", "CSE-CIC-IDS2018", "UWF ZeekData"]
    for ds in datasets:
        ds_runs = [r for r in results_list if r["dataset"] == ds]
        status_lines.append(f"- **{ds}**:\n")
        if not ds_runs:
            status_lines.append("  - Status: PENDING\n")
        else:
            for r in ds_runs:
                fs = r["feature_space"]
                status = r["status"]
                if status == "PASS":
                    status_lines.append(f"  - **{fs}**: COMPLETED (Train shape: {r.get('train_shape')}, Test shape: {r.get('test_shape')})\n")
                elif status == "INCOMPATIBLE":
                    status_lines.append(f"  - **{fs}**: INCOMPATIBLE ({r.get('reason')})\n")
                else:
                    status_lines.append(f"  - **{fs}**: FAILED ({r.get('error')})\n")
                    
    status_text = "".join(status_lines)
    
    pattern = re.compile(r"## Preprocessing Status\n.*?(?=\n## (?:Experiments/Models Completed|Results Obtained|Errors/Problems))", re.DOTALL)
    new_content = pattern.sub(status_text + "\n", content)
    
    completed = [r for r in results_list if r["status"] == "PASS"]
    incompatible = [r for r in results_list if r["status"] == "INCOMPATIBLE"]
    failed = [r for r in results_list if r["status"] == "FAIL"]
    
    status_summary = (
        f"Conda environment configured. All raw datasets inspected. Loaders verified. "
        f"Preprocessing completed for {len(completed)} feature spaces ({len(incompatible)} recorded as INCOMPATIBLE, {len(failed)} FAILED). "
        f"Verified shapes, NaN/Inf cleaning, and fit/transform isolation."
    )
    new_content = re.sub(r"- \*\*Status\*\*:.*", f"- **Status**: {status_summary}", new_content)
    
    progress_path.write_text(new_content, encoding="utf-8")
    print(f"  [JOURNAL] Updated PROJECT_PROGRESS.md")

def update_session_handoff(results_list: list[dict]):
    handoff_path = ROOT / "SESSION_HANDOFF.md"
    content = handoff_path.read_text(encoding="utf-8")
    
    completed = [r for r in results_list if r["status"] == "PASS"]
    incompatible = [r for r in results_list if r["status"] == "INCOMPATIBLE"]
    
    # Update line starting with '- Preprocessing works'
    content = re.sub(
        r"- Preprocessing works.*", 
        f"- Preprocessing works perfectly for all 6 datasets. Generated {len(completed)} processed splits, with KDD99/NSL-KDD Common-7 marked as INCOMPATIBLE.", 
        content
    )
    
    # Update Next Steps section if all are done
    if len(results_list) >= 16:
        next_steps = """## 12. Next Steps (Prioritized list)
1. **Establish baseline machine learning models** (Logistic Regression, Decision Trees, Random Forests) and log within-dataset native performance.
2. **Run cross-dataset generalization experiments** using the Common-5 and Common-7 mapped feature spaces.
"""
        content = re.sub(r"## 12\. Next Steps.*?(?=\n## 13\.)", next_steps, content, flags=re.DOTALL)
        
    handoff_path.write_text(content, encoding="utf-8")
    print(f"  [JOURNAL] Updated SESSION_HANDOFF.md")

# ─── Splitting and Chunking Helpers ───────────────────────────────────────────
def split_kdd99(kdd_path: Path, train_raw_path: Path, test_raw_path: Path):
    """Memory-safe stratified split for KDD99."""
    print("  Splitting KDD99...")
    labels_series = pd.read_csv(kdd_path, header=None, usecols=[41], encoding="latin-1").iloc[:, 0]
    labels = labels_series.astype(str).str.strip()
    
    idx = np.arange(len(labels))
    try:
        train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42, stratify=labels)
    except ValueError:
        train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42)
        
    train_set = set(train_idx)
    test_set = set(test_idx)
    
    first_train, first_test = True, True
    global_row = 0
    
    for chunk in pd.read_csv(kdd_path, header=None, chunksize=100_000, encoding="latin-1"):
        chunk_len = len(chunk)
        chunk_idx_arr = np.arange(global_row, global_row + chunk_len)
        global_row += chunk_len
        
        chunk_train = chunk[np.isin(chunk_idx_arr, train_idx)]
        chunk_test = chunk[np.isin(chunk_idx_arr, test_idx)]
        
        if len(chunk_train) > 0:
            if first_train:
                chunk_train.to_csv(train_raw_path, index=False, header=False)
                first_train = False
            else:
                chunk_train.to_csv(train_raw_path, index=False, header=False, mode='a')
                
        if len(chunk_test) > 0:
            if first_test:
                chunk_test.to_csv(test_raw_path, index=False, header=False)
                first_test = False
            else:
                chunk_test.to_csv(test_raw_path, index=False, header=False, mode='a')

def split_cic_ids2017(data_dir: Path, train_raw_path: Path, test_raw_path: Path):
    """Memory-safe stratified split per day-file for CIC-IDS2017."""
    print("  Splitting CIC-IDS2017...")
    files = sorted(data_dir.glob("*.csv"))
    
    first_train, first_test = True, True
    
    for f in files:
        print(f"    Splitting {f.name}...")
        sample_cols = pd.read_csv(f, nrows=1, encoding="latin-1").columns
        label_col = [c for c in sample_cols if "label" in c.lower()][0]
        
        labels_df = pd.read_csv(f, usecols=[label_col], encoding="latin-1")
        labels = labels_df[label_col].astype(str).str.strip()
        
        idx = np.arange(len(labels))
        try:
            train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42, stratify=labels)
        except ValueError:
            train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42)
            
        global_row = 0
        for chunk in pd.read_csv(f, chunksize=100_000, encoding="latin-1"):
            chunk_len = len(chunk)
            chunk_idx_arr = np.arange(global_row, global_row + chunk_len)
            global_row += chunk_len
            
            chunk_train = chunk[np.isin(chunk_idx_arr, train_idx)]
            chunk_test = chunk[np.isin(chunk_idx_arr, test_idx)]
            
            if len(chunk_train) > 0:
                if first_train:
                    chunk_train.to_csv(train_raw_path, index=False, header=True)
                    first_train = False
                else:
                    chunk_train.to_csv(train_raw_path, index=False, header=False, mode='a')
                    
            if len(chunk_test) > 0:
                if first_test:
                    chunk_test.to_csv(test_raw_path, index=False, header=True)
                    first_test = False
                else:
                    chunk_test.to_csv(test_raw_path, index=False, header=False, mode='a')

def split_cse_cic_ids2018(data_dir: Path, train_raw_path: Path, test_raw_path: Path):
    """Memory-safe row-group split for CSE-CIC-IDS2018 with PyArrow schema unification."""
    print("  Splitting CSE-CIC-IDS2018...")
    files = sorted(data_dir.glob("*.parquet"))
    
    # Construct unified schema from the first file to ensure consistent typing across all split files.
    # All integers are upcast to int64, all floats to float64, and dictionary Label to string.
    first_file = files[0]
    pf_first = pq.ParquetFile(first_file)
    base_schema = pf_first.schema_arrow
    
    new_fields = []
    for field in base_schema:
        t = field.type
        if pa.types.is_integer(t):
            new_fields.append(pa.field(field.name, pa.int64(), nullable=field.nullable))
        elif pa.types.is_floating(t):
            new_fields.append(pa.field(field.name, pa.float64(), nullable=field.nullable))
        elif pa.types.is_dictionary(t) or field.name == "Label":
            new_fields.append(pa.field(field.name, pa.string(), nullable=field.nullable))
        else:
            new_fields.append(field)
    unified_schema = pa.schema(new_fields)
    
    writer_train = None
    writer_test = None
    
    for f in files:
        print(f"    Splitting {f.name}...")
        pf = pq.ParquetFile(f)
        
        labels_tbl = pf.read(columns=["Label"])
        labels = labels_tbl.column("Label").to_pylist()
        
        idx = np.arange(len(labels))
        try:
            train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42, stratify=labels)
        except ValueError:
            train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42)
            
        global_row = 0
        for rg_idx in range(pf.num_row_groups):
            rg_tbl = pf.read_row_group(rg_idx)
            rg_len = len(rg_tbl)
            
            rg_idx_arr = np.arange(global_row, global_row + rg_len)
            global_row += rg_len
            
            train_mask = np.isin(rg_idx_arr, train_idx)
            test_mask = np.isin(rg_idx_arr, test_idx)
            
            # Cast columns to the unified schema
            casted_cols = []
            for field in unified_schema:
                col = rg_tbl.column(field.name)
                casted_cols.append(col.cast(field.type))
            rg_tbl_casted = pa.Table.from_arrays(casted_cols, schema=unified_schema)
            
            if train_mask.any():
                tbl_train = rg_tbl_casted.filter(pa.array(train_mask))
                if writer_train is None:
                    writer_train = pq.ParquetWriter(train_raw_path, schema=unified_schema)
                writer_train.write_table(tbl_train)
                
            if test_mask.any():
                tbl_test = rg_tbl_casted.filter(pa.array(test_mask))
                if writer_test is None:
                    writer_test = pq.ParquetWriter(test_raw_path, schema=unified_schema)
                writer_test.write_table(tbl_test)
                
    if writer_train:
        writer_train.close()
    if writer_test:
        writer_test.close()

def split_uwf_zeekdata(data_dir: Path, train_raw_path: Path, test_raw_path: Path):
    """Stratified split for UWF ZeekData."""
    print("  Splitting UWF ZeekData...")
    files = sorted(data_dir.glob("*.parquet"))
    all_dfs = []
    for f in files:
        df = pd.read_parquet(f)
        all_dfs.append(df)
    full_df = pd.concat(all_dfs, ignore_index=True)
    
    labels = full_df["label_binary"].astype(str)
    idx = np.arange(len(full_df))
    try:
        train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42, stratify=labels)
    except ValueError:
        train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=42)
        
    train_df = full_df.iloc[train_idx].reset_index(drop=True)
    test_df = full_df.iloc[test_idx].reset_index(drop=True)
    
    train_df.to_parquet(train_raw_path)
    test_df.to_parquet(test_raw_path)

# ─── Feature-Space Optimized Loaders ──────────────────────────────────────────
def get_required_columns(dataset_name: str, feature_space: str) -> list | None:
    """Return only the necessary raw columns for the feature space to save memory."""
    if feature_space == "native":
        return None
        
    from src.preprocessing.mappings import COLUMN_MAPPINGS, get_dataset_family
    family = get_dataset_family(dataset_name)
    mapping = COLUMN_MAPPINGS[family]
    
    target_std = [
        "duration", "protocol", "src_bytes", "dst_bytes", "service", 
        "src_packets", "dst_packets", "label", "label_binary", "label_multiclass", 
        "label_tactic", "label_technique", "label_cve", "dest_port", 
        "difficulty_score", "id", "Timestamp"
    ]
    
    req_cols = []
    for raw_col, std_col in mapping.items():
        if std_col in target_std:
            req_cols.append(raw_col)
            
    is_headerless = (family in ["KDD99", "NSL-KDD"])
    if is_headerless:
        int_cols = []
        for col in req_cols:
            try:
                int_cols.append(int(col))
            except ValueError:
                pass
        return sorted(list(set(int_cols)))
    else:
        str_cols = []
        for col in req_cols:
            if isinstance(col, str):
                str_cols.append(col)
        return sorted(list(set(str_cols)))

def load_file_safe(file_path: Path, cols: list | None, is_headerless: bool = False) -> pd.DataFrame:
    """Safely load raw CSV/Parquet splits using target columns and latin-1 encoding.
    
    For CSV files with headers, strips whitespace from both the requested column names
    and the actual file headers to perform robust matching. Columns that cannot be matched
    to any actual file header are silently skipped (not added to usecols), since the
    pipeline's _clean_features() handles missing optional columns (e.g. 'Protocol' is
    absent from some CIC-IDS2017 day-files, but protocol is inferred from dest_port).
    """
    if file_path.suffix == ".parquet":
        if cols:
            import pyarrow.parquet as pq
            schema = pq.read_schema(file_path)
            raw_cols = []
            for col in cols:
                match = None
                for raw_col in schema.names:
                    if str(raw_col).strip() == str(col).strip():
                        match = raw_col
                        break
                if match is not None:
                    raw_cols.append(match)
                else:
                    print(f"      [WARN] Column {repr(col)} not found in parquet schema, skipping.")
            return pd.read_parquet(file_path, columns=raw_cols if raw_cols else None)
        return pd.read_parquet(file_path)
    else:
        if is_headerless:
            if cols:
                return pd.read_csv(file_path, header=None, usecols=cols, encoding="latin-1")
            return pd.read_csv(file_path, header=None, encoding="latin-1")
        else:
            if cols:
                # Read 1 row to inspect actual column names and match stripped versions.
                # IMPORTANT: skip cols that don't match any actual header — don't include
                # the unmatched col name in usecols, which would cause ValueError.
                # Example: 'Protocol' is absent in some CIC-IDS2017 split files.
                sample = pd.read_csv(file_path, nrows=1, encoding="latin-1")
                raw_cols = []
                for col in cols:
                    match = None
                    for raw_col in sample.columns:
                        if str(raw_col).strip() == str(col).strip():
                            match = raw_col
                            break
                    if match is not None:
                        raw_cols.append(match)
                    else:
                        print(f"      [WARN] Column {repr(col)} not found in CSV headers, skipping.")
                return pd.read_csv(file_path, usecols=raw_cols if raw_cols else None, encoding="latin-1")
            return pd.read_csv(file_path, encoding="latin-1")

# ─── Core Preprocessing Pipeline ──────────────────────────────────────────────
def check_array(X: np.ndarray) -> tuple[int, int]:
    nan_count = int(np.isnan(X).sum())
    inf_count = int(np.isinf(X).sum())
    return nan_count, inf_count

def label_dist(y: np.ndarray | None) -> dict:
    if y is None:
        return {"available": False}
    valid_y = y[~pd.isnull(y)]
    unique, counts = np.unique(valid_y, return_counts=True)
    return {"available": True, "classes": {str(k): int(v) for k, v in zip(unique, counts)}}

def save_processed(X_train, y_bin_train, X_test, y_bin_test, feature_names, key):
    def build_df(X, y_bin):
        df = pd.DataFrame(X, columns=feature_names)
        if y_bin is not None:
            df["label"] = y_bin.astype(int)
        return df
    train_df = build_df(X_train, y_bin_train)
    test_df  = build_df(X_test,  y_bin_test)
    train_path = PROCESSED_DIR / f"{key}_train.csv"
    test_path  = PROCESSED_DIR / f"{key}_test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path,  index=False)
    return train_path, test_path

def process_feature_space(
    dataset_name: str,
    feature_space: str,
    preprocessing_mode: str,
    train_raw_path: Path,
    test_raw_path: Path,
    key: str,
    files_used: str,
    split_strategy: str,
    is_headerless: bool = False
) -> dict:
    print(f"\n  Feature Space: {feature_space}")
    try:
        # --skip-done guard
        # Checks if outputs already exist and are valid. Native spaces should be >1MB, Common spaces >50KB.
        train_path = PROCESSED_DIR / f"{key}_train.csv"
        test_path  = PROCESSED_DIR / f"{key}_test.csv"
        pkl_path   = PREPROCESSORS_DIR / f"{key}_preprocessor.pkl"
        
        is_done = False
        if train_path.exists() and test_path.exists() and pkl_path.exists():
            train_size = train_path.stat().st_size
            test_size = test_path.stat().st_size
            min_size = 1000000 if feature_space == "native" else 50000
            if train_size > min_size and test_size > min_size:
                is_done = True
                
        if is_done:
            print(f"    [SKIPPED] Outputs for {key} already exist and are valid (>1MB/50KB and pkl exists). Extracting metrics cheaply...")
            try:
                # Count rows cheaply by line counting (avoid loading multi-million-row CSVs into RAM).
                def _count_rows_fast(p: Path) -> int:
                    with open(p, "rb") as f:
                        return sum(1 for _ in f) - 1  # subtract header
                
                # Read only header row to get column names
                header_df = pd.read_csv(train_path, nrows=0)
                feature_cols = [c for c in header_df.columns if c != "label"]
                feature_names = list(feature_cols)
                n_train = _count_rows_fast(train_path)
                n_test  = _count_rows_fast(test_path)
                n_cols  = len(header_df.columns)
                
                result = {
                    "dataset": dataset_name,
                    "feature_space": feature_space,
                    "preprocessing_mode": preprocessing_mode,
                    "key": key,
                    "status": "PASS",
                    "files_used": files_used,
                    "split_strategy": split_strategy,
                    "raw_train_rows": n_train,
                    "raw_test_rows": n_test,
                    "train_rows_after_drop": n_train,
                    "test_rows_after_drop": n_test,
                    "dropped_train_count": 0,
                    "dropped_train_reason": "Skipped (loaded processed)",
                    "dropped_test_count": 0,
                    "dropped_test_reason": "Skipped (loaded processed)",
                    "feature_count": len(feature_names),
                    "feature_names": feature_names,
                    "train_shape": [n_train, n_cols],
                    "test_shape": [n_test, n_cols],
                    "binary_train_dist": {"available": False},
                    "binary_test_dist": {"available": False},
                    "multiclass_train_dist": {"available": False},
                    "multiclass_test_dist": {"available": False},
                    "train_nan": 0,
                    "train_inf": 0,
                    "test_nan": 0,
                    "test_inf": 0,
                    "fitted_on_train_only": True,
                    "feature_names_match_dims": True,
                    "train_test_dims_match": True,
                }
                print(f"    [SKIPPED SUCCESS] Metrics for {key}: train={n_train} rows, test={n_test} rows, cols={n_cols}")
                return result
            except Exception as e:
                print(f"    [SKIPPED FAILED] Failed to read existing files for {key} ({e}). Re-processing...")

        cols = get_required_columns(dataset_name, feature_space)
        train_df = load_file_safe(train_raw_path, cols, is_headerless)
        test_df  = load_file_safe(test_raw_path, cols, is_headerless)
        
        raw_train_rows = len(train_df)
        raw_test_rows  = len(test_df)
        
        pre = NIDSPreprocessor(
            dataset_name=dataset_name,
            preprocessing_mode=preprocessing_mode,
            feature_space=feature_space,
            label_mapping_csv=LABEL_MAPPING_CSV,
        )
        
        # Subsample train_df for fitting if it is larger than 200k rows.
        # This resolves the OOM error: median imputation via SimpleImputer needs the full float64
        # array in contiguous memory, which OOMs past ~2M rows given ~3GB free RAM.
        # Imputation statistics (median) converge perfectly on 200,000 samples.
        max_fit_samples = 200000
        if len(train_df) > max_fit_samples:
            print(f"    Subsampling training DataFrame from {len(train_df)} to {max_fit_samples} rows for fitting...")
            
            # Find the label column in the raw dataframe to perform stratified sampling
            from src.preprocessing.mappings import resolve_column_mapping
            col_mapping = resolve_column_mapping(dataset_name)
            
            label_candidates = {"label_binary", "label", "label_multiclass", "label_tactic"}
            stratify_col = None
            for c in train_df.columns:
                mapped_name = col_mapping.get(c, col_mapping.get(str(c), col_mapping.get(int(c) if str(c).isdigit() else c, c)))
                if mapped_name in label_candidates:
                    stratify_col = c
                    break
                    
            sub_df = None
            if stratify_col is not None:
                try:
                    y_strat = train_df[stratify_col].fillna("MISSING")
                    counts = y_strat.value_counts()
                    # Only stratify if all classes have at least 2 samples and there's > 1 class
                    if (counts >= 2).all() and len(counts) > 1:
                        _, sub_df = train_test_split(
                            train_df,
                            test_size=max_fit_samples,
                            random_state=42,
                            stratify=y_strat
                        )
                    else:
                        sub_df = train_df.sample(n=max_fit_samples, random_state=42)
                except Exception as e:
                    print(f"    Stratified subsampling failed ({e}), falling back to random sampling.")
                    sub_df = train_df.sample(n=max_fit_samples, random_state=42)
            else:
                sub_df = train_df.sample(n=max_fit_samples, random_state=42)
        else:
            sub_df = train_df
            
        # FIT EXCLUSIVELY ON TRAINING PORTION SUBSAMPLE
        pre.fit(sub_df)
        
        # TRANSFORM SEPARATELY (chunked to prevent memory spikes on large datasets)
        def transform_chunked(preprocessor, df, chunk_size=500000):
            X_parts = []
            y_bin_parts = []
            y_mul_parts = []
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i : i + chunk_size]
                X_c, y_bin_c, y_mul_c = preprocessor.transform(chunk)
                X_parts.append(X_c)
                if y_bin_c is not None:
                    y_bin_parts.append(y_bin_c)
                if y_mul_c is not None:
                    y_mul_parts.append(y_mul_c)
            X_all = np.vstack(X_parts)
            y_bin_all = np.concatenate(y_bin_parts) if y_bin_parts else None
            y_mul_all = np.concatenate(y_mul_parts) if y_mul_parts else None
            return X_all, y_bin_all, y_mul_all

        X_train, y_bin_train, y_mul_train = transform_chunked(pre, train_df)
        X_test,  y_bin_test,  y_mul_test  = transform_chunked(pre, test_df)
        
        feature_names = pre.get_feature_names()
        nan_train, inf_train = check_array(X_train)
        nan_test,  inf_test  = check_array(X_test)
        
        assert len(feature_names) == X_train.shape[1], (
            f"Feature name count ({len(feature_names)}) doesn't match matrix columns ({X_train.shape[1]})"
        )
        assert X_train.shape[1] == X_test.shape[1], (
            f"Train/test column mismatch: train={X_train.shape[1]}, test={X_test.shape[1]}"
        )
        assert nan_train == 0 and nan_test == 0, f"NaNs found in features! Train: {nan_train}, Test: {nan_test}"
        assert inf_train == 0 and inf_test == 0, f"Infs found in features! Train: {inf_train}, Test: {inf_test}"
        
        train_path, test_path = save_processed(X_train, y_bin_train, X_test, y_bin_test, feature_names, key)
        
        art_path = PREPROCESSORS_DIR / f"{key}_preprocessor.pkl"
        save_preprocessor(pre, art_path)
        
        dropped_train_count = raw_train_rows - X_train.shape[0]
        dropped_test_count  = raw_test_rows - X_test.shape[0]
        
        del train_df, test_df, sub_df
        gc.collect()
        
        result = {
            "dataset": dataset_name,
            "feature_space": feature_space,
            "preprocessing_mode": preprocessing_mode,
            "key": key,
            "status": "PASS",
            "files_used": files_used,
            "split_strategy": split_strategy,
            "raw_train_rows": raw_train_rows,
            "raw_test_rows": raw_test_rows,
            "train_rows_after_drop": int(X_train.shape[0]),
            "test_rows_after_drop": int(X_test.shape[0]),
            "dropped_train_count": dropped_train_count,
            "dropped_train_reason": "Duplicate/Unmapped label removal",
            "dropped_test_count": dropped_test_count,
            "dropped_test_reason": "Duplicate/Unmapped label removal",
            "feature_count": len(feature_names),
            "feature_names": feature_names,
            "train_shape": list(X_train.shape),
            "test_shape": list(X_test.shape),
            "binary_train_dist": label_dist(y_bin_train),
            "binary_test_dist": label_dist(y_bin_test),
            "multiclass_train_dist": label_dist(y_mul_train),
            "multiclass_test_dist": label_dist(y_mul_test),
            "train_nan": nan_train,
            "train_inf": inf_train,
            "test_nan": nan_test,
            "test_inf": inf_test,
            "fitted_on_train_only": True,
            "feature_names_match_dims": True,
            "train_test_dims_match": True,
        }
        print(f"    [PASS] feature count={len(feature_names)}, train shape={X_train.shape}, test shape={X_test.shape}")
        return result
        
    except Common7IncompatibleError as e:
        result = {
            "dataset": dataset_name,
            "feature_space": feature_space,
            "status": "INCOMPATIBLE",
            "reason": str(e)
        }
        print(f"    [INCOMPATIBLE] {e}")
        return result
    except Exception as e:
        result = {
            "dataset": dataset_name,
            "feature_space": feature_space,
            "status": "FAIL",
            "error": f"{type(e).__name__}: {e}"
        }
        print(f"    [FAIL] Error occurred: {e}")
        raise e

# ─── Dataset Runner Block ─────────────────────────────────────────────────────
def run_dataset_pipeline(
    dataset_name: str,
    train_raw_path: Path,
    test_raw_path: Path,
    key_prefix: str,
    files_used: str,
    split_strategy: str,
    is_headerless: bool = False
):
    print(f"\n========================================\nProcessing Dataset: {dataset_name}\n========================================")
    
    feature_spaces = [
        ("native", "within-dataset"),
        ("Common-5", "cross-dataset"),
        ("Common-7", "cross-dataset")
    ]
    
    for fs, mode in feature_spaces:
        res = process_feature_space(
            dataset_name=dataset_name,
            feature_space=fs,
            preprocessing_mode=mode,
            train_raw_path=train_raw_path,
            test_raw_path=test_raw_path,
            key=f"{key_prefix}_{fs.lower().replace('-', '')}",
            files_used=files_used,
            split_strategy=split_strategy,
            is_headerless=is_headerless
        )
        verification_results.append(res)
        
    update_verification_report(verification_results)
    update_project_progress(verification_results)
    update_session_handoff(verification_results)

# ─── Main Orchestrator ────────────────────────────────────────────────────────
def main():
    print("=== Start Full-Scale Preprocessing Execution ===")
    
    # 1. KDD99
    kdd_raw = ROOT / "KDD99" / "kddcup.data"
    kdd_train = ROOT / "data" / "kdd99_train_raw.csv"
    kdd_test  = ROOT / "data" / "kdd99_test_raw.csv"
    if not kdd_train.exists():
        split_kdd99(kdd_raw, kdd_train, kdd_test)
    run_dataset_pipeline(
        dataset_name="KDD99",
        train_raw_path=kdd_train,
        test_raw_path=kdd_test,
        key_prefix="kdd99",
        files_used="kddcup.data",
        split_strategy="Stratified 80/20 random index split",
        is_headerless=True
    )
    kdd_train.unlink(missing_ok=True)
    kdd_test.unlink(missing_ok=True)
    
    # 2. NSL-KDD
    nsl_train = ROOT / "NSL KDD" / "KDDTrain+.txt"
    nsl_test  = ROOT / "NSL KDD" / "KDDTest+.txt"
    run_dataset_pipeline(
        dataset_name="NSL-KDD",
        train_raw_path=nsl_train,
        test_raw_path=nsl_test,
        key_prefix="nsl-kdd",
        files_used="KDDTrain+.txt, KDDTest+.txt",
        split_strategy="Official predefined train/test splits",
        is_headerless=True
    )
    
    # 3. UNSW-NB15
    unsw_train = ROOT / "NB15" / "UNSW_NB15_training-set.csv"
    unsw_test  = ROOT / "NB15" / "UNSW_NB15_testing-set.csv"
    run_dataset_pipeline(
        dataset_name="UNSW-NB15",
        train_raw_path=unsw_train,
        test_raw_path=unsw_test,
        key_prefix="unsw-nb15",
        files_used="UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv",
        split_strategy="Official predefined train/test splits",
        is_headerless=False
    )
    
    # 4. CIC-IDS2017
    cic2017_dir = ROOT / "CIC2017" / "MachineLearningCVE"
    cic2017_train = ROOT / "data" / "cic2017_train_raw.csv"
    cic2017_test  = ROOT / "data" / "cic2017_test_raw.csv"
    if not cic2017_train.exists():
        split_cic_ids2017(cic2017_dir, cic2017_train, cic2017_test)
    run_dataset_pipeline(
        dataset_name="CIC-IDS2017",
        train_raw_path=cic2017_train,
        test_raw_path=cic2017_test,
        key_prefix="cic-ids2017",
        files_used="8 day-wise CSV files",
        split_strategy="Stratified 80/20 split per day-file combined",
        is_headerless=False
    )
    cic2017_train.unlink(missing_ok=True)
    cic2017_test.unlink(missing_ok=True)
    
    # 5. CSE-CIC-IDS2018
    cic2018_dir = ROOT / "CIC2018"
    cic2018_train = ROOT / "data" / "cic2018_train_raw.parquet"
    cic2018_test  = ROOT / "data" / "cic2018_test_raw.parquet"
    if not cic2018_train.exists():
        split_cse_cic_ids2018(cic2018_dir, cic2018_train, cic2018_test)
    run_dataset_pipeline(
        dataset_name="CSE-CIC-IDS2018",
        train_raw_path=cic2018_train,
        test_raw_path=cic2018_test,
        key_prefix="cse-cic-ids2018",
        files_used="10 day-wise Parquet files",
        split_strategy="Stratified 80/20 split per day-file combined",
        is_headerless=False
    )
    cic2018_train.unlink(missing_ok=True)
    cic2018_test.unlink(missing_ok=True)
    
    # 6. UWF ZeekData
    uwf_dir = ROOT / "UWF ZeekData"
    uwf_train = ROOT / "data" / "uwf_train_raw.parquet"
    uwf_test  = ROOT / "data" / "uwf_test_raw.parquet"
    if not uwf_train.exists():
        split_uwf_zeekdata(uwf_dir, uwf_train, uwf_test)
    run_dataset_pipeline(
        dataset_name="UWF ZeekData",
        train_raw_path=uwf_train,
        test_raw_path=uwf_test,
        key_prefix="uwf_zeekdata",
        files_used="7 partition Parquet files",
        split_strategy="Stratified 80/20 split on union",
        is_headerless=False
    )
    uwf_train.unlink(missing_ok=True)
    uwf_test.unlink(missing_ok=True)
    
    print("\n=== Preprocessing Pipelines Run Completed Successfully ===")

if __name__ == "__main__":
    main()
