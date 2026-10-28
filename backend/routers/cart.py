from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.models import Cart, Wishlist, Product, Coupon
from schemas.schemas import CartItemAdd, CartItemUpdate, CartItemResponse, WishlistResponse, CouponApply, CouponResponse
from utils.security import get_current_user

router = APIRouter(tags=["Cart & Wishlist"])

@router.get("/api/cart", response_model=List[CartItemResponse])
def get_cart(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Cart).filter(Cart.user_id == current_user.id).all()

@router.post("/api/cart/add", response_model=CartItemResponse)
def add_to_cart(item: CartItemAdd, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == item.product_id
    ).first()

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.put("/api/cart/{id}", response_model=CartItemResponse)
def update_cart_item(id: int, update_data: CartItemUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if update_data.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        raise HTTPException(status_code=200, detail="Item removed from cart")
    
    cart_item.quantity = update_data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/api/cart/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.id == id, Cart.user_id == current_user.id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
    return None

@router.post("/api/cart/apply-coupon", response_model=CouponResponse)
def apply_coupon(data: CouponApply, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.code == data.code.upper(), Coupon.is_active == True).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid or expired coupon code")
    
    if data.cart_total < coupon.min_order:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum order amount of ${coupon.min_order:.2f} required for this coupon"
        )
    
    if coupon.discount_type == "percentage":
        discount = (data.cart_total * coupon.discount_value) / 100.0
        discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value
        discount = min(discount, data.cart_total)

    final_total = max(0.0, data.cart_total - discount)
    return {
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "discount_amount": round(discount, 2),
        "final_total": round(final_total, 2)
    }

@router.get("/api/wishlist", response_model=List[WishlistResponse])
def get_wishlist(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()

@router.post("/api/wishlist/toggle/{product_id}")
def toggle_wishlist(product_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first()

    if item:
        db.delete(item)
        db.commit()
        return {"status": "removed", "message": "Removed from wishlist"}
    else:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        new_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.add(new_item)
        db.commit()
        return {"status": "added", "message": "Added to wishlist"}
