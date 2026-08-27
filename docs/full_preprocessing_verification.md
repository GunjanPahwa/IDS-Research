# Full-Scale Preprocessing Verification Report

## Overview Table

| Dataset | Available files | Existing split? | Chosen split strategy | Reason | Expected train/test sizes | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| KDD99 | kddcup.data | No | 80/20 Stratified Random Split | Ensures representative class distributions on single large file | Train: 3,918,744, Test: 979,687 | native: PASS, Common-5: PASS, Common-7: INCOMPATIBLE |
| NSL-KDD | KDDTrain+.txt, KDDTest+.txt | Yes (Predefined) | Use predefined splits | Official benchmarking splits | Train: 125,973, Test: 22,544 | native: PASS, Common-5: PASS, Common-7: INCOMPATIBLE |
| UNSW-NB15 | UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv | Yes (Predefined) | Use predefined splits | Official benchmarking splits | Train: 175,341, Test: 82,332 | native: PASS, Common-5: PASS, Common-7: PASS |
| CIC-IDS2017 | 8 day-wise CSV files | No | 80/20 Stratified per day-file, then combine | Preserves day-level distributions and attack representatives | Train: ~2,264,574, Test: ~566,144 | native: PASS, Common-5: PASS, Common-7: PASS |
| CSE-CIC-IDS2018 | 10 day-wise Parquet files | No | 80/20 Stratified per day-file, then combine | Preserves day-level distributions and attack representatives | Train: ~5,827,853, Test: ~1,456,964 | PENDING |
| UWF ZeekData | 7 partition Parquet files | No | 80/20 Stratified on union (Duplicate excluded) | Preserves existing project splitting strategy | Train: ~1,533,405, Test: ~383,352 | PENDING |

---

## Per-Dataset Verification Details

### KDD99 | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: kddcup.data
- **Split Strategy**: Stratified 80/20 random index split
- **Train/Test Sizes**: Raw Train = 3918744, Raw Test = 979687
- **Post-Drop Row Counts**: Train = 3918744, Test = 979687
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 58
- **Train matrix shape**: [3918744, 59]
- **Test matrix shape**: [979687, 59]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/kdd99_native_train.csv`
  - Test: `data/processed/kdd99_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/kdd99_native_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### KDD99 | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: kddcup.data
- **Split Strategy**: Stratified 80/20 random index split
- **Train/Test Sizes**: Raw Train = 3918744, Raw Test = 979687
- **Post-Drop Row Counts**: Train = 3918744, Test = 979687
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 17
- **Train matrix shape**: [3918744, 18]
- **Test matrix shape**: [979687, 18]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/kdd99_common5_train.csv`
  - Test: `data/processed/kdd99_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/kdd99_common5_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### KDD99 | Feature Space: Common-7 | Status: INCOMPATIBLE

**Reason**: Common-7 is incompatible with KDD99: src_packets/dst_packets are not available. Use Common-5 instead.

### NSL-KDD | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: KDDTrain+.txt, KDDTest+.txt
- **Split Strategy**: Official predefined train/test splits
- **Train/Test Sizes**: Raw Train = 125973, Raw Test = 22544
- **Post-Drop Row Counts**: Train = 125973, Test = 22544
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 58
- **Train matrix shape**: [125973, 59]
- **Test matrix shape**: [22544, 59]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/nsl-kdd_native_train.csv`
  - Test: `data/processed/nsl-kdd_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/nsl-kdd_native_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### NSL-KDD | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: KDDTrain+.txt, KDDTest+.txt
- **Split Strategy**: Official predefined train/test splits
- **Train/Test Sizes**: Raw Train = 125973, Raw Test = 22544
- **Post-Drop Row Counts**: Train = 125973, Test = 22544
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 17
- **Train matrix shape**: [125973, 18]
- **Test matrix shape**: [22544, 18]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/nsl-kdd_common5_train.csv`
  - Test: `data/processed/nsl-kdd_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/nsl-kdd_common5_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### NSL-KDD | Feature Space: Common-7 | Status: INCOMPATIBLE

**Reason**: Common-7 is incompatible with NSL-KDD: src_packets/dst_packets are not available. Use Common-5 instead.

### UNSW-NB15 | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv
- **Split Strategy**: Official predefined train/test splits
- **Train/Test Sizes**: Raw Train = 175341, Raw Test = 82332
- **Post-Drop Row Counts**: Train = 175341, Test = 82332
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 61
- **Train matrix shape**: [175341, 62]
- **Test matrix shape**: [82332, 62]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/unsw-nb15_native_train.csv`
  - Test: `data/processed/unsw-nb15_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/unsw-nb15_native_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UNSW-NB15 | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv
- **Split Strategy**: Official predefined train/test splits
- **Train/Test Sizes**: Raw Train = 175341, Raw Test = 82332
- **Post-Drop Row Counts**: Train = 175341, Test = 82332
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 17
- **Train matrix shape**: [175341, 18]
- **Test matrix shape**: [82332, 18]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/unsw-nb15_common5_train.csv`
  - Test: `data/processed/unsw-nb15_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/unsw-nb15_common5_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UNSW-NB15 | Feature Space: Common-7 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv
- **Split Strategy**: Official predefined train/test splits
- **Train/Test Sizes**: Raw Train = 175341, Raw Test = 82332
- **Post-Drop Row Counts**: Train = 175341, Test = 82332
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 19
- **Train matrix shape**: [175341, 20]
- **Test matrix shape**: [82332, 20]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/unsw-nb15_common7_train.csv`
  - Test: `data/processed/unsw-nb15_common7_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/unsw-nb15_common7_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### CIC-IDS2017 | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: 8 day-wise CSV files
- **Split Strategy**: Stratified 80/20 split per day-file combined
- **Train/Test Sizes**: Raw Train = 2264591, Raw Test = 566152
- **Post-Drop Row Counts**: Train = 2264591, Test = 566152
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 92
- **Train matrix shape**: [2264591, 93]
- **Test matrix shape**: [566152, 93]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/cic-ids2017_native_train.csv`
  - Test: `data/processed/cic-ids2017_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/cic-ids2017_native_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### CIC-IDS2017 | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 8 day-wise CSV files
- **Split Strategy**: Stratified 80/20 split per day-file combined
- **Train/Test Sizes**: Raw Train = 2264591, Raw Test = 566152
- **Post-Drop Row Counts**: Train = 2264591, Test = 566152
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 17
- **Train matrix shape**: [2264591, 18]
- **Test matrix shape**: [566152, 18]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/cic-ids2017_common5_train.csv`
  - Test: `data/processed/cic-ids2017_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/cic-ids2017_common5_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### CIC-IDS2017 | Feature Space: Common-7 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 8 day-wise CSV files
- **Split Strategy**: Stratified 80/20 split per day-file combined
- **Train/Test Sizes**: Raw Train = 2264591, Raw Test = 566152
- **Post-Drop Row Counts**: Train = 2264591, Test = 566152
- **Dropped Rows**: Train dropped = 0 (Skipped (loaded processed)), Test dropped = 0 (Skipped (loaded processed))
- **Feature count**: 19
- **Train matrix shape**: [2264591, 20]
- **Test matrix shape**: [566152, 20]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**: 
  - Train: `data/processed/cic-ids2017_common7_train.csv`
  - Test: `data/processed/cic-ids2017_common7_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/cic-ids2017_common7_preprocessor.pkl`
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

