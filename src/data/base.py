"""Base classes for memory-efficient dataset loading."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd


@dataclass
class ChunkInfo:
    dataset: str
    split: str
    source_file: str
    chunk_index: int = 0
    partition: Optional[str] = None
    extra: dict = field(default_factory=dict)


class BaseDatasetLoader(ABC):
    """Chunked loader preserving split/partition metadata."""

    dataset_name: str = "unknown"

    def __init__(self, root_dir: Path, chunk_size: int = 100_000):
        self.root_dir = Path(root_dir)
        self.chunk_size = chunk_size

    @abstractmethod
    def list_sources(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def iter_chunks(
        self,
        split: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> Iterator[tuple[pd.DataFrame, ChunkInfo]]:
        raise NotImplementedError

    def load_sample(
        self,
        n_rows: int = 1000,
        split: Optional[str] = None,
        **kwargs,
    ) -> tuple[pd.DataFrame, ChunkInfo]:
        collected = []
        meta: Optional[ChunkInfo] = None
        remaining = n_rows
        for chunk, info in self.iter_chunks(split=split, max_rows=n_rows, **kwargs):
            take = min(remaining, len(chunk))
            collected.append(chunk.iloc[:take])
            meta = info
            remaining -= take
            if remaining <= 0:
                break
        if not collected:
            raise ValueError(f"No data loaded for {self.dataset_name}")
        return pd.concat(collected, ignore_index=True), meta  # type: ignore[arg-type]

    def count_rows(self, split: Optional[str] = None) -> int:
        total = 0
        for chunk, _ in self.iter_chunks(split=split):
            total += len(chunk)
        return total
