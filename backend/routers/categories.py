from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.models import Category, Brand
from schemas.schemas import CategoryResponse, BrandResponse

router = APIRouter(tags=["Categories & Brands"])

@router.get("/api/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/api/brands", response_model=List[BrandResponse])
def get_brands(db: Session = Depends(get_db)):
    return db.query(Brand).all()
