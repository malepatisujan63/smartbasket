import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.utils.logger import logger
from ml.configs import config

try:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.feature_selection import RFE as SklearnRFE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class FeatureSelector:
    """
    Enterprise Feature Selector implementing Variance Thresholding,
    Multicollinearity/Correlation Filtering, VIF analysis, and Recursive Feature Elimination (RFE).
    """
    def __init__(
        self,
        variance_threshold: float = config.VARIANCE_THRESHOLD,
        correlation_threshold: float = config.CORRELATION_FILTER_THRESHOLD,
        vif_threshold: float = config.VIF_THRESHOLD,
        rfe_n_features: Optional[int] = None
    ):
        self.variance_threshold = variance_threshold
        self.correlation_threshold = correlation_threshold
        self.vif_threshold = vif_threshold
        self.rfe_n_features = rfe_n_features
        
        self.selected_features: List[str] = []
        self.dropped_variance: List[str] = []
        self.dropped_correlation: List[str] = []
        self.dropped_rfe: List[str] = []
        self.feature_importances: Dict[str, float] = {}
        self.fitted = False

    def check_multicollinearity_vif(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculates Variance Inflation Factor (VIF) approximation for numerical features."""
        num_cols = df.select_dtypes(include=['number']).columns
        vif_dict = {}
        if len(num_cols) < 2:
            return vif_dict
            
        corr_matrix = df[num_cols].corr().abs().fillna(0.0)
        for col in num_cols:
            # R2 approximation from correlation matrix eigen decomposition or max correlation
            max_corr = corr_matrix.loc[col].drop(col).max() if len(num_cols) > 1 else 0.0
            r2_approx = min(0.999, max_corr ** 2)
            vif = 1.0 / (1.0 - r2_approx) if (1.0 - r2_approx) > 0 else 999.0
            vif_dict[col] = round(float(vif), 2)
        return vif_dict

    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> 'FeatureSelector':
        """Learns which features to keep or drop based on variance, correlation, and RFE."""
        logger.info("Fitting FeatureSelector across dataset...")
        num_df = df.select_dtypes(include=['number'])
        
        if target_col and target_col in num_df.columns:
            feature_cols = [c for c in num_df.columns if c != target_col]
        else:
            feature_cols = list(num_df.columns)
            
        # 1. Variance Threshold
        keep_var = []
        for col in feature_cols:
            var = num_df[col].var()
            if var >= self.variance_threshold and not np.isnan(var):
                keep_var.append(col)
            else:
                self.dropped_variance.append(col)
        logger.info(f"Variance filter dropped {len(self.dropped_variance)} low-variance features.")
        
        # 2. Correlation Filtering (Multicollinearity removal)
        corr_matrix = num_df[keep_var].corr().abs().fillna(0.0)
        upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        to_drop_corr = [col for col in upper_tri.columns if any(upper_tri[col] > self.correlation_threshold)]
        self.dropped_correlation = to_drop_corr
        keep_corr = [c for c in keep_var if c not in to_drop_corr]
        logger.info(f"Correlation filter dropped {len(self.dropped_correlation)} highly correlated features (> {self.correlation_threshold}).")
        
        # 3. Recursive Feature Elimination (RFE) & Feature Importance
        if target_col and target_col in df.columns and SKLEARN_AVAILABLE and len(keep_corr) > 0:
            X = num_df[keep_corr].fillna(0.0)
            y = df[target_col].fillna(0.0)
            
            is_classif = len(np.unique(y)) <= 10 and not pd.api.types.is_float_dtype(y)
            estimator = RandomForestClassifier(n_estimators=50, random_state=42) if is_classif else RandomForestRegressor(n_estimators=50, random_state=42)
            
            try:
                estimator.fit(X, y)
                importances = estimator.feature_importances_
                self.feature_importances = {col: round(float(imp), 4) for col, imp in zip(keep_corr, importances)}
                
                if self.rfe_n_features and len(keep_corr) > self.rfe_n_features:
                    rfe = SklearnRFE(estimator=estimator, n_features_to_select=self.rfe_n_features, step=1)
                    rfe.fit(X, y)
                    self.selected_features = [col for col, keep in zip(keep_corr, rfe.support_) if keep]
                    self.dropped_rfe = [col for col, keep in zip(keep_corr, rfe.support_) if not keep]
                else:
                    self.selected_features = keep_corr
            except Exception as e:
                logger.warning(f"RFE / Importance calculation fallback: {e}")
                self.selected_features = keep_corr
        else:
            self.selected_features = keep_corr
            
        self.fitted = True
        logger.info(f"FeatureSelector finalized {len(self.selected_features)} optimal features.")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Retains only selected optimal features while keeping non-numerical / target columns intact."""
        if not self.fitted:
            raise RuntimeError("FeatureSelector must be fitted before calling transform().")
            
        non_num_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        cols_to_keep = [c for c in self.selected_features if c in df.columns] + non_num_cols
        # Preserve target if present and numeric but not in selected
        for col in df.columns:
            if col not in cols_to_keep and ("target" in col.lower() or "label" in col.lower() or "churned" in col.lower() or "revenue" in col.lower()):
                cols_to_keep.append(col)
                
        # Deduplicate while preserving order
        cols_to_keep = list(dict.fromkeys(cols_to_keep))
        return df[cols_to_keep].copy()

    def fit_transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> pd.DataFrame:
        return self.fit(df, target_col=target_col).transform(df)
