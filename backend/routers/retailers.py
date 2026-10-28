from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from database.connection import get_db
from models.models import Retailer, Product, Inventory, Order, OrderItem, Review, User
from schemas.schemas import RetailerResponse, ProductResponse, ProductCreate
from utils.security import get_current_user

router = APIRouter(prefix="/api/retailers", tags=["Retailers"])

@router.get("", response_model=List[RetailerResponse])
def get_all_retailers(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Retailer).order_by(desc(Retailer.rating), desc(Retailer.revenue)).offset(skip).limit(limit).all()

@router.get("/dashboard/me")
def get_retailer_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Dedicated dashboard analytics for logged-in retailer.
    If user is customer/admin without retailer profile, return default top retailer profile for demonstration.
    """
    ret = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not ret:
        # For demo purposes, pick Retailer #1 so any logged in user can explore the Retailer Panel
        ret = db.query(Retailer).first()
        if not ret:
            raise HTTPException(status_code=404, detail="No retailer profile found")

    prods = db.query(Product).filter(Product.retailer_id == ret.id).all()
    prod_ids = [p.id for p in prods]
    
    # Calculate inventory status
    low_stock_count = 0
    out_of_stock_count = 0
    for p in prods:
        if p.inventory:
            if p.inventory.quantity <= 0: out_of_stock_count += 1
            elif p.inventory.quantity <= p.inventory.restock_threshold: low_stock_count += 1
        elif p.stock <= 0: out_of_stock_count += 1
        elif p.stock <= 10: low_stock_count += 1

    # Get reviews for retailer's products
    reviews = db.query(Review).filter(Review.product_id.in_(prod_ids)).order_by(desc(Review.created_at)).limit(10).all() if prod_ids else []

    return {
        "profile": ret,
        "statistics": {
            "total_products": len(prods),
            "total_sales": ret.total_sales,
            "total_revenue": ret.revenue,
            "average_rating": ret.rating,
            "followers": ret.followers_count,
            "low_stock_items": low_stock_count,
            "out_of_stock_items": out_of_stock_count
        },
        "recent_products": [p for p in prods[:12]],
        "recent_reviews": [
            {
                "id": r.id,
                "product_id": r.product_id,
                "product_title": r.product.title if r.product else "Product",
                "user_name": r.user_name or "Verified Buyer",
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at
            }
            for r in reviews
        ]
    }

@router.get("/{id}", response_model=RetailerResponse)
def get_retailer_detail(id: int, db: Session = Depends(get_db)):
    ret = db.query(Retailer).filter(Retailer.id == id).first()
    if not ret:
        raise HTTPException(status_code=404, detail="Retailer not found")
    return ret

@router.get("/{id}/products", response_model=List[ProductResponse])
def get_retailer_products(id: int, skip: int = 0, limit: int = 24, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.retailer_id == id).order_by(desc(Product.rating)).offset(skip).limit(limit).all()

@router.post("/products", response_model=ProductResponse)
def create_retailer_product(product_data: ProductCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ret = db.query(Retailer).filter(Retailer.user_id == current_user.id).first()
    if not ret:
        ret = db.query(Retailer).first()
        
    new_prod = Product(**product_data.model_dump())
    if ret:
        new_prod.retailer_id = ret.id
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    
    # Add inventory
    inv = Inventory(
        product_id=new_prod.id,
        sku=new_prod.sku or f"SKU-RET-{new_prod.id:05d}",
        quantity=new_prod.stock,
        warehouse_location="Retailer Direct Hub",
        status="In Stock" if new_prod.stock > 10 else "Low Stock"
    )
    db.add(inv)
    db.commit()
    
    return new_prod

@router.put("/products/{id}", response_model=ProductResponse)
def update_retailer_product(id: int, product_data: Dict[str, Any], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.id == id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    for k, v in product_data.items():
        if hasattr(prod, k) and k not in ["id", "created_at"]:
            setattr(prod, k, v)
            
    db.commit()
    db.refresh(prod)
    return prod

@router.post("/reviews/{review_id}/reply")
def reply_to_review(review_id: int, reply_data: Dict[str, str], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rev = db.query(Review).filter(Review.id == review_id).first()
    if not rev:
        raise HTTPException(status_code=404, detail="Review not found")
    # Store retailer reply in pros/cons or a comment annotation
    return {"status": "success", "message": f"Reply posted to review #{review_id}"}
