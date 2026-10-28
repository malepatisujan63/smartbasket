from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc
from database.connection import get_db
from models.models import Product, Category, Brand, Review
from schemas.schemas import ProductResponse, ReviewCreate, ReviewResponse, ProductCreate
from utils.security import get_current_user, get_current_admin

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def get_products(
    category_slug: Optional[str] = None,
    brand_slug: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "rating",  # rating, price_asc, price_desc, reviews, newest
    skip: int = 0,
    limit: int = 24,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
    
    if brand_slug:
        brand = db.query(Brand).filter(Brand.slug == brand_slug).first()
        if brand:
            query = query.filter(Product.brand_id == brand.id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )

    if sort_by == "price_asc":
        query = query.order_by(asc(Product.price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.price))
    elif sort_by == "reviews":
        query = query.order_by(desc(Product.reviews_count))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    else:  # rating default
        query = query.order_by(desc(Product.rating), desc(Product.reviews_count))

    query = query.options(joinedload(Product.category), joinedload(Product.brand))
    return query.offset(skip).limit(limit).all()

@router.get("/{id}", response_model=ProductResponse)
def get_product_detail(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.brand),
        joinedload(Product.retailer),
        joinedload(Product.inventory)
    ).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/{id}/related", response_model=List[ProductResponse])
def get_related_products(id: int, limit: int = 6, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        return []
    
    related = db.query(Product).filter(
        Product.id != id,
        or_(
            Product.category_id == product.category_id,
            Product.brand_id == product.brand_id
        )
    ).order_by(desc(Product.rating)).limit(limit).all()
    
    return related

@router.get("/{id}/frequently-bought-together", response_model=List[ProductResponse])
def get_frequently_bought_together(id: int, limit: int = 3, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        return []
    
    # Return complementary items in different categories or top sellers
    comp = db.query(Product).filter(
        Product.id != id,
        Product.category_id != product.category_id
    ).order_by(desc(Product.reviews_count)).limit(limit).all()
    
    return comp

@router.post("/{id}/reviews", response_model=ReviewResponse)
def create_review(id: int, review_data: ReviewCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    rev = Review(
        product_id=id,
        user_id=current_user.id,
        rating=review_data.rating,
        title=review_data.title,
        comment=review_data.comment,
        helpful_votes=0
    )
    db.add(rev)
    
    # Update product rating and count
    product.reviews_count += 1
    product.rating = round(((product.rating * (product.reviews_count - 1)) + review_data.rating) / product.reviews_count, 1)
    
    db.commit()
    db.refresh(rev)
    return rev

@router.post("", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    new_prod = Product(**product_data.model_dump())
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod
