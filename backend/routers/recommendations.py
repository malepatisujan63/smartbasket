from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from database.connection import get_db
from models.models import Product, Category, User, AnalyticsEvent
from ml.engine import ml_engine
from utils.security import get_optional_user_id

router = APIRouter(tags=["AI Recommendations & Search"])

@router.get("/api/recommendation/personalized")
def get_personalized_recs(
    limit: int = 6,
    session_id: Optional[str] = Query(None, description="Guest session ID for real-time in-session tracking"),
    recent_product_id: Optional[int] = Query(None, description="Current or recently viewed product ID"),
    user_id: Optional[int] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    """
    Returns multi-touch hybrid personalized recommendations based on:
    - Recent clickstream views and dwell time (user and session)
    - Cart items and Wishlist additions
    - Historical orders
    - Category & Brand affinity
    - Maximal Marginal Relevance (MMR) category diversity & exploration
    """
    return ml_engine.get_personalized_recommendations(
        db=db,
        user_id=user_id,
        session_id=session_id,
        recent_product_id=recent_product_id,
        limit=limit
    )

@router.get("/api/recommendation/trending")
def get_trending_products(limit: int = 8, db: Session = Depends(get_db)):
    prods = db.query(Product).order_by(desc(Product.reviews_count), desc(Product.rating)).limit(limit).all()
    return [
        {
            "product": p,
            "explanation": {
                "reason": f"High velocity bestseller with {p.reviews_count} positive reviews",
                "confidence": 0.95,
                "important_features": [
                    {"feature": "Sales Velocity", "impact": "High Positive", "value": "Top 1%", "weight": 0.55},
                    {"feature": "Average Rating", "impact": "High Positive", "value": f"{p.rating} Stars", "weight": 0.45}
                ],
                "recommendation": "Trending Choice"
            }
        }
        for p in prods
    ]

@router.get("/api/recommendation/recently-viewed")
def get_recently_viewed(
    limit: int = 6,
    session_id: Optional[str] = Query(None),
    user_id: Optional[int] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    """
    Returns products that the current user or guest session has ACTUALLY viewed in real time.
    """
    viewed_products = []
    seen_ids = set()
    
    # 1. Check logged-in user recently viewed profile
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.recently_viewed:
            for pid in user.recently_viewed[:limit]:
                p = db.query(Product).filter(Product.id == pid).first()
                if p and p.id not in seen_ids:
                    seen_ids.add(p.id)
                    viewed_products.append(p)
                    
    # 2. Check real-time AnalyticsEvent stream for views
    if len(viewed_products) < limit:
        query_ev = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.event_type == "view",
            AnalyticsEvent.product_id.isnot(None)
        )
        if user_id:
            query_ev = query_ev.filter(AnalyticsEvent.user_id == user_id)
        elif session_id:
            query_ev = query_ev.filter(AnalyticsEvent.metadata_json["session_id"].as_string() == session_id)
            
        recent_events = query_ev.order_by(desc(AnalyticsEvent.timestamp)).limit(20).all()
        for ev in recent_events:
            if ev.product_id and ev.product_id not in seen_ids:
                seen_ids.add(ev.product_id)
                p = db.query(Product).filter(Product.id == ev.product_id).first()
                if p:
                    viewed_products.append(p)
                if len(viewed_products) >= limit:
                    break

    # 3. If user has no browsing history yet, return top-rated flagship products
    if not viewed_products:
        viewed_products = db.query(Product).order_by(desc(Product.rating), desc(Product.reviews_count)).limit(limit).all()
        return [
            {
                "product": p,
                "explanation": {
                    "reason": f"Top rated bestseller in {p.category.name if p.category else 'Catalog'} — recommended for your new session",
                    "confidence": 0.88,
                    "important_features": [
                        {"feature": "Catalog Bestseller", "impact": "High Positive", "value": f"{p.rating} Stars", "weight": 0.60}
                    ],
                    "recommendation": "Discover Flagships"
                }
            }
            for p in viewed_products
        ]

    return [
        {
            "product": p,
            "explanation": {
                "reason": f"Viewed in your active shopping session in {p.category.name if p.category else 'Catalog'}",
                "confidence": 0.94,
                "important_features": [
                    {"feature": "Session Recency", "impact": "High Positive", "value": "Active Session", "weight": 0.70},
                    {"feature": "Brand Affinity", "impact": "Positive", "value": p.brand.name if p.brand else "Brand", "weight": 0.30}
                ],
                "recommendation": "Continue Shopping"
            }
        }
        for p in viewed_products
    ]

@router.get("/api/search/suggestions")
def get_search_suggestions(query: Optional[str] = None, db: Session = Depends(get_db)):
    trending_searches = [
        "Apple MacBook Pro M3",
        "Sony WH-1000XM5 Headphones",
        "Samsung Galaxy S24 Ultra",
        "Nike Air Zoom Pegasus",
        "Dyson V15 Detect Vacuum",
        "Ninja Foodi XL Air Fryer",
        "Logitech G PRO X Superlight",
        "Asus ROG OLED Monitor"
    ]
    
    if not query or len(query.strip()) < 1:
        # Return trending and popular categories
        cats = db.query(Category).limit(6).all()
        return {
            "trending_searches": trending_searches[:6],
            "popular_categories": [{"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon} for c in cats],
            "product_suggestions": []
        }
        
    search_term = f"%{query.strip()}%"
    prods = db.query(Product).filter(
        or_(
            Product.title.ilike(search_term),
            Product.description.ilike(search_term)
        )
    ).limit(5).all()
    
    # Filter matching trending
    matched_trending = [t for t in trending_searches if query.lower() in t.lower()][:4]
    
    return {
        "trending_searches": matched_trending if matched_trending else trending_searches[:3],
        "popular_categories": [],
        "product_suggestions": [
            {
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "rating": p.rating,
                "image": p.images[0] if p.images else "",
                "category": p.category.name if p.category else ""
            }
            for p in prods
        ]
    }
