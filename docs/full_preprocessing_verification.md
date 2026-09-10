# Full-Scale Preprocessing Verification Report

## Overview Table

| Dataset | Available files | Existing split? | Chosen split strategy | Reason | Expected train/test sizes | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| KDD99 | kddcup.data | No | 80/20 Stratified Random Split | Ensures representative class distributions on single large file | Train: 3,918,744, Test: 979,687 | native: PASS, Common-5: PASS, Common-7: INCOMPATIBLE |
| NSL-KDD | KDDTrain+.txt, KDDTest+.txt | Yes (Predefined) | Use predefined splits | Official benchmarking splits | Train: 125,973, Test: 22,544 | native: PASS, Common-5: PASS, Common-7: INCOMPATIBLE |
| UNSW-NB15 | UNSW_NB15_training-set.csv, UNSW_NB15_testing-set.csv | Yes (Predefined) | Use predefined splits | Official benchmarking splits | Train: 175,341, Test: 82,332 | native: PASS, Common-5: PASS, Common-7: PASS |
| CIC-IDS2017 | 8 day-wise CSV files | No | 80/20 Stratified per day-file, then combine | Preserves day-level distributions and attack representatives | Train: ~2,264,574, Test: ~566,144 | native: PASS, Common-5: PASS, Common-7: PASS |
| CSE-CIC-IDS2018 | 10 day-wise Parquet files | No | 80/20 Stratified per day-file, then combine | Preserves day-level distributions and attack representatives | Train: ~5,827,853, Test: ~1,456,964 | native: PASS, Common-5: PASS, Common-7: PASS |
| UWF ZeekData | 7 partition Parquet files | No | 80/20 Stratified on union (Duplicate excluded) | Preserves existing project splitting strategy | Train: ~1,533,405, Test: ~383,352 | native: PASS, Common-5: PASS, Common-7: PASS |

## Per-Dataset Verification Details

### UWF ZeekData | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: 7 partition Parquet files
- **Split Strategy**: Stratified 80/20 split on union
- **Train/Test Sizes**: Raw Train = 1533405, Raw Test = 383352
- **Post-Drop Row Counts**: Train = 1518890, Test = 379723
- **Dropped Rows**: Train dropped = 14515 (Duplicate/Unmapped label removal), Test dropped = 3629 (Duplicate/Unmapped label removal)
- **Feature count**: 19
- **Train matrix shape**: [1518890, 19]
- **Test matrix shape**: [379723, 19]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/uwf_zeekdata_native_train.csv`
  - Test: `data/processed/uwf_zeekdata_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/uwf_zeekdata_native_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 766487, '1.0': 752403}
- **Binary target class distribution (Test)**: {'0.0': 191622, '1.0': 188101}
- **Multiclass target class distribution (Train)**: {'BENIGN': 766487, 'Credential/Access Attack': 696951, 'Infiltration': 3661, 'Other': 5277, 'Probe/Reconnaissance': 46514}
- **Multiclass target class distribution (Test)**: {'BENIGN': 191622, 'Credential/Access Attack': 174237, 'Infiltration': 953, 'Other': 1330, 'Probe/Reconnaissance': 11581}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UWF ZeekData | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 7 partition Parquet files
- **Split Strategy**: Stratified 80/20 split on union
- **Train/Test Sizes**: Raw Train = 1533405, Raw Test = 383352
- **Post-Drop Row Counts**: Train = 1518890, Test = 379723
- **Dropped Rows**: Train dropped = 14515 (Duplicate/Unmapped label removal), Test dropped = 3629 (Duplicate/Unmapped label removal)
- **Feature count**: 17
- **Train matrix shape**: [1518890, 17]
- **Test matrix shape**: [379723, 17]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/uwf_zeekdata_common5_train.csv`
  - Test: `data/processed/uwf_zeekdata_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/uwf_zeekdata_common5_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 766487, '1.0': 752403}
- **Binary target class distribution (Test)**: {'0.0': 191622, '1.0': 188101}
- **Multiclass target class distribution (Train)**: {'BENIGN': 766487, 'Credential/Access Attack': 696951, 'Infiltration': 3661, 'Other': 5277, 'Probe/Reconnaissance': 46514}
- **Multiclass target class distribution (Test)**: {'BENIGN': 191622, 'Credential/Access Attack': 174237, 'Infiltration': 953, 'Other': 1330, 'Probe/Reconnaissance': 11581}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UWF ZeekData | Feature Space: Common-7 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 7 partition Parquet files
- **Split Strategy**: Stratified 80/20 split on union
- **Train/Test Sizes**: Raw Train = 1533405, Raw Test = 383352
- **Post-Drop Row Counts**: Train = 1518890, Test = 379723
- **Dropped Rows**: Train dropped = 14515 (Duplicate/Unmapped label removal), Test dropped = 3629 (Duplicate/Unmapped label removal)
- **Feature count**: 19
- **Train matrix shape**: [1518890, 19]
- **Test matrix shape**: [379723, 19]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/uwf_zeekdata_common7_train.csv`
  - Test: `data/processed/uwf_zeekdata_common7_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/uwf_zeekdata_common7_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 766487, '1.0': 752403}
- **Binary target class distribution (Test)**: {'0.0': 191622, '1.0': 188101}
- **Multiclass target class distribution (Train)**: {'BENIGN': 766487, 'Credential/Access Attack': 696951, 'Infiltration': 3661, 'Other': 5277, 'Probe/Reconnaissance': 46514}
- **Multiclass target class distribution (Test)**: {'BENIGN': 191622, 'Credential/Access Attack': 174237, 'Infiltration': 953, 'Other': 1330, 'Probe/Reconnaissance': 11581}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### CSE-CIC-IDS2018 | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: 10 day-wise Parquet files
- **Split Strategy**: Stratified 80/20 split per day-file combined
- **Train/Test Sizes**: Raw Train = 5327621, Raw Test = 1331911
- **Post-Drop Row Counts**: Train = 5327621, Test = 1331911
- **Dropped Rows**: Train dropped = 0 (Duplicate/Unmapped label removal), Test dropped = 0 (Duplicate/Unmapped label removal)
- **Feature count**: 79
- **Train matrix shape**: [5327621, 79]
- **Test matrix shape**: [1331911, 79]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/cse-cic-ids2018_native_train.csv`
  - Test: `data/processed/cse-cic-ids2018_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/cse-cic-ids2018_native_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 4263202, '1.0': 1064419}
- **Binary target class distribution (Test)**: {'0.0': 1065806, '1.0': 266105}
- **Multiclass target class distribution (Train)**: {'BENIGN': 4263202, 'Botnet': 115628, 'Brute Force': 75281, 'DDoS': 620764, 'DoS': 157254, 'Infiltration': 94786, 'Web Attack': 706}
- **Multiclass target class distribution (Test)**: {'BENIGN': 1065806, 'Botnet': 28907, 'Brute Force': 18820, 'DDoS': 155191, 'DoS': 39314, 'Infiltration': 23697, 'Web Attack': 176}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### CSE-CIC-IDS2018 | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 10 day-wise Parquet files
- **Split Strategy**: Stratified 80/20 split per day-file combined
- **Train/Test Sizes**: Raw Train = 5327621, Raw Test = 1331911
- **Post-Drop Row Counts**: Train = 5327621, Test = 1331911
- **Dropped Rows**: Train dropped = 0 (Duplicate/Unmapped label removal), Test dropped = 0 (Duplicate/Unmapped label removal)
- **Feature count**: 17
- **Train matrix shape**: [5327621, 17]
- **Test matrix shape**: [1331911, 17]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/cse-cic-ids2018_common5_train.csv`
  - Test: `data/processed/cse-cic-ids2018_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/cse-cic-ids2018_common5_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 4263202, '1.0': 1064419}
- **Binary target class distribution (Test)**: {'0.0': 1065806, '1.0': 266105}
- **Multiclass target class distribution (Train)**: {'BENIGN': 4263202, 'Botnet': 115628, 'Brute Force': 75281, 'DDoS': 620764, 'DoS': 157254, 'Infiltration': 94786, 'Web Attack': 706}
- **Multiclass target class distribution (Test)**: {'BENIGN': 1065806, 'Botnet': 28907, 'Brute Force': 18820, 'DDoS': 155191, 'DoS': 39314, 'Infiltration': 23697, 'Web Attack': 176}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### CSE-CIC-IDS2018 | Feature Space: Common-7 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 10 day-wise Parquet files
- **Split Strategy**: Stratified 80/20 split per day-file combined
- **Train/Test Sizes**: Raw Train = 5327621, Raw Test = 1331911
- **Post-Drop Row Counts**: Train = 5327621, Test = 1331911
- **Dropped Rows**: Train dropped = 0 (Duplicate/Unmapped label removal), Test dropped = 0 (Duplicate/Unmapped label removal)
- **Feature count**: 19
- **Train matrix shape**: [5327621, 19]
- **Test matrix shape**: [1331911, 19]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/cse-cic-ids2018_common7_train.csv`
  - Test: `data/processed/cse-cic-ids2018_common7_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/cse-cic-ids2018_common7_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 4263202, '1.0': 1064419}
- **Binary target class distribution (Test)**: {'0.0': 1065806, '1.0': 266105}
- **Multiclass target class distribution (Train)**: {'BENIGN': 4263202, 'Botnet': 115628, 'Brute Force': 75281, 'DDoS': 620764, 'DoS': 157254, 'Infiltration': 94786, 'Web Attack': 706}
- **Multiclass target class distribution (Test)**: {'BENIGN': 1065806, 'Botnet': 28907, 'Brute Force': 18820, 'DDoS': 155191, 'DoS': 39314, 'Infiltration': 23697, 'Web Attack': 176}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UWF ZeekData | Feature Space: native | Status: PASS

- **Preprocessing Mode**: within-dataset
- **Files Used**: 7 partition Parquet files
- **Split Strategy**: Stratified 80/20 split on union
- **Train/Test Sizes**: Raw Train = 1533405, Raw Test = 383352
- **Post-Drop Row Counts**: Train = 1518890, Test = 379723
- **Dropped Rows**: Train dropped = 14515 (Duplicate/Unmapped label removal), Test dropped = 3629 (Duplicate/Unmapped label removal)
- **Feature count**: 19
- **Train matrix shape**: [1518890, 19]
- **Test matrix shape**: [379723, 19]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/uwf_zeekdata_native_train.csv`
  - Test: `data/processed/uwf_zeekdata_native_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/uwf_zeekdata_native_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 766487, '1.0': 752403}
- **Binary target class distribution (Test)**: {'0.0': 191622, '1.0': 188101}
- **Multiclass target class distribution (Train)**: {'BENIGN': 766487, 'Credential/Access Attack': 696951, 'Infiltration': 3661, 'Other': 5277, 'Probe/Reconnaissance': 46514}
- **Multiclass target class distribution (Test)**: {'BENIGN': 191622, 'Credential/Access Attack': 174237, 'Infiltration': 953, 'Other': 1330, 'Probe/Reconnaissance': 11581}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UWF ZeekData | Feature Space: Common-5 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 7 partition Parquet files
- **Split Strategy**: Stratified 80/20 split on union
- **Train/Test Sizes**: Raw Train = 1533405, Raw Test = 383352
- **Post-Drop Row Counts**: Train = 1518890, Test = 379723
- **Dropped Rows**: Train dropped = 14515 (Duplicate/Unmapped label removal), Test dropped = 3629 (Duplicate/Unmapped label removal)
- **Feature count**: 17
- **Train matrix shape**: [1518890, 17]
- **Test matrix shape**: [379723, 17]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/uwf_zeekdata_common5_train.csv`
  - Test: `data/processed/uwf_zeekdata_common5_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/uwf_zeekdata_common5_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 766487, '1.0': 752403}
- **Binary target class distribution (Test)**: {'0.0': 191622, '1.0': 188101}
- **Multiclass target class distribution (Train)**: {'BENIGN': 766487, 'Credential/Access Attack': 696951, 'Infiltration': 3661, 'Other': 5277, 'Probe/Reconnaissance': 46514}
- **Multiclass target class distribution (Test)**: {'BENIGN': 191622, 'Credential/Access Attack': 174237, 'Infiltration': 953, 'Other': 1330, 'Probe/Reconnaissance': 11581}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

### UWF ZeekData | Feature Space: Common-7 | Status: PASS

- **Preprocessing Mode**: cross-dataset
- **Files Used**: 7 partition Parquet files
- **Split Strategy**: Stratified 80/20 split on union
- **Train/Test Sizes**: Raw Train = 1533405, Raw Test = 383352
- **Post-Drop Row Counts**: Train = 1518890, Test = 379723
- **Dropped Rows**: Train dropped = 14515 (Duplicate/Unmapped label removal), Test dropped = 3629 (Duplicate/Unmapped label removal)
- **Feature count**: 19
- **Train matrix shape**: [1518890, 19]
- **Test matrix shape**: [379723, 19]
- **NaN count in features**: Train = 0, Test = 0
- **Inf count in features**: Train = 0, Test = 0
- **Fitted on training data only**: True
- **Feature names match column counts**: True
- **Output file paths**:
  - Train: `data/processed/uwf_zeekdata_common7_train.csv`
  - Test: `data/processed/uwf_zeekdata_common7_test.csv`
- **Fitted preprocessor path**: `data/preprocessors/uwf_zeekdata_common7_preprocessor.pkl`
- **Binary target class distribution (Train)**: {'0.0': 766487, '1.0': 752403}
- **Binary target class distribution (Test)**: {'0.0': 191622, '1.0': 188101}
- **Multiclass target class distribution (Train)**: {'BENIGN': 766487, 'Credential/Access Attack': 696951, 'Infiltration': 3661, 'Other': 5277, 'Probe/Reconnaissance': 46514}
- **Multiclass target class distribution (Test)**: {'BENIGN': 191622, 'Credential/Access Attack': 174237, 'Infiltration': 953, 'Other': 1330, 'Probe/Reconnaissance': 11581}
- **Exact command executed**: `conda run -n ids_research python scratch/run_full_preprocessing.py`

