# SmartRec: Production AI/ML E-Commerce & Hybrid Recommendation Platform

SmartRec is an end-to-end, high-performance intelligent e-commerce platform powered by a hybrid multi-model recommendation pipeline, FAISS semantic vector search, real-time A/B testing, and an interactive admin monitoring suite.

The system is designed to scale across 1.4+ million catalog items while sustaining sub-millisecond database queries, sub-50ms vector similarity searches, and asynchronous background model retraining without blocking the event loop.

---

## 🏛️ System Architecture

```
                                  [ Web Client / Browser ]
                                             │
                                             ▼
                                   [ FastAPI REST Server ]
                                  (Async Thread Pool Exec)
                                             │
      ┌─────────────────────┬────────────────┼────────────────────┬─────────────────────┐
      ▼                     ▼                ▼                    ▼                     ▼
[ CatBoost Engine ]  [ NCF Engine ]  [ FAISS Engine ]  [ Association Rules ]  [ SQLite Engine ]
 (Personalized &      (Deep NeuMF       (Dense Vector      (Apriori Frequent     (WAL Mode,
  Category-Local)      Embeddings)      Semantic Search)     Itemsets Mining)    Composite Indexes)
```

### Hybrid Multi-Model Recommendation Pipeline

1. **Personalized CatBoost Re-ranking (`ecommerce_app/ml_engine.py`)**:
   - **Temporal Train/Test Split (80/20)**: Interaction logs are ordered strictly by timestamp, preventing data leakage.
   - **Extreme Imbalance Mitigation**: Computes dynamic `scale_pos_weight = neg_count / pos_count` to account for view-to-purchase disparities.
   - **Threshold Optimization**: Tunes decision boundaries using Precision-Recall curves maximizing F1-score.
   - **Hierarchical Fallback**: Utilizes Category-Local models when category interaction threshold $\ge 10$, falling back gracefully to Global models, and ultimately popularity ranking.
   - **EAV Feature Ingestion**: Dynamically pivots Entity-Attribute-Value specifications (`ProductFeatures`) into wide feature spaces, leveraging CatBoost's native missing value handling.

2. **Neural Collaborative Filtering (`ecommerce_app/ncf_engine.py`)**:
   - Deep NeuMF (Neural Matrix Factorization) architecture implemented in PyTorch.
   - Combines Generalized Matrix Factorization (GMF) with Multi-Layer Perceptron (MLP) branches to model both linear latent factor interactions and non-linear user-item relationships.
   - Outputs continuous interaction likelihoods for personalized discovery.

3. **Dense Vector Semantic Search (`ecommerce_app/vector_engine.py`)**:
   - Powered by `sentence-transformers` (`all-MiniLM-L6-v2`) and FAISS (`IndexFlatIP`).
   - Cosine-normalized dense embeddings for real-time natural language catalog queries.

4. **Association Rule Mining & Market Basket Analysis**:
   - Uses Apriori algorithm (`mlxtend`) to discover high-confidence co-purchase rules across product categories.
   - Drives "Frequently Bought Together" recommendations.

5. **Unsupervised Subcategory Clustering**:
   - TF-IDF vectorization paired with KMeans clustering to group similar products within broad categories.

---

## 🔒 Enterprise Security & Database Architecture

- **Password Security**: Passwords are protected using **PBKDF2 HMAC SHA-256** with per-user cryptographic salts (100,000 iterations). Supports automatic zero-downtime migration for legacy SHA-256 hashes upon next authentication.
- **High-Concurrency SQLite WAL**: SQLite operates in `PRAGMA journal_mode=WAL` with `synchronous=NORMAL` and thread-safe connection pooling, enabling concurrent readers alongside background ML writers.
- **Relational Integrity**:
  - `Products`: Complete catalog indexed on `asin` and `category_name`.
  - `ProductFeatures`: EAV attributes for rich item specifications.
  - `Users`: Auth credentials, salt, email, and timestamps.
  - `UserLogs`: Interaction stream (`view`, `add_to_cart`, `purchase`, `search`).
  - `UserCart`: Persisted shopping carts with unique constraints.
  - `Orders` & `OrderItems`: Full relational transaction order history.
  - `UserReviews`: Verified user product reviews with numerical ratings.

---

## 📡 API Reference

### Authentication & Profiles
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register` | Register a new user account |
| `POST` | `/api/login` | Authenticate with salted PBKDF2 verification & auto-upgrade |
| `GET` | `/api/profile/{user_id}` | Retrieve profile, interaction history, and real orders |

### Catalog & Discovery
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/categories` | List all product categories |
| `GET` | `/api/category/{name}` | Paginated category product listings |
| `GET` | `/api/product/{asin}` | Detailed product information |
| `GET` | `/api/semantic_search?q={query}` | FAISS dense vector search across catalog |
| `GET` | `/api/search?q={query}` | Text search query |

### Recommendations
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/recommendations/{asin}` | Content/category based similar products |
| `GET` | `/api/recommended_for_you` | Personalized hybrid recommendations for logged-in user |
| `GET` | `/api/frequently_bought_together/{asin}` | Apriori association rule suggestions |

### Cart & Checkout
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/cart_sync/{user_id}` | Sync and persist shopping cart items |
| `POST` | `/api/checkout` | Process order, create persistent `Order` + `OrderItems`, clear cart |

### Reviews
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/reviews/{asin}` | Retrieve verified product reviews |
| `POST` | `/api/reviews` | Submit product review and rating |

### Admin & Operations
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/stats` | Real-time system metrics, catalog counts, and A/B conversion rates |
| `GET` | `/api/admin/users` | Overview of all active platform users |
| `GET` | `/api/admin/user/{user_id}` | Deep user inspection (basket, purchase history, logs, reviews) |
| `POST` | `/api/admin/train_ncf` | Trigger asynchronous NCF model training |

---

## ⚡ Quickstart Guide

### 1. Environment Setup
```bash
# Clone repository and enter directory
cd "d:\3rd sem created files\AIML PROJECT"

# Activate Python virtual environment
.\ecommerce_app\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Feature Population & Vector Index Build
```bash
# Populate ProductFeatures table with EAV specifications
python ecommerce_app/populate_features.py

# Build or refresh FAISS semantic index
python ecommerce_app/vector_engine.py
```

### 3. Launch Server
```bash
# Launch FastAPI via Uvicorn
uvicorn ecommerce_app.app:app --host 127.0.0.1 --port 8000 --reload
```
Or execute the Windows launcher:
```cmd
ecommerce_app\START_SERVER.bat
```
Navigate to `http://127.0.0.1:8000` in your web browser.

---

## 🧪 Automated Testing

Run the full automated test suite using `pytest`:

```bash
.\ecommerce_app\venv\Scripts\python.exe -m pytest ecommerce_app/tests/test_api.py -v
```

The test suite validates:
- Core HTML views and page rendering
- Category browsing and pagination
- Dense FAISS semantic vector search
- Salted PBKDF2 authentication and invalid credential rejection
- User cart persistence and validation
- Real checkout transaction flow with relational order persistence
- Verified customer reviews creation and retrieval
- Admin dashboard metrics and user inspection modals
- CatBoost and NCF model loading and inference integrity
