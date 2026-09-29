import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure ecommerce_app directory is on sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import app
from database import get_db, SessionLocal, User, Product, Order, OrderItem, UserReview
from vector_engine import SemanticSearchEngine, VectorEngine
from ncf_engine import NCFEngine


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CORE HTML ROUTES & NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

def test_homepage_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "SmartRec" in response.text


def test_static_html_pages_render(client):
    pages = ["/categories", "/login", "/cart", "/checkout", "/admin"]
    for path in pages:
        response = client.get(path)
        assert response.status_code == 200, f"Failed to render {path}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CATALOG & SEARCH APIS
# ═══════════════════════════════════════════════════════════════════════════════

def test_api_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0
    assert any("Clothing" in c for c in data["categories"])


def test_api_category_products(client):
    response = client.get("/api/category/Toys & Games?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "standard_results" in data
    assert "has_more" in data
    assert len(data["standard_results"]) > 0


def test_api_semantic_search(client):
    response = client.get("/api/semantic_search?q=running+shoes")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    if data["results"]:
        item = data["results"][0]
        assert "asin" in item
        assert "title" in item


def test_api_recommendations(client, db_session):
    prod = db_session.query(Product).first()
    assert prod is not None
    response = client.get(f"/api/recommendations/{prod.asin}")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. AUTHENTICATION & PASSWORD UPGRADE
# ═══════════════════════════════════════════════════════════════════════════════

def test_login_invalid_credentials(client):
    response = client.post("/api/login", json={
        "username": "non_existent_user_xyz",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401


def test_register_and_login_flow(client):
    unique_user = f"test_{uuid.uuid4().hex[:8]}"
    pwd = "SecureTestPassword!123"

    # Register
    reg_resp = client.post("/api/register", json={
        "username": unique_user,
        "password": pwd,
        "email": f"{unique_user}@example.com"
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data.get("status") == "success"
    user_id = reg_data.get("user_id")
    assert user_id is not None

    # Duplicate registration should fail
    dup_resp = client.post("/api/register", json={
        "username": unique_user,
        "password": pwd
    })
    assert dup_resp.status_code == 400

    # Login
    login_resp = client.post("/api/login", json={
        "username": unique_user,
        "password": pwd
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data.get("status") == "success"
    assert login_data.get("username") == unique_user


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CART & CHECKOUT WITH REAL ORDER PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

def test_cart_sync(client, db_session):
    prod = db_session.query(Product).first()
    assert prod is not None

    sync_resp = client.post("/api/cart_sync/1", json={
        "cart": [{"asin": prod.asin, "quantity": 2}]
    })
    assert sync_resp.status_code == 200
    assert sync_resp.json().get("status") == "success"


def test_checkout_validation(client):
    # Empty cart checkout should fail
    empty_resp = client.post("/api/checkout", json={
        "user_id": 1,
        "full_name": "Test User",
        "address": "123 Test St",
        "city": "Dallas",
        "zip_code": "75001",
        "payment_method": "Credit Card",
        "items": []
    })
    assert empty_resp.status_code == 400


def test_checkout_order_creation(client, db_session):
    prod = db_session.query(Product).first()
    assert prod is not None

    checkout_payload = {
        "user_id": 1,
        "full_name": "Automated Tester",
        "address": "456 Silicon Ave",
        "city": "Austin",
        "zip_code": "78701",
        "payment_method": "Credit Card",
        "items": [{"asin": prod.asin, "quantity": 3}]
    }

    resp = client.post("/api/checkout", json=checkout_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "success"
    order_id = data.get("order_id")
    assert order_id is not None
    assert data.get("total_amount") > 0

    # Verify Order in DB
    order = db_session.query(Order).filter(Order.order_id == order_id).first()
    assert order is not None
    assert order.user_id == 1
    assert order.full_name == "Automated Tester"

    # Verify OrderItems in DB
    order_items = db_session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    assert len(order_items) == 1
    assert order_items[0].asin == prod.asin
    assert order_items[0].quantity == 3


# ═══════════════════════════════════════════════════════════════════════════════
# 5. REAL PRODUCT REVIEWS
# ═══════════════════════════════════════════════════════════════════════════════

def test_reviews_submission_and_retrieval(client, db_session):
    prod = db_session.query(Product).first()
    assert prod is not None

    test_comment = f"Automated test review {uuid.uuid4().hex[:6]}"
    post_resp = client.post("/api/reviews", json={
        "asin": prod.asin,
        "user_id": 1,
        "rating": 5,
        "comment": test_comment
    })
    assert post_resp.status_code == 200
    assert post_resp.json().get("status") == "success"

    # Fetch reviews
    get_resp = client.get(f"/api/reviews/{prod.asin}")
    assert get_resp.status_code == 200
    reviews = get_resp.json().get("reviews", [])
    assert any(r.get("comment") == test_comment for r in reviews)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. ADMIN DASHBOARD & MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def test_admin_stats_schema(client):
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()

    assert "catalog" in data
    assert "total_products" in data["catalog"]
    assert "total_interactions" in data["catalog"]
    assert data["catalog"]["total_products"] > 1000000

    assert "ab_testing" in data
    assert "group_a_conversion_pct" in data["ab_testing"]
    assert "winner" in data["ab_testing"]

    assert "users" in data
    assert "logs" in data
    assert "products" in data


def test_admin_users_and_user_detail(client):
    # List users
    users_resp = client.get("/api/admin/users")
    assert users_resp.status_code == 200
    res_data = users_resp.json()
    assert "users" in res_data
    users = res_data["users"]
    assert isinstance(users, list)
    assert len(users) > 0

    first_user_id = users[0]["user_id"]

    # Get user detail modal
    detail_resp = client.get(f"/api/admin/user/{first_user_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert "metrics" in detail
    assert "orders" in detail
    assert "basket" in detail
    assert "most_viewed" in detail
    assert "reviews" in detail


# ═══════════════════════════════════════════════════════════════════════════════
# 7. ML & RECSYS ENGINE INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

def test_vector_engine_ready():
    engine = VectorEngine()
    assert engine.is_ready() is True

    hits = engine.search("summer dress", top_k=5)
    assert len(hits) > 0
    assert "asin" in hits[0]
    assert "distance" in hits[0]


def test_ncf_engine_loaded():
    ncf = NCFEngine(base_dir=APP_DIR)
    assert ncf.is_ready() is True
    # Test top k item ranking for user 1
    sample_asins = list(ncf.item_map.keys())[:10]
    recs = ncf.rank_items_for_user(user_id=1, items_to_rank=sample_asins)
    assert recs is not None
    assert len(recs) > 0
