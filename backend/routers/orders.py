import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Header, Query
from sqlalchemy.orm import Session, joinedload
from database.connection import get_db
from models.models import Order, OrderItem, Cart, Product, Inventory, SalesHistory, Notification, User
from schemas.schemas import OrderCreate, OrderResponse
from utils.security import get_current_user, get_current_admin, decode_token
from services.pdf_generator import generate_invoice_pdf

router = APIRouter(tags=["Orders & Checkout"])

@router.post("/api/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(order_data: OrderCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Standardize payment method
    pm = (order_data.payment_method or "Cash on Delivery").strip()
    if pm.lower() not in ["cash on delivery", "cod", "cash_on_delivery"]:
        raise HTTPException(
            status_code=400,
            detail="ONLY Cash on Delivery is supported as per platform security policy."
        )

    # Resolve delivery address
    from models.models import Address
    delivery_address = order_data.delivery_address
    if not delivery_address or not isinstance(delivery_address, dict):
        if order_data.delivery_address_id:
            addr = db.query(Address).filter(Address.id == order_data.delivery_address_id, Address.user_id == current_user.id).first()
            if addr:
                delivery_address = {
                    "full_name": addr.full_name,
                    "phone": addr.phone,
                    "street_address": addr.street_address,
                    "city": addr.city,
                    "state": addr.state,
                    "postal_code": addr.postal_code,
                    "country": addr.country
                }
        if not delivery_address:
            addr = db.query(Address).filter(Address.user_id == current_user.id).first()
            if addr:
                delivery_address = {
                    "full_name": addr.full_name,
                    "phone": addr.phone,
                    "street_address": addr.street_address,
                    "city": addr.city,
                    "state": addr.state,
                    "postal_code": addr.postal_code,
                    "country": addr.country
                }
            else:
                delivery_address = {
                    "full_name": current_user.full_name or "Valued Customer",
                    "phone": "+91 9876543210",
                    "street_address": "Flat 402, Reliance Greens, Silicon Highway",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "postal_code": "560100",
                    "country": "India"
                }

    # Resolve cart items: check DB cart first, fall back to order_data.items
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    items_to_process = []
    if cart_items:
        for it in cart_items:
            items_to_process.append({"product_id": it.product_id, "quantity": it.quantity})
    elif order_data.items:
        for it in order_data.items:
            pid = it.get("product_id") if isinstance(it, dict) else getattr(it, "product_id", None)
            qty = it.get("quantity", 1) if isinstance(it, dict) else getattr(it, "quantity", 1)
            if pid:
                items_to_process.append({"product_id": pid, "quantity": qty})

    if not items_to_process:
        raise HTTPException(status_code=400, detail="Your shopping bag is empty")

    subtotal = 0.0
    order_items_to_create = []

    for item in items_to_process:
        prod = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not prod:
            continue
        qty = item["quantity"]
        if prod.stock < qty:
            raise HTTPException(
                status_code=400,
                detail=f"Product '{prod.title}' only has {prod.stock} units left in stock."
            )
        
        item_total = round(prod.price * qty, 2)
        subtotal += item_total
        
        # Deduct stock
        prod.stock -= qty
        if prod.inventory:
            prod.inventory.quantity -= qty
            if prod.inventory.quantity <= 0:
                prod.inventory.status = "Out of Stock"
            elif prod.inventory.quantity <= prod.inventory.restock_threshold:
                prod.inventory.status = "Low Stock"
        
        order_items_to_create.append({
            "product_id": prod.id,
            "quantity": qty,
            "unit_price": prod.price,
            "total_price": item_total,
            "category_id": prod.category_id
        })

    tax = round(subtotal * 0.08, 2)
    delivery = 0.0 if subtotal >= 100.0 else 10.0
    
    # Check coupon discount if any
    discount = 0.0
    if order_data.coupon_code:
        from models.models import Coupon
        coupon = db.query(Coupon).filter(Coupon.code == order_data.coupon_code.upper(), Coupon.is_active == True).first()
        if coupon and subtotal >= coupon.min_order:
            if coupon.discount_type == "percentage":
                discount = min((subtotal * coupon.discount_value) / 100.0, coupon.max_discount)
            else:
                discount = min(coupon.discount_value, subtotal)

    total_amount = round(subtotal + tax + delivery - discount, 2)
    now = datetime.datetime.utcnow()
    order_num = f"ORD-{now.year}-{int(now.timestamp())}"

    new_order = Order(
        order_number=order_num,
        user_id=current_user.id,
        total_amount=total_amount,
        tax=tax,
        delivery_charge=delivery,
        status="Pending",
        payment_method="Cash on Delivery",
        delivery_address=delivery_address,
        timeline=[
            {
                "status": "Pending",
                "timestamp": str(now),
                "note": "Order placed successfully (Cash on Delivery)"
            },
            {
                "status": "Packed",
                "timestamp": str(now + datetime.timedelta(minutes=15)),
                "note": "Order verified and sent to Fulfillment Center"
            }
        ],
        created_at=now
    )
    db.add(new_order)
    db.flush()

    for oi_data in order_items_to_create:
        oi = OrderItem(
            order_id=new_order.id,
            product_id=oi_data["product_id"],
            quantity=oi_data["quantity"],
            unit_price=oi_data["unit_price"],
            total_price=oi_data["total_price"]
        )
        db.add(oi)

        # Record sales history
        sh = SalesHistory(
            date=now,
            product_id=oi_data["product_id"],
            category_id=oi_data["category_id"],
            units_sold=oi_data["quantity"],
            revenue=oi_data["total_price"],
            profit=round(oi_data["total_price"] * 0.28, 2)
        )
        db.add(sh)

    # Clear user cart
    for item in cart_items:
        db.delete(item)

    # Create notification
    notif = Notification(
        user_id=current_user.id,
        title=f"Order Placed #{order_num}",
        message=f"Your order for ${total_amount:.2f} (Cash on Delivery) has been confirmed and is being packed!",
        type="order"
    )
    db.add(notif)

    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/api/orders", response_model=List[OrderResponse])
def get_user_orders(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.get("/api/orders/{id}", response_model=OrderResponse)
def get_order_detail(id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order

@router.get("/api/orders/{id}/invoice")
def download_invoice_pdf(
    id: int,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # Authenticate via header or query token
    auth_token = None
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization.split(" ")[1]
    elif token:
        auth_token = token
    
    if not auth_token:
        raise HTTPException(status_code=401, detail="Authentication token required to download invoice")
    
    payload = decode_token(auth_token)
    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    current_user = db.query(User).filter(User.id == int(user_id_raw)).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to download this invoice")

    order_dict = {
        "order_number": order.order_number,
        "created_at": order.created_at,
        "total_amount": order.total_amount,
        "tax": order.tax,
        "delivery_charge": order.delivery_charge,
        "payment_method": order.payment_method,
        "status": order.status,
        "delivery_address": order.delivery_address,
        "items": [
            {
                "product_title": item.product.title if item.product else f"Product #{item.product_id}",
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "total_price": item.total_price
            }
            for item in order.items
        ]
    }

    pdf_bytes = generate_invoice_pdf(order_dict)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Invoice-{order.order_number}.pdf"'
        }
    )

@router.get("/api/admin/orders", response_model=List[OrderResponse], dependencies=[Depends(get_current_admin)])
def get_all_orders_admin(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).all()

@router.put("/api/admin/orders/{id}/status", response_model=OrderResponse, dependencies=[Depends(get_current_admin)])
def update_order_status(id: int, status_str: str, note: str = "", db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_str
    new_event = {
        "status": status_str,
        "timestamp": str(datetime.datetime.utcnow()),
        "note": note or f"Order status updated to {status_str} by Admin"
    }
    
    # SQLAlchemy JSON mutation handling
    current_timeline = list(order.timeline or [])
    current_timeline.append(new_event)
    order.timeline = current_timeline

    # Notify customer
    notif = Notification(
        user_id=order.user_id,
        title=f"Order Update #{order.order_number}",
        message=f"Your order status is now: {status_str}. {note}",
        type="order"
    )
    db.add(notif)
    
    db.commit()
    db.refresh(order)
    return order
