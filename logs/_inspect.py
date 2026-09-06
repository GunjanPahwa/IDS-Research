import pandas as pd
from pathlib import Path
base = Path("data/processed")
for ds in ["cic-ids2017","cse-cic-ids2018","unsw-nb15","uwf_zeekdata"]:
    df = pd.read_csv(base / f"{ds}_common7_train.csv", nrows=0)
    vc = pd.read_csv(base / f"{ds}_common7_train.csv", usecols=["label"])["label"].value_counts().sort_index()
    n = sum(1 for _ in open(base / f"{ds}_common7_train.csv","rb")) - 1
    print(f"{ds}: cols={list(df.columns)}, n_train={n:,}, dist={vc.to_dict()}")
