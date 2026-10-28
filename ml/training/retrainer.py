import datetime
import pandas as pd
from typing import Dict, Any, Optional
from ml.utils.logger import logger
from ml.monitoring.drift_detector import drift_detector
from ml.forecasting.sales_forecaster import EnterpriseSalesForecaster
from ml.churn.churn_predictor import EnterpriseChurnPredictor

class EnterpriseRetrainer:
    """
    Automated MLOps Retraining & Continuous Learning Pipeline.
    Monitors data drift (PSI / KS-test) and automatically triggers full retraining
    and champion model promotion when distribution drift exceeds thresholds.
    """
    def __init__(self):
        self.last_retrain_date: Optional[str] = None
        self.retrain_history: list = []

    def check_and_retrain_sales_forecaster(
        self,
        baseline_df: pd.DataFrame,
        current_df: pd.DataFrame,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """Checks sales data drift and triggers retraining if PSI >= 0.25 or force_retrain is True."""
        logger.info("Evaluating MLOps Retraining triggers for Sales Forecaster...")
        
        drift_report = drift_detector.detect_data_drift(baseline_df, current_df, model_name="SalesForecaster")
        should_retrain = force_retrain or (drift_report["system_status"] == "CRITICAL DRIFT - RETRAINING RECOMMENDED")
        
        if not should_retrain:
            logger.info("No critical data drift detected. Current Production Champion remains active.")
            return {"status": "NO_RETRAIN_NEEDED", "drift_report": drift_report}
            
        logger.warning("RETRAINING TRIGGERED: Starting full multi-model competitive re-evaluation for Sales Forecaster...")
        forecaster = EnterpriseSalesForecaster()
        
        # Combine historical baseline and current data for fresh training
        combined_df = pd.concat([baseline_df, current_df], ignore_index=True)
        results = forecaster.fit_and_compare(combined_df)
        
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "target": "sales_forecaster",
            "trigger": "FORCE_RETRAIN" if force_retrain else "DATA_DRIFT_PSI",
            "new_champion": results["champion_model"],
            "metrics": results["best_metrics"]
        }
        self.retrain_history.append(record)
        self.last_retrain_date = record["timestamp"]
        
        logger.info(f"RETRAINING SUCCESSFUL: Promoted new champion '{results['champion_model']}' to Production.")
        return {"status": "RETRAINED_AND_PROMOTED", "retrain_record": record, "drift_report": drift_report}

    def check_and_retrain_churn_predictor(
        self,
        baseline_df: pd.DataFrame,
        current_df: pd.DataFrame,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """Checks customer churn data drift and triggers retraining if needed."""
        logger.info("Evaluating MLOps Retraining triggers for Churn Predictor...")
        
        drift_report = drift_detector.detect_data_drift(baseline_df, current_df, model_name="ChurnPredictor")
        should_retrain = force_retrain or (drift_report["system_status"] == "CRITICAL DRIFT - RETRAINING RECOMMENDED")
        
        if not should_retrain:
            logger.info("No critical data drift detected for Customer Churn models.")
            return {"status": "NO_RETRAIN_NEEDED", "drift_report": drift_report}
            
        logger.warning("RETRAINING TRIGGERED: Starting full multi-model competitive re-evaluation for Churn Predictor...")
        predictor = EnterpriseChurnPredictor()
        
        combined_df = pd.concat([baseline_df, current_df], ignore_index=True)
        results = predictor.fit_and_compare(combined_df)
        
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "target": "churn_predictor",
            "trigger": "FORCE_RETRAIN" if force_retrain else "DATA_DRIFT_PSI",
            "new_champion": results["champion_model"],
            "metrics": results["best_metrics"]
        }
        self.retrain_history.append(record)
        
        logger.info(f"RETRAINING SUCCESSFUL: Promoted new churn champion '{results['champion_model']}' to Production.")
        return {"status": "RETRAINED_AND_PROMOTED", "retrain_record": record, "drift_report": drift_report}

# Global singleton Retrainer
retrainer = EnterpriseRetrainer()
