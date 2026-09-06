from pathlib import Path
base = Path("data/processed")
for fs in ["native","common5","common7"]:
    tr = base / f"uwf_zeekdata_{fs}_train.csv"
    te = base / f"uwf_zeekdata_{fs}_test.csv"
    nt = sum(1 for _ in open(tr,"rb")) - 1
    nv = sum(1 for _ in open(te,"rb")) - 1
    print(f"{fs}: train={nt:,}  test={nv:,}")
