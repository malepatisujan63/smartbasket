import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger

class RFMFeatureGenerator:
    """
    Advanced Customer RFM & Behavioral Feature Generator.
    Calculates Recency, Frequency, Monetary metrics, Customer Lifetime Value (CLV),
    Customer Engagement Score, and Behavioral Archetypes.
    """
    def __init__(self, recency_bins: int = 5, frequency_bins: int = 5, monetary_bins: int = 5):
        self.r_bins = recency_bins
        self.f_bins = frequency_bins
        self.m_bins = monetary_bins

    def generate_rfm_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes raw customer transaction dataframe and appends RFM quintiles,
        CLV projections, Engagement Scores, and Behavior Segment labels.
        """
        logger.info("Generating RFM and Customer Behavioral features...")
        df_rfm = df.copy()
        
        # Ensure base columns exist
        required = ['recency', 'frequency', 'monetary']
        for col in required:
            if col not in df_rfm.columns:
                logger.warning(f"Column '{col}' not found. Defaulting to 0/1.")
                df_rfm[col] = 1 if col == 'frequency' else (100.0 if col == 'monetary' else 30)
                
        # 1. Calculate RFM Scores (1 to 5)
        # Recency: lower is better (5 is best)
        try:
            df_rfm['R_Score'] = pd.qcut(df_rfm['recency'], q=self.r_bins, labels=range(self.r_bins, 0, -1), duplicates='drop').astype(int)
        except Exception:
            df_rfm['R_Score'] = 3
            
        # Frequency: higher is better (5 is best)
        try:
            df_rfm['F_Score'] = pd.qcut(df_rfm['frequency'].rank(method='first'), q=self.f_bins, labels=range(1, self.f_bins + 1), duplicates='drop').astype(int)
        except Exception:
            df_rfm['F_Score'] = 3
            
        # Monetary: higher is better (5 is best)
        try:
            df_rfm['M_Score'] = pd.qcut(df_rfm['monetary'].rank(method='first'), q=self.m_bins, labels=range(1, self.m_bins + 1), duplicates='drop').astype(int)
        except Exception:
            df_rfm['M_Score'] = 3
            
        # Composite RFM Score & String
        df_rfm['RFM_Composite'] = (df_rfm['R_Score'] * 100) + (df_rfm['F_Score'] * 10) + df_rfm['M_Score']
        df_rfm['RFM_Score_Sum'] = df_rfm['R_Score'] + df_rfm['F_Score'] + df_rfm['M_Score']
        
        # 2. Customer Lifetime Value (CLV Projection)
        # Formula: Monetary * (1 + Frequency * 0.1) * (1 / max(1, Recency/30))
        df_rfm['CLV_Projected'] = round(df_rfm['monetary'] * (1.0 + df_rfm['frequency'] * 0.15) * (30.0 / np.maximum(10.0, df_rfm['recency'])), 2)
        
        # 3. Customer Engagement & Behavior Score
        tickets = df_rfm['support_tickets'] if 'support_tickets' in df_rfm.columns else 0
        logins = df_rfm['app_logins_30d'] if 'app_logins_30d' in df_rfm.columns else 10
        
        df_rfm['Engagement_Score'] = round((logins * 2.0) + (df_rfm['frequency'] * 5.0) - (tickets * 8.0), 1)
        df_rfm['Engagement_Score'] = df_rfm['Engagement_Score'].clip(lower=0.0, upper=100.0)
        
        # 4. Behavioral Archetype Assignment
        def assign_segment(row):
            r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
            if r >= 4 and f >= 4 and m >= 4:
                return "VIP Champions"
            elif f >= 4 and m >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2:
                return "Recent New Buyers"
            elif r <= 2 and f >= 3:
                return "At-Risk Loyalists"
            elif r <= 2 and f <= 2:
                return "Inactive / Lost Customers"
            else:
                return "Potential Loyalists"
                
        df_rfm['Behavior_Segment'] = df_rfm.apply(assign_segment, axis=1)
        logger.info("RFM feature generation completed.")
        return df_rfm
