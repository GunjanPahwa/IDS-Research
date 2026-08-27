"""Smoke test for dataset splitting helpers."""
import os
import sys
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(r"C:\Users\HP\OneDrive\Desktop\Minor Project")
sys.path.insert(0, str(ROOT))

from scratch.run_full_preprocessing import split_kdd99, split_cic_ids2017, split_cse_cic_ids2018, split_uwf_zeekdata

def test_smoke():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        print(f"Using temp dir: {tmp_path}")
        
        # 1. Test split_kdd99
        print("Testing split_kdd99 smoke...")
        mock_kdd = tmp_path / "mock_kdd.data"
        # 100 rows, 42 columns, column 41 is label
        df_kdd = pd.DataFrame(np.random.randn(100, 41))
        df_kdd[41] = ["normal." if i % 2 == 0 else "neptune." for i in range(100)]
        df_kdd.to_csv(mock_kdd, index=False, header=False)
        
        train_kdd = tmp_path / "kdd_train.csv"
        test_kdd = tmp_path / "kdd_test.csv"
        split_kdd99(mock_kdd, train_kdd, test_kdd)
        
        assert train_kdd.exists()
        assert test_kdd.exists()
        print("  split_kdd99 PASS")
        
        # 2. Test split_cic_ids2017
        print("Testing split_cic_ids2017 smoke...")
        mock_cic_dir = tmp_path / "CIC2017"
        mock_cic_dir.mkdir()
        df_cic = pd.DataFrame(np.random.randn(100, 5), columns=["Flow Duration", "Protocol", "src_bytes", "dst_bytes", "Label"])
        df_cic["Label"] = ["BENIGN" if i % 2 == 0 else "DDoS" for i in range(100)]
        df_cic.to_csv(mock_cic_dir / "day1.csv", index=False)
        
        train_cic = tmp_path / "cic_train.csv"
        test_cic = tmp_path / "cic_test.csv"
        split_cic_ids2017(mock_cic_dir, train_cic, test_cic)
        
        assert train_cic.exists()
        assert test_cic.exists()
        print("  split_cic_ids2017 PASS")
        
        # 3. Test split_cse_cic_ids2018
        print("Testing split_cse_cic_ids2018 smoke...")
        mock_cic2018_dir = tmp_path / "CIC2018"
        mock_cic2018_dir.mkdir()
        df_cic18 = pd.DataFrame(np.random.randn(100, 5), columns=["Flow Duration", "Protocol", "src_bytes", "dst_bytes", "Label"])
        df_cic18["Label"] = ["Benign" if i % 2 == 0 else "Bot" for i in range(100)]
        
        # Save as parquet with multiple row groups to test row group iteration
        table = pa.Table.from_pandas(df_cic18)
        pq.write_table(table, mock_cic2018_dir / "day1.parquet", row_group_size=20)
        
        train_cic18 = tmp_path / "cic18_train.parquet"
        test_cic18 = tmp_path / "cic18_test.parquet"
        split_cse_cic_ids2018(mock_cic2018_dir, train_cic18, test_cic18)
        
        assert train_cic18.exists()
        assert test_cic18.exists()
        print("  split_cse_cic_ids2018 PASS")
        
        # 4. Test split_uwf_zeekdata
        print("Testing split_uwf_zeekdata smoke...")
        mock_uwf_dir = tmp_path / "UWF"
        mock_uwf_dir.mkdir()
        df_uwf = pd.DataFrame(np.random.randn(100, 5), columns=["duration", "proto", "src_bytes", "dst_bytes", "label_binary"])
        df_uwf["label_binary"] = ["False" if i % 2 == 0 else "True" for i in range(100)]
        df_uwf.to_parquet(mock_uwf_dir / "part1.parquet")
        
        train_uwf = tmp_path / "uwf_train.parquet"
        test_uwf = tmp_path / "uwf_test.parquet"
        split_uwf_zeekdata(mock_uwf_dir, train_uwf, test_uwf)
        
        assert train_uwf.exists()
        assert test_uwf.exists()
        print("  split_uwf_zeekdata PASS")

if __name__ == "__main__":
    test_smoke()
    print("ALL SPLIT SMOKE TESTS PASSED SUCCESSFULLY!")
