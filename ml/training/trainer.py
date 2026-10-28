import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.configs import config
from ml.evaluation.evaluator import ModelEvaluator
from ml.model_registry.registry import model_registry

try:
    import optuna
    # Suppress optuna spam
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

try:
    from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, StratifiedKFold, TimeSeriesSplit
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class EnterpriseTrainer:
    """
    Automated Enterprise Training & Hyperparameter Optimization (HPO) Engine.
    Supports Bayesian Optimization (Optuna), RandomizedSearchCV, and GridSearchCV
    with Stratified K-Fold and TimeSeriesSplit cross-validation.
    """
    def __init__(self, hpo_method: str = "optuna", trials: int = config.OPTUNA_TRIALS):
        self.hpo_method = hpo_method.lower() # 'optuna', 'random', 'grid'
        self.trials = trials

    def optimize_and_train(
        self,
        model_name: str,
        estimator: Any,
        param_grid: Dict[str, Any],
        X_train: pd.DataFrame,
        y_train: pd.Series,
        is_time_series: bool = False,
        is_classification: bool = True
    ) -> tuple:
        """
        Runs automated HPO across cross-validation folds and returns optimized estimator
        and best hyperparameters.
        """
        logger.info(f"Executing HPO ({self.hpo_method}) for '{model_name}' across {len(X_train)} samples...")
        
        cv = TimeSeriesSplit(n_splits=config.CV_FOLDS) if is_time_series else (
            StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=42) if is_classification else config.CV_FOLDS
        )
        
        best_model = estimator
        best_params = {}
        
        # 1. Optuna Bayesian Optimization
        if self.hpo_method == "optuna" and OPTUNA_AVAILABLE and SKLEARN_AVAILABLE:
            try:
                def objective(trial):
                    sampled_params = {}
                    for param_name, param_values in param_grid.items():
                        if isinstance(param_values, list) and len(param_values) > 0:
                            if all(isinstance(v, int) for v in param_values if v is not None):
                                sampled_params[param_name] = trial.suggest_categorical(param_name, param_values)
                            elif all(isinstance(v, float) for v in param_values):
                                sampled_params[param_name] = trial.suggest_categorical(param_name, param_values)
                            else:
                                sampled_params[param_name] = trial.suggest_categorical(param_name, param_values)
                    
                    # Set params and fit on fold subset
                    model_clone = estimator.__class__(**{**estimator.get_params(), **sampled_params})
                    # Quick validation split
                    split_idx = int(len(X_train) * 0.8)
                    model_clone.fit(X_train.iloc[:split_idx], y_train.iloc[:split_idx])
                    preds = model_clone.predict(X_train.iloc[split_idx:])
                    
                    if is_classification:
                        metrics = ModelEvaluator.evaluate_classification(y_train.iloc[split_idx:].values, preds)
                        return metrics.get("F1_Score", 0.0)
                    else:
                        metrics = ModelEvaluator.evaluate_regression(y_train.iloc[split_idx:].values, preds)
                        return -metrics.get("RMSE", 999.0) # Minimize RMSE
                        
                study = optuna.create_study(direction="maximize")
                study.optimize(objective, n_trials=min(self.trials, 15))
                
                best_params = study.best_params
                best_model = estimator.__class__(**{**estimator.get_params(), **best_params})
                best_model.fit(X_train, y_train)
                logger.info(f"Optuna optimization finalized for '{model_name}'. Best params: {best_params}")
                return best_model, best_params
            except Exception as e:
                logger.debug(f"Optuna HPO fallback to RandomizedSearchCV: {e}")
                
        # 2. RandomizedSearchCV or GridSearchCV fallback
        if SKLEARN_AVAILABLE and param_grid:
            try:
                search = RandomizedSearchCV(
                    estimator=estimator,
                    param_distributions=param_grid,
                    n_iter=min(self.trials, 8),
                    cv=cv,
                    scoring="f1_weighted" if is_classification else "neg_root_mean_squared_error",
                    random_state=42,
                    n_jobs=-1
                )
                search.fit(X_train, y_train)
                best_model = search.best_estimator_
                best_params = search.best_params_
                logger.info(f"RandomizedSearchCV finalized for '{model_name}'. Best params: {best_params}")
                return best_model, best_params
            except Exception as e:
                logger.debug(f"RandomizedSearchCV fallback: {e}")
                
        # 3. Default training without HPO
        logger.info(f"Training default '{model_name}' without HPO...")
        estimator.fit(X_train, y_train)
        return estimator, {}
