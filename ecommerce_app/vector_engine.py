import os
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from database import engine

class SemanticSearchEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.index_path = os.path.join(self.base_dir, 'models', 'product_vectors.index')
        self.asin_mapping_path = os.path.join(self.base_dir, 'models', 'asin_mapping.csv')
        
        print(f"Loading SentenceTransformer model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        self.index = None
        self.asins = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.asin_mapping_path):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(self.index_path)
            self.asins = pd.read_csv(self.asin_mapping_path)['asin'].tolist()
        else:
            print("FAISS index not found. Please build the index first.")

    def build_index(self, limit=5000):
        print(f"Fetching top {limit} products from database for vectorization...")
        query = """
            SELECT asin, title, category_name 
            FROM Products
            WHERE isBestSeller = 1 OR reviews >= 50
            ORDER BY reviews DESC
            LIMIT ?
        """
        import sqlite3
        db_path = os.path.join(self.base_dir, "fast_ecommerce.db")
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
            
        if df.empty:
            print("No products found in the database.")
            return

        print(f"Generating embeddings for {len(df)} products...")
        df['semantic_text'] = df['category_name'].fillna('') + " " + df['title'].fillna('')
        
        embeddings = self.model.encode(df['semantic_text'].tolist(), batch_size=64, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Normalize for cosine similarity via Inner Product index
        faiss.normalize_L2(embeddings)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        
        self.asins = df['asin'].tolist()
        
        # Save to disk
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        pd.DataFrame({'asin': self.asins}).to_csv(self.asin_mapping_path, index=False)
        print(f"Index successfully built and saved ({len(self.asins)} vectors).")

    def search(self, query_text, top_k=20):
        if self.index is None:
            self._load_or_create_index()
            if self.index is None:
                print("Index is not loaded.")
                return []
            
        # Convert user intent to vector and normalize for cosine similarity
        query_vector = self.model.encode([query_text])
        query_vector = np.array(query_vector).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Search FAISS index
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.asins):
                results.append({
                    'asin': self.asins[idx],
                    'distance': float(distances[0][i])
                })
        return results

    def hybrid_search(self, query_text, top_k=20, rrf_k=60):
        """
        State-of-the-art Hybrid Search combining:
        1. Dense Semantic Search (FAISS + all-MiniLM-L6-v2) for conceptual match
        2. Sparse Lexical Search (SQLite token search) for exact brand & model match
        3. Reciprocal Rank Fusion (RRF) to combine rank positions:
           Score(d) = 1 / (rrf_k + rank_dense) + 1 / (rrf_k + rank_lexical)
        """
        import sqlite3

        # 1. Dense Semantic Retrieval
        dense_hits = self.search(query_text, top_k=max(top_k * 2, 40))
        dense_rank = {hit["asin"]: (rank + 1) for rank, hit in enumerate(dense_hits)}
        dense_dist = {hit["asin"]: hit["distance"] for hit in dense_hits}

        # 2. Sparse Lexical Keyword Retrieval
        tokens = [t.strip() for t in query_text.split() if len(t.strip()) > 2]
        lexical_rank = {}
        if tokens:
            try:
                db_path = os.path.join(self.base_dir, "fast_ecommerce.db")
                conn = sqlite3.connect(db_path)
                where_clauses = " AND ".join(["title LIKE ?"] * len(tokens))
                params = [f"%{t}%" for t in tokens] + [max(top_k * 2, 40)]
                lex_rows = conn.execute(
                    f"SELECT asin FROM Products WHERE {where_clauses} ORDER BY reviews DESC LIMIT ?",
                    params
                ).fetchall()
                conn.close()
                for rank, r in enumerate(lex_rows):
                    lexical_rank[r[0]] = rank + 1
            except Exception as e:
                print(f"[Hybrid Search] Lexical retrieval fallback: {e}")

        # 3. Reciprocal Rank Fusion (RRF)
        all_candidate_asins = set(dense_rank.keys()) | set(lexical_rank.keys())
        if not all_candidate_asins:
            return dense_hits[:top_k]

        rrf_scores = {}
        for asin in all_candidate_asins:
            score = 0.0
            if asin in dense_rank:
                score += 1.0 / (rrf_k + dense_rank[asin])
            if asin in lexical_rank:
                score += 1.0 / (rrf_k + lexical_rank[asin])
            rrf_scores[asin] = score

        # Sort descending by fused RRF score
        sorted_asins = sorted(rrf_scores.keys(), key=lambda a: rrf_scores[a], reverse=True)[:top_k]

        results = []
        for asin in sorted_asins:
            results.append({
                "asin": asin,
                "distance": dense_dist.get(asin, 0.5),
                "rrf_score": round(rrf_scores[asin], 6)
            })

        return results

    def is_ready(self):
        return self.index is not None and len(self.asins) > 0

VectorEngine = SemanticSearchEngine

if __name__ == "__main__":
    # If run standalone, build the index
    engine = SemanticSearchEngine()
    engine.build_index(limit=5000)
