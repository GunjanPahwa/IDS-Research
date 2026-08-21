"""Verification tests for dataset loaders."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.data.registry import get_loader, list_datasets

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("dataset_name", list_datasets())
def test_loader_sample_non_empty(dataset_name):
    loader = get_loader(dataset_name, ROOT)
    df, meta = loader.load_sample(n_rows=50)
    assert len(df) > 0
    assert meta.dataset == dataset_name


def test_uwf_has_seven_partitions():
    loader = get_loader("UWF ZeekData", ROOT)
    assert len(loader.list_partitions()) == 7


def test_uwf_all_partitions_sample():
    loader = get_loader("UWF ZeekData", ROOT)
    for partition in loader.list_partitions():
        df, meta = loader.load_sample(n_rows=20, partition=partition)
        assert len(df) > 0
        assert meta.partition == partition
        assert "label_binary" in df.columns


def test_nsl_kdd_splits():
    loader = get_loader("NSL-KDD", ROOT)
    for split in ["train", "test", "test-21"]:
        df, meta = loader.load_sample(n_rows=20, split=split)
        assert meta.split == split
        assert df.shape[1] == 43


def test_unsw_predefined_splits():
    loader = get_loader("UNSW-NB15", ROOT)
    train, _ = loader.load_sample(n_rows=20, split="train")
    test, _ = loader.load_sample(n_rows=20, split="test")
    assert "attack_cat" in train.columns
    assert "label" in test.columns
