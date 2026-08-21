"""Dataset loader registry."""

from __future__ import annotations

from pathlib import Path

from src.data.base import BaseDatasetLoader
from src.data.cic_ids2017 import CICIDS2017Loader
from src.data.cse_cic_ids2018 import CSECICIDS2018Loader
from src.data.kdd99 import KDD99Loader
from src.data.nsl_kdd import NSLKDDLoader
from src.data.unsw_nb15 import UNSWNB15Loader
from src.data.uwf_zeekdata import UWFZeekDataLoader

LOADERS = {
    "KDD99": KDD99Loader,
    "NSL-KDD": NSLKDDLoader,
    "UNSW-NB15": UNSWNB15Loader,
    "CIC-IDS2017": CICIDS2017Loader,
    "CSE-CIC-IDS2018": CSECICIDS2018Loader,
    "UWF ZeekData": UWFZeekDataLoader,
}


def get_loader(dataset_name: str, root_dir: Path, chunk_size: int = 100_000) -> BaseDatasetLoader:
    if dataset_name not in LOADERS:
        raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(LOADERS.keys())}")
    return LOADERS[dataset_name](root_dir=root_dir, chunk_size=chunk_size)


def list_datasets() -> list[str]:
    return list(LOADERS.keys())
