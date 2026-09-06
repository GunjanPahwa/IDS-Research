import pandas as pd, numpy as np
from pathlib import Path
base = Path("data/processed")
for fs in ["native","common5","common7"]:
    tr = pd.read_csv(base / f"uwf_zeekdata_{fs}_train.csv", nrows=5000)
    feat = tr.drop(columns=["label"], errors="ignore")
    nan_c = feat.isna().sum().sum()
    inf_c = np.isinf(feat.select_dtypes("number")).sum().sum()
    dist = tr["label"].value_counts().to_dict()
    print(f"{fs}: NaN={nan_c} Inf={inf_c}  classes={dist}")
