"""CIC-IDS2017 day-wise CSV loader."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

from src.data.base import BaseDatasetLoader, ChunkInfo


class CICIDS2017Loader(BaseDatasetLoader):
    dataset_name = "CIC-IDS2017"

    def __init__(self, root_dir: Path, chunk_size: int = 100_000):
        super().__init__(root_dir, chunk_size)
        self.data_dir = self.root_dir / "CIC2017" / "MachineLearningCVE"

    def list_sources(self) -> list[str]:
        return sorted(str(p) for p in self.data_dir.glob("*.csv"))

    def iter_chunks(
        self,
        split: Optional[str] = None,
        max_rows: Optional[int] = None,
        source_file: Optional[str] = None,
    ) -> Iterator[tuple[pd.DataFrame, ChunkInfo]]:
        files = self.list_sources()
        if source_file:
            files = [f for f in files if Path(f).name == source_file or f == source_file]
        if split:
            files = [f for f in files if split in Path(f).name]
        if not files:
            raise ValueError(f"No CIC-IDS2017 files matched split/source: {split}, {source_file}")

        emitted = 0
        for file_path in files:
            chunk_index = 0
            reader = pd.read_csv(
                file_path,
                chunksize=self.chunk_size,
                encoding="latin-1",
                low_memory=False,
            )
            for chunk in reader:
                chunk.columns = [str(c).strip() for c in chunk.columns]
                if max_rows is not None:
                    remaining = max_rows - emitted
                    if remaining <= 0:
                        return
                    chunk = chunk.iloc[:remaining]
                emitted += len(chunk)
                yield chunk, ChunkInfo(
                    dataset=self.dataset_name,
                    split=Path(file_path).stem,
                    source_file=file_path,
                    chunk_index=chunk_index,
                )
                chunk_index += 1
