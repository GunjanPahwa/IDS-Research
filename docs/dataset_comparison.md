# Dataset Comparison

This document provides a comparative analysis of the six network intrusion detection datasets, highlighting their creation environments, features, temporal properties, and known limitations.

## Comparative Overview

| Dimension | KDD99 | NSL-KDD | UNSW-NB15 | CIC-IDS2017 | CSE-CIC-IDS2018 | UWF ZeekData |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Release Year** | 1999 | 2009 | 2015 | 2017 | 2018 | 2021 |
| **Network Type** | Simulated (DARPA) | Simulated (DARPA) | Hybrid (IXIA tool) | Realistic (B-Profile) | AWS Simulated | Cyber Range |
| **Collection Method**| Packet Tcpdump | Filtered KDD99 | IXIA PerfectStorm | CICFlowMeter (pcap) | CICFlowMeter (pcap) | Zeek Log Analyzer |
| **Flow vs Packet** | Connection-based | Connection-based | Flow-based | Flow-based | Flow-based | Log/Connection-based|
| **Features Count** | 41 + Label | 41 + Label + Score| 43 + Category + Label| 78 + Label | 77 + Label | 22 + 4 Targets |
| **Timestamps** | No | No | No | No | Yes | Yes |
| **IP Addresses** | No | No | No (in split files) | No | No | Yes (Source & Dest) |
| **Ports** | No | No | No (in split files) | Yes (Dest Port) | Yes (Dest Port) | Yes (Source & Dest) |
| **Flow ID / UID** | No | No | No | No | No | Yes (`uid`, `community_id`) |
| **Class Imbalance** | Extreme (~80% flood)| Moderate | Moderate | Severe (Monday Benign)| Severe | Severe |
| **Known Limitations**| Redundancy (~78%) | Outdated (1998 data) | Synthetic patterns | NaN/Inf values, noise | Missing values | Severe Leakage (IPs) |

---

## Detailed Dimension Analysis

### 1. Dataset Creation Period & Evolution
- **1999 (KDD99) & 2009 (NSL-KDD)**: Built on simulated traffic from Lincoln Labs representing a 1998 military network. The attacks reflect late-90s vectors (e.g., smurf, neptune, land).
- **2015 (UNSW-NB15)**: Created in a lab environment using the IXIA PerfectStorm tool to generate modern attack behaviors (e.g., Fuzzers, Backdoors, Analysis) alongside normal traffic.
- **2017 (CIC-IDS2017) & 2018 (CSE-CIC-IDS2018)**: Designed to address the lack of realistic normal traffic. Generated using profile systems (B-Profiles) that emulate human behavior, combined with recent attacks (Heartbleed, Botnets, Web Attacks).
- **2021 (UWF ZeekData)**: Represents contemporary security monitoring data, generated in a specialized cyber range and logged via the Zeek network monitoring tool rather than custom flow exporters.

### 2. Feature Representation: Flow-based vs. Packet-based
- **KDD99 & NSL-KDD**: Connection-based. They group packets into TCP connections or UDP/ICMP sessions, extracting 41 features that represent connection properties (duration, service, bytes) and window-based traffic statistics.
- **UNSW-NB15**: Flow-based. It captures flow characteristics from start to end, exporting packet sizes, statistical summaries (jitter, packet inter-arrival times), and state properties.
- **CIC-IDS2017 & CSE-CIC-IDS2018**: Flow-based, processed via the CICFlowMeter tool. They extract 77-78 distinct flow-level statistical features (e.g., forward/backward packet length variance, inter-arrival time stats).
- **UWF ZeekData**: Log-based. Features represent connection state records extracted by Zeek (e.g., `conn_state`, `history`, `local_orig`), making them highly structural and dependent on Zeek's parsing logic.

### 3. Data Leakage and Target Representation
- **KDD99**: The target label is a text string indicating the specific attack category or `"normal."`. It does not contain network identifiers (IPs, timestamps), reducing direct ID leakage.
- **NSL-KDD**: The raw txt files include a `difficulty_score` column. This score correlates directly with the classification difficulty of KDD99 models and must be excluded from feature vectors.
- **UNSW-NB15**: Includes an `'id'` column that acts as an incremental row index. Models can easily overfit on this identifier if it isn't removed.
- **CIC-IDS2017 & CSE-CIC-IDS2018**: Do not contain IP addresses, but include `'Destination Port'` (sometimes labeled `'Destination_Port'`), which can cause partial leakage if the model learns to flag specific services (like port 80/443 or specific malicious ports) instead of traffic patterns. CSE-CIC-IDS2018 contains timestamps which can leak the chronological order of simulated attacks.
- **UWF ZeekData**: Contains severe leakage columns including `src_ip_zeek`, `dest_ip_zeek`, `src_port_zeek`, `dest_port_zeek`, `community_id`, and `uid`. An ML model trained on this dataset without removing these columns will overfit on the IP address space and connection hashes, failing to generalize to any other network segment.

### 4. Known Anomalies and Data Quality Issues
- **NaN/Infinity Values**: CIC-IDS2017 and CSE-CIC-IDS2018 contain infinite values (represented as `inf` or `Infinity`) and missing values in rate columns like `'Flow Bytes/s'` and `'Flow Packets/s'`. These must be handled during preprocessing.
- **Redundancy**: KDD99 has over 3.8 million duplicate rows (78% of the dataset), which heavily biases model evaluation if a simple train/test split is performed. NSL-KDD resolves this issue by design.
- **Incompatible Schemas**: Features from KDD99/NSL-KDD are completely disjoint from CICFlowMeter features. Similarly, Zeek features are log-structural and cannot be directly compared to CICFlowMeter's statistical features without significant feature mapping or custom extraction.
