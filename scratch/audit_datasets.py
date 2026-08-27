"""Temporary dataset audit script - read-only inspection."""
import os
import sys
import pyarrow.parquet as pq
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inspect_csv_header(path, n=1):
    df = pd.read_csv(path, nrows=n, encoding="latin-1")
    return [str(c).strip() for c in df.columns]


def main():
    print("=== KDD99 ===")
    kdd = os.path.join(ROOT, "KDD99", "kddcup.data")
    print(f"File size MB: {os.path.getsize(kdd) / 1e6:.2f}")
    df = pd.read_csv(kdd, nrows=2, header=None, encoding="latin-1")
    print(f"cols={df.shape[1]}, first5={list(df.iloc[0, :5])}, last3={list(df.iloc[0, -3:])}")

    print("\n=== NSL-KDD ===")
    for fn in ["KDDTrain+.txt", "KDDTest+.txt", "KDDTest-21.txt"]:
        p = os.path.join(ROOT, "NSL KDD", fn)
        df = pd.read_csv(p, nrows=2, header=None, encoding="latin-1")
        print(f"{fn} cols={df.shape[1]} last3={list(df.iloc[0, -3:])}")

    print("\n=== UNSW-NB15 ===")
    for fn in ["UNSW_NB15_training-set.csv", "UNSW_NB15_testing-set.csv"]:
        p = os.path.join(ROOT, "NB15", fn)
        cols = inspect_csv_header(p)
        print(f"{fn} ncols={len(cols)} label_cols={[c for c in cols if 'label' in c.lower() or 'attack' in c.lower()]}")
        df = pd.read_csv(p, usecols=["attack_cat", "label"], encoding="latin-1")
        print(f"  attack_cat: {sorted(df['attack_cat'].unique())}")
        print(f"  label: {sorted(df['label'].unique())}")

    print("\n=== CIC-IDS2017 ===")
    cic17_dir = os.path.join(ROOT, "CIC2017", "MachineLearningCVE")
    all_labels_17 = set()
    for fn in sorted(os.listdir(cic17_dir)):
        if not fn.endswith(".csv"):
            continue
        p = os.path.join(cic17_dir, fn)
        cols = inspect_csv_header(p)
        has_proto = any("protocol" in c.lower() for c in cols)
        has_dest = any("destination port" in c.lower() for c in cols)
        df = pd.read_csv(p, encoding="latin-1", usecols=lambda c: "label" in str(c).lower())
        df.columns = [str(c).strip() for c in df.columns]
        labels = sorted(df.iloc[:, 0].astype(str).str.strip().unique())
        all_labels_17.update(labels)
        print(f"{fn[:45]:45} proto={has_proto} dest_port={has_dest} labels={labels}")
    print(f"ALL CIC2017 unique labels ({len(all_labels_17)}): {sorted(all_labels_17)}")
    for lbl in sorted(all_labels_17):
        print(f"  repr: {repr(lbl)}")

    print("\n=== CSE-CIC-IDS2018 ===")
    all_labels_18 = set()
    for fn in sorted(os.listdir(os.path.join(ROOT, "CIC2018"))):
        if not fn.endswith(".parquet"):
            continue
        p = os.path.join(ROOT, "CIC2018", fn)
        pf = pq.ParquetFile(p)
        cols = pf.schema_arrow.names
        has_proto = any("protocol" in str(c).lower() for c in cols)
        port_cols = [c for c in cols if "port" in str(c).lower()]
        tbl = pf.read(columns=["Label"])
        labels = sorted(set(str(x) for x in tbl.column("Label").to_pylist()))
        all_labels_18.update(labels)
        print(f"{fn[:45]:45} rows={pf.metadata.num_rows} proto={has_proto} port_cols={port_cols} labels={labels}")
    print(f"ALL CIC2018 unique labels: {sorted(all_labels_18)}")
    for lbl in sorted(all_labels_18):
        if "infil" in lbl.lower():
            print(f"  infiltration repr: {repr(lbl)}")

    print("\n=== UWF ZeekData ALL FILES ===")
    uwf_dir = os.path.join(ROOT, "UWF ZeekData")
    total_rows = 0
    agg_binary = {}
    agg_tactic = {}
    for fn in sorted(os.listdir(uwf_dir)):
        if not fn.endswith(".parquet"):
            continue
        p = os.path.join(ROOT, "UWF ZeekData", fn)
        pf = pq.ParquetFile(p)
        cols = pf.schema_arrow.names
        rows = pf.metadata.num_rows
        total_rows += rows
        print(f"\nFile: {fn}")
        print(f"  rows={rows}, cols={len(cols)}")
        print(f"  columns: {cols}")
        label_cols = [c for c in cols if c in ["label_binary", "tactic", "technique", "cve"]]
        tbl = pf.read(columns=label_cols)
        pdf = tbl.to_pandas()
        for lc in ["label_binary", "tactic", "technique"]:
            if lc not in pdf.columns:
                continue
            vc = pdf[lc].value_counts(dropna=False)
            print(f"  {lc}:")
            for k, v in vc.items():
                print(f"    {repr(k)}: {v}")
                if lc == "label_binary":
                    agg_binary[k] = agg_binary.get(k, 0) + v
                elif lc == "tactic":
                    agg_tactic[k] = agg_tactic.get(k, 0) + v

    print(f"\nUWF TOTAL rows across all files: {total_rows}")
    print(f"UWF aggregate label_binary: {agg_binary}")
    print(f"UWF aggregate tactic: {agg_tactic}")

    print("\n=== PROCESSED FILES ===")
    proc_dir = os.path.join(ROOT, "data", "processed")
    if os.path.isdir(proc_dir):
        for fn in sorted(os.listdir(proc_dir)):
            p = os.path.join(proc_dir, fn)
            size = os.path.getsize(p)
            df = pd.read_csv(p, nrows=3)
            print(f"{fn} size={size} cols={list(df.columns)} shape_sample={df.shape}")

    print("\n=== PIPELINE SMOKE TEST ===")
    sys.path.insert(0, ROOT)
    from src.preprocessing.pipeline import NIDSPreprocessor
    from src.preprocessing.mappings import LEAKAGE_COLUMNS

    print("LEAKAGE_COLUMNS used in pipeline.py:", "NO - only defined in mappings.py")
    # Test column mapping on sample
    sample = pd.read_csv(os.path.join(ROOT, "NB15", "UNSW_NB15_training-set.csv"), nrows=100, encoding="latin-1")
    pre = NIDSPreprocessor("UNSW-NB15", feature_space="Common-7", label_mapping_csv=os.path.join(ROOT, "data", "label_mapping.csv"))
    pre.fit(sample)
    X, y_bin, y_mul = pre.transform(sample)
    print(f"UNSW-NB15 smoke: X shape={X.shape}, y_bin unique={set(y_bin) if y_bin is not None else None}")
    print(f"Feature names count: {len(pre.get_feature_names())}")

    # CIC2018 column mapping test
    p18 = os.path.join(ROOT, "CIC2018", "Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet")
    sample18 = pq.read_table(p18).slice(0, 100).to_pandas()
    pre18 = NIDSPreprocessor("CSE-CIC-IDS2018", feature_space="Common-7", label_mapping_csv=os.path.join(ROOT, "data", "label_mapping.csv"))
    try:
        pre18.fit(sample18)
        X18, y18_bin, y18_mul = pre18.transform(sample18)
        print(f"CIC2018 smoke: X shape={X18.shape}, OK")
    except Exception as e:
        print(f"CIC2018 smoke FAILED: {e}")

    # KDD99 headerless test
    kdd_sample = pd.read_csv(kdd, nrows=100, header=None, encoding="latin-1")
    pre_kdd = NIDSPreprocessor("KDD99", feature_space="Common-5", label_mapping_csv=os.path.join(ROOT, "data", "label_mapping.csv"))
    try:
        pre_kdd.fit(kdd_sample)
        Xk, yk_bin, yk_mul = pre_kdd.transform(kdd_sample)
        print(f"KDD99 smoke: X shape={Xk.shape}, y_bin unique={set(yk_bin) if yk_bin is not None else None}")
    except Exception as e:
        print(f"KDD99 smoke FAILED: {e}")

    # CIC2017 web attack label mapping
    web_path = os.path.join(cic17_dir, "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv")
    web_sample = pd.read_csv(web_path, nrows=500, encoding="latin-1")
    web_sample.columns = [str(c).strip() for c in web_sample.columns]
    lbls = web_sample["Label"].unique()
    print(f"CIC2017 web attack raw labels: {[repr(l) for l in lbls]}")
    ls = __import__("src.preprocessing.mappings", fromlist=["LabelStandardizer"]).LabelStandardizer(os.path.join(ROOT, "data", "label_mapping.csv"))
    for l in lbls:
        print(f"  {repr(l)} -> binary {ls.standardize(l, 'CIC-IDS2017')}, lookup hit={( 'CIC-IDS2017', str(l).strip().rstrip('.') ) in ls._processor.lookup}")


if __name__ == "__main__":
    main()
