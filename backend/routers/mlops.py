from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database.connection import get_db
from ml import inference_engine, logger

router = APIRouter(tags=["MLOps & AI Enterprise Intelligence"])

@router.get("/predict/recommendation")
@router.get("/api/mlops/predict/recommendation")
def get_personalized_recommendations(
    user_id: Optional[int] = Query(None, description="Shopper User ID for collaborative filtering"),
    session_id: Optional[str] = Query(None, description="Session ID for guest shoppers"),
    recent_product_id: Optional[int] = Query(None, description="Recently viewed Product ID for content similarity"),
    limit: int = Query(6, ge=1, le=24, description="Number of recommendations to return")
):
    """
    Returns Top-N hybrid personalized recommendations (Ensemble of Content-Based SVD,
    Collaborative Filtering NCF/SVD, and Bestseller Popularity Velocity) with SHAP/XAI explanations.
    """
    try:
        return inference_engine.predict_recommendations(
            user_id=user_id,
            recent_product_id=recent_product_id,
            session_id=session_id,
            limit=limit
        )
    except Exception as e:
        logger.error("Endpoint /predict/recommendation failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to generate AI recommendations.")

@router.get("/predict/sales")
@router.get("/api/mlops/predict/sales")
def get_sales_forecast(
    days: int = Query(30, ge=7, le=90, description="Future forecast horizon in days"),
    db: Session = Depends(get_db)
):
    """
    Returns multi-model revenue and sales volume forecast trajectory with 95% confidence intervals
    and automated executive staffing/promotional advice.
    """
    try:
        return inference_engine.predict_sales_forecast(days=days, db_session=db)
    except Exception as e:
        logger.error("Endpoint /predict/sales failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to generate sales forecasting trajectory.")

@router.get("/predict/churn")
@router.get("/api/mlops/predict/churn")
def get_customer_churn_prediction(
    user_id: int = Query(1, ge=1, description="Customer Account ID to evaluate"),
    recency: Optional[int] = Query(None, description="Days since last purchase"),
    frequency: Optional[int] = Query(None, description="Total order count"),
    monetary: Optional[float] = Query(None, description="Total lifetime spend")
):
    """
    Predicts customer churn probability, assigns risk tier (Critical, Moderate, Stable),
    and outputs SHAP feature attribution with tailored retention campaigns.
    """
    try:
        features = None
        if recency is not None and frequency is not None and monetary is not None:
            features = {"recency": recency, "frequency": frequency, "monetary": monetary}
        return inference_engine.predict_customer_churn(user_id=user_id, user_features_dict=features)
    except Exception as e:
        logger.error("Endpoint /predict/churn failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to compute customer churn risk.")

@router.get("/predict/inventory")
@router.get("/api/mlops/predict/inventory")
def get_inventory_intelligence(
    db: Session = Depends(get_db)
):
    """
    Returns SKU-level inventory health diagnostics, safety stock buffers, Reorder Points (ROP),
    Economic Order Quantity (EOQ), and automated supplier reorder alerts.
    """
    try:
        return inference_engine.predict_inventory_intelligence(db_session=db)
    except Exception as e:
        logger.error("Endpoint /predict/inventory failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to analyze inventory intelligence.")

@router.get("/predict/segmentation")
@router.get("/api/mlops/predict/segmentation")
def get_customer_segmentation(
    db: Session = Depends(get_db)
):
    """
    Returns customer behavioral segmentation tiers (KMeans, DBSCAN, Hierarchical, GMM)
    with marketing strategy recommendations for each persona.
    """
    try:
        return inference_engine.predict_customer_segmentation(db_session=db)
    except Exception as e:
        logger.error("Endpoint /predict/segmentation failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to compute customer segmentation.")

@router.get("/predict/trending")
@router.get("/api/mlops/predict/trending")
def get_trending_bestsellers(
    limit: int = Query(8, ge=1, le=24, description="Number of trending items to return")
):
    """
    Returns high-velocity trending bestsellers scored by customer rating velocity and order frequency.
    """
    try:
        return inference_engine.predict_trending(limit=limit)
    except Exception as e:
        logger.error("Endpoint /predict/trending failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to fetch trending bestsellers.")

@router.get("/model/status")
@router.get("/api/mlops/model/status")
def get_model_registry_status():
    """
    Returns full catalog of registered model versions, hyperparameters, evaluation metrics,
    and lifecycle stages (Staging, Production Champion, Archived).
    """
    try:
        return inference_engine.get_model_registry_status()
    except Exception as e:
        logger.error("Endpoint /model/status failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to fetch Model Registry status.")

@router.get("/model/version")
@router.get("/api/mlops/model/version")
def get_active_model_version():
    """
    Returns active production champion versions across all MLOps engines and system uptime status.
    """
    try:
        return inference_engine.get_model_version()
    except Exception as e:
        logger.error("Endpoint /model/version failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to fetch active model versions.")
