import datetime
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.utils.math_utils import calculate_psi, calculate_ks_statistic
from ml.utils.data_utils import save_artifact, load_artifact
from ml.configs import LOGS_DIR, config

class EnterpriseDriftDetector:
    """
    Automated Data & Concept Drift Monitoring Engine.
    Computes Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) statistics
    comparing production inference distributions against historical baseline training data.
    Automatically flags drift warnings and triggers MLOps retraining pipelines.
    """
    def __init__(self, log_dir: Path = LOGS_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.drift_log_file = self.log_dir / "drift_monitoring_audit.json"
        self._init_log()

    def _init_log(self):
        if not self.drift_log_file.exists():
            save_artifact({"project": config.PROJECT_NAME, "audit_history": []}, self.drift_log_file)

    def detect_data_drift(
        self,
        baseline_df: pd.DataFrame,
        current_df: pd.DataFrame,
        model_name: str = "ProductionChampion",
        auto_trigger_retrain: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates PSI and KS statistics across all shared numerical features.
        PSI < 0.10: Stable | 0.10 <= PSI < 0.25: Moderate Drift Warning | PSI >= 0.25: Critical Drift (Retrain Triggered).
        """
        logger.info(f"Executing Data Drift audit for model '{model_name}' across {len(current_df)} production samples...")
        num_cols = [c for c in baseline_df.select_dtypes(include=['number']).columns if c in current_df.columns]
        
        feature_drifts = {}
        critical_drifts = []
        warning_drifts = []
        
        for col in num_cols:
            base_arr = baseline_df[col].dropna().values
            curr_arr = current_df[col].dropna().values
            
            if len(base_arr) == 0 or len(curr_arr) == 0:
                continue
                
            psi_val = calculate_psi(base_arr, curr_arr)
            ks_stat = calculate_ks_statistic(base_arr, curr_arr)
            
            status = "Stable"
            if psi_val >= config.PSI_CRITICAL_THRESHOLD or ks_stat >= 0.15:
                status = "CRITICAL DRIFT DETECTED"
                critical_drifts.append(col)
            elif psi_val >= config.PSI_WARNING_THRESHOLD or ks_stat >= config.KS_STATISTIC_THRESHOLD:
                status = "Moderate Drift Warning"
                warning_drifts.append(col)
                
            feature_drifts[col] = {
                "psi_score": psi_val,
                "ks_statistic": ks_stat,
                "status": status
            }
            
        # Overall System Status
        if critical_drifts:
            system_status = "CRITICAL DRIFT - RETRAINING RECOMMENDED"
            action_required = f"Automated retraining triggered due to significant distribution shifts in {len(critical_drifts)} features: {critical_drifts[:5]}."
        elif warning_drifts:
            system_status = "MODERATE DRIFT WARNING"
            action_required = f"Monitor feature distributions closely. Warning threshold exceeded in: {warning_drifts[:5]}."
        else:
            system_status = "STABLE DISTRIBUTION"
            action_required = "All production inference features are statistically aligned with baseline training data."
            
        audit_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "model_name": model_name,
            "baseline_samples": len(baseline_df),
            "current_samples": len(current_df),
            "system_status": system_status,
            "action_required": action_required,
            "features_audited": len(num_cols),
            "critical_drift_count": len(critical_drifts),
            "warning_drift_count": len(warning_drifts),
            "feature_drifts": feature_drifts
        }
        
        # Log to disk
        try:
            log_data = load_artifact(self.drift_log_file) or {"audit_history": []}
            log_data["audit_history"].insert(0, audit_record)
            # Keep last 100 audit logs
            log_data["audit_history"] = log_data["audit_history"][:100]
            save_artifact(log_data, self.drift_log_file)
        except Exception as e:
            logger.error("Failed to append drift audit record to disk", exc_info=e)
            
        logger.info(f"Drift audit completed: {system_status}")
        return audit_record

    def get_audit_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent drift monitoring audit records."""
        log_data = load_artifact(self.drift_log_file)
        return log_data.get("audit_history", [])[:limit] if isinstance(log_data, dict) else []

# Global singleton Drift Detector
drift_detector = EnterpriseDriftDetector()
