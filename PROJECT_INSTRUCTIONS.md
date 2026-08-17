# Project Instructions & Constraints

This document lists the constraints and rules that must be strictly followed throughout this research project.

## 1. Raw Data Integrity
- Do NOT delete, overwrite, or modify the raw datasets inside the directory:
  - `CIC2017/`
  - `CIC2018/`
  - `KDD99/`
  - `NB15/`
  - `NSL KDD/`
  - `UWF ZeekData/`
- Processed files must be written separately to a `processed/` directory.

## 2. Environment Constraints
- Use only the Conda environment named `ids_research` (Python 3.11).
- Base Conda environment must not be modified.
- Verify interpreter path before running any script.

## 3. Large Dataset Handling
- Do NOT load multi-GB files completely into RAM.
- Use chunks, lazy loading, and sampling for large CSV files.
- For Parquet files, read metadata (row counts, schemas) using `pyarrow` or `polars` without full load.
- Never copy large Parquet datasets to CSV format.

## 4. Preprocessing Constraints
- Avoid data leakage: Scalers, encoders, and imputer objects must be fitted **only** on the training split. Do NOT fit on train + test combined.
- Store preprocessing pipelines separately to ensure reproducible feature transformations.

## 5. Cross-Dataset Generalization
- Do NOT concatenate datasets and split them randomly to test generalization.
- Train models on one dataset (e.g. KDD99) and test on a different dataset (e.g. NSL-KDD), only when features and label mappings are scientifically valid.
- Document and defend all feature and label mappings.

## 6. Scientific Integrity
- Never fabricate results, dataset statistics, or model metrics.
- Keep original class distributions visible; do not hide class imbalance.
- Clearly state limitations and write conclusions in conditional terms ("Under our experimental setup...").
