import os
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, event, text, UniqueConstraint
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import func

# ─────────────────────────────────────────────────────────────────────────────
# Database URL
# ─────────────────────────────────────────────────────────────────────────────
base_dir = os.path.dirname(os.path.abspath(__file__))
sqlite_path = os.path.join(base_dir, "fast_ecommerce.db")
default_db = f"sqlite:///{sqlite_path}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default_db)

IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

# ─────────────────────────────────────────────────────────────────────────────
# Apply MAXIMUM PERFORMANCE PRAGMAs directly to the SQLite file (persistent)
# These persist across all connections — not just event-listener scope.
# ─────────────────────────────────────────────────────────────────────────────
if IS_SQLITE:
    try:
        _raw = sqlite3.connect(sqlite_path)
        _raw.execute("PRAGMA journal_mode=WAL")          # Write-Ahead Log: readers never block writers
        _raw.execute("PRAGMA wal_autocheckpoint=1000")   # Checkpoint every 1000 pages
        _raw.execute("PRAGMA synchronous=NORMAL")        # Safe but faster than FULL
        _raw.execute("PRAGMA cache_size=-131072")        # 128 MB in-memory page cache
        _raw.execute("PRAGMA temp_store=MEMORY")         # All temp tables/indexes in RAM
        _raw.execute("PRAGMA mmap_size=5368709120")      # 5 GB memory-mapped I/O
        _raw.execute("PRAGMA page_size=4096")            # Optimal for most OS block sizes
        _raw.execute("PRAGMA locking_mode=NORMAL")       # Allow concurrent readers
        _raw.execute("PRAGMA busy_timeout=5000")         # Wait 5s before "database locked" error
        _raw.execute("PRAGMA optimize")                  # Auto-analyze query planner stats
        _raw.commit()
        _raw.close()
    except Exception as _e:
        print(f"[database] Note on initial PRAGMA: {_e}")

# ─────────────────────────────────────────────────────────────────────────────
# SQLAlchemy Engine — with connection pool for concurrent request handling
# ─────────────────────────────────────────────────────────────────────────────
if IS_SQLITE:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,           # Wait up to 30s on locked DB
        },
        poolclass=QueuePool,
        pool_size=10,                # Keep 10 connections ready in pool
        max_overflow=20,             # Allow up to 20 extra connections under load
        pool_timeout=30,             # Max wait for a connection from pool
        pool_recycle=1800,           # Recycle connections every 30 min (prevent stale)
        pool_pre_ping=True,          # Test connection health before use
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Per-connection PRAGMA reinforcement (catches any missed initial connections)
# ─────────────────────────────────────────────────────────────────────────────
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if IS_SQLITE:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-131072")   # 128 MB cache per connection
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=5368709120") # 5 GB mmap
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ─────────────────────────────────────────────────────────────────────────────
# Session Factory
# ─────────────────────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "Users"

    user_id    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username   = Column(String(255), unique=True, index=True, nullable=False)
    password   = Column(String(255), nullable=False)
    ab_group   = Column(String(1), default="A")   # 'A' = ML, 'B' = Baseline
    is_admin   = Column(Integer, default=0)        # 0 = False, 1 = True

    logs = relationship("UserLog", back_populates="user")


class Product(Base):
    __tablename__ = "Products"

    asin              = Column(String(255), primary_key=True, index=True)
    title             = Column(String)
    brand             = Column(String(255), index=True)
    imgUrl            = Column(String)
    productURL        = Column(String)
    stars             = Column(Float, default=0.0)
    reviews           = Column(Integer, default=0)
    price             = Column(Float, default=0.0)
    listPrice         = Column(Float, default=0.0)
    category_id       = Column(String(255))
    isBestSeller      = Column(Integer, default=0)
    boughtInLastMonth = Column(Integer, default=0)
    alt               = Column(String)
    category_name     = Column(String(255), index=True)

    logs     = relationship("UserLog", back_populates="product")
    features = relationship("ProductFeature", back_populates="product")


class ProductFeature(Base):
    __tablename__ = "ProductFeatures"

    feature_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asin       = Column(String(255), ForeignKey("Products.asin"), index=True)
    key        = Column(String(255), index=True)
    value      = Column(String(255))

    product = relationship("Product", back_populates="features")


class UserLog(Base):
    __tablename__ = "UserLogs"

    log_id       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("Users.user_id"), index=True)
    asin         = Column(String(255), ForeignKey("Products.asin"), index=True)
    action       = Column(String(50), index=True)   # 'view', 'cart', 'purchase'
    timestamp    = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    search_query = Column(String)
    view_duration= Column(Integer, default=0)

    user    = relationship("User", back_populates="logs")
    product = relationship("Product", back_populates="logs")


class UserCart(Base):
    __tablename__ = "UserCart"
    __table_args__ = (UniqueConstraint('user_id', 'asin', name='uq_user_cart_asin'),)

    cart_id  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id  = Column(Integer, ForeignKey("Users.user_id"), index=True)
    asin     = Column(String(255), ForeignKey("Products.asin"))
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    user    = relationship("User")
    product = relationship("Product")


class UserReview(Base):
    __tablename__ = "UserReviews"

    review_id  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("Users.user_id"), index=True)
    asin       = Column(String(255), ForeignKey("Products.asin"), index=True)
    rating     = Column(Float, nullable=False, default=5.0)
    comment    = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user    = relationship("User")
    product = relationship("Product")


class Order(Base):
    __tablename__ = "Orders"

    order_id     = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("Users.user_id"), index=True, nullable=False)
    full_name    = Column(String(255), nullable=False)
    address      = Column(String(255), nullable=False)
    city         = Column(String(100), nullable=False)
    zip_code     = Column(String(50), nullable=False)
    total_amount = Column(Float, default=0.0)
    status       = Column(String(50), default="Completed")
    created_at   = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user  = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "OrderItems"

    item_id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id           = Column(Integer, ForeignKey("Orders.order_id"), index=True, nullable=False)
    asin               = Column(String(255), ForeignKey("Products.asin"), index=True, nullable=False)
    title              = Column(String)
    imgUrl             = Column(String)
    price_at_purchase  = Column(Float, default=0.0)
    quantity           = Column(Integer, default=1)

    order   = relationship("Order", back_populates="items")
    product = relationship("Product")


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

    # Ensure critical composite indexes exist for maximum query speed
    if IS_SQLITE:
        with engine.connect() as conn:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_products_cat_reviews "
                "ON Products(category_name, reviews DESC)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_products_bestseller_reviews "
                "ON Products(isBestSeller, reviews DESC)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_userlogs_user_action "
                "ON UserLogs(user_id, action)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_userlogs_user_ts "
                "ON UserLogs(user_id, timestamp DESC)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_orders_user_ts "
                "ON Orders(user_id, created_at DESC)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_order_items_order "
                "ON OrderItems(order_id)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_userreviews_asin_ts "
                "ON UserReviews(asin, created_at DESC)"
            ))
            conn.commit()

def get_db():
    """FastAPI dependency: yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

