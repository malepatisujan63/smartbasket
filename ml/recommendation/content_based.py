import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from ml.utils.logger import logger
from ml.utils.math_utils import cosine_similarity_matrix

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class ContentBasedRecommender:
    """
    Content-Based Recommendation Engine.
    Uses TF-IDF text vectorization, category/brand attribute similarity,
    and TruncatedSVD embedding generation to find similar products.
    """
    def __init__(self, max_features: int = 500):
        self.max_features = max_features
        self.tfidf = TfidfVectorizer(stop_words='english', max_features=max_features) if SKLEARN_AVAILABLE else None
        self.svd = TruncatedSVD(n_components=min(50, max_features // 2), random_state=42) if SKLEARN_AVAILABLE else None
        
        self.product_ids: List[int] = []
        self.product_titles: List[str] = []
        self.similarity_matrix: Optional[np.ndarray] = None
        self.embeddings: Optional[np.ndarray] = None
        self.fitted = False

    def fit(self, df_products: pd.DataFrame) -> 'ContentBasedRecommender':
        """Learns TF-IDF embeddings and cosine similarity matrix across product catalog."""
        logger.info("Fitting ContentBasedRecommender TF-IDF and embeddings...")
        if len(df_products) == 0:
            return self
            
        self.product_ids = df_products['id'].tolist() if 'id' in df_products.columns else list(range(len(df_products)))
        self.product_titles = df_products['title'].tolist() if 'title' in df_products.columns else [f"Product {i}" for i in self.product_ids]
        
        # Build rich text corpus: Title + Category + Brand + Description + Features
        corpus = []
        for _, row in df_products.iterrows():
            parts = [
                str(row.get('title', '')),
                str(row.get('category', '')),
                str(row.get('brand', '')),
                str(row.get('description', '')),
                str(row.get('specifications', ''))
            ]
            corpus.append(" ".join(parts).lower())
            
        if SKLEARN_AVAILABLE and self.tfidf:
            try:
                tfidf_matrix = self.tfidf.fit_transform(corpus).toarray()
                if tfidf_matrix.shape[1] > 5:
                    n_comp = min(30, tfidf_matrix.shape[1] - 1, len(df_products) - 1)
                    if n_comp >= 2:
                        self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
                        self.embeddings = self.svd.fit_transform(tfidf_matrix)
                    else:
                        self.embeddings = tfidf_matrix
                else:
                    self.embeddings = tfidf_matrix
            except Exception as e:
                logger.debug(f"TF-IDF embedding fallback: {e}")
                self.embeddings = np.eye(len(df_products))
        else:
            # Fallback simple bag of words encoding
            self.embeddings = np.eye(len(df_products))
            
        self.similarity_matrix = cosine_similarity_matrix(self.embeddings)
        self.fitted = True
        logger.info(f"ContentBasedRecommender fitted across {len(self.product_ids)} items.")
        return self

    def get_similar_products(self, product_id: int, top_n: int = 6) -> List[Dict[str, Any]]:
        """Returns Top-N most similar products based on content attributes."""
        if not self.fitted or self.similarity_matrix is None or product_id not in self.product_ids:
            return []
            
        idx = self.product_ids.index(product_id)
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        # Sort descending, exclude self (index 0)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        
        results = []
        for i, score in sim_scores:
            results.append({
                "product_id": self.product_ids[i],
                "title": self.product_titles[i],
                "similarity_score": round(float(score), 4),
                "explanation": {
                    "reason": f"Content similarity match ({round(float(score)*100, 1)}%) based on shared category, brand, and feature specifications.",
                    "confidence": round(float(score), 4),
                    "important_features": [
                        {"feature": "Attribute & Text Similarity", "impact": "High Positive", "value": f"{round(float(score)*100, 1)}% Match", "weight": round(float(score), 4)}
                    ],
                    "recommendation": "Similar Item Match"
                }
            })
        return results
