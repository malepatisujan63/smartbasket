import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="customer")  # customer, retailer, or admin
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    
    # Personalization & History fields
    browsing_history = Column(JSON, default=list)  # list of product IDs
    recently_viewed = Column(JSON, default=list)   # list of product IDs
    search_history = Column(JSON, default=list)    # list of search query strings
    favorite_categories = Column(JSON, default=list) # list of category names/IDs
    preferred_brands = Column(JSON, default=list)    # list of brand names/IDs
    recommendation_profile = Column(JSON, default=dict) # budget, interests, personas (student, gamer, etc.)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    addresses = relationship("Address", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")
    wishlist_items = relationship("Wishlist", back_populates="user")
    retailer_profile = relationship("Retailer", back_populates="user", uselist=False)
    analytics_events = relationship("AnalyticsEvent", back_populates="user")

class Retailer(Base):
    __tablename__ = "retailers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    store_name = Column(String, unique=True, index=True, nullable=False)
    store_slug = Column(String, unique=True, index=True)
    store_logo = Column(String, nullable=True)
    store_banner = Column(String, nullable=True)
    business_description = Column(Text, nullable=True)
    verified_badge = Column(Boolean, default=True)
    rating = Column(Float, default=4.8)
    location = Column(String, default="Seattle, WA, USA")
    followers_count = Column(Integer, default=1250)
    years_of_selling = Column(Integer, default=5)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    shipping_policy = Column(Text, default="Free 2-Day Shipping on all orders over $35. Dispatched via Amazon-AI Prime Logistics.")
    return_policy = Column(Text, default="30-Day Hassle-Free Returns. Full refund guaranteed upon inspection.")
    total_sales = Column(Integer, default=5400)
    revenue = Column(Float, default=450000.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="retailer_profile")
    products = relationship("Product", back_populates="retailer")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True)
    icon = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    products = relationship("Product", back_populates="category")

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True)
    logo = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="brand")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    marketing_description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    rating = Column(Float, default=4.5)
    reviews_count = Column(Integer, default=0)
    stock = Column(Integer, default=50)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=True)
    
    images = Column(JSON, default=list)  # list of image URLs
    gallery_images = Column(JSON, default=list)  # extra gallery images
    specifications = Column(JSON, default=dict)  # key-value pairs
    features = Column(JSON, default=list)  # bullet points
    
    # Extended Professional Specifications
    country_of_origin = Column(String, default="United States")
    warranty = Column(String, default="2 Years Manufacturer Warranty")
    model_number = Column(String, index=True, nullable=True)
    sku = Column(String, unique=True, index=True, nullable=True)
    weight = Column(String, default="1.5 kg")
    dimensions = Column(String, default="30 x 20 x 5 cm")
    color_variants = Column(JSON, default=list)    # e.g., ["Space Black", "Silver", "Titanium Gray"]
    storage_variants = Column(JSON, default=list)  # e.g., ["256GB", "512GB", "1TB", "2TB"]
    available_sizes = Column(JSON, default=list)   # e.g., ["S", "M", "L", "XL"] or ["13-inch", "15-inch", "16-inch"]
    material = Column(String, default="Aerospace-Grade Aluminum / Premium Polymer")
    manufacturing_date = Column(String, default="2025-11-15")
    shipping_info = Column(String, default="Free Express Shipping via Amazon-AI Air Logistics")
    delivery_estimate = Column(String, default="1-2 Business Days")
    return_policy = Column(String, default="30-Day Money-Back Guarantee with Free Return Shipping")
    box_contents = Column(JSON, default=list)      # e.g., ["Product unit", "100W USB-C Power Adapter", "Braided Charging Cable", "Quick Start Guide"]
    package_dimensions = Column(String, default="35 x 25 x 8 cm")
    
    # Q&A, FAQ, and AI Insights
    faqs = Column(JSON, default=list)  # list of dicts: [{"question": "...", "answer": "..."}]
    qna = Column(JSON, default=list)   # list of dicts: [{"question": "...", "answer": "...", "user": "...", "date": "..."}]
    related_products = Column(JSON, default=list) # list of related product IDs
    frequently_bought_together = Column(JSON, default=list) # list of complementary product IDs
    accessories = Column(JSON, default=list) # list of accessory product IDs
    ai_buying_tips = Column(JSON, default=list) # list of AI insights: e.g. ["Best for developers and AI researchers", "High battery efficiency"]
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    retailer = relationship("Retailer", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    sku = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=50)
    warehouse_location = Column(String, default="Zone A - Shelf 4")
    restock_threshold = Column(Integer, default=10)
    status = Column(String, default="In Stock")  # In Stock, Low Stock, Out of Stock
    last_restocked = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="inventory")

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    street_address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, default="United States")
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=0.0)
    status = Column(String, default="Pending")  # Pending, Packed, Shipped, Out For Delivery, Delivered
    payment_method = Column(String, default="Cash on Delivery")
    delivery_address = Column(JSON, nullable=False)
    timeline = Column(JSON, default=list)  # List of status history with timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String, nullable=True)
    rating = Column(Float, nullable=False)
    title = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    pros = Column(JSON, default=list)  # e.g., ["Excellent battery", "Stunning display"]
    cons = Column(JSON, default=list)  # e.g., ["Pricey", "Heavier than expected"]
    verified_purchase = Column(Boolean, default=True)
    review_images = Column(JSON, default=list)
    helpful_votes = Column(Integer, default=0)
    retailer_reply = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False) # view, click, search, wishlist_add, cart_add, checkout
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    query = Column(String, nullable=True)
    metadata_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="analytics_events")

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    discount_type = Column(String, default="percentage")  # percentage or fixed
    discount_value = Column(Float, nullable=False)
    min_order = Column(Float, default=0.0)
    max_discount = Column(Float, default=100.0)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class SalesHistory(Base):
    __tablename__ = "sales_history"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    units_sold = Column(Integer, default=1)
    revenue = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommended_product_ids = Column(JSON, default=list)
    algorithm_type = Column(String, default="Hybrid")
    confidence_score = Column(Float, default=0.92)
    reasons = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    churn_probability = Column(Float, default=0.15)
    churn_reasons = Column(JSON, default=list)
    segment_name = Column(String, default="Loyal Customers")  # VIP Champions, Loyal, Potential, At-Risk, Sleeping
    clv_score = Column(Float, default=500.0)
    last_purchase_date = Column(DateTime, default=datetime.datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="order")  # order, promotion, alert, ai
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    refresh_token = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=True)
    entity_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(JSON, default=dict)
