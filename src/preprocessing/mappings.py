"""Column mappings, leakage definitions, and shared constants."""

from __future__ import annotations

import pandas as pd

COMMON_5_COLS = ["duration", "protocol", "src_bytes", "dst_bytes", "service"]
COMMON_7_COLS = COMMON_5_COLS + ["src_packets", "dst_packets"]

COMMON_7_INCOMPATIBLE = {"KDD99", "NSL-KDD"}

# Used only for service inference in cross-dataset mode; never kept as model features.
INFERENCE_ONLY_COLUMNS = ["dest_port"]

COLUMN_MAPPINGS = {
    "KDD99": {
        0: "duration", "0": "duration",
        1: "protocol", "1": "protocol",
        2: "service", "2": "service",
        4: "src_bytes", "4": "src_bytes",
        5: "dst_bytes", "5": "dst_bytes",
        41: "label", "41": "label",
        "duration": "duration",
        "protocol_type": "protocol",
        "src_bytes": "src_bytes",
        "dst_bytes": "dst_bytes",
        "service": "service",
        "label": "label",
    },
    "NSL-KDD": {
        0: "duration", "0": "duration",
        1: "protocol", "1": "protocol",
        2: "service", "2": "service",
        4: "src_bytes", "4": "src_bytes",
        5: "dst_bytes", "5": "dst_bytes",
        41: "label", "41": "label",
        42: "difficulty_score", "42": "difficulty_score",
        "duration": "duration",
        "protocol_type": "protocol",
        "src_bytes": "src_bytes",
        "dst_bytes": "dst_bytes",
        "service": "service",
        "label": "label",
        "difficulty_score": "difficulty_score",
    },
    "UNSW-NB15": {
        "dur": "duration",
        "proto": "protocol",
        "sbytes": "src_bytes",
        "dbytes": "dst_bytes",
        "spkts": "src_packets",
        "dpkts": "dst_packets",
        "service": "service",
        "attack_cat": "label_multiclass",
        "label": "label_binary",
    },
    "CIC-IDS2017": {
        "Flow Duration": "duration",
        "Protocol": "protocol",
        "Total Length of Fwd Packets": "src_bytes",
        "Total Length of Bwd Packets": "dst_bytes",
        "Total Fwd Packets": "src_packets",
        "Total Backward Packets": "dst_packets",
        "Destination Port": "dest_port",
        "Label": "label",
    },
    "CSE-CIC-IDS2018": {
        "Flow Duration": "duration",
        "Protocol": "protocol",
        "Fwd Packets Length Total": "src_bytes",
        "Bwd Packets Length Total": "dst_bytes",
        "Total Fwd Packets": "src_packets",
        "Total Backward Packets": "dst_packets",
        "Label": "label",
    },
    "UWF ZeekData": {
        "duration": "duration",
        "proto": "protocol",
        "orig_bytes": "src_bytes",
        "resp_bytes": "dst_bytes",
        "orig_pkts": "src_packets",
        "resp_pkts": "dst_packets",
        "dest_port_zeek": "dest_port",
        "service": "service",
        "label_binary": "label_binary",
        "label_tactic": "label_tactic",
        "label_technique": "label_technique",
        "label_cve": "label_cve",
    },
}

LEAKAGE_COLUMNS = {
    "KDD99": [],
    "NSL-KDD": ["difficulty_score"],
    "UNSW-NB15": ["id"],
    "CIC-IDS2017": [],
    "CSE-CIC-IDS2018": ["Timestamp"],
    "UWF ZeekData": [
        "community_id", "src_ip_zeek", "src_port_zeek",
        "dest_ip_zeek", "local_orig", "local_resp", "ts", "uid", "datetime",
        "orig_ip_bytes", "resp_ip_bytes", "conn_state", "history",
    ],
}

# dest_port_zeek is retained in within-dataset native features but excluded in cross-dataset
# experiments after service inference (see docs/preprocessing_decisions.md).
CROSS_DATASET_EXTRA_DROP = {
    "UWF ZeekData": ["dest_port"],
}

NATIVE_FEATURE_EXCLUDE = {
    "KDD99": {"label", "difficulty_score"},
    "NSL-KDD": {"label", "difficulty_score"},
    "UNSW-NB15": {"label_binary", "label_multiclass", "id"},
    "CIC-IDS2017": {"label", "dest_port"},
    "CSE-CIC-IDS2018": {"label", "Timestamp"},
    "UWF ZeekData": {
        "label_binary", "label_tactic", "label_technique", "label_cve",
        *LEAKAGE_COLUMNS["UWF ZeekData"],
    },
}

PORT_SERVICE_MAP = {
    80: "http",
    443: "http",
    21: "ftp",
    20: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    67: "dhcp",
    68: "dhcp",
    123: "ntp",
    161: "snmp",
    162: "snmp",
    389: "ldap",
    445: "smb",
    1433: "sql",
    3306: "mysql",
}


def get_dataset_family(dataset_name: str) -> str:
    ds_upper = dataset_name.upper()
    if "KDD99" in ds_upper:
        return "KDD99"
    if "NSL-KDD" in ds_upper or "NSL KDD" in ds_upper:
        return "NSL-KDD"
    if "UNSW" in ds_upper or "NB15" in ds_upper:
        return "UNSW-NB15"
    if "2017" in ds_upper:
        return "CIC-IDS2017"
    if "2018" in ds_upper:
        return "CSE-CIC-IDS2018"
    if "ZEEK" in ds_upper or "UWF" in ds_upper:
        return "UWF ZeekData"
    return dataset_name


def resolve_column_mapping(dataset_name: str) -> dict:
    family = get_dataset_family(dataset_name)
    for key, mapping in COLUMN_MAPPINGS.items():
        if key == family:
            return mapping
    raise ValueError(f"No column mapping found for dataset: {dataset_name}")


def normalize_raw_label(label) -> str:
    return str(label).strip().rstrip(".")


def map_port_to_service(port):
    try:
        p = int(float(port))
        return PORT_SERVICE_MAP.get(p, "other")
    except (ValueError, TypeError):
        return "other"


class LabelStandardizer:
    """Backward-compatible wrapper around BinaryLabelProcessor."""

    def __init__(self, mapping_csv_path):
        from src.preprocessing.labels import BinaryLabelProcessor

        self._processor = BinaryLabelProcessor(mapping_csv_path=mapping_csv_path)

    def standardize(self, label_val, dataset_name):
        return self._processor.to_binary(label_val, dataset_name)
