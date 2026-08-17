import os
import pandas as pd

# Standardized feature columns
COMMON_5_COLS = ["duration", "protocol", "src_bytes", "dst_bytes", "service"]
COMMON_7_COLS = ["duration", "protocol", "src_bytes", "dst_bytes", "src_packets", "dst_packets", "service"]

# Raw column mappings per dataset (all keys will be stripped of spaces)
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
        "label": "label"
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
        "difficulty_score": "difficulty_score"
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
        "label": "label_binary"
    },
    "CIC-IDS2017": {
        "Flow Duration": "duration",
        "Protocol": "protocol",
        "Total Length of Fwd Packets": "src_bytes",
        "Total Length of Bwd Packets": "dst_bytes",
        "Total Fwd Packets": "src_packets",
        "Total Backward Packets": "dst_packets",
        "Destination Port": "dest_port",
        "Label": "label"
    },
    "CSE-CIC-IDS2018": {
        "Flow Duration": "duration",
        "Protocol": "protocol",
        "Fwd Packets Length Total": "src_bytes",
        "Bwd Packets Length Total": "dst_bytes",
        "Total Fwd Packets": "src_packets",
        "Total Backward Packets": "dst_packets",
        "Dst Port": "dest_port",
        "Label": "label"
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
        "label_binary": "label"
    }
}

# Leakage columns to drop per dataset group
LEAKAGE_COLUMNS = {
    "KDD99": [],
    "NSL-KDD": ["difficulty_score"],
    "UNSW-NB15": ["id"],
    "CIC-IDS2017": [],
    "CSE-CIC-IDS2018": ["Timestamp"],
    "UWF ZeekData": [
        "community_id", "src_ip_zeek", "src_port_zeek", 
        "dest_ip_zeek", "local_orig", "local_resp", "ts", "uid",
        "orig_ip_bytes", "resp_ip_bytes", "conn_state", "history"
    ]
}

# Port to service mapping to infer service for CIC2017/CIC2018 where service is missing
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
    3306: "mysql"
}

def map_port_to_service(port):
    """Maps a port number to a standard service string."""
    try:
        p = int(port)
        return PORT_SERVICE_MAP.get(p, "other")
    except (ValueError, TypeError):
        return "other"

class LabelStandardizer:
    """Standardizes target labels to binary classification (0: BENIGN, 1: ATTACK)."""
    def __init__(self, mapping_csv_path):
        self.mapping_df = pd.read_csv(mapping_csv_path)
        # Create a fast lookup map: (dataset_family, original_label) -> standardized_label
        self.lookup = {}
        for _, row in self.mapping_df.iterrows():
            ds_family = self._get_dataset_family(row['dataset'])
            # Strip periods and spaces to normalize raw labels
            orig_lbl = str(row['original_label']).strip().rstrip('.')
            self.lookup[(ds_family, orig_lbl)] = row['standardized_label']

    def _get_dataset_family(self, ds_name):
        """Simplifies dataset names into family keys."""
        ds_upper = ds_name.upper()
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
        return ds_name

    def standardize(self, label_val, dataset_name):
        """Converts raw labels to standardized category and returns binary class (0 or 1)."""
        if pd.isna(label_val):
            return 0 # Default to Benign if missing, or we can handle it
        
        lbl_str = str(label_val).strip().rstrip('.')
        ds_family = self._get_dataset_family(dataset_name)
        
        # Check direct lookup first
        std_lbl = self.lookup.get((ds_family, lbl_str), None)
        
        if std_lbl is None:
            # Fallback checks based on naming keywords
            lbl_lower = lbl_str.lower()
            if "normal" in lbl_lower or "benign" in lbl_lower or lbl_str == "0":
                std_lbl = "BENIGN"
            else:
                std_lbl = "Other" # Default class for unmapped attacks
                
        # Return binary output: 0 for BENIGN, 1 for ATTACK
        return 0 if std_lbl == "BENIGN" else 1
