"""Binary and multiclass label processing for the two-stage IDS pipeline."""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd

from src.preprocessing.mappings import get_dataset_family, normalize_raw_label


class DuplicatePolicy(str, Enum):
    """Explicit policy for UWF label_binary == 'Duplicate' rows."""

    EXCLUDE = "exclude"
    ATTACK = "attack"
    BENIGN = "benign"


# UWF tactic values observed in data -> project standardized taxonomy.
# Verified against label_tactic fields; not copied blindly from stale CSV rows.
UWF_TACTIC_TO_STANDARD = {
    "Reconnaissance": "Probe/Reconnaissance",
    "Credential Access": "Credential/Access Attack",
    "Initial Access": "Infiltration",
    "Defense Evasion": "Other",
    "Persistence": "Other",
    "Privilege Escalation": "Privilege Escalation",
    "Exfiltration": "Other",
    "Execution": "Exploitation",
    "Collection": "Other",
    "Lateral Movement": "Other",
    "Command and Control": "Botnet",
    "Impact": "DoS",
    "Discovery": "Probe/Reconnaissance",
    "none": "BENIGN",
    "None": "BENIGN",
    "": "BENIGN",
}

BENIGN_KEYWORDS = {"normal", "benign", "none"}


class LabelProcessingError(ValueError):
    """Raised when a label cannot be processed under the configured policy."""


def normalize_cic2017_web_attack_label(label: str) -> str:
    """Normalize corrupted Web Attack separators (U+FFFD / en-dash) to ASCII hyphen."""
    text = str(label).strip()
    text = re.sub(r"\s[\u2013\u2014\ufffd\u00ad]\s", " - ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def apply_label_aliases(dataset_family: str, label: str) -> str:
    """Apply dataset-specific label aliases before taxonomy lookup."""
    lbl = normalize_raw_label(label)
    if dataset_family == "CIC-IDS2017":
        lbl = normalize_cic2017_web_attack_label(lbl)
    if dataset_family == "CSE-CIC-IDS2018" and lbl == "Infilteration":
        lbl = "Infiltration"
    return lbl


class BinaryLabelProcessor:
    """Stage 1: BENIGN (0) vs ATTACK (1)."""

    def __init__(
        self,
        mapping_csv_path: Optional[str] = None,
        duplicate_policy: DuplicatePolicy = DuplicatePolicy.EXCLUDE,
        on_missing: str = "raise",
    ):
        self.duplicate_policy = duplicate_policy
        self.on_missing = on_missing
        self.lookup: dict[tuple[str, str], str] = {}
        if mapping_csv_path:
            mapping_df = pd.read_csv(mapping_csv_path)
            for _, row in mapping_df.iterrows():
                ds_family = get_dataset_family(row["dataset"])
                orig_lbl = apply_label_aliases(ds_family, row["original_label"])
                self.lookup[(ds_family, orig_lbl)] = row["standardized_label"]

    def _uwf_binary(self, label_val) -> Optional[int]:
        lbl = str(label_val).strip()
        if lbl == "False":
            return 0
        if lbl == "True":
            return 1
        if lbl == "Duplicate":
            if self.duplicate_policy == DuplicatePolicy.EXCLUDE:
                return None
            if self.duplicate_policy == DuplicatePolicy.ATTACK:
                return 1
            if self.duplicate_policy == DuplicatePolicy.BENIGN:
                return 0
        return None

    def to_binary(self, label_val, dataset_name: str) -> Optional[int]:
        if pd.isna(label_val):
            if self.on_missing == "raise":
                raise LabelProcessingError(f"Missing label for dataset {dataset_name}")
            return None

        ds_family = get_dataset_family(dataset_name)

        if ds_family == "UWF ZeekData":
            lbl = str(label_val).strip()
            if lbl == "Duplicate" and self.duplicate_policy == DuplicatePolicy.EXCLUDE:
                return None
            uwf = self._uwf_binary(label_val)
            if uwf is not None:
                return uwf

        if ds_family == "UNSW-NB15":
            if str(label_val).strip() in {"0", "0.0"}:
                return 0
            if str(label_val).strip() in {"1", "1.0"}:
                return 1

        lbl_str = apply_label_aliases(ds_family, label_val)
        std_lbl = self.lookup.get((ds_family, lbl_str))

        if std_lbl is None:
            lbl_lower = lbl_str.lower()
            if lbl_lower in BENIGN_KEYWORDS or lbl_str in {"0", "False"}:
                std_lbl = "BENIGN"
            elif lbl_str in {"1", "True"}:
                std_lbl = "Other"
            else:
                std_lbl = "Other"

        return 0 if std_lbl == "BENIGN" else 1

    def process_series(self, series: pd.Series, dataset_name: str) -> tuple[np.ndarray, np.ndarray]:
        """Return (y_binary, keep_mask). keep_mask False where rows should be dropped."""
        values = []
        keep = []
        for val in series:
            binary = self.to_binary(val, dataset_name)
            if binary is None:
                keep.append(False)
                values.append(np.nan)
            else:
                keep.append(True)
                values.append(binary)
        return np.array(values, dtype=float), np.array(keep, dtype=bool)


class MulticlassLabelProcessor:
    """Stage 2: standardized attack category/tactic (BENIGN for benign rows)."""

    def __init__(
        self,
        mapping_csv_path: Optional[str] = None,
        on_missing: str = "raise",
    ):
        self.on_missing = on_missing
        self.lookup: dict[tuple[str, str], str] = {}
        if mapping_csv_path:
            mapping_df = pd.read_csv(mapping_csv_path)
            for _, row in mapping_df.iterrows():
                ds_family = get_dataset_family(row["dataset"])
                orig_lbl = apply_label_aliases(ds_family, row["original_label"])
                self.lookup[(ds_family, orig_lbl)] = row["standardized_label"]

    def _uwf_multiclass(self, row: pd.Series) -> Optional[str]:
        tactic = row.get("label_tactic")
        if pd.notna(tactic):
            tactic_str = str(tactic).strip()
            if tactic_str in UWF_TACTIC_TO_STANDARD:
                return UWF_TACTIC_TO_STANDARD[tactic_str]
            return tactic_str if tactic_str else None

        technique = row.get("label_technique")
        if pd.notna(technique) and str(technique).strip() not in {"", "Duplicate", "none", "None"}:
            return f"MITRE-{str(technique).strip()}"

        binary = row.get("label_binary")
        if pd.notna(binary):
            if str(binary).strip() == "False":
                return "BENIGN"
            if str(binary).strip() == "Duplicate":
                return None
        return None

    def to_standard(self, label_val, dataset_name: str, row: Optional[pd.Series] = None) -> Optional[str]:
        if pd.isna(label_val):
            if self.on_missing == "raise":
                raise LabelProcessingError(f"Missing multiclass label for dataset {dataset_name}")
            return None

        ds_family = get_dataset_family(dataset_name)

        if ds_family == "UWF ZeekData" and row is not None:
            uwf = self._uwf_multiclass(row)
            if uwf is not None:
                return uwf

        if ds_family == "UNSW-NB15":
            lbl_str = str(label_val).strip()
            if lbl_str == "Normal":
                return "BENIGN"
            std = self.lookup.get((ds_family, lbl_str))
            return std if std is not None else lbl_str

        lbl_str = apply_label_aliases(ds_family, label_val)
        std_lbl = self.lookup.get((ds_family, lbl_str))

        if std_lbl is not None:
            return std_lbl

        lbl_lower = lbl_str.lower()
        if lbl_lower in BENIGN_KEYWORDS:
            return "BENIGN"
        return "Other"

    def process_dataframe(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        multiclass_col: str = "label",
    ) -> tuple[np.ndarray, np.ndarray]:
        values = []
        keep = []
        for idx, val in df[multiclass_col].items():
            row = df.loc[idx]
            try:
                std = self.to_standard(val, dataset_name, row=row)
            except LabelProcessingError:
                keep.append(False)
                values.append(None)
                continue
            if std is None:
                keep.append(False)
                values.append(None)
            else:
                keep.append(True)
                values.append(std)
        return np.array(values, dtype=object), np.array(keep, dtype=bool)
