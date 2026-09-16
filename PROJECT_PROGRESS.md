# Project Progress - Network IDS Research & Cross-Dataset Generalization

This document tracks the active progress of our Network Intrusion Detection System (IDS) and Cross-Dataset Generalization research.

## Overall Project Status

- **Phase**: Model Training & Cross-Dataset Generalization Complete

- **Status**: Model training phase fully completed across all 6 datasets for Stage 1 binary classification, Stage 2 multi-class attack classification, Unified single-stage baselines, and Cross-dataset generalization matrices (Common-5 6x6 & Common-7 4x4). All models saved in `models/`, full metrics logged to `results/model_benchmarks.json`.

## Work Completed
- Created the dedicated `ids_research` Conda environment and installed all required packages (`xgboost`, `lightgbm`, etc.).
- Built modular machine learning codebase in `src/models/` (`binary.py`, `multiclass.py`, `pipeline.py`) and `src/evaluation/` (`metrics.py`, `cross_dataset.py`).
- Implemented `Stage1BinaryClassifier` with class-imbalance loss weighting (`scale_pos_weight`).
- Implemented `Stage2MultiClassClassifier` (trained attack-only) and `UnifiedSingleStageClassifier` (trained benign + attack types).
- Implemented `TwoStageIDSPipeline` for end-to-end cascaded evaluation.
- Executed `src/train_and_evaluate.py` across all datasets and feature spaces.
- Generated full 6×6 (Common-5) and 4×4 (Common-7) cross-dataset generalization matrices.
- Saved trained models into `models/` and structured benchmark outputs to `results/model_benchmarks.json`.

## Experiments/Models Completed
- **Stage 1 Binary Classifiers**: 16 models trained and evaluated (Native, Common-5, Common-7).
- **Stage 2 Multi-Class Classifiers**: 6 models trained (attack-only) and evaluated under Isolated and Cascaded End-to-End setups.
- **Unified Single-Stage Baseline**: 6 models trained on benign + specific attack types directly.
- **Cross-Dataset Generalization**: 36-pair Common-5 matrix + 16-pair Common-7 matrix evaluated.

## Results Obtained
- **Stage 1 Native F1-Scores**: KDD99 (0.9999), CIC-IDS2017 (0.9958), CSE-CIC-IDS2018 (0.9930), UWF ZeekData (0.9292), UNSW-NB15 (0.9111), NSL-KDD (0.7623).
- **Two-Stage vs. Unified**: Unified single-stage classifiers slightly edge out two-stage pipelines in Macro F1 (+0.2% to +2.2%), though two-stage pipelines provide independent operational control over alarm sensitivity.
- **Cross-Dataset Transferability**: High intra-family transfer between CIC-IDS2017 and CSE-CIC-IDS2018 (~0.90 to ~0.96 F1). Significant domain shift drop when evaluating legacy KDD models on modern CIC datasets (~0.37 F1).


## Files Created/Modified
- `requirements.txt` (Created)
- `PROJECT_PROGRESS.md` (Created/Updated)
- `PROJECT_INSTRUCTIONS.md` (Created)
- `SESSION_HANDOFF.md` (Created/Updated)
- `data/label_mapping.csv` (Created)
- `docs/dataset_inventory.md` (Created)
- `docs/dataset_comparison.md` (Created)
- `docs/label_analysis.md` (Created)
- `docs/feature_analysis.md` (Created)
- `docs/preprocessing_decisions.md` (Created)
- `src/data/` loaders codebase (Created)
- `src/preprocessing/` pipeline codebase (Created/Updated)
- `tests/test_loaders.py` (Created/Updated to unittest TestCase)
- `scratch/verify_processed.py` (Created/Updated)
- `scratch/audit_datasets.py` (Updated to match 3-value pipeline API)
- `scratch/audit_extra.py` (Updated to match 3-value pipeline and LabelStandardizer APIs)

## Errors/Problems Encountered and Their Status
- **Resolved**: **OneHotEncoder Shape Mismatch Bug in Native Mode**. Fixed by setting `categories='auto'` in `NIDSPreprocessor` for Native feature spaces. Tested and confirmed working across all datasets.
- **Resolved**: **Broken Scratch Scripts**. Modified unpacking calls to `X, y_bin, y_mul` in `scratch/audit_datasets.py` and `scratch/audit_extra.py` and wrapped lookup accesses to `.ls._processor.lookup`. Both run to completion.
- **Resolved**: **No Pytest in Environment**. Rewrote `tests/test_loaders.py` to use `unittest.TestCase` and `self.subTest()` parameters. Ran using `python -m unittest tests/test_loaders.py` and confirmed all 5 major test sequences pass (covering all 6 loader families).
- **Resolved**: Encoding error in UNSW-NB15's feature file. Specified `latin-1` fallback.
- **Resolved**: NaN/Inf values present in CIC-IDS2017 and CIC-IDS2018 flow statistics. Imputed and handled.
- **Resolved**: UWF duplicate label leak. Handled via `DuplicatePolicy.EXCLUDE`.

## Important Methodological Decisions
- **Environment Isolation**: Opted for a dedicated Conda environment to avoid modifying the user's base Conda setup.
- **Memory-Efficient Analysis**: Running scans and data processing via custom streaming chunk loaders (pandas chunks, pyarrow row groups) to avoid loading multi-gigabyte files into RAM.
- **Data Leakage Mitigation**: Excluded leakage-prone columns (`difficulty_score`, `id`, IP fields, timestamps, community hashes) during preprocessing.

## Current Task/State
- All 6 datasets fully preprocessed. Conda environment `ids_research` set up on new machine (Miniconda at `C:\Users\Yukta.Thakran\AppData\Local\miniconda3`). Ready to begin Stage 1 binary classifier.

## Next Steps (Prioritized)
1. **Stage 1 — Binary Classifier**: Train attack/benign classifiers (Logistic Regression, Random Forest, XGBoost) per dataset in native feature space. Log accuracy, precision, recall, F1, ROC-AUC.
2. **Stage 2 — Multi-class Classifier**: Train attack-type classifiers on attack-only subset.
3. **Cross-dataset generalization**: Train on one dataset, evaluate on others using Common-5 and Common-7 feature spaces.
