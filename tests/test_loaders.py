"""Verification tests for dataset loaders."""

from __future__ import annotations

from pathlib import Path
import unittest

from src.data.registry import get_loader, list_datasets

ROOT = Path(__file__).resolve().parents[1]


class TestDatasetLoaders(unittest.TestCase):

    def test_loader_sample_non_empty(self):
        for dataset_name in list_datasets():
            with self.subTest(dataset_name=dataset_name):
                loader = get_loader(dataset_name, ROOT)
                df, meta = loader.load_sample(n_rows=50)
                self.assertGreater(len(df), 0)
                self.assertEqual(meta.dataset, dataset_name)

    def test_uwf_has_seven_partitions(self):
        loader = get_loader("UWF ZeekData", ROOT)
        self.assertEqual(len(loader.list_partitions()), 7)

    def test_uwf_all_partitions_sample(self):
        loader = get_loader("UWF ZeekData", ROOT)
        for partition in loader.list_partitions():
            with self.subTest(partition=partition):
                df, meta = loader.load_sample(n_rows=20, partition=partition)
                self.assertGreater(len(df), 0)
                self.assertEqual(meta.partition, partition)
                self.assertIn("label_binary", df.columns)

    def test_nsl_kdd_splits(self):
        loader = get_loader("NSL-KDD", ROOT)
        for split in ["train", "test", "test-21"]:
            with self.subTest(split=split):
                df, meta = loader.load_sample(n_rows=20, split=split)
                self.assertEqual(meta.split, split)
                self.assertEqual(df.shape[1], 43)

    def test_unsw_predefined_splits(self):
        loader = get_loader("UNSW-NB15", ROOT)
        train, _ = loader.load_sample(n_rows=20, split="train")
        test, _ = loader.load_sample(n_rows=20, split="test")
        self.assertIn("attack_cat", train.columns)
        self.assertIn("label", test.columns)


if __name__ == "__main__":
    unittest.main()
