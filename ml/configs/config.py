import os
from pathlib import Path
from typing import Dict, Any, List

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
REGISTRY_DIR = BASE_DIR / "model_registry" / "artifacts"
LOGS_DIR = BASE_DIR / "monitoring" / "logs"

# Ensure directories exist
for folder in [DATASETS_DIR, REGISTRY_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

class MLOpsConfig:
    """
    Global Enterprise MLOps Configuration and Hyperparameter Definition.
    Follows production standards from DeepMind and Databricks.
    """
    PROJECT_NAME = "Amazon-AI-Retail-Intelligence"
    VERSION = "2.4.0-PROD"
    ENVIRONMENT = os.getenv("ML_ENV", "production")
    
    # Data Preprocessing Thresholds
    MISSING_VALUE_NUMERICAL_STRATEGY = "median"
    MISSING_VALUE_CATEGORICAL_STRATEGY = "mode"
    OUTLIER_Z_THRESHOLD = 3.0
    OUTLIER_IQR_MULTIPLIER = 1.5
    VARIANCE_THRESHOLD = 0.01
    CORRELATION_FILTER_THRESHOLD = 0.85
    VIF_THRESHOLD = 10.0
    
    # Feature Engineering Settings
    RFM_RECENCY_BINS = 5
    RFM_FREQUENCY_BINS = 5
    RFM_MONETARY_BINS = 5
    ROLLING_WINDOWS = [7, 14, 30]
    LAG_STEPS = [1, 7, 14, 30]
    
    # Training & HPO Configuration
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    CV_FOLDS = 5
    OPTUNA_TRIALS = 20
    HYPERPARAMETER_GRIDS: Dict[str, Dict[str, Any]] = {
        "random_forest": {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 20, 30, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4]
        },
        "xgboost": {
            "n_estimators": [100, 250, 500],
            "max_depth": [3, 6, 9],
            "learning_rate": [0.01, 0.05, 0.1],
            "subsample": [0.8, 1.0],
            "colsample_bytree": [0.8, 1.0]
        },
        "lightgbm": {
            "n_estimators": [100, 250, 500],
            "num_leaves": [31, 63, 127],
            "learning_rate": [0.01, 0.05, 0.1],
            "feature_fraction": [0.8, 1.0]
        },
        "catboost": {
            "iterations": [200, 500],
            "depth": [4, 6, 8],
            "learning_rate": [0.03, 0.1]
        }
    }
    
    # Drift Monitoring Tolerances
    PSI_WARNING_THRESHOLD = 0.10
    PSI_CRITICAL_THRESHOLD = 0.25
    KS_STATISTIC_THRESHOLD = 0.05
    
    # Model Explainability
    SHAP_BACKGROUND_SAMPLE_SIZE = 100
    LIME_NUM_FEATURES = 10
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        return {
            "project": cls.PROJECT_NAME,
            "version": cls.VERSION,
            "env": cls.ENVIRONMENT,
            "cv_folds": cls.CV_FOLDS,
            "random_state": cls.RANDOM_STATE,
            "registry_path": str(REGISTRY_DIR)
        }

config = MLOpsConfig()
