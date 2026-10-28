from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Token & Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[Any] = None

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "customer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    favorite_categories: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    profile_picture: Optional[str] = None
    is_active: bool
    browsing_history: List[int] = []
    recently_viewed: List[int] = []
    favorite_categories: List[str] = []
    preferred_brands: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Retailer Schemas
class RetailerCreate(BaseModel):
    store_name: str
    store_slug: str
    store_logo: Optional[str] = None
    store_banner: Optional[str] = None
    business_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    shipping_policy: Optional[str] = None
    return_policy: Optional[str] = None

class RetailerResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    store_name: str
    store_slug: str
    store_logo: Optional[str] = None
    store_banner: Optional[str] = None
    business_description: Optional[str] = None
    verified_badge: bool
    rating: float
    location: str
    followers_count: int
    years_of_selling: int
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    shipping_policy: str
    return_policy: str
    total_sales: int
    revenue: float
    created_at: datetime

    class Config:
        from_attributes = True

# Category & Brand Schemas
class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class BrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    logo: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

# Product & Inventory Schemas
class InventoryResponse(BaseModel):
    sku: str
    quantity: int
    warehouse_location: str
    status: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    marketing_description: Optional[str] = None
    price: float
    discount_percentage: Optional[float] = 0.0
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    retailer_id: Optional[int] = None
    stock: Optional[int] = 50
    images: List[str] = []
    gallery_images: List[str] = []
    specifications: Dict[str, Any] = {}
    features: List[str] = []
    country_of_origin: Optional[str] = "United States"
    warranty: Optional[str] = "2 Years Manufacturer Warranty"
    model_number: Optional[str] = None
    sku: Optional[str] = None
    weight: Optional[str] = "1.5 kg"
    dimensions: Optional[str] = "30 x 20 x 5 cm"
    color_variants: List[str] = []
    storage_variants: List[str] = []
    available_sizes: List[str] = []
    material: Optional[str] = None
    shipping_info: Optional[str] = None
    delivery_estimate: Optional[str] = "1-2 Business Days"
    return_policy: Optional[str] = None
    box_contents: List[str] = []
    package_dimensions: Optional[str] = None
    faqs: List[Dict[str, Any]] = []
    qna: List[Dict[str, Any]] = []
    ai_buying_tips: List[str] = []

class ProductResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    marketing_description: Optional[str] = None
    price: float
    discount_percentage: float
    rating: float
    reviews_count: int
    stock: int
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    retailer_id: Optional[int] = None
    images: List[str]
    gallery_images: List[str] = []
    specifications: Dict[str, Any]
    features: List[str]
    country_of_origin: str = "United States"
    warranty: str = "2 Years Manufacturer Warranty"
    model_number: Optional[str] = None
    sku: Optional[str] = None
    weight: str = "1.5 kg"
    dimensions: str = "30 x 20 x 5 cm"
    color_variants: List[str] = []
    storage_variants: List[str] = []
    available_sizes: List[str] = []
    material: str = "Aerospace-Grade Aluminum"
    manufacturing_date: str = "2025-11-15"
    shipping_info: str = "Free Express Shipping via Amazon-AI Air Logistics"
    delivery_estimate: str
    return_policy: str = "30-Day Money-Back Guarantee"
    box_contents: List[str] = []
    package_dimensions: str = "35 x 25 x 8 cm"
    faqs: List[Dict[str, Any]] = []
    qna: List[Dict[str, Any]] = []
    related_products: List[int] = []
    frequently_bought_together: List[int] = []
    accessories: List[int] = []
    ai_buying_tips: List[str] = []
    category: Optional[CategoryResponse] = None
    brand: Optional[BrandResponse] = None
    retailer: Optional[RetailerResponse] = None
    inventory: Optional[InventoryResponse] = None

    class Config:
        from_attributes = True

# Review Schemas
class ReviewCreate(BaseModel):
    product_id: int
    rating: float = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
    pros: List[str] = []
    cons: List[str] = []
    review_images: List[str] = []

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    user_name: Optional[str] = None
    rating: float
    title: Optional[str] = None
    comment: Optional[str] = None
    pros: List[str] = []
    cons: List[str] = []
    verified_purchase: bool = True
    review_images: List[str] = []
    helpful_votes: int
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

# Cart & Wishlist Schemas
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse

    class Config:
        from_attributes = True

# Address Schemas
class AddressCreate(BaseModel):
    full_name: str
    phone: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: Optional[str] = "United States"
    is_default: Optional[bool] = False

class AddressResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool

    class Config:
        from_attributes = True

# Coupon Schemas
class CouponApply(BaseModel):
    code: str
    cart_total: float

class CouponResponse(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    discount_amount: float
    final_total: float

# Order Schemas
class OrderCreate(BaseModel):
    delivery_address: Optional[Dict[str, Any]] = None
    delivery_address_id: Optional[int] = None
    payment_method: str = "Cash on Delivery"
    coupon_code: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    total_amount: float
    tax: float
    delivery_charge: float
    status: str
    payment_method: str
    delivery_address: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

# ML & AI Schemas
class ExplanationFeature(BaseModel):
    feature: str
    impact: str  # High Positive, Medium Positive, Negative, etc.
    value: Any
    weight: float

class PredictionExplanation(BaseModel):
    reason: str
    confidence: float
    important_features: List[ExplanationFeature]
    recommendation: str

class RecommendationItem(BaseModel):
    product: ProductResponse
    explanation: PredictionExplanation

class CustomerChurnResponse(BaseModel):
    user_id: int
    user_email: str
    churn_probability: float
    risk_level: str  # High, Medium, Low
    clv_score: float
    segment_name: str
    explanation: PredictionExplanation

class ForecastDataPoint(BaseModel):
    date: str
    predicted_revenue: float
    predicted_orders: int
    confidence_upper: float
    confidence_lower: float

class DemandForecastResponse(BaseModel):
    product_id: int
    product_title: str
    thirty_day_demand: int
    trend: str  # Increasing, Stable, Decreasing
    restock_recommended: bool
    explanation: PredictionExplanation

# Analytics Event Schemas
class AnalyticsEventCreate(BaseModel):
    event_type: str
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    query: Optional[str] = None
    metadata_json: Dict[str, Any] = {}

class AnalyticsEventResponse(BaseModel):
    id: int
    event_type: str
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    query: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
