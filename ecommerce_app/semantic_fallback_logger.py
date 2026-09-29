import os
import sys
import sqlite3
import numpy as np
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

DB_PATH = os.path.join(APP_DIR, "fast_ecommerce.db")


class SemanticFallbackManager:
    """
    Handles automatic detection and fallback resolution when a real-time user
    browses an item, search query, or external product that is NOT present in
    the website's catalog database.

    Resolution Mechanism:
    1. Direct Catalog Match: Checks if ASIN or exact title exists in Products table.
    2. Dense Semantic Vector Retrieval: If item is missing, runs FAISS dense vector search
       using SentenceTransformer ('all-MiniLM-L6-v2') embeddings on product semantic space.
    3. Sparse Lexical Fallback: Searches category keywords and titles.
    4. Popularity Fallback: Selects top-reviewed item in matching category.
    5. Browsing Logger: Inserts strictly a 'view' action log into UserLogs.
    """
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._semantic_engine = None
        self._resolved_cache = {}
        self._catalog_asin_set = None
        self._init_catalog_cache()

    def _init_catalog_cache(self):
        """Pre-index catalog ASINs in a fast in-memory set for O(1) membership checks."""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT asin FROM Products LIMIT 100000")
            self._catalog_asin_set = set(r[0] for r in cur.fetchall())
            conn.close()
        except Exception as e:
            print(f"[SemanticFallback] Warning initializing ASIN cache: {e}")
            self._catalog_asin_set = set()

    def _get_semantic_engine(self):
        if self._semantic_engine is None:
            try:
                from vector_engine import SemanticSearchEngine
                self._semantic_engine = SemanticSearchEngine()
            except Exception as e:
                print(f"[SemanticFallback] Vector engine unavailable: {e}")
                self._semantic_engine = False
        return self._semantic_engine if self._semantic_engine is not False else None

    def resolve_browsed_item(self, item_query_or_asin, category_hint=None):
        """
        Resolves a browsed product identifier or search query.
        Returns:
            dict containing:
              - 'asin': Valid catalog ASIN
              - 'title': Product title
              - 'category_name': Product category
              - 'price': Product price
              - 'stars': Product rating
              - 'catalog_status': 'Found in Catalog' or 'Unlisted - Semantically Mapped'
              - 'similarity_score': Cosine similarity (1.0 for direct match, 0.70-0.95 for fallback)
        """
        item_str = str(item_query_or_asin).strip()
        cache_key = f"{category_hint or ''}:{item_str}"
        if cache_key in self._resolved_cache:
            return self._resolved_cache[cache_key]

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Step 1: Direct ASIN lookup in Products
        row = cur.execute(
            "SELECT asin, title, category_name, price, stars FROM Products WHERE asin = ?",
            (item_str,)
        ).fetchone()

        if row:
            res = {
                "asin": row[0],
                "title": row[1],
                "category_name": row[2],
                "price": float(row[3] or 0.0),
                "stars": float(row[4] or 0.0),
                "catalog_status": "Found in Catalog",
                "similarity_score": 1.0000
            }
            conn.close()
            self._resolved_cache[cache_key] = res
            return res

        # Step 2: Dense Semantic Vector Fallback
        # Item browsed by user is NOT in website! Pick closest related item from catalog.
        engine = self._get_semantic_engine()
        mapped_asin = None
        sim_score = 0.8500

        query_text = f"{category_hint or ''} {item_str}".strip()
        if engine:
            try:
                hits = engine.search(query_text, top_k=3)
                if hits:
                    mapped_asin = hits[0]["asin"]
                    sim_score = round(float(hits[0]["distance"]), 4)
            except Exception as e:
                print(f"[SemanticFallback] FAISS query error: {e}")

        # Step 3: Sparse Lexical / Category Fallback if FAISS missed
        if not mapped_asin and category_hint:
            lex_row = cur.execute(
                "SELECT asin, title, category_name, price, stars FROM Products WHERE category_name LIKE ? ORDER BY reviews DESC LIMIT 1",
                (f"%{category_hint}%",)
            ).fetchone()
            if lex_row:
                mapped_asin = lex_row[0]
                sim_score = 0.8000

        # Step 4: Final Popularity Fallback
        if not mapped_asin:
            pop_row = cur.execute(
                "SELECT asin, title, category_name, price, stars FROM Products WHERE isBestSeller = 1 ORDER BY reviews DESC LIMIT 1"
            ).fetchone()
            if pop_row:
                mapped_asin = pop_row[0]
                sim_score = 0.7200

        # Retrieve matched product details
        matched_row = cur.execute(
            "SELECT asin, title, category_name, price, stars FROM Products WHERE asin = ?",
            (mapped_asin,)
        ).fetchone()
        conn.close()

        if matched_row:
            res = {
                "asin": matched_row[0],
                "title": matched_row[1],
                "category_name": matched_row[2],
                "price": float(matched_row[3] or 0.0),
                "stars": float(matched_row[4] or 0.0),
                "catalog_status": "Unlisted - Semantically Mapped",
                "similarity_score": sim_score
            }
        else:
            res = {
                "asin": item_str,
                "title": "Uncataloged Item",
                "category_name": category_hint or "General",
                "price": 25.0,
                "stars": 4.5,
                "catalog_status": "Unlisted",
                "similarity_score": 0.5000
            }

        self._resolved_cache[cache_key] = res
        return res

    def log_browsing_interaction(self, user_id, browsed_item, category_hint=None, view_duration=None, timestamp=None):
        """
        Resolves unlisted items to closely related catalog items and records strictly
        a browsing ('view') log into UserLogs.
        """
        resolved = self.resolve_browsed_item(browsed_item, category_hint=category_hint)
        catalog_asin = resolved["asin"]
        
        if view_duration is None:
            view_duration = int(np.clip(np.random.normal(35, 14), 5, 180))
            
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO UserLogs (user_id, asin, action, view_duration, search_query, timestamp)
            VALUES (?, ?, 'view', ?, ?, ?)
        """, (int(user_id), catalog_asin, int(view_duration), str(browsed_item), timestamp))
        conn.commit()
        conn.close()

        return resolved
