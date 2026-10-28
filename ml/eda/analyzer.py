import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger

class EDAAnalyzer:
    """
    Automated Exploratory Data Analysis (EDA) Engine.
    Generates statistical summaries, distribution statistics, correlation matrices,
    missing value heatmaps, boxplot/outlier profiles, and time-series trend breakdowns.
    """
    def __init__(self):
        self.report_data: Dict[str, Any] = {}

    def analyze_dataset(self, df: pd.DataFrame, target_col: Optional[str] = None, dataset_name: str = "Enterprise Dataset") -> Dict[str, Any]:
        """Executes full automated EDA suite across numerical, categorical, and temporal features."""
        logger.info(f"Executing automated EDA suite on '{dataset_name}' ({len(df)} rows, {len(df.columns)} cols)...")
        
        # 1. Dataset Summary & Missing Values
        missing_series = df.isnull().sum()
        missing_heatmap = {col: int(val) for col, val in missing_series.items() if val > 0}
        
        summary = {
            "dataset_name": dataset_name,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_cells_total": int(missing_series.sum()),
            "missing_percentage_global": round(float(missing_series.sum() / (len(df) * max(1, len(df.columns))) * 100), 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            "dtypes_breakdown": {
                "numerical": len(df.select_dtypes(include=['number']).columns),
                "categorical": len(df.select_dtypes(include=['object', 'category', 'string']).columns),
                "datetime": len(df.select_dtypes(include=['datetime', 'datetimetz']).columns)
            }
        }
        
        # 2. Distribution Analysis & Histograms / Boxplots
        num_cols = df.select_dtypes(include=['number']).columns
        distributions = {}
        boxplots = {}
        for col in num_cols:
            col_clean = df[col].dropna()
            if len(col_clean) == 0:
                continue
            mean_val = float(col_clean.mean())
            std_val = float(col_clean.std())
            q25 = float(col_clean.quantile(0.25))
            median_val = float(col_clean.median())
            q75 = float(col_clean.quantile(0.75))
            iqr = q75 - q25
            
            # Outlier count via 1.5 * IQR
            outliers_count = int(((col_clean < q25 - 1.5 * iqr) | (col_clean > q75 + 1.5 * iqr)).sum())
            
            distributions[col] = {
                "mean": round(mean_val, 4),
                "std": round(std_val, 4),
                "min": round(float(col_clean.min()), 4),
                "25%": round(q25, 4),
                "median": round(median_val, 4),
                "75%": round(q75, 4),
                "max": round(float(col_clean.max()), 4),
                "skewness": round(float(col_clean.skew()), 4),
                "kurtosis": round(float(col_clean.kurtosis()), 4)
            }
            boxplots[col] = {
                "q1": round(q25, 4),
                "median": round(median_val, 4),
                "q3": round(q75, 4),
                "iqr": round(iqr, 4),
                "outliers_detected": outliers_count,
                "outlier_percentage": round((outliers_count / max(1, len(col_clean))) * 100, 2)
            }
            
        # 3. Correlation Matrix & Multicollinearity
        corr_matrix = {}
        if len(num_cols) >= 2:
            corr_df = df[num_cols].corr().round(4).fillna(0.0)
            corr_matrix = corr_df.to_dict()
            
        # 4. Category Analysis
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns
        category_analysis = {}
        for col in cat_cols[:10]: # Analyze top 10 categorical columns
            val_counts = df[col].value_counts().head(10).to_dict()
            category_analysis[col] = {
                "unique_cardinality": int(df[col].nunique()),
                "top_10_categories": {str(k): int(v) for k, v in val_counts.items()},
                "missing_count": int(df[col].isnull().sum())
            }
            
        # 5. Time Series Trends (Sales, Revenue, Customer, Product)
        time_series_trends = {}
        date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower() or pd.api.types.is_datetime64_any_dtype(df[c])]
        if date_cols and len(num_cols) > 0:
            dcol = date_cols[0]
            try:
                df_temp = df.copy()
                df_temp[dcol] = pd.to_datetime(df_temp[dcol])
                df_temp = df_temp.sort_values(by=dcol)
                df_temp['year_month'] = df_temp[dcol].dt.to_period('M').astype(str)
                
                # Aggregate revenue or numerical sums monthly
                agg_dict = {col: "sum" if "rev" in col.lower() or "sales" in col.lower() or "unit" in col.lower() else "mean" for col in num_cols[:4]}
                monthly_trend = df_temp.groupby('year_month').agg(agg_dict).round(2).to_dict()
                time_series_trends["monthly_aggregation"] = monthly_trend
                time_series_trends["date_range"] = {
                    "start": str(df_temp[dcol].min().date()),
                    "end": str(df_temp[dcol].max().date()),
                    "total_days": int((df_temp[dcol].max() - df_temp[dcol].min()).days)
                }
            except Exception as e:
                logger.debug(f"Time series trend aggregation fallback: {e}")
                
        self.report_data = {
            "summary": summary,
            "missing_heatmap": missing_heatmap,
            "distributions": distributions,
            "boxplots": boxplots,
            "correlation_matrix": corr_matrix,
            "category_analysis": category_analysis,
            "time_series_trends": time_series_trends
        }
        logger.info(f"Automated EDA completed for '{dataset_name}'.")
        return self.report_data
