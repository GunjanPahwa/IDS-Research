# Network Intrusion Detection & Cross-Dataset Generalization

This repository contains the codebase and documentation for a research-oriented Network Intrusion Detection System (IDS) focused on **dataset evolution** and **cross-dataset generalization**.

## Project Objective
To study how network intrusion datasets evolve over time, standardize their feature spaces and attack label taxonomies where scientifically valid, build machine learning baselines, and investigate how well classifiers trained on one dataset generalize to completely different, unseen datasets.

## Directory Structure
```text
├── CIC2017/            # CIC-IDS2017 raw dataset
├── CIC2018/            # CSE-CIC-IDS2018 raw dataset
├── KDD99/              # KDD99 raw dataset
├── NB15/               # UNSW-NB15 raw dataset (treated as UNSW-NB15)
├── NSL KDD/            # NSL-KDD raw dataset
├── UWF ZeekData/       # UWF ZeekData raw dataset
│
├── docs/               # Research documentation and inventories
├── results/            # Performance metrics, heatmaps, and figures
├── src/                # Machine learning source code
│   ├── data/           # Dataset loaders and streams
│   ├── preprocessing/  # Feature transformation pipelines
│   ├── models/         # Classification algorithms
│   └── evaluation/     # Metrics and cross-dataset testing
│
├── requirements.txt    # Project dependencies
├── PROJECT_PROGRESS.md # Overall project status and logs
└── PROJECT_INSTRUCTIONS.md # Research constraints and guidelines
```

## Setup and Environment
We use a dedicated Conda environment named `ids_research` with Python 3.11:
```bash
conda activate ids_research
pip install -r requirements.txt
```

## Documentation
Refer to the `docs/` directory for detailed analysis:
- [Dataset Inventory](docs/dataset_inventory.md)
- [Dataset Comparison](docs/dataset_comparison.md)
- [Label Analysis](docs/label_analysis.md)
- [Feature Analysis](docs/feature_analysis.md)
