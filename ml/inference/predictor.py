import time
import hashlib
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.monitoring.performance_tracker import performance_tracker
from ml.datasets.data_loader import EnterpriseDataLoader
from ml.recommendation.hybrid import HybridRecommendationEngine
from ml.forecasting.sales_forecaster import EnterpriseSalesForecaster
from ml.inventory.inventory_forecaster import EnterpriseInventoryForecaster
from ml.segmentation.customer_segmenter import EnterpriseCustomerSegmenter
from ml.churn.churn_predictor import EnterpriseChurnPredictor
from ml.model_registry.registry import model_registry

class EnterpriseInferenceEngine:
    """
    High-Performance Unified Real-Time & Batch Inference Engine.
    Provides sub-10ms latency caching, batch processing, and monitors throughput
    across Recommendations, Sales Forecasting, Inventory Intelligence, Segmentation, and Churn.
    """
    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, tuple] = {} # key -> (timestamp, result)
        
        # Core Engines
        self.recommender = HybridRecommendationEngine()
        self.sales_forecaster = EnterpriseSalesForecaster()
        self.inventory_forecaster = EnterpriseInventoryForecaster()
        self.segmenter = EnterpriseCustomerSegmenter()
        self.churn_predictor = EnterpriseChurnPredictor()
        
        self.is_bootstrapped = False

    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        param_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(f"{endpoint}_{param_str}".encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self.cache_ttl:
                return val
            else:
                del self._cache[key]
        return None

    def _set_in_cache(self, key: str, val: Any):
        self._cache[key] = (time.time(), val)

    def bootstrap_all_engines(self, db_session=None):
        """
        Bootstraps data from DB/synthetic generator and trains/loads all models
        into memory for real-time inference.
        """
        if self.is_bootstrapped:
            logger.info("EnterpriseInferenceEngine already bootstrapped.")
            return
            
        logger.info("BOOTSTRAPPING ENTERPRISE MLOPS INFERENCE ENGINE...")
        start_t = time.time()
        loader = EnterpriseDataLoader(db_session)
        
        # 1. Load Data
        df_sales = loader.load_sales_forecasting_data()
        df_churn = loader.load_customer_churn_data()
        df_inv = loader.load_inventory_data()
        
        # Construct synthetic interactions for recs
        interactions = []
        for u in range(1, 51):
            for p in range(1, min(30, len(df_inv) + 1)):
                if (u + p) % 3 == 0:
                    interactions.append({"user_id": u, "product_id": p, "rating": float((u * p) % 5 + 1)})
        df_inter = pd.DataFrame(interactions)
        
        # 2. Fit Engines
        logger.info("Fitting Hybrid Recommendation Engine...")
        self.recommender.fit(df_inv, df_inter)
        
        logger.info("Fitting Multi-Model Sales Forecaster...")
        self.sales_forecaster.fit_and_compare(df_sales)
        
        logger.info("Fitting Multi-Algorithm Customer Segmenter...")
        self.segmenter.fit_and_cluster(df_churn)
        
        logger.info("Fitting Multi-Model Churn Predictor...")
        self.churn_predictor.fit_and_compare(df_churn)
        
        self.is_bootstrapped = True
        elapsed = round(time.time() - start_t, 2)
        logger.info(f"BOOTSTRAP COMPLETE in {elapsed} seconds! All MLOps engines are READY and Online.")

    # --- Real-Time Inference Endpoints ---

    def predict_recommendations(self, user_id: Optional[int] = None, recent_product_id: Optional[int] = None, limit: int = 6) -> List[Dict[str, Any]]:
        """Returns personalized recommendations with caching and latency tracking."""
        start_t = time.time()
        if not self.is_bootstrapped:
            self.bootstrap_all_engines()
        cache_key = self._get_cache_key("/predict/recommendation", {"u": user_id, "p": recent_product_id, "l": limit})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            performance_tracker.track_inference("/predict/recommendation", start_t, cache_hit=True)
            return cached
            
        try:
            results = self.recommender.get_personalized_recommendations(user_id=user_id, recent_product_id=recent_product_id, top_n=limit)
            self._set_in_cache(cache_key, results)
            performance_tracker.track_inference("/predict/recommendation", start_t, cache_hit=False)
            return results
        except Exception as e:
            logger.error("Recommendation inference error", exc_info=e)
            performance_tracker.track_inference("/predict/recommendation", start_t, cache_hit=False, error=str(e))
            return []

    def predict_sales_forecast(self, days: int = 30, db_session=None) -> Dict[str, Any]:
        """Returns sales forecast trajectory with 95% confidence bounds."""
        start_t = time.time()
        if not self.is_bootstrapped:
            self.bootstrap_all_engines(db_session)
        cache_key = self._get_cache_key("/predict/sales", {"days": days})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            performance_tracker.track_inference("/predict/sales", start_t, cache_hit=True)
            return cached
            
        try:
            loader = EnterpriseDataLoader(db_session)
            df_sales = loader.load_sales_forecasting_data()
            results = self.sales_forecaster.predict_future(df_sales, days=days)
            self._set_in_cache(cache_key, results)
            performance_tracker.track_inference("/predict/sales", start_t, cache_hit=False)
            return results
        except Exception as e:
            logger.error("Sales forecast inference error", exc_info=e)
            performance_tracker.track_inference("/predict/sales", start_t, cache_hit=False, error=str(e))
            return {}

    def predict_inventory_intelligence(self, db_session=None) -> List[Dict[str, Any]]:
        """Returns inventory SKU health, safety stock, and reorder alerts."""
        start_t = time.time()
        if not self.is_bootstrapped:
            self.bootstrap_all_engines(db_session)
        cache_key = self._get_cache_key("/predict/inventory", {})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            performance_tracker.track_inference("/predict/inventory", start_t, cache_hit=True)
            return cached
            
        try:
            loader = EnterpriseDataLoader(db_session)
            df_inv = loader.load_inventory_data()
            results = self.inventory_forecaster.analyze_inventory_health(df_inv)
            self._set_in_cache(cache_key, results)
            performance_tracker.track_inference("/predict/inventory", start_t, cache_hit=False)
            return results
        except Exception as e:
            logger.error("Inventory intelligence error", exc_info=e)
            performance_tracker.track_inference("/predict/inventory", start_t, cache_hit=False, error=str(e))
            return []

    def predict_customer_segmentation(self, db_session=None) -> List[Dict[str, Any]]:
        """Returns customer marketing personas and RFM segmentation breakdown."""
        start_t = time.time()
        if not self.is_bootstrapped:
            self.bootstrap_all_engines(db_session)
        cache_key = self._get_cache_key("/predict/segmentation", {})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            performance_tracker.track_inference("/predict/segmentation", start_t, cache_hit=True)
            return cached
            
        try:
            loader = EnterpriseDataLoader(db_session)
            df_churn = loader.load_customer_churn_data()
            seg_report = self.segmenter.fit_and_cluster(df_churn)
            summary = self.segmenter.get_segmentation_summary(seg_report["segmented_dataframe"])
            self._set_in_cache(cache_key, summary)
            performance_tracker.track_inference("/predict/segmentation", start_t, cache_hit=False)
            return summary
        except Exception as e:
            logger.error("Customer segmentation error", exc_info=e)
            performance_tracker.track_inference("/predict/segmentation", start_t, cache_hit=False, error=str(e))
            return []

    def predict_customer_churn(self, user_id: int, user_features_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Returns churn probability, risk tier, XAI triggers, and retention strategy."""
        start_t = time.time()
        if not self.is_bootstrapped:
            self.bootstrap_all_engines()
        cache_key = self._get_cache_key("/predict/churn", {"u": user_id, "f": user_features_dict})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            performance_tracker.track_inference("/predict/churn", start_t, cache_hit=True)
            return cached
            
        try:
            if user_features_dict:
                df_u = pd.DataFrame([user_features_dict])
            else:
                df_u = pd.DataFrame([{"recency": 25, "frequency": 8, "monetary": 650.0, "support_tickets": 1, "app_logins_30d": 15}])
                
            results = self.churn_predictor.predict_user_churn(df_u, user_id=user_id)
            self._set_in_cache(cache_key, results)
            performance_tracker.track_inference("/predict/churn", start_t, cache_hit=False)
            return results
        except Exception as e:
            logger.error("Churn prediction error", exc_info=e)
            performance_tracker.track_inference("/predict/churn", start_t, cache_hit=False, error=str(e))
            return {}

    def predict_trending(self, limit: int = 8) -> List[Dict[str, Any]]:
        """Returns trending bestsellers based on popularity velocity and ratings."""
        start_t = time.time()
        if not self.is_bootstrapped:
            self.bootstrap_all_engines()
        cache_key = self._get_cache_key("/predict/trending", {"l": limit})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            performance_tracker.track_inference("/predict/trending", start_t, cache_hit=True)
            return cached
            
        try:
            top_pop = sorted(self.recommender.popularity_map.items(), key=lambda x: x[1], reverse=True)[:limit]
            results = []
            for pid, score in top_pop:
                prod = self.recommender.product_catalog.get(pid, {"id": pid, "title": f"Product {pid}", "price": 49.99, "rating": 4.8, "reviews_count": 120})
                results.append({
                    "product": prod,
                    "explanation": {
                        "reason": f"High velocity bestseller ({round(score*100, 1)}% popularity index) with positive reviews.",
                        "confidence": round(float(score), 4),
                        "important_features": [
                            {"feature": "Sales Velocity & Ratings", "impact": "High Positive", "value": "Top Bestseller", "weight": round(float(score), 4)}
                        ],
                        "recommendation": "Trending Choice"
                    }
                })
            self._set_in_cache(cache_key, results)
            performance_tracker.track_inference("/predict/trending", start_t, cache_hit=False)
            return results
        except Exception as e:
            logger.error("Trending prediction error", exc_info=e)
            performance_tracker.track_inference("/predict/trending", start_t, cache_hit=False, error=str(e))
            return []

    def get_model_version(self) -> Dict[str, Any]:
        """Returns active production champion versions and system metadata."""
        status = self.get_model_registry_status()
        champions = status.get("production_champions", {})
        return {
            "platform_version": "2.4.0-PROD",
            "active_champions": {name: m.get("version", "v1.0.0") for name, m in champions.items()},
            "system_status": "ONLINE - High Fidelity Enterprise MLOps Active",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def get_model_registry_status(self) -> Dict[str, Any]:
        """Returns catalog of registered model versions and production champions."""
        return model_registry.list_models()

# Global singleton Inference Engine
inference_engine = EnterpriseInferenceEngine()

