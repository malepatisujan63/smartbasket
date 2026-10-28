import pandas as pd
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.preprocessing.cleaner import DataCleaner
from ml.preprocessing.encoder import CategoricalEncoder
from ml.preprocessing.scaler import FeatureScaler
from ml.preprocessing.selector import FeatureSelector

class AutomatedPreprocessingPipeline:
    """
    End-to-end Automated Preprocessing Pipeline for Retail Sales Intelligence.
    Executes: Cleaning -> Categorical Encoding -> Scaling -> Feature Selection.
    """
    def __init__(
        self,
        scaling_method: str = "standard",
        outlier_method: str = "iqr",
        rfe_n_features: Optional[int] = None
    ):
        self.cleaner = DataCleaner(outlier_method=outlier_method)
        self.encoder = CategoricalEncoder()
        self.scaler = FeatureScaler(method=scaling_method)
        self.selector = FeatureSelector(rfe_n_features=rfe_n_features)
        
        self.target_col: Optional[str] = None
        self.fitted = False

    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> 'AutomatedPreprocessingPipeline':
        """Fits all preprocessing stages sequentially on training data."""
        logger.info("Executing AutomatedPreprocessingPipeline fit()...")
        self.target_col = target_col
        
        # 1. Clean
        df_step1 = self.cleaner.fit_transform(df)
        
        # 2. Encode
        df_step2 = self.encoder.fit_transform(df_step1, target_col=target_col)
        
        # 3. Scale (Exclude target column from scaling)
        if target_col:
            self.scaler.exclude_cols = [target_col]
        df_step3 = self.scaler.fit_transform(df_step2)
        
        # 4. Select
        self.selector.fit(df_step3, target_col=target_col)
        
        self.fitted = True
        logger.info("AutomatedPreprocessingPipeline fit completed successfully.")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms new/test datasets using fitted preprocessing pipeline."""
        if not self.fitted:
            raise RuntimeError("AutomatedPreprocessingPipeline must be fitted before calling transform().")
            
        logger.debug("Transforming dataset through AutomatedPreprocessingPipeline...")
        df_step1 = self.cleaner.transform(df)
        df_step2 = self.encoder.transform(df_step1)
        df_step3 = self.scaler.transform(df_step2)
        df_step4 = self.selector.transform(df_step3)
        return df_step4

    def fit_transform(self, df: pd.DataFrame, target_col: Optional[str] = None) -> pd.DataFrame:
        return self.fit(df, target_col=target_col).transform(df)

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Returns metadata and feature importance summary of the pipeline."""
        return {
            "imputation_features": len(self.cleaner.imputation_values),
            "one_hot_columns": self.encoder.one_hot_cols,
            "target_encoded_columns": self.encoder.target_cols,
            "scaling_method": self.scaler.method,
            "selected_features_count": len(self.selector.selected_features),
            "feature_importances": self.selector.feature_importances
        }
