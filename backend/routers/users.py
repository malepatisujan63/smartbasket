from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.models import User, Address, Notification
from schemas.schemas import UserResponse, AddressCreate, AddressResponse
from utils.security import get_current_user, get_current_admin

router = APIRouter(tags=["Users & Account"])

@router.get("/api/users/profile", response_model=UserResponse)
def get_user_profile(current_user = Depends(get_current_user)):
    return current_user

@router.get("/api/users/addresses", response_model=List[AddressResponse])
def get_user_addresses(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Address).filter(Address.user_id == current_user.id).all()

@router.post("/api/users/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(addr_data: AddressCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if addr_data.is_default:
        # Reset other default addresses
        existing = db.query(Address).filter(Address.user_id == current_user.id, Address.is_default == True).all()
        for e in existing:
            e.is_default = False
            
    new_addr = Address(
        user_id=current_user.id,
        **addr_data.model_dump()
    )
    db.add(new_addr)
    db.commit()
    db.refresh(new_addr)
    return new_addr

@router.delete("/api/users/addresses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    addr = db.query(Address).filter(Address.id == id, Address.user_id == current_user.id).first()
    if addr:
        db.delete(addr)
        db.commit()
    return None

@router.get("/api/users/notifications")
def get_notifications(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifs
    ]

@router.put("/api/users/notifications/read-all")
def mark_notifications_read(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"status": "success"}

@router.get("/api/admin/users", dependencies=[Depends(get_current_admin)])
def get_all_users_admin(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "orders_count": len(u.orders),
            "total_spent": round(sum(o.total_amount for o in u.orders), 2)
        }
        for u in users
    ]
