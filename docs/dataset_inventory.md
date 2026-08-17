# Dataset Inventory

This document provides a comprehensive inventory of the raw network intrusion datasets available in this project.

## Summary Table

| Dataset | File | Format | Size (MB) | Rows | Columns | Target Column | Classes | Benign Label(s) | Missing | Duplicates | Leakage Columns |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| KDD99 | kddcup.data | CSV | 708.18 | 4,898,431 | 42 | label | 23 | normal | 0 | 3,823,439 | None |
| NSL-KDD (KDDTrain+.txt) | KDDTrain+.txt | Text/CSV | 18.22 | 125,973 | 43 | label | 23 | normal | 0 | 0 | difficulty_score |
| NSL-KDD (KDDTest+.txt) | KDDTest+.txt | Text/CSV | 3.28 | 22,544 | 43 | label | 38 | normal | 0 | 0 | difficulty_score |
| NSL-KDD (KDDTest-21.txt) | KDDTest-21.txt | Text/CSV | 1.73 | 11,850 | 43 | label | 38 | normal | 0 | 0 | difficulty_score |
| UNSW-NB15 (UNSW_NB15_training-set.csv) | UNSW_NB15_training-set.csv | CSV | 30.80 | 175,341 | 45 | attack_cat (multiclass) & label (binary) | 10 | Normal | 0 | 0 | id |
| UNSW-NB15 (UNSW_NB15_testing-set.csv) | UNSW_NB15_testing-set.csv | CSV | 14.67 | 82,332 | 45 | attack_cat (multiclass) & label (binary) | 10 | Normal | 0 | 0 | id |
| CIC-IDS2017 (Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv) | Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv | CSV | 73.55 | 225,745 | 79 | Label | 2 | BENIGN | 4 | 2,633 | None |
| CIC-IDS2017 (Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv) | Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv | CSV | 73.34 | 286,467 | 79 | Label | 2 | BENIGN | 15 | 72,353 | None |
| CIC-IDS2017 (Friday-WorkingHours-Morning.pcap_ISCX.csv) | Friday-WorkingHours-Morning.pcap_ISCX.csv | CSV | 55.62 | 191,033 | 79 | Label | 2 | BENIGN | 28 | 6,888 | None |
| CIC-IDS2017 (Monday-WorkingHours.pcap_ISCX.csv) | Monday-WorkingHours.pcap_ISCX.csv | CSV | 168.73 | 529,918 | 79 | Label | 1 | BENIGN | 64 | 26,935 | None |
| CIC-IDS2017 (Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv) | Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv | CSV | 79.25 | 288,602 | 79 | Label | 2 | BENIGN | 18 | 35,630 | None |
| CIC-IDS2017 (Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv) | Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv | CSV | 49.61 | 170,366 | 79 | Label | 4 | BENIGN | 20 | 6,066 | None |
| CIC-IDS2017 (Tuesday-WorkingHours.pcap_ISCX.csv) | Tuesday-WorkingHours.pcap_ISCX.csv | CSV | 128.82 | 445,909 | 79 | Label | 3 | BENIGN | 201 | 24,065 | None |
| CIC-IDS2017 (Wednesday-workingHours.pcap_ISCX.csv) | Wednesday-workingHours.pcap_ISCX.csv | CSV | 214.74 | 692,703 | 79 | Label | 6 | BENIGN | 1,008 | 81,909 | None |
| CSE-CIC-IDS2018 (Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet) | Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 79.61 | 771,587 | 78 | Label | 2 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (Bruteforce-Wednesday-14-02-2018_TrafficForML_CICFlowMeter.parquet) | Bruteforce-Wednesday-14-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 72.89 | 619,346 | 78 | Label | 3 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (DDoS1-Tuesday-20-02-2018_TrafficForML_CICFlowMeter.parquet) | DDoS1-Tuesday-20-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 85.35 | 954,846 | 78 | Label | 2 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (DDoS2-Wednesday-21-02-2018_TrafficForML_CICFlowMeter.parquet) | DDoS2-Wednesday-21-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 31.90 | 561,396 | 78 | Label | 3 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (DoS1-Thursday-15-02-2018_TrafficForML_CICFlowMeter.parquet) | DoS1-Thursday-15-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 94.05 | 794,812 | 78 | Label | 3 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (DoS2-Friday-16-02-2018_TrafficForML_CICFlowMeter.parquet) | DoS2-Friday-16-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 55.31 | 591,873 | 78 | Label | 3 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (Infil1-Wednesday-28-02-2018_TrafficForML_CICFlowMeter.parquet) | Infil1-Wednesday-28-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 48.59 | 456,873 | 78 | Label | 2 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (Infil2-Thursday-01-03-2018_TrafficForML_CICFlowMeter.parquet) | Infil2-Thursday-01-03-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 27.93 | 249,170 | 78 | Label | 2 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (Web1-Thursday-22-02-2018_TrafficForML_CICFlowMeter.parquet) | Web1-Thursday-22-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 99.14 | 830,224 | 78 | Label | 4 | Benign | 0 | 0 | None |
| CSE-CIC-IDS2018 (Web2-Friday-23-02-2018_TrafficForML_CICFlowMeter.parquet) | Web2-Friday-23-02-2018_TrafficForML_CICFlowMeter.parquet | Parquet | 96.69 | 829,405 | 78 | Label | 4 | Benign | 0 | 0 | None |
| UWF ZeekData | part-00000-69700ccb-c1c1-4763-beb7-cd0f1a61c268-c000.snappy.parquet | Parquet | 31.63 | 454,846 | 26 | label_binary (also tactic, technique, cve) | 1 | 0 | 97,241 | 0 | community_id, src_ip_zeek, src_port_zeek, dest_ip_zeek, dest_port_zeek, orig_ip_bytes, orig_pkts, resp_ip_bytes, resp_pkts, ts, uid |

---

## Detailed Dataset Profiles

### KDD99
- **Filename**: `kddcup.data`
- **Format**: CSV
- **File Size**: 708.18 MB
- **Record Count**: 4,898,431
- **Feature Count**: 42
- **Target Column(s)**: `label`
- **Missing Values**: 0
- **Duplicate Rows**: 3,823,439
- **Categorical Features (3):** `['protocol_type', 'service', 'flag']`
- **Numerical Features (38):** `['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Classic dataset. Contains trailing period in labels.
  - Missing column headers in raw file.
  - Extremely high number of duplicates (representing redundant ICMP/TCP flood packets).

### NSL-KDD (KDDTrain+.txt)
- **Filename**: `KDDTrain+.txt`
- **Format**: Text/CSV
- **File Size**: 18.22 MB
- **Record Count**: 125,973
- **Feature Count**: 43
- **Target Column(s)**: `label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (3):** `['protocol_type', 'service', 'flag']`
- **Numerical Features (38):** `['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells']`...
- **Leakage-prone Columns:** `['difficulty_score']`
- **Notes**:
  - Cleaned version of KDD99. Removes duplicates.
  - Contains an extra column at the end: `difficulty_score`, which is a metadata feature from KDD99 filtering. This must be excluded as it is a major leakage column.

### NSL-KDD (KDDTest+.txt)
- **Filename**: `KDDTest+.txt`
- **Format**: Text/CSV
- **File Size**: 3.28 MB
- **Record Count**: 22,544
- **Feature Count**: 43
- **Target Column(s)**: `label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (3):** `['protocol_type', 'service', 'flag']`
- **Numerical Features (38):** `['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells']`...
- **Leakage-prone Columns:** `['difficulty_score']`
- **Notes**:
  - Cleaned version of KDD99. Removes duplicates.
  - Contains an extra column at the end: `difficulty_score`, which is a metadata feature from KDD99 filtering. This must be excluded as it is a major leakage column.

### NSL-KDD (KDDTest-21.txt)
- **Filename**: `KDDTest-21.txt`
- **Format**: Text/CSV
- **File Size**: 1.73 MB
- **Record Count**: 11,850
- **Feature Count**: 43
- **Target Column(s)**: `label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (3):** `['protocol_type', 'service', 'flag']`
- **Numerical Features (38):** `['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells']`...
- **Leakage-prone Columns:** `['difficulty_score']`
- **Notes**:
  - Cleaned version of KDD99. Removes duplicates.
  - Contains an extra column at the end: `difficulty_score`, which is a metadata feature from KDD99 filtering. This must be excluded as it is a major leakage column.

### UNSW-NB15 (UNSW_NB15_training-set.csv)
- **Filename**: `UNSW_NB15_training-set.csv`
- **Format**: CSV
- **File Size**: 30.80 MB
- **Record Count**: 175,341
- **Feature Count**: 45
- **Target Column(s)**: `attack_cat (multiclass) & label (binary)`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (3):** `['proto', 'service', 'state']`
- **Numerical Features (39):** `['dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt', 'sjit']`...
- **Leakage-prone Columns:** `['id']`
- **Notes**:
  - Contains both binary target (`label`) and multiclass target (`attack_cat`).
  - Has an index column `id` which must be removed before training to prevent data leakage.

### UNSW-NB15 (UNSW_NB15_testing-set.csv)
- **Filename**: `UNSW_NB15_testing-set.csv`
- **Format**: CSV
- **File Size**: 14.67 MB
- **Record Count**: 82,332
- **Feature Count**: 45
- **Target Column(s)**: `attack_cat (multiclass) & label (binary)`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (3):** `['proto', 'service', 'state']`
- **Numerical Features (39):** `['dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt', 'sjit']`...
- **Leakage-prone Columns:** `['id']`
- **Notes**:
  - Contains both binary target (`label`) and multiclass target (`attack_cat`).
  - Has an index column `id` which must be removed before training to prevent data leakage.

### CIC-IDS2017 (Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv)
- **Filename**: `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 73.55 MB
- **Record Count**: 225,745
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 4
- **Duplicate Rows**: 2,633
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv)
- **Filename**: `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 73.34 MB
- **Record Count**: 286,467
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 15
- **Duplicate Rows**: 72,353
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Friday-WorkingHours-Morning.pcap_ISCX.csv)
- **Filename**: `Friday-WorkingHours-Morning.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 55.62 MB
- **Record Count**: 191,033
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 28
- **Duplicate Rows**: 6,888
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Monday-WorkingHours.pcap_ISCX.csv)
- **Filename**: `Monday-WorkingHours.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 168.73 MB
- **Record Count**: 529,918
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 64
- **Duplicate Rows**: 26,935
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv)
- **Filename**: `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 79.25 MB
- **Record Count**: 288,602
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 18
- **Duplicate Rows**: 35,630
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv)
- **Filename**: `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 49.61 MB
- **Record Count**: 170,366
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 20
- **Duplicate Rows**: 6,066
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Tuesday-WorkingHours.pcap_ISCX.csv)
- **Filename**: `Tuesday-WorkingHours.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 128.82 MB
- **Record Count**: 445,909
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 201
- **Duplicate Rows**: 24,065
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CIC-IDS2017 (Wednesday-workingHours.pcap_ISCX.csv)
- **Filename**: `Wednesday-workingHours.pcap_ISCX.csv`
- **Format**: CSV
- **File Size**: 214.74 MB
- **Record Count**: 692,703
- **Feature Count**: 79
- **Target Column(s)**: `Label`
- **Missing Values**: 1,008
- **Duplicate Rows**: 81,909
- **Categorical Features (0):** `[]`
- **Numerical Features (78):** `['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Contains trailing/leading spaces in column headers (e.g. `' Label'`).
  - Known to contain NaN/Inf values (specifically in `'Flow Bytes/s'` and `'Flow Packets/s'').

### CSE-CIC-IDS2018 (Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `Botnet-Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 79.61 MB
- **Record Count**: 771,587
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (49):** `['Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (Bruteforce-Wednesday-14-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `Bruteforce-Wednesday-14-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 72.89 MB
- **Record Count**: 619,346
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (47):** `['Flow Duration', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Max', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (DDoS1-Tuesday-20-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `DDoS1-Tuesday-20-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 85.35 MB
- **Record Count**: 954,846
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (48):** `['Flow Duration', 'Total Fwd Packets', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (DDoS2-Wednesday-21-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `DDoS2-Wednesday-21-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 31.90 MB
- **Record Count**: 561,396
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (45):** `['Flow Duration', 'Total Fwd Packets', 'Fwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (DoS1-Thursday-15-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `DoS1-Thursday-15-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 94.05 MB
- **Record Count**: 794,812
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (47):** `['Flow Duration', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Max', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (DoS2-Friday-16-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `DoS2-Friday-16-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 55.31 MB
- **Record Count**: 591,873
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (40):** `['Flow Duration', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (Infil1-Wednesday-28-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `Infil1-Wednesday-28-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 48.59 MB
- **Record Count**: 456,873
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (50):** `['Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (Infil2-Thursday-01-03-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `Infil2-Thursday-01-03-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 27.93 MB
- **Record Count**: 249,170
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (49):** `['Flow Duration', 'Total Backward Packets', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (Web1-Thursday-22-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `Web1-Thursday-22-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 99.14 MB
- **Record Count**: 830,224
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (47):** `['Flow Duration', 'Total Backward Packets', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### CSE-CIC-IDS2018 (Web2-Friday-23-02-2018_TrafficForML_CICFlowMeter.parquet)
- **Filename**: `Web2-Friday-23-02-2018_TrafficForML_CICFlowMeter.parquet`
- **Format**: Parquet
- **File Size**: 96.69 MB
- **Record Count**: 829,405
- **Feature Count**: 78
- **Target Column(s)**: `Label`
- **Missing Values**: 0
- **Duplicate Rows**: 0
- **Categorical Features (0):** `[]`
- **Numerical Features (49):** `['Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 'Fwd Packets Length Total', 'Bwd Packets Length Total', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min']`...
- **Leakage-prone Columns:** `[]`
- **Notes**:
  - Stored as parquet files.
  - Contains timestamp columns that can leak dataset collection order.

### UWF ZeekData
- **Filename**: `part-00000-69700ccb-c1c1-4763-beb7-cd0f1a61c268-c000.snappy.parquet`
- **Format**: Parquet
- **File Size**: 31.63 MB
- **Record Count**: 454,846
- **Feature Count**: 26
- **Target Column(s)**: `label_binary (also tactic, technique, cve)`
- **Missing Values**: 97,241
- **Duplicate Rows**: 0
- **Categorical Features (8):** `['community_id', 'conn_state', 'history', 'src_ip_zeek', 'dest_ip_zeek', 'proto', 'service', 'uid']`
- **Numerical Features (11):** `['duration', 'src_port_zeek', 'dest_port_zeek', 'missed_bytes', 'orig_bytes', 'orig_ip_bytes', 'orig_pkts', 'resp_bytes', 'resp_ip_bytes', 'resp_pkts', 'ts']`
- **Leakage-prone Columns:** `['community_id', 'src_ip_zeek', 'src_port_zeek', 'dest_ip_zeek', 'dest_port_zeek', 'orig_ip_bytes', 'orig_pkts', 'resp_ip_bytes', 'resp_pkts', 'ts', 'uid']`
- **Notes**:
  - Stored as a single parquet file.
  - Features are extracted from Zeek logs (flow features are different from CICFlowMeter features).
  - Contains explicit IP addresses, ports, and `community_id` hash, which are severe leakage sources.
  - Contains multiple target labels (`label_binary`, `label_tactic`, `label_technique`, `label_cve`).
