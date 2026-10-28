import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.utils.logger import logger
from ml.configs import config

class DataCleaner:
    """
    Automated Data Cleaner for Enterprise MLOps Pipelines.
    Handles missing value imputation, duplicate removal, and outlier detection/capping.
    """
    def __init__(
        self,
        num_strategy: str = config.MISSING_VALUE_NUMERICAL_STRATEGY,
        cat_strategy: str = config.MISSING_VALUE_CATEGORICAL_STRATEGY,
        outlier_method: str = "iqr", # 'iqr' or 'zscore'
        z_threshold: float = config.OUTLIER_Z_THRESHOLD,
        iqr_multiplier: float = config.OUTLIER_IQR_MULTIPLIER
    ):
        self.num_strategy = num_strategy
        self.cat_strategy = cat_strategy
        self.outlier_method = outlier_method
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        
        self.imputation_values: Dict[str, Any] = {}
        self.outlier_bounds: Dict[str, Tuple[float, float]] = {}
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> 'DataCleaner':
        """Learns imputation statistics and outlier boundaries from training data."""
        logger.info("Fitting DataCleaner statistics on dataset...")
        
        # 1. Imputation values
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if self.num_strategy == "median":
                    self.imputation_values[col] = df[col].median()
                elif self.num_strategy == "mean":
                    self.imputation_values[col] = df[col].mean()
                else:
                    self.imputation_values[col] = 0.0
                    
                # Calculate Outlier Bounds
                col_clean = df[col].dropna()
                if len(col_clean) > 0:
                    if self.outlier_method == "zscore":
                        mean = col_clean.mean()
                        std = col_clean.std()
                        if std > 0:
                            self.outlier_bounds[col] = (mean - self.z_threshold * std, mean + self.z_threshold * std)
                    else: # IQR
                        q25 = col_clean.quantile(0.25)
                        q75 = col_clean.quantile(0.75)
                        iqr = q75 - q25
                        self.outlier_bounds[col] = (q25 - self.iqr_multiplier * iqr, q75 + self.iqr_multiplier * iqr)
            else:
                if self.cat_strategy == "mode":
                    mode_val = df[col].mode()
                    self.imputation_values[col] = mode_val[0] if len(mode_val) > 0 else "Missing"
                else:
                    self.imputation_values[col] = "Missing"
                    
        self.fitted = True
        logger.info(f"DataCleaner fitted successfully across {len(self.imputation_values)} features.")
        return self

    def transform(self, df: pd.DataFrame, handle_outliers: bool = True) -> pd.DataFrame:
        """Applies imputation, removes duplicates, and caps outliers."""
        if not self.fitted:
            raise RuntimeError("DataCleaner must be fitted before calling transform().")
            
        df_clean = df.copy()
        
        # 1. Duplicate removal
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates().reset_index(drop=True)
        dropped_dups = initial_rows - len(df_clean)
        if dropped_dups > 0:
            logger.info(f"Removed {dropped_dups} duplicate rows.")
            
        # 2. Missing value imputation
        for col, imp_val in self.imputation_values.items():
            if col in df_clean.columns and df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna(imp_val)
                
        # 3. Outlier handling (Capping / Winsorization)
        if handle_outliers:
            outliers_capped = 0
            for col, (low, high) in self.outlier_bounds.items():
                if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                    # Check how many values exceed bounds
                    mask = (df_clean[col] < low) | (df_clean[col] > high)
                    outliers_capped += int(mask.sum())
                    df_clean[col] = df_clean[col].clip(lower=low, upper=high)
            if outliers_capped > 0:
                logger.debug(f"Capped {outliers_capped} outlier values across numeric columns.")
                
        return df_clean

    def fit_transform(self, df: pd.DataFrame, handle_outliers: bool = True) -> pd.DataFrame:
        return self.fit(df).transform(df, handle_outliers=handle_outliers)
