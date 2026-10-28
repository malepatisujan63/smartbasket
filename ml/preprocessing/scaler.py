import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.utils.logger import logger

class FeatureScaler:
    """
    Modular Feature Scaler implementing StandardScaler, MinMaxScaler, and RobustScaler.
    Persists scaling parameters for deterministic production inference.
    """
    def __init__(self, method: str = "standard", exclude_cols: Optional[List[str]] = None):
        self.method = method.lower() # 'standard', 'minmax', 'robust'
        self.exclude_cols = exclude_cols or []
        
        self.params: Dict[str, Dict[str, float]] = {}
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> 'FeatureScaler':
        """Learns scaling parameters (mean/std, min/max, median/iqr) from numerical columns."""
        logger.info(f"Fitting FeatureScaler with method '{self.method}'...")
        
        for col in df.select_dtypes(include=['number']).columns:
            if col in self.exclude_cols:
                continue
            col_clean = df[col].dropna()
            if len(col_clean) == 0:
                continue
                
            if self.method == "standard":
                mean = float(col_clean.mean())
                std = float(col_clean.std())
                self.params[col] = {"mean": mean, "std": std if std > 1e-8 else 1.0}
            elif self.method == "minmax":
                min_val = float(col_clean.min())
                max_val = float(col_clean.max())
                diff = max_val - min_val
                self.params[col] = {"min": min_val, "max": max_val, "diff": diff if diff > 1e-8 else 1.0}
            elif self.method == "robust":
                median = float(col_clean.median())
                q25 = float(col_clean.quantile(0.25))
                q75 = float(col_clean.quantile(0.75))
                iqr = q75 - q25
                self.params[col] = {"median": median, "iqr": iqr if iqr > 1e-8 else 1.0}
            else:
                raise ValueError(f"Unknown scaling method '{self.method}'. Use 'standard', 'minmax', or 'robust'.")
                
        self.fitted = True
        logger.info(f"FeatureScaler fitted across {len(self.params)} numerical features.")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies scaling parameters to numerical columns."""
        if not self.fitted:
            raise RuntimeError("FeatureScaler must be fitted before calling transform().")
            
        df_scaled = df.copy()
        for col, p in self.params.items():
            if col in df_scaled.columns:
                if self.method == "standard":
                    df_scaled[col] = (df_scaled[col] - p["mean"]) / p["std"]
                elif self.method == "minmax":
                    df_scaled[col] = (df_scaled[col] - p["min"]) / p["diff"]
                elif self.method == "robust":
                    df_scaled[col] = (df_scaled[col] - p["median"]) / p["iqr"]
                    
        return df_scaled

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)
