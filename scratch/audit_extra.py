import os, sys, pyarrow.parquet as pq, pandas as pd
ROOT = r"C:\Users\HP\OneDrive\Desktop\Minor Project"
sys.path.insert(0, ROOT)

p = os.path.join(ROOT, "CIC2018", "Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet")
print("CIC2018 columns:", pq.ParquetFile(p).schema_arrow.names)

p = os.path.join(ROOT, "UWF ZeekData", "part-00000-071774ae-97f3-4f31-9700-8bfcdf41305a-c000.snappy.parquet")
tbl = pq.read_table(p, columns=["label_tactic", "label_technique", "label_binary", "label_cve"])
pdf = tbl.to_pandas()
print("\nUWF attack file label_tactic top 15:")
print(pdf["label_tactic"].value_counts(dropna=False).head(15))
print("\nUWF attack file label_technique top 15:")
print(pdf["label_technique"].value_counts(dropna=False).head(15))

from src.preprocessing.mappings import LabelStandardizer
ls = LabelStandardizer(os.path.join(ROOT, "data", "label_mapping.csv"))
for v in ["True", "False", "Duplicate", "normal"]:
    out = ls.standardize(v, "UWF ZeekData")
    print(f"UWF label {v!r} -> {out}")

web = os.path.join(ROOT, "CIC2017", "MachineLearningCVE", "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv")
df = pd.read_csv(web, usecols=lambda c: "label" in c.lower(), encoding="latin-1")
df.columns = [c.strip() for c in df.columns]
for l in df["Label"].unique():
    if "Web" in str(l):
        print(f"Web label repr: {l!r}")
        print(f"  codepoints: {[hex(ord(c)) for c in str(l)]}")
        key = ("CIC-IDS2017", str(l).strip().rstrip("."))
        print(f"  lookup hit: {key in ls._processor.lookup}, mapped binary: {ls.standardize(l, 'CIC-IDS2017')}")

proc = os.path.join(ROOT, "data", "processed", "uwf_zeekdata_common5_train.csv")
dfp = pd.read_csv(proc)
print("\nProcessed UWF train label counts:", dfp["label"].value_counts().to_dict(), "rows", len(dfp))

from src.preprocessing.pipeline import NIDSPreprocessor, Common7IncompatibleError
kdd = pd.read_csv(os.path.join(ROOT, "KDD99", "kddcup.data"), nrows=50, header=None, encoding="latin-1")
pre7 = NIDSPreprocessor("KDD99", feature_space="Common-5", label_mapping_csv=os.path.join(ROOT, "data", "label_mapping.csv"))
pre7.fit(kdd)
X, y_bin, y_mul = pre7.transform(kdd)
print(f"KDD99 Common-5 X shape={X.shape}")
df_std = pre7._standardize_columns(kdd)
print("KDD99 mapped cols:", [c for c in ["src_packets", "dst_packets", "duration", "protocol", "service"] if c in df_std.columns])

# UWF pipeline smoke
uwf = pq.read_table(p).slice(0, 200).to_pandas()
pre_uwf = NIDSPreprocessor("UWF ZeekData", feature_space="Common-7", label_mapping_csv=os.path.join(ROOT, "data", "label_mapping.csv"))
try:
    pre_uwf.fit(uwf)
    Xu, yu_bin, yu_mul = pre_uwf.transform(uwf)
    print(f"UWF smoke X={Xu.shape}, y_bin unique={set(yu_bin) if yu_bin is not None else None}")
except Exception as e:
    print(f"UWF smoke FAILED: {e}")

# CIC2018 Infilteration mapping
infil = os.path.join(ROOT, "CIC2018", "Infil1-Wednesday-28-02-2018_TrafficForML_CICFlowMeter.parquet")
lbl = pq.read_table(infil, columns=["Label"]).to_pandas()["Label"].unique()
for l in lbl:
    print(f"CIC2018 label {l!r} -> binary {ls.standardize(l, 'CSE-CIC-IDS2018')}, lookup={( 'CSE-CIC-IDS2018', str(l).strip().rstrip('.') ) in ls._processor.lookup}")
