import numpy as np
import pandas as pd

def clean_numeric_extremes(df, numeric_cols):
    """Replaces infinite and invalid values in numeric columns with NaN so they can be imputed."""
    df_clean = df.copy()
    for col in numeric_cols:
        if col in df_clean.columns:
            # Convert to numeric, forcing errors to NaN
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            # Replace inf and -inf with NaN
            df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
    return df_clean

def get_chunk_iterator(file_path, format_type, chunk_size=100000):
    """Memory-efficient file reader chunk iterator."""
    if format_type.lower() == 'csv' or format_type.lower() == 'txt':
        # Handles CSV and text formats chunk-by-chunk
        return pd.read_csv(file_path, chunksize=chunk_size, low_memory=False, encoding='latin-1')
    elif format_type.lower() == 'parquet':
        # Reads Parquet file in chunks of rows using PyArrow
        import pyarrow.parquet as pq
        parquet_file = pq.ParquetFile(file_path)
        
        def parquet_generator():
            for i in range(parquet_file.num_row_groups):
                # Read row group as pandas df
                yield parquet_file.read_row_group(i).to_pandas()
                
        return parquet_generator()
    else:
        raise ValueError(f"Unsupported format type: {format_type}")
