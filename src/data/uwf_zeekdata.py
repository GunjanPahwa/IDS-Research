"""UWF ZeekData loader — all parquet partitions."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

import pandas as pd
import pyarrow.parquet as pq

from src.data.base import BaseDatasetLoader, ChunkInfo


class UWFZeekDataLoader(BaseDatasetLoader):
    dataset_name = "UWF ZeekData"

    def __init__(self, root_dir: Path, chunk_size: int = 100_000):
        super().__init__(root_dir, chunk_size)
        self.data_dir = self.root_dir / "UWF ZeekData"

    def list_sources(self) -> list[str]:
        return sorted(str(p) for p in self.data_dir.glob("*.parquet"))

    def list_partitions(self) -> list[str]:
        return [Path(p).name for p in self.list_sources()]

    def iter_chunks(
        self,
        split: Optional[str] = None,
        max_rows: Optional[int] = None,
        partition: Optional[str] = None,
    ) -> Iterator[tuple[pd.DataFrame, ChunkInfo]]:
        files = self.list_sources()
        if partition:
            files = [f for f in files if Path(f).name == partition or partition in f]
        if split == "attack":
            files = [f for f in files if self._partition_has_attacks(f)]
        elif split == "benign":
            files = [f for f in files if not self._partition_has_attacks(f)]
        if not files:
            raise ValueError(f"No UWF partitions matched: split={split}, partition={partition}")

        emitted = 0
        for file_path in files:
            pf = pq.ParquetFile(file_path)
            chunk_index = 0
            for rg_idx in range(pf.num_row_groups):
                chunk = pf.read_row_group(rg_idx).to_pandas()
                if max_rows is not None:
                    remaining = max_rows - emitted
                    if remaining <= 0:
                        return
                    chunk = chunk.iloc[:remaining]
                emitted += len(chunk)
                yield chunk, ChunkInfo(
                    dataset=self.dataset_name,
                    split=split or "full",
                    source_file=file_path,
                    chunk_index=chunk_index,
                    partition=Path(file_path).name,
                    extra={"row_group": rg_idx},
                )
                chunk_index += 1

    @staticmethod
    def _partition_has_attacks(file_path: str) -> bool:
        pf = pq.ParquetFile(file_path)
        tbl = pf.read_row_group(0, columns=["label_binary"])
        values = set(str(v) for v in tbl.column("label_binary").to_pylist()[:5000])
        return "True" in values or "Duplicate" in values
