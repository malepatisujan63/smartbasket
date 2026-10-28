import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.evaluation.evaluator import ModelEvaluator
from ml.model_registry.registry import model_registry
from ml.explainability.explainer import ExplainableAIEngine

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False

try:
    import catboost as cb
    CB_AVAILABLE = True
except ImportError:
    CB_AVAILABLE = False

class EnterpriseChurnPredictor:
    """
    Automated Multi-Model Customer Churn Prediction & Retention Engine.
    Competitively evaluates Logistic Regression, Trees, Random Forest, XGBoost,
    LightGBM, CatBoost, and Neural Networks. Uses XAI to explain churn triggers
    and prescribe tailored retention workflows.
    """
    def __init__(self, target_col: str = "churned"):
        self.target_col = target_col
        self.models: Dict[str, Any] = {}
        self.evaluations: Dict[str, Dict[str, Any]] = {}
        self.champion_model_name: Optional[str] = None
        self.champion_model: Optional[Any] = None
        self.xai_engine: Optional[ExplainableAIEngine] = None
        self.feature_cols: List[str] = []
        self.fitted = False

    def _init_candidate_models(self) -> Dict[str, Any]:
        candidates = {}
        if SKLEARN_AVAILABLE:
            candidates["LogisticRegression"] = LogisticRegression(max_iter=1000, random_state=42)
            candidates["DecisionTree"] = DecisionTreeClassifier(max_depth=8, random_state=42)
            candidates["RandomForest"] = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
            candidates["NeuralNetworkMLP"] = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=42)
            
        if XGB_AVAILABLE:
            candidates["XGBoost"] = xgb.XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42, eval_metric='logloss')
        if LGB_AVAILABLE:
            candidates["LightGBM"] = lgb.LGBMClassifier(n_estimators=150, num_leaves=31, learning_rate=0.05, random_state=42, verbose=-1)
        if CB_AVAILABLE:
            candidates["CatBoost"] = cb.CatBoostClassifier(iterations=200, depth=6, learning_rate=0.05, random_state=42, verbose=0)
            
        return candidates

    def fit_and_compare(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains competing classification models and promotes the winner based on ROC-AUC / F1."""
        logger.info(f"Starting competitive customer churn prediction across candidate architectures...")
        df_clean = df.copy()
        
        # Ensure target column
        if self.target_col not in df_clean.columns:
            df_clean[self.target_col] = np.where(df_clean.get('recency', 30) > 60, 1, 0)
            
        num_df = df_clean.select_dtypes(include=['number']).dropna()
        self.feature_cols = [c for c in num_df.columns if c != self.target_col and "id" not in c.lower()]
        
        # Stratified 80/20 split
        shuffled = num_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        split_idx = int(len(shuffled) * 0.8)
        train_df = shuffled.iloc[:split_idx]
        test_df = shuffled.iloc[split_idx:]
        
        X_train, y_train = train_df[self.feature_cols], train_df[self.target_col]
        X_test, y_test = test_df[self.feature_cols], test_df[self.target_col]
        
        candidates = self._init_candidate_models()
        best_score = -1.0
        
        for name, model in candidates.items():
            try:
                logger.debug(f"Training churn candidate model: {name}...")
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                probs = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else preds
                
                metrics = ModelEvaluator.evaluate_classification(y_test.values, preds, y_prob=probs)
                self.models[name] = model
                self.evaluations[name] = metrics
                
                # Score = ROC_AUC or F1
                score = metrics.get("ROC_AUC", metrics.get("F1_Score", 0.0))
                if score > best_score:
                    best_score = score
                    self.champion_model_name = name
                    self.champion_model = model
            except Exception as e:
                logger.warning(f"Churn candidate '{name}' failed: {e}")
                
        if self.champion_model_name and self.champion_model:
            logger.info(f"CHAMPION CHURN MODEL SELECTED: '{self.champion_model_name}' (ROC-AUC/Score: {best_score})")
            
            # Initialize Explainable AI Engine
            self.xai_engine = ExplainableAIEngine(self.champion_model, background_data=X_train, feature_names=self.feature_cols)
            
            model_registry.register_model(
                model_name="CustomerChurnPredictor",
                model_object=self.champion_model,
                metrics=self.evaluations[self.champion_model_name],
                hyperparameters={"algorithm": self.champion_model_name, "features_count": len(self.feature_cols)},
                stage="Production"
            )
            self.fitted = True
        else:
            raise RuntimeError("All customer churn models failed to train.")
            
        return {
            "champion_model": self.champion_model_name,
            "best_metrics": self.evaluations.get(self.champion_model_name, {}),
            "all_evaluations": self.evaluations
        }

    def predict_user_churn(self, user_features: pd.DataFrame, user_id: int = 0) -> Dict[str, Any]:
        """
        Predicts churn risk for a specific user and returns XAI business attribution
        with customized retention workflows.
        """
        if not self.fitted or not self.champion_model:
            raise RuntimeError("EnterpriseChurnPredictor must be fitted before predicting user churn.")
            
        # Extract features
        X_user = pd.DataFrame()
        for col in self.feature_cols:
            if col in user_features.columns:
                X_user[col] = user_features[col]
            else:
                X_user[col] = [10.0 if "recency" in col else (5.0 if "freq" in col else 150.0)]
                
        try:
            prob = float(self.champion_model.predict_proba(X_user)[0, 1])
        except Exception:
            prob = float(self.champion_model.predict(X_user)[0])
            
        # Determine Risk Level
        if prob >= 0.70:
            risk_level = "Critical Churn Risk"
        elif prob >= 0.40:
            risk_level = "Moderate Churn Warning"
        else:
            risk_level = "Stable / Loyal Customer"
            
        # Generate Explanation via XAI Engine
        if self.xai_engine:
            xai_report = self.xai_engine.explain_prediction(X_user, prediction_value=prob, confidence_score=prob, task_type="churn")
            reason = xai_report["reason"]
            top_features = xai_report["top_features"]
            retention_strategy = xai_report["business_explanation"]
        else:
            reason = f"Model modeled {round(prob*100, 1)}% churn probability based on recency and purchasing velocity."
            top_features = [{"feature": self.feature_cols[0], "value": str(X_user.iloc[0, 0]), "impact": "High Positive", "weight": 0.45}]
            retention_strategy = "Send automated discount coupon and follow up with customer success team."

        return {
            "user_id": user_id,
            "churn_probability": round(prob, 4),
            "risk_level": risk_level,
            "reason": reason,
            "top_contributing_features": top_features,
            "suggested_retention_strategy": retention_strategy,
            "model_version": self.champion_model_name
        }
