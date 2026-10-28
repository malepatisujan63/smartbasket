import numpy as np
from typing import List, Dict, Any, Union

def cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
    """Computes pairwise cosine similarity matrix efficiently using NumPy."""
    norm = np.linalg.norm(matrix, axis=1, keepdims=True)
    # Avoid division by zero
    norm[norm == 0] = 1e-10
    normalized_matrix = matrix / norm
    return np.dot(normalized_matrix, normalized_matrix.T)

def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
    """
    Computes Population Stability Index (PSI) to quantify Data Drift between two distributions.
    PSI < 0.1: No significant drift.
    0.1 <= PSI < 0.25: Moderate drift warning.
    PSI >= 0.25: Significant drift (Trigger retraining).
    """
    try:
        # Remove NaNs
        expected = expected[~np.isnan(expected)]
        actual = actual[~np.isnan(actual)]
        
        if len(expected) == 0 or len(actual) == 0:
            return 0.0
            
        percentiles = np.linspace(0, 100, num_buckets + 1)
        buckets = np.percentile(expected, percentiles)
        buckets[0] = -np.inf
        buckets[-1] = np.inf
        
        expected_counts, _ = np.histogram(expected, bins=buckets)
        actual_counts, _ = np.histogram(actual, bins=buckets)
        
        # Add epsilon to prevent div by zero / log zero
        eps = 1e-4
        expected_pct = (expected_counts + eps) / (len(expected) + eps * num_buckets)
        actual_pct = (actual_counts + eps) / (len(actual) + eps * num_buckets)
        
        psi_value = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(round(psi_value, 4))
    except Exception:
        return 0.0

def calculate_ks_statistic(data1: np.ndarray, data2: np.ndarray) -> float:
    """
    Computes two-sample Kolmogorov-Smirnov test statistic approximation for distribution drift.
    """
    try:
        data1 = np.sort(data1[~np.isnan(data1)])
        data2 = np.sort(data2[~np.isnan(data2)])
        
        if len(data1) == 0 or len(data2) == 0:
            return 0.0
            
        data_all = np.concatenate([data1, data2])
        cdf1 = np.searchsorted(data1, data_all, side='right') / len(data1)
        cdf2 = np.searchsorted(data2, data_all, side='right') / len(data2)
        
        ks_stat = np.max(np.abs(cdf1 - cdf2))
        return float(round(ks_stat, 4))
    except Exception:
        return 0.0
