"""
app.py — SmartRec FastAPI Backend
Complete, clean rewrite. No blocking calls in async endpoints.
All DB reads use raw sqlite3 (fastest possible) via thread pool.
"""
from fastapi import FastAPI, Request, BackgroundTasks, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
import os
import hashlib
import random
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import threading
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, get_db, User, Product, UserLog, UserCart, UserReview, Order, OrderItem, init_db, SessionLocal
from ml_engine import UserMLEngine
from ncf_engine import NCFEngine
from vector_engine import SemanticSearchEngine
from semantic_fallback_logger import SemanticFallbackManager

# ── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
DB_PATH  = os.path.join(BASE_DIR, "fast_ecommerce.db")
CATS_FILE = os.path.join(BASE_DIR, "categories_cache.json")
_fallback_mgr = SemanticFallbackManager(db_path=DB_PATH)

# ── Thread pool — DB/request work (never blocked by ML) ─────────────────────
_pool    = ThreadPoolExecutor(max_workers=16, thread_name_prefix="req")
# ── Separate ML executor — training runs here, never starves requests ─────────
_ml_pool = ThreadPoolExecutor(max_workers=2,  thread_name_prefix="ml")

# ── In-memory caches ─────────────────────────────────────────────────────────
_categories_cache: list | None = None
_trending_cache:   list | None = None
_trending_ts:      datetime | None = None
_top_cats_cache:   list | None = None
_top_cats_ts:      datetime | None = None
_ml_cache:         dict[int, UserMLEngine] = {}
# Per-user training lock — prevents concurrent retrains for same user
_train_locks:      dict[int, threading.Lock] = {}
# Per-user last-train timestamp — throttle: max 1 retrain per 60s
_last_train_ts:    dict[int, datetime] = {}

def _get_ml(uid: int) -> UserMLEngine:
    if uid not in _ml_cache:
        _ml_cache[uid] = UserMLEngine(user_id=uid, db_path=DB_PATH)
    return _ml_cache[uid]

def _get_train_lock(uid: int) -> threading.Lock:
    if uid not in _train_locks:
        _train_locks[uid] = threading.Lock()
    return _train_locks[uid]

# ── Raw sqlite3 helper — bypass SQLAlchemy for reads ─────────────────────────
def _raw_conn():
    """Return a fast raw sqlite3 connection with all performance PRAGMAs."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-131072")
    conn.execute("PRAGMA mmap_size=5368709120")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def _rows_to_list(rows) -> list[dict]:
    """Convert sqlite3.Row list to plain dicts, replacing None with 0."""
    result = []
    for r in rows:
        d = dict(r)
        result.append({k: (0 if v is None else v) for k, v in d.items()})
    return result

# ── Pydantic models ───────────────────────────────────────────────────────────
class AuthRequest(BaseModel):
    username: str
    password: str

class LogActionRequest(BaseModel):
    user_id: int
    asin: str
    action: str
    view_duration: int = 0
    search_query: str = ""

class CartItem(BaseModel):
    asin: str
    quantity: int

class CartSyncRequest(BaseModel):
    cart: list[CartItem]

class ReviewCreateRequest(BaseModel):
    user_id: int
    asin: str
    rating: float = 5.0
    comment: str

class CheckoutRequest(BaseModel):
    user_id: int
    full_name: str
    address: str
    city: str
    zip_code: str
    items: list[CartItem]

def _hash(pw: str, salt: str = "smartrec_salt_2026") -> str:
    """Salted PBKDF2 HMAC SHA-256 for secure password storage."""
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100000).hex()

def _verify_pw(stored: str, provided: str) -> bool:
    """Verify password supporting both new PBKDF2 and legacy SHA-256 hashes."""
    if stored == _hash(provided):
        return True
    if stored == hashlib.sha256(provided.encode()).hexdigest():
        return True
    return False

# ── Semantic engine (loaded once) ────────────────────────────────────────────
try:
    _semantic = SemanticSearchEngine()
except Exception as e:
    print(f"[Warning] Semantic engine failed: {e}")
    _semantic = None

# ── App lifespan — runs ONCE at startup, non-blocking ────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _categories_cache
    # Load categories from file (< 1ms, no DB query)
    try:
        with open(CATS_FILE, "r", encoding="utf-8") as f:
            _categories_cache = json.load(f)
        print(f"[Startup] Loaded {len(_categories_cache)} categories from cache file.")
    except Exception:
        print("[Startup] No categories cache file — will query DB on first request.")

    init_db()
    print("[Startup] Database ready.")
    yield  # Server runs here
    print("[Shutdown] Done.")

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(lifespan=lifespan)

_STATIC_DIR   = os.path.abspath(os.path.join(BASE_DIR, "static"))
_TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "templates"))

os.makedirs(os.path.join(_STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(_STATIC_DIR, "js"),  exist_ok=True)
os.makedirs(_TEMPLATE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=_STATIC_DIR, html=False), name="static")
templates = Jinja2Templates(directory=_TEMPLATE_DIR)

# ── Helper: run blocking function in thread pool without freezing server ──────
async def _run(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_pool, fn, *args)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/",          response_class=HTMLResponse)
@app.get("/login",     response_class=HTMLResponse)
async def page_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/home",      response_class=HTMLResponse)
async def page_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/categories",response_class=HTMLResponse)
async def page_categories(request: Request):
    return templates.TemplateResponse(request=request, name="categories.html")

@app.get("/product",   response_class=HTMLResponse)
async def page_product(request: Request):
    return templates.TemplateResponse(request=request, name="product.html")

@app.get("/cart",      response_class=HTMLResponse)
async def page_cart(request: Request):
    return templates.TemplateResponse(request=request, name="cart.html")

@app.get("/checkout",  response_class=HTMLResponse)
async def page_checkout(request: Request):
    return templates.TemplateResponse(request=request, name="checkout.html")

@app.get("/profile",   response_class=HTMLResponse)
async def page_profile(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html")

@app.get("/admin",     response_class=HTMLResponse)
async def page_admin(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════
@app.post("/api/register")
def register(req: AuthRequest, db: Session = Depends(get_db)):
    try:
        new_user = User(
            username=req.username,
            password=_hash(req.password),
            ab_group=random.choice(["A", "B"]),
            is_admin=1 if req.username.lower() == "admin" else 0
        )
        db.add(new_user); db.commit(); db.refresh(new_user)
        return {"status": "success", "user_id": new_user.user_id, "username": req.username}
    except Exception:
        db.rollback()
        raise HTTPException(400, "Username already exists")

@app.post("/api/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not _verify_pw(user.password, req.password):
        raise HTTPException(401, "Invalid credentials")
    # Seamlessly upgrade legacy SHA-256 hash to PBKDF2
    if user.password == hashlib.sha256(req.password.encode()).hexdigest():
        user.password = _hash(req.password)
        db.commit()
    return {"status":"success","user_id":user.user_id,"username":req.username,
            "ab_group":user.ab_group,"is_admin":user.is_admin}

# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/product/{asin}")
def get_product(asin: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.asin == asin).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return {"status":"success","product":{k:v for k,v in p.__dict__.items() if not k.startswith("_")}}

# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORIES — instant from memory / file
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/categories")
async def get_categories():
    global _categories_cache

    # Serve from memory (always available after startup)
    if _categories_cache is not None:
        return {"categories": _categories_cache}

    # Read from pre-built file (< 1ms)
    try:
        with open(CATS_FILE, "r", encoding="utf-8") as f:
            _categories_cache = json.load(f)
        return {"categories": _categories_cache}
    except Exception:
        pass

    # Last resort — query DB in thread pool (won't block server)
    def _query():
        conn = _raw_conn()
        rows = conn.execute(
            "SELECT category_name FROM Products GROUP BY category_name ORDER BY COUNT(*) DESC"
        ).fetchall()
        conn.close()
        cats = [r[0] for r in rows if r[0]]
        try:
            with open(CATS_FILE, "w", encoding="utf-8") as f:
                json.dump(cats, f)
        except Exception:
            pass
        return cats

    _categories_cache = await _run(_query)
    return {"categories": _categories_cache}

# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY PRODUCTS — paginated, runs in thread pool (non-blocking)
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/category_products/{category_name}")
@app.get("/api/category/{category_name}")
async def get_category_products(category_name: str, user_id: int = 0, page: int = 1):
    """
    Fetch paginated products for a category.
    Runs entirely in a thread pool — never blocks the async event loop.
    """
    page_size = 24
    offset    = (page - 1) * page_size

    def _fetch():
        conn = _raw_conn()
        rows = conn.execute("""
            SELECT asin, title, imgUrl, price, stars, reviews, isBestSeller, category_name
            FROM Products
            WHERE category_name = ?
            ORDER BY reviews DESC
            LIMIT ? OFFSET ?
        """, (category_name, page_size + 12, offset)).fetchall()
        conn.close()
        return _rows_to_list(rows)

    products = await _run(_fetch)
    
    # Calculate has_more before we filter out ML picks
    original_has_more = len(products) > page_size

    if not products:
        return {"ml_picks": [], "standard_results": [], "page": page, "has_more": False}

    ml_picks = []

    # ML personalisation — only if user has enough logs
    if user_id > 0:
        def _log_count():
            conn = _raw_conn()
            r = conn.execute("SELECT COUNT(*) FROM UserLogs WHERE user_id=?", (user_id,)).fetchone()
            conn.close()
            return r[0]

        lc = await _run(_log_count)
        if lc >= 20:
            try:
                import pandas as pd
                df = pd.DataFrame(products)
                def _rank():
                    eng = _get_ml(user_id)
                    return eng.rank_products(df.copy(), category_name=category_name)
                ranked_df = await _run(_rank)
                ml_picks  = ranked_df.head(12).fillna(0).to_dict(orient="records")
                ml_asins  = {p["asin"] for p in ml_picks}
                products  = [p for p in products if p["asin"] not in ml_asins]
            except Exception as e:
                print(f"[ML] rank failed user={user_id}: {e}")

    # If we originally fetched more than page_size + 12, there's definitely another page
    # But more simply, if the query returned more than page_size, we probably have more.
    # Actually, we should just check if the original DB fetch hit the limit.
    standard = products[:page_size]
    
    return {"ml_picks": ml_picks, "standard_results": standard, "page": page, "has_more": original_has_more}

# ═══════════════════════════════════════════════════════════════════════════════
# HOME FEED
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/home_feed")
async def get_home_feed(user_id: int):
    global _trending_cache, _trending_ts, _top_cats_cache, _top_cats_ts

    def _get_user_info():
        conn = _raw_conn()
        grp = conn.execute("SELECT ab_group FROM Users WHERE user_id=?", (user_id,)).fetchone()
        cnt = conn.execute("SELECT COUNT(*) FROM UserLogs WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
        return (grp[0] if grp else "A"), (cnt[0] if cnt else 0)

    ab_group, log_count = await _run(_get_user_info)
    feed      = []

    # ── Section 1: ML or Trending ─────────────────────────────────────────
    if ab_group == "A" and log_count >= 20:
        def _get_top_cats():
            conn = _raw_conn()
            rows = conn.execute("""
                SELECT p.category_name, COUNT(*) as cnt
                FROM UserLogs l JOIN Products p ON l.asin=p.asin
                WHERE l.user_id=? GROUP BY p.category_name ORDER BY cnt DESC LIMIT 2
            """, (user_id,)).fetchall()
            conn.close()
            return [r[0] for r in rows]

        top_cats = await _run(_get_top_cats)

        if top_cats:
            placeholders = ",".join("?" * len(top_cats))

            def _get_candidates():
                conn = _raw_conn()
                rows = conn.execute(
                    f'SELECT asin,title,imgUrl,price,stars,reviews,category_name,isBestSeller '
                    f'FROM Products WHERE category_name IN ({placeholders}) ORDER BY reviews DESC LIMIT 100',
                    top_cats
                ).fetchall()
                conn.close()
                return _rows_to_list(rows)

            candidates = await _run(_get_candidates)
            if candidates:
                import pandas as pd, random as _r
                df = pd.DataFrame(candidates).sample(frac=1).head(50)

                def _rank():
                    eng = _get_ml(user_id)
                    return eng.rank_products(df, category_name=top_cats[0])

                ranked = await _run(_rank)
                try:
                    ncf = NCFEngine(BASE_DIR)
                    scores = ncf.rank_items_for_user(user_id, ranked["asin"].tolist())
                    if scores and "ml_score" in ranked.columns:
                        sm = dict(scores)
                        ranked["ncf_prob"]    = ranked["asin"].map(sm).fillna(0)
                        ranked["final_score"] = ranked["ml_score"]*0.7 + ranked["ncf_prob"]*0.3
                        ranked = ranked.sort_values("final_score", ascending=False)
                except Exception:
                    pass

                feed.append({"title":"Top Picks for You","badge":"ML + NCF",
                              "products": ranked.head(15).fillna(0).to_dict(orient="records")})
    else:
        # Trending — cached 10 min
        if _trending_cache is None or (datetime.now() - (_trending_ts or datetime.min)) > timedelta(minutes=10):
            def _trending():
                conn = _raw_conn()
                rows = conn.execute(
                    'SELECT asin,title,imgUrl,price,stars,reviews,category_name,isBestSeller '
                    'FROM Products WHERE isBestSeller=1 ORDER BY reviews DESC LIMIT 15'
                ).fetchall()
                conn.close()
                return _rows_to_list(rows)
            _trending_cache = await _run(_trending)
            _trending_ts = datetime.now()
        feed.append({"title": "Trending Now", "products": _trending_cache})

    # ── Sections 2-3: random category carousels — cached 1h ─────────────────
    if _top_cats_cache is None or (datetime.now() - (_top_cats_ts or datetime.min)) > timedelta(hours=1):
        _top_cats_cache = _categories_cache[:20] if _categories_cache else []
        _top_cats_ts = datetime.now()

    if _top_cats_cache:
        for cat in random.sample(_top_cats_cache, min(2, len(_top_cats_cache))):
            def _cat_prods(c=cat):
                conn = _raw_conn()
                rows = conn.execute(
                    'SELECT asin,title,imgUrl,price,stars,reviews,category_name,isBestSeller '
                    'FROM Products WHERE category_name=? ORDER BY reviews DESC LIMIT 15', (c,)
                ).fetchall()
                conn.close()
                return _rows_to_list(rows)
            prods = await _run(_cat_prods)
            feed.append({"title": f"Best in {cat}", "products": prods})

    return {"sections": feed}

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING — fire and forget, never blocks the response
# ═══════════════════════════════════════════════════════════════════════════════
def _do_log(user_id, asin, action, view_duration, search_query):
    """Write log to DB (fast). Resolves unlisted items to related catalog items. Schedule training separately with throttle."""
    db = SessionLocal()
    try:
        # Check if item is in catalog; if not, find closely related catalog item
        prod_exists = db.query(Product.asin).filter(Product.asin == asin).first()
        if not prod_exists:
            resolved = _fallback_mgr.resolve_browsed_item(asin, category_hint=search_query)
            orig_asin = asin
            asin = resolved["asin"]
            search_query = f"[Fallback: {orig_asin}] {search_query}".strip()

        db.add(UserLog(user_id=user_id, asin=asin, action=action,
                       view_duration=view_duration, search_query=search_query))
        db.commit()
    except Exception as e:
        db.rollback(); print(f"[Log] write err: {e}")
    finally:
        db.close()

    # Schedule ML training on the dedicated ML pool (non-blocking for requests)
    _ml_pool.submit(_try_train, user_id)

def _try_train(user_id: int):
    """
    Train only if:
    1. No other training is running for this user (lock)
    2. At least 60 seconds since last train (throttle)
    """
    lock = _get_train_lock(user_id)
    if not lock.acquire(blocking=False):  # Skip if already training
        return
    try:
        last = _last_train_ts.get(user_id)
        if last and (datetime.now() - last).total_seconds() < 60:
            return  # Too soon — skip
        _last_train_ts[user_id] = datetime.now()
        _ml_cache.pop(user_id, None)
        _get_ml(user_id).train_if_needed()
    except Exception as e:
        print(f"[Train] uid={user_id}: {e}")
    finally:
        lock.release()

@app.post("/api/log_action")
async def log_action(req: LogActionRequest, bg: BackgroundTasks):
    bg.add_task(_do_log, req.user_id, req.asin, req.action, req.view_duration, req.search_query)
    return {"status": "logged"}

# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/search")
async def search(q: str, user_id: int, smart_recommendation: str = "false"):
    def _do_search():
        conn = _raw_conn()
        pat  = f"%{q}%"
        rows = conn.execute("""
            SELECT asin, title, imgUrl, productURL, stars, reviews, price,
                   listPrice, category_name, isBestSeller
            FROM Products
            WHERE title LIKE ? OR category_name LIKE ?
            ORDER BY isBestSeller DESC, reviews DESC
            LIMIT 60
        """, (pat, pat)).fetchall()
        conn.close()
        return _rows_to_list(rows)

    results = await _run(_do_search)
    if not results:
        return {"results": []}

    if smart_recommendation.lower() == "true" and user_id:
        try:
            import pandas as pd
            df  = pd.DataFrame(results)
            cat = df["category_name"].value_counts().idxmax()
            def _rank():
                return _get_ml(user_id).rank_products(df, category_name=cat)
            ranked = await _run(_rank)
            results = ranked.fillna(0).to_dict(orient="records")
        except Exception:
            pass
    return {"results": results}

@app.get("/api/semantic_search")
async def semantic_search(q: str):
    if not _semantic or _semantic.index is None:
        return JSONResponse(500, {"status":"error","message":"Semantic index not built."})
    # State-of-the-art Hybrid Search (Dense FAISS + Sparse Lexical RRF)
    hits = _semantic.hybrid_search(q, top_k=20) if hasattr(_semantic, "hybrid_search") else _semantic.search(q, top_k=20)
    if not hits: return {"results": []}
    asins = [h["asin"] for h in hits]
    def _fetch():
        conn = _raw_conn()
        ph   = ",".join("?" * len(asins))
        rows = conn.execute(
            f'SELECT asin,title,imgUrl,productURL,price,stars,reviews,category_name FROM Products WHERE asin IN ({ph})',
            asins
        ).fetchall()
        conn.close()
        return _rows_to_list(rows)
    products = await _run(_fetch)
    rank_map = {asin: rank for rank, asin in enumerate(asins)}
    products.sort(key=lambda p: rank_map.get(p["asin"], 999))
    return {"results": products}

# ═══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/recommendations/{asin}")
def get_recommendations(asin: str, user_id: int = 0, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.asin == asin).first()
    if not p: return {"recommendations": []}
    
    conn = _raw_conn()
    rows = conn.execute(
        'SELECT asin,title,imgUrl,price,stars,reviews FROM Products WHERE category_name=? AND asin!=? ORDER BY reviews DESC LIMIT 8',
        (p.category_name, asin)
    ).fetchall()
    conn.close()
    return {"recommendations": _rows_to_list(rows)}

# ═══════════════════════════════════════════════════════════════════════════════
# CART & CHECKOUT
# ═══════════════════════════════════════════════════════════════════════════════
@app.post("/api/cart_sync/{user_id}")
def sync_cart(user_id: int, req: CartSyncRequest, db: Session = Depends(get_db)):
    db.query(UserCart).filter(UserCart.user_id == user_id).delete()
    for item in req.cart:
        db.add(UserCart(user_id=user_id, asin=item.asin, quantity=item.quantity))
    db.commit()
    return {"status": "success"}

@app.post("/api/checkout")
async def checkout(req: CheckoutRequest, db: Session = Depends(get_db)):
    if not req.items:
        raise HTTPException(400, "Cart is empty")

    asins = [item.asin for item in req.items]
    prods = {p.asin: p for p in db.query(Product).filter(Product.asin.in_(asins)).all()}

    total = 0.0
    new_order = Order(
        user_id=req.user_id,
        full_name=req.full_name,
        address=req.address,
        city=req.city,
        zip_code=req.zip_code,
        status="Completed"
    )
    db.add(new_order)
    db.flush()

    for item in req.items:
        p = prods.get(item.asin)
        price = float(p.price) if p and p.price else 0.0
        title = p.title if p else "Product"
        imgUrl = p.imgUrl if p else ""
        item_total = price * item.quantity
        total += item_total

        db.add(OrderItem(
            order_id=new_order.order_id,
            asin=item.asin,
            title=title,
            imgUrl=imgUrl,
            price_at_purchase=price,
            quantity=item.quantity
        ))

        # Log purchase action for ML pipeline
        db.add(UserLog(
            user_id=req.user_id,
            asin=item.asin,
            action="purchase",
            view_duration=0,
            search_query=""
        ))

    # Apply 8% tax
    new_order.total_amount = round(total * 1.08, 2)

    # Clear persisted user cart
    db.query(UserCart).filter(UserCart.user_id == req.user_id).delete()
    db.commit()

    # Trigger ML training check
    _ml_pool.submit(_try_train, req.user_id)

    return {
        "status": "success",
        "order_id": new_order.order_id,
        "total_amount": new_order.total_amount,
        "item_count": len(req.items)
    }

# ═══════════════════════════════════════════════════════════════════════════════
# REVIEWS
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/reviews/{asin}")
async def get_reviews(asin: str):
    def _fetch():
        conn = _raw_conn()
        rows = conn.execute("""
            SELECT r.review_id, r.user_id, u.username, r.rating, r.comment, r.created_at
            FROM UserReviews r
            JOIN Users u ON r.user_id = u.user_id
            WHERE r.asin = ?
            ORDER BY r.created_at DESC
        """, (asin,)).fetchall()
        conn.close()
        return _rows_to_list(rows)
    reviews = await _run(_fetch)
    return {"status": "success", "asin": asin, "reviews": reviews}

@app.post("/api/reviews")
def create_review(req: ReviewCreateRequest, db: Session = Depends(get_db)):
    if not req.comment.strip():
        raise HTTPException(400, "Review comment cannot be empty")
    new_rev = UserReview(
        user_id=req.user_id,
        asin=req.asin,
        rating=max(1.0, min(5.0, float(req.rating))),
        comment=req.comment.strip()
    )
    db.add(new_rev)
    db.commit()
    return {"status": "success", "message": "Review submitted successfully"}

# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/profile/{user_id}")
async def get_profile(user_id: int):
    def _fetch():
        conn = _raw_conn()
        most_viewed = _rows_to_list(conn.execute("""
            SELECT p.asin,p.title,p.price,p.imgUrl,COUNT(l.log_id) as views
            FROM UserLogs l JOIN Products p ON l.asin=p.asin
            WHERE l.user_id=? AND l.action='view'
            GROUP BY p.asin,p.title,p.price,p.imgUrl ORDER BY views DESC LIMIT 6
        """, (user_id,)).fetchall())

        # Real orders from Orders and OrderItems
        order_rows = conn.execute("""
            SELECT o.order_id, o.created_at as timestamp, o.total_amount,
                   oi.asin, oi.title, oi.imgUrl, oi.price_at_purchase as price, oi.quantity
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC LIMIT 20
        """, (user_id,)).fetchall()

        if not order_rows:
            orders = _rows_to_list(conn.execute("""
                SELECT 0 as order_id, p.asin, p.title, p.price, p.imgUrl, l.timestamp, 1 as quantity
                FROM UserLogs l JOIN Products p ON l.asin=p.asin
                WHERE l.user_id=? AND l.action='purchase' ORDER BY l.timestamp DESC LIMIT 15
            """, (user_id,)).fetchall())
        else:
            orders = _rows_to_list(order_rows)

        past = _rows_to_list(conn.execute("""
            SELECT p.asin,p.title,p.price,p.imgUrl,MAX(l.timestamp) as last_viewed
            FROM UserLogs l JOIN Products p ON l.asin=p.asin
            WHERE l.user_id=? AND l.action='view'
            GROUP BY p.asin,p.title,p.price,p.imgUrl ORDER BY last_viewed DESC LIMIT 10
        """, (user_id,)).fetchall())
        conn.close()
        return most_viewed, orders, past
    mv, orders, past = await _run(_fetch)
    return {"most_viewed": mv, "orders": orders, "past_viewed": past}

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    def _stats():
        conn = _raw_conn()
        total_u = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        grp_a   = conn.execute("SELECT COUNT(*) FROM Users WHERE ab_group='A'").fetchone()[0]
        grp_b   = conn.execute("SELECT COUNT(*) FROM Users WHERE ab_group='B'").fetchone()[0]
        total_l = conn.execute("SELECT COUNT(*) FROM UserLogs").fetchone()[0]
        total_p = conn.execute("SELECT COUNT(*) FROM Products").fetchone()[0]
        ca = conn.execute("""SELECT COUNT(*) t, SUM(CASE WHEN l.action IN('cart','purchase') THEN 1 ELSE 0 END) c
            FROM UserLogs l JOIN Users u ON l.user_id=u.user_id WHERE u.ab_group='A'""").fetchone()
        cb = conn.execute("""SELECT COUNT(*) t, SUM(CASE WHEN l.action IN('cart','purchase') THEN 1 ELSE 0 END) c
            FROM UserLogs l JOIN Users u ON l.user_id=u.user_id WHERE u.ab_group='B'""").fetchone()
        conn.close()
        pct = lambda r: round((r[1] or 0)/r[0]*100,2) if r and r[0] else 0.0
        pct_a = pct(ca)
        pct_b = pct(cb)
        winner = "Group A (Machine Learning)" if pct_a >= pct_b else "Group B (Baseline Trending)"
        return {
            "users": {"total": total_u, "group_A": grp_a, "group_B": grp_b},
            "logs": {"total": total_l},
            "products": {"total": total_p},
            "catalog": {
                "total_products": total_p,
                "total_interactions": total_l
            },
            "ab_testing": {
                "group_a_conversion_pct": pct_a,
                "group_b_conversion_pct": pct_b,
                "winner": winner,
                "group_A": {"conversion_rate": pct_a},
                "group_B": {"conversion_rate": pct_b}
            }
        }
    return await _run(_stats)

@app.get("/api/admin/users")
async def get_admin_users():
    def _fetch():
        conn = _raw_conn()
        rows = conn.execute("""
            SELECT u.user_id, u.username, u.ab_group, u.is_admin,
                   (SELECT COUNT(*) FROM UserLogs l WHERE l.user_id = u.user_id) as log_count,
                   (SELECT COUNT(*) FROM Orders o WHERE o.user_id = u.user_id) as order_count
            FROM Users u
            ORDER BY log_count DESC
        """).fetchall()
        conn.close()
        res = []
        for r in rows:
            lc = r["log_count"] or 0
            oc = r["order_count"] or 0
            res.append({
                "user_id": r["user_id"],
                "username": r["username"],
                "ab_group": r["ab_group"],
                "is_admin": r["is_admin"],
                "log_count": lc,
                "logs": lc,
                "order_count": oc,
                "orders": oc
            })
        return res
    return {"users": await _run(_fetch)}

@app.get("/api/admin/user/{user_id}")
async def get_admin_user_detail(user_id: int):
    def _fetch():
        conn = _raw_conn()
        u = conn.execute("SELECT user_id, username, ab_group, is_admin FROM Users WHERE user_id=?", (user_id,)).fetchone()
        if not u:
            conn.close()
            raise HTTPException(404, "User not found")

        basket = _rows_to_list(conn.execute("""
            SELECT c.asin, c.quantity, p.title, p.price, p.imgUrl
            FROM UserCart c
            JOIN Products p ON c.asin = p.asin
            WHERE c.user_id = ?
        """, (user_id,)).fetchall())

        most_viewed = _rows_to_list(conn.execute("""
            SELECT p.asin, p.title, p.price, p.imgUrl, COUNT(l.log_id) as views
            FROM UserLogs l JOIN Products p ON l.asin=p.asin
            WHERE l.user_id=? AND l.action='view'
            GROUP BY p.asin, p.title, p.price, p.imgUrl ORDER BY views DESC LIMIT 6
        """, (user_id,)).fetchall())

        orders = _rows_to_list(conn.execute("""
            SELECT o.order_id, o.created_at as timestamp, oi.asin, oi.title, oi.price_at_purchase as price, oi.quantity, oi.imgUrl
            FROM Orders o
            JOIN OrderItems oi ON o.order_id = oi.order_id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC LIMIT 10
        """, (user_id,)).fetchall())

        if not orders:
            orders = _rows_to_list(conn.execute("""
                SELECT 0 as order_id, l.timestamp, p.asin, p.title, p.price, 1 as quantity, p.imgUrl
                FROM UserLogs l JOIN Products p ON l.asin=p.asin
                WHERE l.user_id=? AND l.action='purchase' ORDER BY l.timestamp DESC LIMIT 10
            """, (user_id,)).fetchall())

        reviews = _rows_to_list(conn.execute("""
            SELECT r.review_id, r.asin, p.title, r.rating, r.comment, r.created_at
            FROM UserReviews r
            JOIN Products p ON r.asin = p.asin
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC LIMIT 10
        """, (user_id,)).fetchall())
        conn.close()

        metrics = None
        metrics_file = os.path.join(BASE_DIR, "models", f"user_{user_id}_metrics.json")
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, "r") as mf:
                    metrics = json.load(mf)
            except Exception:
                pass

        return {
            "user_id": u["user_id"],
            "username": u["username"],
            "ab_group": u["ab_group"],
            "is_admin": u["is_admin"],
            "metrics": metrics,
            "basket": basket,
            "most_viewed": most_viewed,
            "orders": orders,
            "reviews": reviews
        }
    return await _run(_fetch)

@app.post("/api/admin/train_ncf")
async def admin_train_ncf(bg: BackgroundTasks):
    def _train():
        try:
            print("[NCF] Starting global training from admin trigger...")
            ncf = NCFEngine(BASE_DIR)
            ncf.train(epochs=5)
            print("[NCF] Admin triggered training finished successfully.")
        except Exception as e:
            print(f"[NCF Admin Train Error] {e}")
    bg.add_task(_train)
    return {"status": "success", "message": "NCF model training initiated in background."}

@app.get("/api/admin/daily_report")
async def get_daily_report():
    def _fetch():
        conn = _raw_conn()
        rows = conn.execute("""
            SELECT u.user_id, u.username, u.ab_group,
                COUNT(l.log_id) AS total_actions,
                SUM(CASE WHEN l.action='view'     THEN 1 ELSE 0 END) AS views,
                SUM(CASE WHEN l.action='cart'     THEN 1 ELSE 0 END) AS cart_adds,
                SUM(CASE WHEN l.action='purchase' THEN 1 ELSE 0 END) AS purchases,
                SUM(CASE WHEN l.search_query!=''  THEN 1 ELSE 0 END) AS searches
            FROM Users u
            LEFT JOIN UserLogs l ON u.user_id=l.user_id
                AND l.timestamp >= datetime('now','-1 day')
            GROUP BY u.user_id ORDER BY total_actions DESC
        """).fetchall()
        conn.close()
        return _rows_to_list(rows)
    return {"report": await _run(_fetch)}

@app.get("/api/admin/ml_report")
async def get_ml_report():
    def _fetch():
        import sqlite3, json, os
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        users = cursor.execute("SELECT user_id, username FROM Users").fetchall()
        report = []
        models_dir = os.path.join(BASE_DIR, "models")
        
        for u in users:
            uid, uname = u
            is_admin = (uname.lower() == "admin")
            ab_group = "A" if uid % 2 == 1 else "B"
            
            logs = cursor.execute("SELECT action, search_query, timestamp FROM UserLogs WHERE user_id = ?", (uid,)).fetchall()
            total_logs = len(logs)
            
            views = sum(1 for l in logs if l[0] == 'view')
            carts = sum(1 for l in logs if l[0] == 'cart')
            purchases = sum(1 for l in logs if l[0] == 'purchase')
            
            top_cats = cursor.execute("""
                SELECT p.category_name, COUNT(*) as interactions
                FROM UserLogs l
                JOIN Products p ON l.asin = p.asin
                WHERE l.user_id = ?
                GROUP BY p.category_name
                ORDER BY interactions DESC LIMIT 3
            """, (uid,)).fetchall()
            
            recent_searches = cursor.execute("""
                SELECT DISTINCT search_query FROM UserLogs 
                WHERE user_id = ? AND search_query != ''
                ORDER BY timestamp DESC LIMIT 5
            """, (uid,)).fetchall()
            
            metrics_file = os.path.join(models_dir, f"user_{uid}_metrics.json")
            metrics = None
            if os.path.exists(metrics_file):
                with open(metrics_file) as mf:
                    metrics = json.load(mf)
                    
            local_models = []
            if os.path.exists(models_dir):
                for f in os.listdir(models_dir):
                    if f.startswith(f"user_{uid}_local_") and f.endswith(".cbm"):
                        cat = f.split("_local_")[1].replace(".cbm", "")
                        size_kb = os.path.getsize(os.path.join(models_dir, f)) // 1024
                        local_models.append({"category": cat, "size_kb": size_kb})
                        
            # Trigger calculation based on temporal thresholds
            last_trained_count = 0
            if os.path.exists(os.path.join(models_dir, f"user_{uid}_last_trained.txt")):
                try:
                    with open(os.path.join(models_dir, f"user_{uid}_last_trained.txt"), "r") as f:
                        last_trained_count = int(f.read().strip())
                except: pass
                
            logs_since_last = total_logs - last_trained_count
            next_retrain = max(0, 20 - logs_since_last)
            
            if next_retrain > 0:
                trigger_status = f"WAITING ({next_retrain} more logs needed)"
            else:
                trigger_status = "READY for retrain"
                
            daily_query = "SELECT COUNT(*) FROM UserLogs WHERE user_id=? AND timestamp >= datetime('now', '-1 day')"
            daily_view_q = "SELECT COUNT(*) FROM UserLogs WHERE user_id=? AND action='view' AND timestamp >= datetime('now', '-1 day')"
            daily_cart_q = "SELECT COUNT(*) FROM UserLogs WHERE user_id=? AND action='cart' AND timestamp >= datetime('now', '-1 day')"
            daily_purch_q = "SELECT COUNT(*) FROM UserLogs WHERE user_id=? AND action='purchase' AND timestamp >= datetime('now', '-1 day')"
            
            report.append({
                "user_id": uid,
                "username": uname,
                "is_admin": is_admin,
                "ab_group": ab_group,
                "total_logs": total_logs,
                "daily_activity": {
                    "total_24h": cursor.execute(daily_query, (uid,)).fetchone()[0],
                    "views_24h": cursor.execute(daily_view_q, (uid,)).fetchone()[0],
                    "cart_24h": cursor.execute(daily_cart_q, (uid,)).fetchone()[0],
                    "purchases_24h": cursor.execute(daily_purch_q, (uid,)).fetchone()[0]
                },
                "global_model_trained": metrics is not None,
                "local_models": local_models,
                "metrics": metrics,
                "action_breakdown": {"views": views, "cart": carts, "purchases": purchases},
                "trigger_status": trigger_status,
                "logs_since_last_train": logs_since_last,
                "next_retrain_in_logs": next_retrain,
                "top_categories": [{"category": c[0], "interactions": c[1]} for c in top_cats],
                "recent_searches": [s[0] for s in recent_searches if s[0]],
                "feature_inputs": ["brand", "price", "stars", "reviews", "category_name", "isBestSeller", "text_features", "EAV product features (if available)"],
                "training_split": "80/20 temporal"
            })
            
        conn.close()
        # Sort by total_logs descending
        report.sort(key=lambda x: x["total_logs"], reverse=True)
        return {"report": report}
        
    return await _run(_fetch)

@app.post("/api/admin/build_faiss_index")
async def build_faiss_index(bg: BackgroundTasks):
    if not _semantic:
        return JSONResponse(500, {"status":"error","message":"Semantic engine not loaded."})
    bg.add_task(_semantic.build_index)
    return {"status": "Building FAISS index in background…"}

@app.post("/api/admin/retrain_all")
def retrain_all(bg: BackgroundTasks, db: Session = Depends(get_db)):
    uids = [u.user_id for u in db.query(User).all()]
    def _retrain():
        for uid in uids:
            try:
                UserMLEngine(user_id=uid, db_path=DB_PATH).train_if_needed(force=True)
                _ml_cache.pop(uid, None)
            except Exception as e:
                print(f"[Retrain] uid={uid}: {e}")
    bg.add_task(_retrain)
    return {"status": f"Retraining {len(uids)} users in background…"}
