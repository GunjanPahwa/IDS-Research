"""Preprocessing pipeline for within-dataset and cross-dataset experiments."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler

from src.preprocessing.labels import BinaryLabelProcessor, DuplicatePolicy, MulticlassLabelProcessor
from src.preprocessing.mappings import (
    COMMON_5_COLS,
    COMMON_7_COLS,
    COMMON_7_INCOMPATIBLE,
    CROSS_DATASET_EXTRA_DROP,
    INFERENCE_ONLY_COLUMNS,
    LEAKAGE_COLUMNS,
    NATIVE_FEATURE_EXCLUDE,
    get_dataset_family,
    map_port_to_service,
    resolve_column_mapping,
)
from src.preprocessing.utils import clean_numeric_extremes

PROTOCOL_VOCAB = ["tcp", "udp", "icmp", "other"]
SERVICE_VOCAB = ["http", "ftp", "smtp", "ssh", "dns", "telnet", "dhcp", "ntp", "snmp", "other"]


class Common7IncompatibleError(ValueError):
    """Raised when Common-7 is requested for datasets without packet-count features."""


class NIDSPreprocessor:
    """Reusable preprocessor supporting within-dataset and cross-dataset modes."""

    def __init__(
        self,
        dataset_name: str,
        preprocessing_mode: str = "cross-dataset",
        feature_space: str = "Common-5",
        label_mapping_csv: Optional[str] = None,
        duplicate_policy: DuplicatePolicy = DuplicatePolicy.EXCLUDE,
    ):
        self.dataset_name = dataset_name
        self.dataset_family = get_dataset_family(dataset_name)
        self.preprocessing_mode = preprocessing_mode
        self.feature_space = feature_space
        self.duplicate_policy = duplicate_policy

        if preprocessing_mode not in {"within-dataset", "cross-dataset"}:
            raise ValueError("preprocessing_mode must be 'within-dataset' or 'cross-dataset'")
        if feature_space not in {"native", "Common-5", "Common-7"}:
            raise ValueError("feature_space must be 'native', 'Common-5', or 'Common-7'")
        if feature_space == "Common-7" and self.dataset_family in COMMON_7_INCOMPATIBLE:
            raise Common7IncompatibleError(
                f"Common-7 is incompatible with {self.dataset_family}: "
                "src_packets/dst_packets are not available. Use Common-5 instead."
            )
        if preprocessing_mode == "within-dataset" and feature_space != "native":
            raise ValueError("within-dataset mode requires feature_space='native'")
        if preprocessing_mode == "cross-dataset" and feature_space == "native":
            raise ValueError("cross-dataset mode requires feature_space='Common-5' or 'Common-7'")

        if feature_space == "native":
            self.feature_cols = None
        elif feature_space == "Common-5":
            self.feature_cols = COMMON_5_COLS.copy()
        else:
            self.feature_cols = COMMON_7_COLS.copy()

        self.binary_processor = BinaryLabelProcessor(
            mapping_csv_path=label_mapping_csv,
            duplicate_policy=duplicate_policy,
        ) if label_mapping_csv else BinaryLabelProcessor(duplicate_policy=duplicate_policy)
        self.multiclass_processor = MulticlassLabelProcessor(
            mapping_csv_path=label_mapping_csv,
        ) if label_mapping_csv else MulticlassLabelProcessor()

        self.imputer = SimpleImputer(strategy="median")
        self.scaler = RobustScaler()
        self.encoder = OneHotEncoder(
            categories=[PROTOCOL_VOCAB, SERVICE_VOCAB],
            handle_unknown="ignore",
            sparse_output=False,
        )
        self.native_numeric_cols: list[str] = []
        self.native_categorical_cols: list[str] = []
        self.is_fitted = False

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df_mapped = df.copy()
        df_mapped.columns = [str(c).strip() for c in df_mapped.columns]
        mapping = resolve_column_mapping(self.dataset_name)
        return df_mapped.rename(columns=mapping)

    def _drop_leakage(self, df: pd.DataFrame) -> pd.DataFrame:
        leakage = LEAKAGE_COLUMNS.get(self.dataset_family, [])
        drop_cols = [c for c in leakage if c in df.columns]
        if self.preprocessing_mode == "cross-dataset":
            extra = CROSS_DATASET_EXTRA_DROP.get(self.dataset_family, [])
            drop_cols.extend(c for c in extra if c in df.columns)
        return df.drop(columns=drop_cols, errors="ignore")

    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()

        if "protocol" in df_clean.columns:
            def std_proto(val):
                val_str = str(val).strip().lower()
                if "tcp" in val_str or val_str == "6":
                    return "tcp"
                if "udp" in val_str or val_str == "17":
                    return "udp"
                if "icmp" in val_str or val_str == "1" or "icmp6" in val_str:
                    return "icmp"
                return "other"

            df_clean["protocol"] = df_clean["protocol"].apply(std_proto)
        elif "dest_port" in df_clean.columns:
            def infer_proto(port):
                try:
                    p = int(float(port))
                    return "udp" if p in [53, 123] else "tcp"
                except (ValueError, TypeError):
                    return "tcp"

            df_clean["protocol"] = df_clean["dest_port"].apply(infer_proto)
        elif self.feature_space != "native":
            df_clean["protocol"] = "tcp"

        port_col = "dest_port" if "dest_port" in df_clean.columns else None
        if "service" in df_clean.columns:
            def std_service(row):
                val = row["service"]
                port = row[port_col] if port_col else None
                if pd.isna(val) or str(val).strip() in {"", "-", "0", "-"}:
                    if port is not None and not pd.isna(port):
                        return map_port_to_service(port)
                    return "other"
                val_str = str(val).strip().lower()
                return val_str if val_str in SERVICE_VOCAB else "other"

            df_clean["service"] = df_clean.apply(std_service, axis=1)
        elif port_col:
            df_clean["service"] = df_clean[port_col].apply(map_port_to_service)
        elif self.feature_space != "native":
            df_clean["service"] = "other"

        if self.dataset_family in {"CIC-IDS2017", "CSE-CIC-IDS2018"} and "duration" in df_clean.columns:
            df_clean["duration"] = pd.to_numeric(df_clean["duration"], errors="coerce") / 1_000_000.0

        if self.preprocessing_mode == "cross-dataset":
            drop_inference = [c for c in INFERENCE_ONLY_COLUMNS if c in df_clean.columns]
            if drop_inference:
                df_clean = df_clean.drop(columns=drop_inference)

        return df_clean

    def _resolve_native_features(self, df: pd.DataFrame) -> tuple[list[str], list[str]]:
        exclude = NATIVE_FEATURE_EXCLUDE.get(self.dataset_family, set())
        label_cols = {
            "label", "label_binary", "label_multiclass", "label_tactic",
            "label_technique", "label_cve",
        }
        exclude = exclude | label_cols
        candidates = [c for c in df.columns if c not in exclude]
        numeric_cols = []
        categorical_cols = []
        for col in candidates:
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
        return numeric_cols, categorical_cols

    def _extract_labels(self, df: pd.DataFrame) -> tuple[Optional[np.ndarray], Optional[np.ndarray], np.ndarray]:
        binary_col = None
        multiclass_col = None

        if "label_binary" in df.columns:
            binary_col = "label_binary"
        elif "label" in df.columns:
            binary_col = "label"

        if "label_multiclass" in df.columns:
            multiclass_col = "label_multiclass"
        elif self.dataset_family == "UWF ZeekData" and "label_tactic" in df.columns:
            multiclass_col = "label_tactic"
        elif "label" in df.columns:
            multiclass_col = "label"

        keep_mask = np.ones(len(df), dtype=bool)
        y_binary = None
        y_multiclass = None

        if binary_col is not None:
            y_binary, binary_keep = self.binary_processor.process_series(df[binary_col], self.dataset_name)
            keep_mask &= binary_keep

        if multiclass_col is not None:
            y_multiclass, multi_keep = self.multiclass_processor.process_dataframe(
                df, self.dataset_name, multiclass_col=multiclass_col
            )
            keep_mask &= multi_keep

        return y_binary, y_multiclass, keep_mask

    def fit(self, df: pd.DataFrame):
        df_std = self._standardize_columns(df)
        df_std = self._drop_leakage(df_std)
        df_clean = self._clean_features(df_std)

        if self.feature_space == "native":
            self.native_numeric_cols, self.native_categorical_cols = self._resolve_native_features(df_clean)
            num_cols = self.native_numeric_cols
            cat_cols = self.native_categorical_cols
        else:
            num_cols = [c for c in self.feature_cols if c not in {"protocol", "service"}]
            cat_cols = ["protocol", "service"]

        missing = [c for c in num_cols + cat_cols if c not in df_clean.columns]
        if missing:
            raise KeyError(f"Missing required feature columns after mapping: {missing}")

        df_clean = clean_numeric_extremes(df_clean, num_cols)
        if num_cols:
            self.imputer.fit(df_clean[num_cols].values)
            self.scaler.fit(self.imputer.transform(df_clean[num_cols].values))
        if cat_cols:
            self.encoder.fit(df_clean[cat_cols].astype(str).values)

        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame):
        if not self.is_fitted:
            raise ValueError("Preprocessor is not fitted yet. Call fit() first.")

        df_std = self._standardize_columns(df)
        y_binary, y_multiclass, keep_mask = self._extract_labels(df_std)
        df_std = df_std.loc[keep_mask].reset_index(drop=True)
        if y_binary is not None:
            y_binary = y_binary[keep_mask]
        if y_multiclass is not None:
            y_multiclass = y_multiclass[keep_mask]

        df_std = self._drop_leakage(df_std)
        df_clean = self._clean_features(df_std)

        if self.feature_space == "native":
            num_cols = self.native_numeric_cols
            cat_cols = self.native_categorical_cols
        else:
            num_cols = [c for c in self.feature_cols if c not in {"protocol", "service"}]
            cat_cols = ["protocol", "service"]

        df_clean = clean_numeric_extremes(df_clean, num_cols)
        if num_cols:
            X_num = self.scaler.transform(self.imputer.transform(df_clean[num_cols].values))
        else:
            X_num = np.empty((len(df_clean), 0))

        if cat_cols:
            X_cat = self.encoder.transform(df_clean[cat_cols].astype(str).values)
            X = np.hstack([X_num, X_cat])
        else:
            X = X_num

        return X, y_binary, y_multiclass

    def get_feature_names(self) -> list[str]:
        if self.feature_space == "native":
            num_cols = self.native_numeric_cols
            cat_prefix = self.native_categorical_cols
            if cat_prefix:
                cat_names = list(self.encoder.get_feature_names_out(cat_prefix))
            else:
                cat_names = []
            return num_cols + cat_names
        num_cols = [c for c in self.feature_cols if c not in {"protocol", "service"}]
        cat_names = list(self.encoder.get_feature_names_out(["protocol", "service"]))
        return num_cols + cat_names
