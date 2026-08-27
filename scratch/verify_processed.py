import os
import sys
import pandas as pd
import numpy as np

ROOT = r"C:\Users\HP\OneDrive\Desktop\Minor Project"
sys.path.insert(0, ROOT)

from src.preprocessing.pipeline import NIDSPreprocessor
from src.data.registry import get_loader

def test_pipeline_reporting():
    mapping_csv = os.path.join(ROOT, "data", "label_mapping.csv")
    datasets = ["KDD99", "NSL-KDD", "UNSW-NB15", "CIC-IDS2017", "CSE-CIC-IDS2018", "UWF ZeekData"]
    
    print("=== Pipeline Verification Report ===")
    for ds in datasets:
        print(f"\n--- {ds} ---")
        try:
            loader = get_loader(ds, ROOT)
            df, meta = loader.load_sample(n_rows=1000)
            
            pre = NIDSPreprocessor(
                dataset_name=ds,
                preprocessing_mode="within-dataset",
                feature_space="native",
                label_mapping_csv=mapping_csv
            )
            
            # 1. Test fit
            fit_ok = False
            try:
                pre.fit(df)
                fit_ok = True
                print("  fit() status: SUCCESS")
            except Exception as e:
                print(f"  fit() status: FAILED ({type(e).__name__}: {e})")
                
            if not fit_ok:
                continue
                
            # 2. Test transform
            try:
                X, y_bin, y_mul = pre.transform(df)
                print("  transform() status: SUCCESS")
                print(f"  X.shape: {X.shape}")
                print(f"  Binary target shape: {y_bin.shape if y_bin is not None else None}")
                print(f"  Multiclass target shape: {y_mul.shape if y_mul is not None else None}")
                
                # Feature names
                feat_names = pre.get_feature_names()
                print(f"  Number of generated feature names: {len(feat_names)}")
                
                # Check NaNs and Infs in X
                nan_count = np.isnan(X).sum()
                inf_count = np.isinf(X).sum()
                print(f"  X contains NaN: {nan_count > 0} (count: {nan_count})")
                print(f"  X contains Inf: {inf_count > 0} (count: {inf_count})")
                
                # Assertions for dimensions
                assert X.shape[1] == len(feat_names), f"Feature dim mismatch: X has {X.shape[1]}, feature names has {len(feat_names)}"
                
            except Exception as e:
                print(f"  transform() status: FAILED ({type(e).__name__}: {e})")
                
        except Exception as e:
            print(f"  Setup FAILED ({type(e).__name__}: {e})")

if __name__ == "__main__":
    test_pipeline_reporting()
