# Project Progress - Network IDS Research & Cross-Dataset Generalization

This document tracks the active progress of our Network Intrusion Detection System (IDS) and Cross-Dataset Generalization research.

## Overall Project Status
- **Phase**: Preprocessing Complete — Ready for Stage 1 Modeling
- **Status**: All 6 datasets fully preprocessed across all applicable feature spaces. UWF ZeekData confirmed complete (28-Aug-2026). Zero NaN/Inf in features. All preprocessors saved. Ready for Stage 1 binary classifier.

## Environment & Setup Information
- **Conda Environment**: `ids_research`
- **Python Version**: 3.11.15
- **Active Interpreter**: `C:\Users\Yukta.Thakran\AppData\Local\miniconda3\envs\ids_research\python.exe`
- **Core Dependencies**:
  - `pandas`
  - `numpy`
  - `pyarrow`
  - `polars`
  - `scikit-learn`
  - `matplotlib`
  - `seaborn`
  - `jupyter`
- **Important Commands**:
  - Activate environment: `conda activate ids_research`
  - Run python command: `conda run -n ids_research python <script>`
  - Run unittest suite: `conda run -n ids_research python -m unittest tests/test_loaders.py`

## Work Completed
- Created the dedicated `ids_research` Conda environment and installed all required packages.
- Created `requirements.txt` containing core project dependencies.
- Wrote memory-efficient data analysis scripts using Polars to parse KDD99, NSL-KDD, UNSW-NB15, CIC-IDS2017, CSE-CIC-IDS2018, and UWF ZeekData.
- Generated `docs/dataset_inventory.md` containing record counts, file sizes, format descriptions, missing values, duplicates, and leakage-prone columns.
- Generated `docs/label_analysis.md` containing class frequency lists and proportions for all datasets.
- Created `docs/dataset_comparison.md` comparing creation periods, environments, methodologies, features, and constraints of the datasets.
- Created `docs/feature_analysis.md` mapping out identical, equivalent, disjoint, and dataset-specific feature groups.
- Created `data/label_mapping.csv` mapping all unique labels to standardized categories.
- Created `PROJECT_INSTRUCTIONS.md` and `SESSION_HANDOFF.md`.
- Implemented memory-efficient dataset loaders in `src/data/` (using pandas chunking for CSV/text and PyArrow row-group loading for Parquet).
- Implemented `NIDSPreprocessor` and label processors in `src/preprocessing/` supporting two-stage target labeling (binary and multiclass) and feature space mapping.
- Verified dataset loader compatibility and cross-dataset (Common-5/Common-7) pipeline transformations on all six datasets.
- **Fixed and Verified the Native-mode Preprocessing Bug**: Resolved the `OneHotEncoder` shape mismatch bug in `src/preprocessing/pipeline.py` by initializing with `categories='auto'` dynamically for Native feature spaces. Verified that Native-mode preprocessing succeeds for all six datasets.
- **Fixed and Verified Scratch Scripts**: Resolved unpacking signature errors in `scratch/audit_datasets.py` and `scratch/audit_extra.py` (which now correctly unpack `X, y_bin, y_mul` and access internal `LabelStandardizer._processor.lookup` mappings). Both scripts now execute to completion (exit code 0).
- **Migrated Loader Tests to unittest**: Rewrote `tests/test_loaders.py` to inherit from `unittest.TestCase` and utilize `self.subTest()` for parameterized checks, allowing the automated test suite to run successfully without `pytest`.

## Datasets Inspected/Processed
- **KDD99**: `kddcup.data` (708.18 MB, 4,898,431 rows, 42 columns, CSV, no header).
- **NSL-KDD**: Standardized KDD subset (`KDDTrain+.txt`, `KDDTest+.txt`, `KDDTest-21.txt`), 43 columns including `difficulty_score`.
- **UNSW-NB15**: Modern network datasets (`UNSW_NB15_training-set.csv` and `UNSW_NB15_testing-set.csv`), 45 columns.
- **CIC-IDS2017**: 8 day-wise CSV files in `CIC2017/MachineLearningCVE/` containing 79 columns.
- **CSE-CIC-IDS2018**: 10 day-wise Parquet files in `CIC2018/` containing 78 columns.
- **UWF ZeekData**: 1 Snappy Parquet file in `UWF ZeekData/` containing 26 columns of Zeek logs.

## Preprocessing Status
- **KDD99**: ✅ COMPLETED — native (3,918,744/979,687), common5 (3,918,744/979,687); common7 INCOMPATIBLE
- **NSL-KDD**: ✅ COMPLETED — native (125,973/22,544), common5 (125,973/22,544); common7 INCOMPATIBLE
- **UNSW-NB15**: ✅ COMPLETED — native (175,341/82,332), common5, common7
- **CIC-IDS2017**: ✅ COMPLETED — native (2,264,591/566,152), common5, common7
- **CSE-CIC-IDS2018**: ✅ COMPLETED — native (5,327,621/1,331,911), common5, common7
- **UWF ZeekData**: ✅ COMPLETED (28-Aug-2026)
  - **native**: Train=1,518,890 / Test=379,723 | features=19 | NaN=0 Inf=0
  - **common5**: Train=1,518,890 / Test=379,723 | features=17 | NaN=0 Inf=0
  - **common7**: Train=1,518,890 / Test=379,723 | features=19 | NaN=0 Inf=0


## Experiments/Models Completed
*None.*

## Results Obtained
*None.*

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
