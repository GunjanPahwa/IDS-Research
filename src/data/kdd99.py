"""KDD99 headerless CSV loader."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

from src.data.base import BaseDatasetLoader, ChunkInfo


class KDD99Loader(BaseDatasetLoader):
    dataset_name = "KDD99"

    def __init__(self, root_dir: Path, chunk_size: int = 100_000):
        super().__init__(root_dir, chunk_size)
        self.data_file = self.root_dir / "KDD99" / "kddcup.data"

    def list_sources(self) -> list[str]:
        return [str(self.data_file)]

    def iter_chunks(
        self,
        split: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> Iterator[tuple[pd.DataFrame, ChunkInfo]]:
        if split and split != "full":
            raise ValueError("KDD99 only supports split='full'")

        emitted = 0
        chunk_index = 0
        reader = pd.read_csv(
            self.data_file,
            header=None,
            chunksize=self.chunk_size,
            encoding="latin-1",
            low_memory=False,
        )
        for chunk in reader:
            if max_rows is not None:
                remaining = max_rows - emitted
                if remaining <= 0:
                    break
                chunk = chunk.iloc[:remaining]
            emitted += len(chunk)
            yield chunk, ChunkInfo(
                dataset=self.dataset_name,
                split="full",
                source_file=str(self.data_file),
                chunk_index=chunk_index,
            )
            chunk_index += 1
