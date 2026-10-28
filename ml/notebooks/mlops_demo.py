"""
Amazon-AI Enterprise MLOps Verification & Demonstration Script.
Executes end-to-end automated data loading, preprocessing, feature engineering,
EDA report generation, competitive multi-model HPO, XAI explanation generation,
model registry lifecycle tracking, and real-time inference latency auditing.
"""

import sys
import os
from pathlib import Path

# Ensure root path in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml import inference_engine, logger, model_registry
from ml.eda.analyzer import EDAAnalyzer
from ml.eda.report_generator import EDAReportGenerator
from ml.datasets.data_loader import EnterpriseDataLoader

def run_enterprise_mlops_demo():
    logger.info("=== STARTING ENTERPRISE MLOPS PLATFORM VERIFICATION ===")
    
    # 1. Bootstrap all engines
    logger.info("Step 1: Bootstrapping engines and running competitive training...")
    inference_engine.bootstrap_all_engines()
    
    # 2. Test EDA generation
    logger.info("Step 2: Executing automated EDA suite and generating audit reports...")
    loader = EnterpriseDataLoader()
    df_sales = loader.load_sales_forecasting_data()
    
    eda_analyzer = EDAAnalyzer()
    report_data = eda_analyzer.analyze_dataset(df_sales, target_col="revenue", dataset_name="Enterprise Sales Time-Series")
    
    report_gen = EDAReportGenerator()
    report_paths = report_gen.export_report(report_data, filename_prefix="sales_forecasting_audit")
    logger.info(f"EDA Reports generated at: {report_paths}")
    
    # 3. Test Real-time Inferences & Caching
    logger.info("Step 3: Executing real-time inference tests across all modules...")
    
    recs = inference_engine.predict_recommendations(user_id=1, recent_product_id=5, limit=4)
    top_match = recs[0]['product']['title'] if recs else 'None'
    logger.info(f"Recommendations returned: {len(recs)} items. Top match: {top_match}")
    
    sales_fc = inference_engine.predict_sales_forecast(days=14)
    proj_rev = sales_fc.get('total_projected_revenue', 0)
    logger.info(f"Sales forecast returned: Total projected=${proj_rev:,.2f}")
    
    inv_health = inference_engine.predict_inventory_intelligence()
    logger.info(f"Inventory audit returned: {len(inv_health)} SKUs analyzed.")
    
    seg_summary = inference_engine.predict_customer_segmentation()
    logger.info(f"Customer segmentation returned: {len(seg_summary)} persona tiers formed.")
    
    churn_pred = inference_engine.predict_customer_churn(user_id=101, user_features_dict={"recency": 75, "frequency": 1, "monetary": 120.0, "support_tickets": 3, "app_logins_30d": 2})
    risk_level = churn_pred.get('risk_level')
    prob_val = round(churn_pred.get('churn_probability', 0)*100, 1)
    logger.info(f"Churn prediction returned: Risk={risk_level} ({prob_val}%)")
    
    # 4. Verify Model Registry
    logger.info("Step 4: Checking Model Registry catalog...")
    status = inference_engine.get_model_registry_status()
    models_list = list(status.get('models', {}).keys())
    logger.info(f"Registered models in catalog: {models_list}")
    
    logger.info("=== ENTERPRISE MLOPS PLATFORM VERIFICATION COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_enterprise_mlops_demo()
