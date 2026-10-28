from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.ai_assistant_service import rag_assistant_service
from models.models import Product
from schemas.schemas import ProductResponse

router = APIRouter(prefix="/api/ai-assistant", tags=["AI Shopping Assistant"])

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[int] = None
    category_filter: Optional[str] = None
    max_price: Optional[float] = None

class CompareRequest(BaseModel):
    product_ids: List[int]

@router.post("/chat")
def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    """
    RAG-powered AI Shopping Assistant endpoint.
    Returns markdown explanation, top 5 ranked products, comparison table matrix, and winner.
    """
    if not req.query or len(req.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
        
    result = rag_assistant_service.process_query(db, req.query, req.user_id)
    return result

@router.post("/compare")
def compare_products(req: CompareRequest, db: Session = Depends(get_db)):
    """
    Product comparison engine endpoint.
    Compares up to 5 products side-by-side with AI recommendation awards.
    """
    if not req.product_ids or len(req.product_ids) == 0:
        return {"products": [], "comparison_table": [], "winner": None}
        
    prods = db.query(Product).filter(Product.id.in_(req.product_ids[:5])).all()
    if not prods:
        return {"products": [], "comparison_table": [], "winner": None}
        
    # Generate comparison table
    comp_table = []
    best_value = prods[0]
    best_perf = prods[0]
    best_batt = prods[0]
    best_disp = prods[0]
    winner = sorted(prods, key=lambda x: (x.rating, x.reviews_count), reverse=True)[0]
    
    for p in prods:
        if p.price < best_value.price: best_value = p
        if p.price > best_perf.price or p.rating > best_perf.rating: best_perf = p
        
        specs = p.specifications or {}
        comp_table.append({
            "id": p.id,
            "title": p.title,
            "brand": p.brand.name if p.brand else "Brand",
            "price": f"${p.price:,.2f}",
            "rating": f" {p.rating} ({p.reviews_count} reviews)",
            "processor": specs.get("Processor", specs.get("CPU", "AI Silicon Core")),
            "ram": specs.get("RAM", specs.get("Memory", "32GB Unified")),
            "storage": specs.get("Storage", "1TB NVMe SSD"),
            "display": specs.get("Display", specs.get("Resolution", "OLED XDR")),
            "battery": specs.get("Battery Life", specs.get("Battery", "Up to 24 Hours")),
            "camera": specs.get("Camera", specs.get("Sensors", "Pro AI Studio Camera")),
            "warranty": p.warranty,
            "pros": p.features[:2] if p.features else ["Premium Quality", "Express Shipping"],
            "cons": ["High Demand"] if p.stock < 20 else ["Premium Price"]
        })
        
    return {
        "products": [p for p in prods],
        "comparison_table": comp_table,
        "awards": {
            "overall_winner": winner,
            "best_value": best_value,
            "best_performance": best_perf,
            "best_battery": best_batt,
            "best_display": best_disp
        }
    }
