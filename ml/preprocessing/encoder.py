import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger

class CategoricalEncoder:
    """
    Automated Categorical Encoder supporting Label Encoding, One-Hot Encoding,
    and regularized Target Encoding with Laplace smoothing to prevent overfitting.
    """
    def __init__(
        self,
        label_cols: Optional[List[str]] = None,
        one_hot_cols: Optional[List[str]] = None,
        target_cols: Optional[List[str]] = None,
        max_one_hot_cardinality: int = 10,
        smoothing: float = 10.0
    ):
        self.label_cols = label_cols or []
        self.one_hot_cols = one_hot_cols or []
        self.target_cols = target_cols or []
        self.max_one_hot_cardinality = max_one_hot_cardinality
        self.smoothing = smoothing
        
        self.label_maps: Dict[str, Dict[str, int]] = {}
        self.one_hot_categories: Dict[str, List[str]] = {}
        self.target_maps: Dict[str, Dict[str, float]] = {}
        self.global_target_mean: float = 0.0
        self.fitted = False

    def auto_detect_columns(self, df: pd.DataFrame, target_col: Optional[str] = None):
        """Automatically categorizes string/categorical columns into One-Hot or Target Encoding."""
        for col in df.select_dtypes(include=['object', 'category', 'string']).columns:
            if col == target_col or col in self.label_cols:
                continue
            unique_count = df[col].nunique()
            if unique_count <= self.max_one_hot_cardinality:
                if col not in self.one_hot_cols:
                    self.one_hot_cols.append(col)
            else:
                if col not in self.target_cols and target_col is not None:
                    self.target_cols.append(col)
                elif col not in self.label_cols:
                    self.label_cols.append(col)
        logger.info(f"Auto-detected encoders - One-Hot: {self.one_hot_cols}, Target: {self.target_cols}, Label: {self.label_cols}")

    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> 'CategoricalEncoder':
        """Learns categorical mappings and target encoding priors."""
        logger.info("Fitting CategoricalEncoder...")
        
        if not self.label_cols and not self.one_hot_cols and not self.target_cols:
            self.auto_detect_columns(df, target_col)
            
        # 1. Label Encoding
        for col in self.label_cols:
            if col in df.columns:
                uniques = sorted(df[col].astype(str).unique())
                self.label_maps[col] = {val: idx for idx, val in enumerate(uniques)}
                
        # 2. One-Hot Encoding
        for col in self.one_hot_cols:
            if col in df.columns:
                self.one_hot_categories[col] = sorted(df[col].astype(str).unique())
                
        # 3. Target Encoding (with regularized smoothing)
        if self.target_cols and target_col and target_col in df.columns:
            self.global_target_mean = float(df[target_col].mean())
            for col in self.target_cols:
                if col in df.columns:
                    stats = df.groupby(col)[target_col].agg(['count', 'mean'])
                    # Smoothed target encoding formula: (count * mean + smoothing * global_mean) / (count + smoothing)
                    smoothed = (stats['count'] * stats['mean'] + self.smoothing * self.global_target_mean) / (stats['count'] + self.smoothing)
                    self.target_maps[col] = smoothed.to_dict()
                    
        self.fitted = True
        logger.info("CategoricalEncoder fitted successfully.")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies learned encodings to dataframe."""
        if not self.fitted:
            raise RuntimeError("CategoricalEncoder must be fitted before calling transform().")
            
        df_enc = df.copy()
        
        # 1. Apply Label Encoding
        for col, mapping in self.label_maps.items():
            if col in df_enc.columns:
                df_enc[col] = df_enc[col].astype(str).map(mapping).fillna(-1).astype(int)
                
        # 2. Apply One-Hot Encoding
        for col, categories in self.one_hot_categories.items():
            if col in df_enc.columns:
                for cat in categories:
                    new_col_name = f"{col}_{cat}"
                    df_enc[new_col_name] = (df_enc[col].astype(str) == cat).astype(int)
                df_enc = df_enc.drop(columns=[col])
                
        # 3. Apply Target Encoding
        for col, mapping in self.target_maps.items():
            if col in df_enc.columns:
                df_enc[col] = df_enc[col].astype(str).map(mapping).fillna(self.global_target_mean)
                
        return df_enc

    def fit_transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> pd.DataFrame:
        return self.fit(df, target_col=target_col).transform(df)
