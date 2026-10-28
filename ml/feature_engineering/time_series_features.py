import pandas as pd
import numpy as np
from typing import List, Optional
from ml.utils.logger import logger

class TimeSeriesFeatureGenerator:
    """
    Enterprise Time-Series Feature Generator for Retail Demand & Sales Forecasting.
    Creates lag features, moving averages, rolling volatility, seasonality,
    and festival/holiday calendar indicators.
    """
    def __init__(
        self,
        target_cols: List[str] = ["revenue", "units_sold"],
        windows: List[int] = [7, 14, 30],
        lags: List[int] = [1, 7, 14, 30]
    ):
        self.target_cols = target_cols
        self.windows = windows
        self.lags = lags

    def generate_features(self, df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
        """Appends lag, rolling window, temporal, and seasonality features to time-series dataframe."""
        logger.info("Generating Time-Series Lag, Rolling, and Seasonality features...")
        df_ts = df.copy()
        
        if date_col in df_ts.columns:
            df_ts[date_col] = pd.to_datetime(df_ts[date_col])
            df_ts = df_ts.sort_values(by=date_col).reset_index(drop=True)
            
            # Calendar Indicators
            df_ts['day_of_week'] = df_ts[date_col].dt.dayofweek
            df_ts['day_of_month'] = df_ts[date_col].dt.day
            df_ts['month'] = df_ts[date_col].dt.month
            df_ts['quarter'] = df_ts[date_col].dt.quarter
            df_ts['is_weekend'] = df_ts['day_of_week'].isin([5, 6]).astype(int)
            
            # Seasonality & Festival Indicators
            df_ts['is_q4_holiday_season'] = df_ts['month'].isin([11, 12]).astype(int)
            df_ts['is_summer_sale'] = (df_ts['month'] == 7).astype(int)
            
            # Cyclical encoding of month and day of week
            df_ts['month_sin'] = np.sin(2 * np.pi * df_ts['month'] / 12.0)
            df_ts['month_cos'] = np.cos(2 * np.pi * df_ts['month'] / 12.0)
            df_ts['dow_sin'] = np.sin(2 * np.pi * df_ts['day_of_week'] / 7.0)
            df_ts['dow_cos'] = np.cos(2 * np.pi * df_ts['day_of_week'] / 7.0)
            
        # 1. Generate Lag Features
        for col in self.target_cols:
            if col in df_ts.columns:
                for lag in self.lags:
                    df_ts[f"{col}_lag_{lag}"] = df_ts[col].shift(lag)
                    
        # 2. Generate Rolling Moving Averages and Volatility
        for col in self.target_cols:
            if col in df_ts.columns:
                for w in self.windows:
                    # Shift 1 to prevent data leakage from current day
                    shifted = df_ts[col].shift(1)
                    df_ts[f"{col}_ma_{w}"] = shifted.rolling(window=w, min_periods=1).mean()
                    df_ts[f"{col}_std_{w}"] = shifted.rolling(window=w, min_periods=1).std().fillna(0.0)
                    df_ts[f"{col}_max_{w}"] = shifted.rolling(window=w, min_periods=1).max()
                    df_ts[f"{col}_min_{w}"] = shifted.rolling(window=w, min_periods=1).min()
                    
        # 3. Revenue Growth Rate & Momentum
        if "revenue" in df_ts.columns:
            df_ts["revenue_growth_wow"] = (df_ts["revenue"] - df_ts["revenue_lag_7"]) / (df_ts["revenue_lag_7"] + 1e-4)
            df_ts["revenue_growth_mom"] = (df_ts["revenue"] - df_ts["revenue_lag_30"]) / (df_ts["revenue_lag_30"] + 1e-4)
            
        # Backfill initial NaN lags with median/mean or 0 to keep dataset intact
        df_ts = df_ts.bfill().fillna(0.0)
        logger.info(f"Time-Series feature generation finalized. Total columns: {len(df_ts.columns)}")
        return df_ts
