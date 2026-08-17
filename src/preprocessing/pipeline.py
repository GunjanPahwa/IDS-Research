import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from src.preprocessing.mappings import (
    COLUMN_MAPPINGS, LEAKAGE_COLUMNS, LabelStandardizer, map_port_to_service,
    COMMON_5_COLS, COMMON_7_COLS
)
from src.preprocessing.utils import clean_numeric_extremes

# Fixed vocabularies for categories to guarantee identical column ordering across datasets
PROTOCOL_VOCAB = ["tcp", "udp", "icmp", "other"]
SERVICE_VOCAB = ["http", "ftp", "smtp", "ssh", "dns", "telnet", "dhcp", "ntp", "snmp", "other"]

class NIDSPreprocessor:
    """Reusable preprocessor for network intrusion detection datasets."""
    def __init__(self, dataset_name, feature_space="Common-5", label_mapping_csv=None):
        self.dataset_name = dataset_name
        self.feature_space = feature_space
        self.label_mapping_csv = label_mapping_csv
        
        if feature_space == "Common-5":
            self.feature_cols = COMMON_5_COLS
        elif feature_space == "Common-7":
            self.feature_cols = COMMON_7_COLS
        else:
            raise ValueError(f"Unknown feature space: {feature_space}")
            
        if label_mapping_csv:
            self.label_standardizer = LabelStandardizer(label_mapping_csv)
        else:
            self.label_standardizer = None
            
        # Initialize preprocessing objects
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = RobustScaler()
        # Predefined categories for OneHotEncoder ensures identical column alignment
        self.encoder = OneHotEncoder(
            categories=[PROTOCOL_VOCAB, SERVICE_VOCAB],
            handle_unknown="ignore",
            sparse_output=False
        )
        self.is_fitted = False
        
    def _standardize_columns(self, df):
        """Strips column names of spaces and maps them to standardized names."""
        df_mapped = df.copy()
        # Strip all whitespace from columns
        df_mapped.columns = [str(c).strip() for c in df_mapped.columns]
        
        # Get column mappings for this dataset family
        # Match dataset name to dictionary keys
        mapping = None
        for key in COLUMN_MAPPINGS.keys():
            if key.lower() in self.dataset_name.lower():
                mapping = COLUMN_MAPPINGS[key]
                break
                
        if mapping is None:
            raise ValueError(f"No column mapping found for dataset: {self.dataset_name}")
            
        # Rename columns based on mapping
        df_mapped = df_mapped.rename(columns=mapping)
        return df_mapped

    def _clean_features(self, df):
        """Cleans and standardizes features (protocols, services, numerical rates)."""
        df_clean = df.copy()
        
        # 1. Standardize protocol
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
        else:
            # If protocol is missing (specifically in CIC-IDS2017)
            # Infer from dest_port: port 53 (DNS) and 123 (NTP) -> udp, else default to tcp
            def infer_proto(port):
                try:
                    p = int(float(port))
                    return "udp" if p in [53, 123] else "tcp"
                except (ValueError, TypeError):
                    return "tcp"
            if "dest_port" in df_clean.columns:
                df_clean["protocol"] = df_clean["dest_port"].apply(infer_proto)
            else:
                df_clean["protocol"] = "tcp"
            
        # 2. Standardize service
        if "service" in df_clean.columns:
            port_col = "dest_port" if "dest_port" in df_clean.columns else None
            
            def std_service(row):
                val = row["service"]
                port = row[port_col] if port_col else None
                if pd.isna(val) or str(val).strip() in ["", "-", "0"]:
                    if port is not None and not pd.isna(port):
                        return map_port_to_service(port)
                    return "other"
                
                val_str = str(val).strip().lower()
                if val_str in SERVICE_VOCAB:
                    return val_str
                return "other"
                
            df_clean["service"] = df_clean.apply(std_service, axis=1)
        elif "dest_port" in df_clean.columns and "service" not in df_clean.columns:
            # Infer service if missing but port exists (like in CIC datasets)
            df_clean["service"] = df_clean["dest_port"].apply(map_port_to_service)
            
        # Add placeholder service if service doesn't exist anywhere
        if "service" not in df_clean.columns:
            df_clean["service"] = "other"
            
        # 3. Microseconds to seconds conversion for CIC duration
        if "CIC" in self.dataset_name.upper() and "duration" in df_clean.columns:
            df_clean["duration"] = df_clean["duration"] / 1000000.0
            
        return df_clean

    def fit(self, df):
        """Fits imputation, scaling, and encoding on the training set."""
        df_std = self._standardize_columns(df)
        df_clean = self._clean_features(df_std)
        
        # Select target columns
        num_cols = [c for c in self.feature_cols if c not in ["protocol", "service"]]
        
        # Handle nan/inf in numerical features
        df_clean = clean_numeric_extremes(df_clean, num_cols)
        
        # Fit imputer and scaler
        if num_cols:
            X_num = df_clean[num_cols].values
            self.imputer.fit(X_num)
            X_num_imp = self.imputer.transform(X_num)
            self.scaler.fit(X_num_imp)
            
        # Fit OneHotEncoder
        X_cat = df_clean[["protocol", "service"]].astype(str).values
        self.encoder.fit(X_cat)
        
        self.is_fitted = True
        return self

    def transform(self, df):
        """Transforms a dataset using the fitted parameters."""
        if not self.is_fitted:
            raise ValueError("Preprocessor is not fitted yet. Call fit() first.")
            
        df_std = self._standardize_columns(df)
        df_clean = self._clean_features(df_std)
        
        # Extract target labels if label column is present
        y = None
        label_col = "label"
        # Find mapped label column name
        if "label" in df_clean.columns:
            label_col = "label"
        elif "label_binary" in df_clean.columns:
            label_col = "label_binary"
            
        if label_col in df_clean.columns and self.label_standardizer:
            y = df_clean[label_col].apply(lambda v: self.label_standardizer.standardize(v, self.dataset_name)).to_numpy()
        elif "label_binary" in df_clean.columns and not self.label_standardizer:
            y = df_clean["label_binary"].to_numpy()
            
        # Process numerical features
        num_cols = [c for c in self.feature_cols if c not in ["protocol", "service"]]
        df_clean = clean_numeric_extremes(df_clean, num_cols)
        
        if num_cols:
            X_num = df_clean[num_cols].values
            X_num_imp = self.imputer.transform(X_num)
            X_num_scaled = self.scaler.transform(X_num_imp)
        else:
            X_num_scaled = np.empty((len(df), 0))
            
        # Process categorical features
        X_cat = df_clean[["protocol", "service"]].astype(str).values
        X_cat_encoded = self.encoder.transform(X_cat)
        
        # Combine numerical and categorical features
        X_combined = np.hstack([X_num_scaled, X_cat_encoded])
        
        # Return features and optional targets
        return X_combined, y

    def get_feature_names(self):
        """Returns the list of feature column names after one-hot encoding."""
        num_cols = [c for c in self.feature_cols if c not in ["protocol", "service"]]
        cat_feature_names = self.encoder.get_feature_names_out(["protocol", "service"])
        return num_cols + list(cat_feature_names)
