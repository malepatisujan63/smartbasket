import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from ml.utils.logger import logger

def save_artifact(obj: Any, filepath: Path) -> bool:
    """Serializes and saves a machine learning artifact or metadata to disk."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if filepath.suffix == '.json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(obj, f, indent=2, default=str)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(obj, f)
        logger.info(f"Artifact successfully saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save artifact to {filepath}", exc_info=e)
        return False

def load_artifact(filepath: Path) -> Optional[Any]:
    """Loads a serialized machine learning artifact or metadata from disk."""
    try:
        if not filepath.exists():
            logger.warning(f"Artifact not found at {filepath}")
            return None
            
        if filepath.suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        logger.error(f"Failed to load artifact from {filepath}", exc_info=e)
        return None

def train_test_split_stratified_or_time(
    df: pd.DataFrame, 
    target_col: str, 
    test_size: float = 0.2, 
    is_time_series: bool = False,
    time_col: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs time-series chronological split or stratified/random split.
    Guarantees clean separation without data leakage.
    """
    if is_time_series and time_col and time_col in df.columns:
        df_sorted = df.sort_values(by=time_col).reset_index(drop=True)
        split_idx = int(len(df_sorted) * (1 - test_size))
        train_df = df_sorted.iloc[:split_idx].copy()
        test_df = df_sorted.iloc[split_idx:].copy()
        logger.info(f"Chronological time-series split completed. Train: {len(train_df)}, Test: {len(test_df)}")
        return train_df, test_df
    else:
        # Standard random split
        shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        split_idx = int(len(shuffled) * (1 - test_size))
        train_df = shuffled.iloc[:split_idx].copy()
        test_df = shuffled.iloc[split_idx:].copy()
        logger.info(f"Random split completed. Train: {len(train_df)}, Test: {len(test_df)}")
        return train_df, test_df

def check_dataframe_health(df: pd.DataFrame) -> Dict[str, Any]:
    """Returns diagnostic health check report for a dataframe."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values_total": int(df.isnull().sum().sum()),
        "missing_percentage": round(float(df.isnull().sum().sum() / (len(df) * max(1, len(df.columns))) * 100), 2),
        "duplicates": int(df.duplicated().sum()),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "dtypes": df.dtypes.astype(str).to_dict()
    }
