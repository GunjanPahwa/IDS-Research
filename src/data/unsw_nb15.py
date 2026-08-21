"""UNSW-NB15 loader with predefined train/test CSV splits."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

from src.data.base import BaseDatasetLoader, ChunkInfo

SPLIT_FILES = {
    "train": "UNSW_NB15_training-set.csv",
    "test": "UNSW_NB15_testing-set.csv",
}


class UNSWNB15Loader(BaseDatasetLoader):
    dataset_name = "UNSW-NB15"

    def __init__(self, root_dir: Path, chunk_size: int = 100_000):
        super().__init__(root_dir, chunk_size)
        self.split_dir = self.root_dir / "NB15"

    def list_sources(self) -> list[str]:
        return [str(self.split_dir / fname) for fname in SPLIT_FILES.values()]

    def iter_chunks(
        self,
        split: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> Iterator[tuple[pd.DataFrame, ChunkInfo]]:
        splits = [split] if split else list(SPLIT_FILES.keys())
        emitted = 0
        for split_name in splits:
            if split_name not in SPLIT_FILES:
                raise ValueError(f"Unknown UNSW-NB15 split: {split_name}")
            path = self.split_dir / SPLIT_FILES[split_name]
            chunk_index = 0
            reader = pd.read_csv(
                path,
                chunksize=self.chunk_size,
                encoding="latin-1",
                low_memory=False,
            )
            for chunk in reader:
                if max_rows is not None:
                    remaining = max_rows - emitted
                    if remaining <= 0:
                        return
                    chunk = chunk.iloc[:remaining]
                emitted += len(chunk)
                yield chunk, ChunkInfo(
                    dataset=self.dataset_name,
                    split=split_name,
                    source_file=str(path),
                    chunk_index=chunk_index,
                )
                chunk_index += 1
