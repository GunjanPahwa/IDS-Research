# Network Intrusion Detection and Cross-Dataset Generalization

## 1. Executive Summary

This project is a research-oriented machine-learning Network Intrusion Detection System (NIDS). It studies whether an intrusion detector trained on one network dataset continues to work when it is evaluated on a different dataset collected with different sensors, feature definitions, traffic environments, attack families, and label taxonomies.

The project is currently between data engineering and experimental modeling:

- The six raw datasets have been inspected.
- Dataset inventories, label analysis, feature comparisons, and preprocessing decisions have been documented.
- Memory-aware dataset loaders have been implemented.
- Standardized binary and multiclass label processing has been implemented.
- Native, Common-5, and Common-7 processed feature spaces have been generated where scientifically possible.
- A first Stage 1 XGBoost binary-classification experiment has been run for the four datasets compatible with Common-7.
- Stage 2 multiclass modeling, broader baseline comparisons, artifact versioning, plots, and final interpretation remain incomplete.

The central result so far is that within-dataset performance is high, while cross-dataset F1 performance is usually poor. This supports the research motivation: high scores on a familiar benchmark do not demonstrate reliable cross-dataset generalization.

## 2. What the Project Is

The system is designed to answer three related questions:

1. **Can network flows be classified as benign or malicious?**
   This is Stage 1, a binary task: `BENIGN` versus `ATTACK`.
2. **Can malicious flows be assigned to a standardized attack category?**
   This is Stage 2, a multiclass task performed using standardized categories such as DoS, DDoS, Probe/Reconnaissance, Exploitation, Brute Force, Web Attack, Botnet, Infiltration, and Other.
3. **Does a detector generalize across datasets?**
   A model is trained on one dataset and tested on a different dataset without mixing the two datasets into a random split. This is the main research question.

The project is not currently a production IDS, live packet-monitoring daemon, firewall, or network sensor. It is an offline research pipeline for preparing tabular flow/log data, training classifiers, evaluating them, and measuring dataset shift.

## 3. Intended End-to-End Workflow

```text
Raw CSV/TXT/Parquet datasets
        |
        v
Dataset-specific loaders
        |
        v
Column standardization and label normalization
        |
        v
Leakage removal + duplicate policy + invalid-value handling
        |
        v
Train/test split with preprocessor fit on training data only
        |
        v
Native or Common-5/Common-7 feature matrix
        |
        +--> Stage 1: BENIGN vs ATTACK
        |
        +--> Stage 2: standardized attack category
        |
        v
Within-dataset and cross-dataset metrics
        |
        v
Generalization analysis, figures, limitations, and conclusions
```

The intended experimental discipline is to preserve official dataset splits where they exist, create documented stratified splits where they do not, and never concatenate unrelated datasets before a random split when measuring generalization.

## 4. Datasets

Six datasets are present in the repository.

| Dataset | Raw format and scale | Main characteristics | Current role |
|---|---|---|---|
| KDD99 | `kddcup.data`; CSV; 4,898,431 rows; 42 columns; about 708 MB | Classic connection-record intrusion dataset; very high duplication | Native and Common-5 preprocessing; Common-7 incompatible |
| NSL-KDD | `KDDTrain+.txt`, `KDDTest+.txt`, `KDDTest-21.txt`; 43 columns | A cleaned KDD-family benchmark with no duplicate rows in the inspected files | Native and Common-5 preprocessing; Common-7 incompatible |
| UNSW-NB15 | Training and testing CSVs; 175,341 training rows and 82,332 testing rows; 45 columns | Modern network-flow dataset with binary `label` and multiclass `attack_cat` | Native, Common-5, and Common-7 preprocessing |
| CIC-IDS2017 | Eight day-wise CSV files; 79 columns | CICFlowMeter features and multiple attack scenarios | Native, Common-5, and Common-7 preprocessing |
| CSE-CIC-IDS2018 | Ten day/scenario Parquet files; 78 columns | CICFlowMeter-derived features and multiple attack scenarios | Native, Common-5, and Common-7 preprocessing |
| UWF ZeekData | Seven Parquet partitions; 26 columns | Zeek connection/log features with binary, tactic, technique, and CVE-related labels | Native, Common-5, and Common-7 preprocessing |

### Dataset quality observations

- KDD99 contains 3,823,439 duplicate rows out of 4,898,431 inspected rows, approximately 78%.
- NSL-KDD was designed to reduce KDD99 duplication and has zero duplicates in the listed files.
- CIC-IDS2017 contains missing and infinite values in flow-rate features such as `Flow Bytes/s` and `Flow Packets/s`.
- UNSW-NB15 contains an `id` field that is treated as leakage-prone and excluded.
- NSL-KDD contains `difficulty_score`, which is metadata related to dataset filtering and is excluded.
- UWF contains identifiers, addresses, timestamps, ports, and related fields that can identify the source or collection environment rather than represent portable traffic behavior.
- UWF `Duplicate` labels are handled explicitly. The default is to exclude them.

## 5. Repository Structure

- `CIC2017/`, `CIC2018/`, `KDD99/`, `NB15/`, `NSL KDD/`, `UWF ZeekData/`: raw input datasets. These must not be modified.
- `src/data/`: dataset loader abstractions, registry, and dataset-specific loaders.
- `src/preprocessing/`: feature mappings, label processors, preprocessing pipeline, utilities, and artifact persistence.
- `data/processed/`: full-scale transformed train/test CSV files.
- `data/preprocessors/`: fitted preprocessing artifacts and metadata.
- `data/label_mapping.csv`: explicit raw-label to standardized-label mapping with confidence and rationale.
- `docs/`: dataset inventory, comparisons, label analysis, feature analysis, preprocessing decisions, and verification documentation.
- `scratch/`: analysis, preprocessing, verification, and Stage 1 training scripts.
- `tests/`: loader verification tests.
- `results/`: experiment result JSON files. The current artifact is `stage1_binary_results.json`.
- `logs/`: execution logs and temporary inspection files.
- `setup_and_run.ps1`: Windows setup, dependency verification, and background preprocessing launcher.
- `requirements.txt`: Python dependency list.
- `PROJECT_PROGRESS.md`: working progress log.
- `SESSION_HANDOFF.md`: continuation notes from the previous work session.
- `PROJECT_INSTRUCTIONS.md`: research and data-integrity constraints.

## 6. Environment and Reproducibility

The intended environment is:

- Conda environment: `ids_research`
- Python: 3.11, recorded as 3.11.15 in the progress log
- Important libraries: pandas, NumPy, PyArrow, Polars, scikit-learn, joblib, SciPy, matplotlib, seaborn, and Jupyter
- Recorded interpreter: `C:\Users\Yukta.Thakran\AppData\Local\miniconda3\envs\ids_research\python.exe`

Typical commands are:

```powershell
conda activate ids_research
pip install -r requirements.txt
conda run -n ids_research python -m unittest tests/test_loaders.py
conda run -n ids_research python scratch/run_full_preprocessing.py
conda run -n ids_research python scratch/train_stage1_binary.py
```

The PowerShell setup script checks for Miniconda, creates `ids_research` when missing, installs requirements, verifies imports, and launches preprocessing in a detached process with logs. The script is useful for setup, but preprocessing has already been completed and should not be rerun casually because the files are full-scale.

## 7. Data Loading Layer

`BaseDatasetLoader` defines the common loader contract:

- `list_sources()` identifies source files.
- `iter_chunks()` yields pandas chunks together with `ChunkInfo` metadata.
- `load_sample()` loads a bounded sample without reading an entire source.
- `count_rows()` counts rows through the iterator.

The implementation uses:

- pandas chunk iteration for large CSV/text sources;
- PyArrow row-group access for Parquet sources;
- dataset-specific handling for headers, encodings, predefined splits, and UWF partitions;
- a registry so callers can request loaders by dataset name.

This design keeps raw datasets untouched and limits memory pressure during inspection and preprocessing. The UWF splitter is an exception in the current implementation: it reads and concatenates the seven UWF partitions for its union split, so this path should be reviewed before scaling to larger versions of the dataset.

## 8. Preprocessing Pipeline

`NIDSPreprocessor` supports two modes:

- `within-dataset` with `native` features;
- `cross-dataset` with `Common-5` or `Common-7` features.

The pipeline performs the following operations:

1. Strip whitespace from column names and apply dataset-specific column aliases.
2. Extract and standardize binary and multiclass labels.
3. Apply the configured UWF duplicate policy.
4. Remove leakage-prone fields.
5. Normalize protocol values to a fixed vocabulary: TCP, UDP, ICMP, or other.
6. Normalize or infer service values using a fixed service vocabulary and, where needed, destination-port inference.
7. Convert CIC flow duration from microseconds to seconds.
8. Remove cross-dataset inference-only fields.
9. Cap or clean extreme numeric values.
10. Fit a median imputer and `RobustScaler` on training data only.
11. Fit a one-hot encoder on categorical features.
12. Transform test data using the already-fitted objects.
13. Return the feature matrix plus binary and multiclass targets.

The Native-mode `OneHotEncoder` shape mismatch was fixed by using `categories="auto"`, allowing each native dataset to establish its own categorical vocabulary during fitting. Unknown categories during transformation are ignored.

### Feature spaces

- **Native**: dataset-specific features retained for within-dataset experiments.
- **Common-5**: a small portable feature space for cross-dataset comparison.
- **Common-7**: Common-5 plus source and destination packet counts where available.

KDD99 and NSL-KDD do not contain the packet-count fields required by Common-7. Their Common-7 incompatibility is expected and is represented by `Common7IncompatibleError`; it is not a preprocessing failure.

The cross-dataset mappings are scientifically limited. Duration, bytes, packets, protocol, and service are not perfectly equivalent across all collection tools. CIC protocol/service values may be inferred from ports, and CIC2018 files in this repository may not contain a usable port field, causing service to become `other`. These limitations must be included in the final interpretation.

## 9. Label Taxonomy

The project uses two targets:

### Stage 1

- `0`: `BENIGN`
- `1`: `ATTACK`

### Stage 2

Raw labels are mapped to standardized categories. Examples include:

- `DoS` and `DDoS`
- `Probe/Reconnaissance`
- `Brute Force`
- `Credential/Access Attack`
- `Exploitation`
- `Web Attack`
- `Botnet`
- `Infiltration`
- `Privilege Escalation`
- `Other`
- `BENIGN`

`data/label_mapping.csv` records the original label, standardized label, mapping confidence, reason, and notes. Dataset-specific aliases are handled in code, including CIC2017 Web Attack separator normalization and the CIC2018 misspelling `Infilteration`.

The UWF dataset is special: binary labels come from `label_binary`, while multiclass labels can use `label_tactic` and, when available, `label_technique`. UWF tactics are mapped to the project taxonomy. The default duplicate policy excludes rows whose binary label is `Duplicate`; alternative explicit policies are `attack` and `benign`.

## 10. Splitting and Leakage Controls

The documented split policies are:

- KDD99: stratified 80/20 split of the single raw file.
- NSL-KDD: official predefined train/test split.
- UNSW-NB15: official predefined train/test split.
- CIC-IDS2017: stratified 80/20 split per day file, followed by combination.
- CSE-CIC-IDS2018: stratified 80/20 split per Parquet source file.
- UWF ZeekData: stratified 80/20 split across the union of seven partitions, after duplicate handling during transformation.

The preprocessing objects are fitted on training data only. Test data is transformed with those objects. This prevents the test set from influencing medians, scales, or categorical vocabularies.

For cross-dataset experiments, datasets are not randomly concatenated before splitting. A model trained on one dataset is evaluated on a separate dataset. This is essential because random mixing would measure interpolation within a combined distribution rather than generalization to an unseen source.

## 11. Completed Engineering Work

Completed work includes:

- dedicated Conda environment and dependency specification;
- raw dataset inspection scripts;
- dataset inventory with sizes, schemas, missing values, duplicates, labels, and leakage fields;
- label-frequency and proportion analysis;
- dataset methodology comparison;
- feature compatibility analysis;
- standardized label mapping;
- memory-aware loaders for all six dataset families;
- reusable preprocessing pipeline;
- native-mode encoder bug fix;
- full-scale processed outputs and fitted preprocessor artifacts;
- loader tests migrated from pytest-style assumptions to Python `unittest`;
- scratch audit scripts fixed for the current three-value pipeline return signature;
- preprocessing verification for UWF Native, Common-5, and Common-7 with zero feature NaN/Inf values;
- initial Stage 1 XGBoost result artifact dated 2026-09-01.

## 12. Current Processed Data State

The processed directory contains train/test outputs for the six datasets in applicable feature spaces:

- KDD99: Native and Common-5; Common-7 unavailable.
- NSL-KDD: Native and Common-5; Common-7 unavailable.
- UNSW-NB15: Native, Common-5, and Common-7.
- CIC-IDS2017: Native, Common-5, and Common-7.
- CSE-CIC-IDS2018: Native, Common-5, and Common-7.
- UWF ZeekData: Native, Common-5, and Common-7.

That represents 16 dataset/feature-space combinations, each with train and test files, with two combinations intentionally incompatible. The project notes use the phrase “13 PASS + 3 INCOMPATIBLE,” but the repository listing and the explicit incompatibility rule indicate two Common-7 incompatibilities: KDD99 and NSL-KDD. This count should be reconciled in the progress documentation.

The UWF verification records the following post-drop sizes for all three spaces:

- train: 1,518,890 rows;
- test: 379,723 rows;
- Native features: 19;
- Common-5 features: 17;
- Common-7 features: 19;
- feature NaN count: 0;
- feature Inf count: 0;
- fitted on training data only: true.

## 13. Stage 1 Experiment Completed

The current result artifact is `results/stage1_binary_results.json`. It records a Common-7 experiment run on:

- CIC-IDS2017
- CSE-CIC-IDS2018
- UNSW-NB15
- UWF ZeekData

KDD99 and NSL-KDD were excluded because Common-7 is incompatible with them.

The model was `XGBClassifier` with:

- 300 estimators;
- maximum depth 6;
- learning rate 0.1;
- histogram tree method;
- all available CPU workers;
- random state 42;
- log-loss evaluation metric;
- per-training-dataset `scale_pos_weight` calculated from the training class balance.

The script trains one model per source dataset, evaluates every model on all four test datasets, trains one pooled model on all four training datasets, and evaluates the pooled model on each test set plus the combined test set. It records accuracy, precision, recall, F1, ROC-AUC, and confusion matrices.

### Class balance used in the experiment

| Dataset | Train rows | Train attack ratio | Test rows | Test attack ratio |
|---|---:|---:|---:|---:|
| CIC-IDS2017 | 2,264,591 | 19.70% | 566,152 | 19.70% |
| CSE-CIC-IDS2018 | 5,327,621 | 19.98% | 1,331,911 | 19.98% |
| UNSW-NB15 | 175,341 | 68.06% | 82,332 | 55.06% |
| UWF ZeekData | 1,518,890 | 49.54% | 379,723 | 49.54% |

### Same-dataset results

| Training dataset | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| CIC-IDS2017 | 0.992322 | 0.969512 | 0.992226 | 0.980737 | 0.999535 |
| CSE-CIC-IDS2018 | 0.969204 | 0.930982 | 0.913587 | 0.922202 | 0.982137 |
| UNSW-NB15 | 0.908407 | 0.903035 | 0.933932 | 0.918224 | 0.979564 |
| UWF ZeekData | 0.998760 | 0.997508 | 0.999995 | 0.998750 | 0.999960 |

These are benchmark-specific results, not evidence that the detector works equally well on unseen datasets.

### Cross-dataset F1 matrix

Rows are training source; columns are evaluation dataset.

| Train \\ Test | CIC2017 | CIC2018 | UNSW-NB15 | UWF |
|---|---:|---:|---:|---:|
| CIC2017 | 0.980737 | 0.006962 | 0.020691 | 0.000000 |
| CIC2018 | 0.356070 | 0.922202 | 0.049963 | 0.000234 |
| UNSW-NB15 | 0.317999 | 0.054542 | 0.918224 | 0.553301 |
| UWF | 0.472307 | 0.320072 | 0.344824 | 0.998750 |

Most cross-dataset entries were flagged by the training script as suspiciously low because F1 was below 0.55. The UNSW-to-UWF F1 of 0.553301 is only marginally above that threshold and has ROC-AUC 0.493042, so it should not be treated as convincing generalization.

### Pooled model results

The pooled model was trained on all four Common-7 training sets.

| Evaluation dataset | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| CIC-IDS2017 | 0.989413 | 0.957008 | 0.990765 | 0.973594 | 0.999222 |
| CSE-CIC-IDS2018 | 0.972747 | 0.954727 | 0.906586 | 0.930034 | 0.979245 |
| UNSW-NB15 | 0.796968 | 0.739785 | 0.973771 | 0.840803 | 0.944785 |
| UWF ZeekData | 0.998696 | 0.997507 | 0.999867 | 0.998686 | 0.999912 |
| Combined test set | 0.974788 | 0.947432 | 0.955648 | 0.951522 | 0.992818 |

The script itself flags very high pooled results on CIC2017, CIC2018, and UWF for additional investigation. These results could be legitimate, but they also could reflect residual distribution signals, feature scaling behavior, source-specific artifacts, or other forms of unintended shortcut learning. They should be audited before being presented as a central scientific conclusion.

## 14. What the Current Results Suggest

Under the current setup, each dataset is relatively learnable when the model sees data from the same source, but portable performance is weak across most dataset pairs. Likely contributors include:

- different feature-generation tools and measurement semantics;
- different traffic environments and attack scenarios;
- different label definitions and attack coverage;
- class-prior differences, especially UNSW-NB15 versus CIC datasets;
- inferred rather than observed protocol/service fields;
- source-specific residual signals in the supposedly common features;
- differences in train/test construction and duplication;
- possible threshold and calibration effects.

The result should therefore be stated conditionally: under this Common-7 mapping, this split strategy, this XGBoost configuration, and this label taxonomy, cross-dataset generalization is substantially weaker than within-dataset performance for most source-target pairs.

## 15. Known Inconsistencies and Risks to Resolve

1. `PROJECT_PROGRESS.md` and `SESSION_HANDOFF.md` still describe experiments as “None,” even though `stage1_binary_results.json` contains Stage 1 results dated 2026-09-01.
2. `docs/full_preprocessing_verification.md` still contains `PENDING` entries for datasets whose processed files exist.
3. The recorded “13 PASS + 3 INCOMPATIBLE” count does not match the six-dataset, three-space matrix and the two explicit Common-7 incompatibilities.
4. The Stage 1 training script reads very large processed CSVs fully into pandas memory and concatenates them for the pooled model. This is separate from the memory-safe preprocessing design and may be a scalability risk.
5. The Stage 1 result flags suspiciously high pooled scores but does not yet provide the follow-up audit.
6. The UWF ROC-AUC can be high while thresholded F1 is near zero for some cross-dataset predictions. This indicates that discrimination and threshold calibration differ; future analysis should inspect score distributions and tune thresholds using a declared protocol.
7. There are generated logs, temporary inspection scripts, and Python cache directories in the worktree. They are useful for local history but should be classified before packaging or submission.
8. The current automated tests focus on loaders. There is not yet a complete automated test suite for label mappings, leakage exclusion, feature counts, preprocessing fit isolation, processed-file integrity, or model-result reproducibility.

## 16. Work Still Required

### Immediate validation

- Reconcile progress and verification documents with the actual processed files and Stage 1 result artifact.
- Verify that every processed file has the expected schema, target columns, row counts, finite feature values, and matching preprocessor metadata.
- Audit the Stage 1 result generation path, especially pooled training, feature scaling, label alignment, and any source-identifying columns that survived mapping.
- Add result provenance: command, environment, package versions, input file hashes or metadata, and model artifact paths.

### Stage 1 completion

- Run Native-space baselines for all six datasets.
- Compare Logistic Regression, Decision Tree or Random Forest, and XGBoost under a fixed evaluation protocol.
- Add balanced accuracy, specificity, PR-AUC, calibration, and per-class error summaries where appropriate.
- Save trained models and structured experiment configuration.
- Generate accuracy/F1/ROC-AUC matrices and confusion-matrix figures.

### Stage 2

- Train multiclass classifiers on attack-only rows.
- Define how `BENIGN` rows are handled and how rare or unmapped categories are reported.
- Compare per-dataset native performance with Common-5/Common-7 cross-dataset performance.
- Report macro-F1 and per-class recall so frequent classes do not hide rare-class failures.

### Cross-dataset study

- Evaluate all scientifically valid source-target pairs, including KDD99/NSL-KDD where their compatible feature space permits it.
- Keep source and target datasets strictly separate.
- Test both default threshold 0.5 and a predeclared threshold-calibration strategy.
- Compare source-only, pooled, and possibly domain-adaptation baselines without contaminating the target test set.
- Analyze which common features contribute to transfer and whether removing inferred or source-sensitive features changes results.

### Final research output

- Write the methods section from the recorded implementation and decisions.
- Write the results section from generated artifacts only.
- State dataset and mapping limitations explicitly.
- Avoid claiming production readiness or universal IDS performance.
- Include reproducibility commands and an experiment manifest.

## 17. Recommended Next Checkpoint

The next concrete checkpoint should be a Stage 1 audit and documentation synchronization pass. It should confirm the existing JSON result against the training script, update stale progress statements, and add a reproducible summary table. Only after that should the project expand to Native baselines and Stage 2 multiclass experiments.

## 18. Source Artifacts

The detailed supporting artifacts are:

- [README.md](README.md)
- [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)
- [SESSION_HANDOFF.md](SESSION_HANDOFF.md)
- [PROJECT_INSTRUCTIONS.md](PROJECT_INSTRUCTIONS.md)
- [docs/dataset_inventory.md](docs/dataset_inventory.md)
- [docs/dataset_comparison.md](docs/dataset_comparison.md)
- [docs/label_analysis.md](docs/label_analysis.md)
- [docs/feature_analysis.md](docs/feature_analysis.md)
- [docs/preprocessing_decisions.md](docs/preprocessing_decisions.md)
- [docs/full_preprocessing_verification.md](docs/full_preprocessing_verification.md)
- [data/label_mapping.csv](data/label_mapping.csv)
- [results/stage1_binary_results.json](results/stage1_binary_results.json)
- [scratch/train_stage1_binary.py](scratch/train_stage1_binary.py)
- [src/preprocessing/pipeline.py](src/preprocessing/pipeline.py)
- [src/preprocessing/labels.py](src/preprocessing/labels.py)
- [src/data/base.py](src/data/base.py)
- [tests/test_loaders.py](tests/test_loaders.py)
