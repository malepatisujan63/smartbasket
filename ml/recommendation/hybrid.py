import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ml.utils.logger import logger
from ml.recommendation.content_based import ContentBasedRecommender
from ml.recommendation.collaborative import CollaborativeFilteringRecommender

class HybridRecommendationEngine:
    """
    Enterprise Hybrid Recommendation Engine.
    Ensembles Content-Based TF-IDF/SVD similarity, Collaborative Filtering (SVD/NCF),
    and product popularity velocity to deliver high-converting personalized recommendations.
    """
    def __init__(
        self,
        content_weight: float = 0.40,
        collab_weight: float = 0.45,
        popularity_weight: float = 0.15,
        cf_method: str = "svd"
    ):
        self.content_weight = content_weight
        self.collab_weight = collab_weight
        self.popularity_weight = popularity_weight
        
        self.content_recommender = ContentBasedRecommender()
        self.collab_recommender = CollaborativeFilteringRecommender(method=cf_method)
        self.popularity_map: Dict[int, float] = {}
        self.product_catalog: Dict[int, Dict[str, Any]] = {}
        self.fitted = False

    def fit(self, df_products: pd.DataFrame, df_interactions: pd.DataFrame) -> 'HybridRecommendationEngine':
        """Fits both Content-Based and Collaborative engines and maps popularity scores."""
        logger.info("Fitting HybridRecommendationEngine ensemble...")
        
        # 1. Fit Content-Based
        self.content_recommender.fit(df_products)
        
        # 2. Fit Collaborative
        self.collab_recommender.fit(df_interactions)
        
        # 3. Build Catalog & Popularity Map
        for _, row in df_products.iterrows():
            pid = int(row['id']) if 'id' in row else 0
            rating = float(row.get('rating', 4.0))
            reviews = int(row.get('reviews_count', 10))
            pop_score = min(1.0, (rating / 5.0) * np.log1p(reviews) / 10.0)
            
            self.popularity_map[pid] = pop_score
            self.product_catalog[pid] = {
                "id": pid,
                "title": str(row.get('title', f"Product {pid}")),
                "price": float(row.get('price', 49.99)),
                "rating": rating,
                "reviews_count": reviews,
                "category": str(row.get('category', 'General')),
                "brand": str(row.get('brand', 'Enterprise Brand')),
                "image": row['images'][0] if isinstance(row.get('images'), list) and row['images'] else ""
            }
            
        self.fitted = True
        logger.info("HybridRecommendationEngine fitted successfully.")
        return self

    def get_personalized_recommendations(
        self,
        user_id: Optional[int] = None,
        recent_product_id: Optional[int] = None,
        top_n: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Generates Top-N hybrid personalized recommendations with rich feature attribution explanations.
        """
        if not self.fitted:
            return []
            
        item_scores: Dict[int, Dict[str, float]] = {}
        
        # 1. Collaborative Scores
        if user_id is not None:
            cf_recs = self.collab_recommender.recommend_for_user(user_id, top_n=top_n * 2)
            for rec in cf_recs:
                pid = rec["product_id"]
                item_scores[pid] = {"collab": rec["cf_score"] / 5.0, "content": 0.0, "popularity": self.popularity_map.get(pid, 0.5)}
                
        # 2. Content-Based Scores (if recent product viewed/purchased)
        if recent_product_id is not None and recent_product_id in self.product_catalog:
            cb_recs = self.content_recommender.get_similar_products(recent_product_id, top_n=top_n * 2)
            for rec in cb_recs:
                pid = rec["product_id"]
                if pid not in item_scores:
                    item_scores[pid] = {"collab": 0.0, "content": rec["similarity_score"], "popularity": self.popularity_map.get(pid, 0.5)}
                else:
                    item_scores[pid]["content"] = rec["similarity_score"]
                    
        # 3. If no personalized signals, fallback to Top Popularity & Trending
        if not item_scores:
            top_pop = sorted(self.popularity_map.items(), key=lambda x: x[1], reverse=True)[:top_n * 2]
            for pid, pop in top_pop:
                item_scores[pid] = {"collab": 0.5, "content": 0.5, "popularity": pop}

        # 4. Calculate Weighted Hybrid Score
        ranked_items = []
        for pid, scores in item_scores.items():
            if pid == recent_product_id:
                continue
            hybrid_score = (
                self.content_weight * scores["content"] +
                self.collab_weight * scores["collab"] +
                self.popularity_weight * scores["popularity"]
            )
            ranked_items.append((pid, hybrid_score, scores))
            
        ranked_items = sorted(ranked_items, key=lambda x: x[1], reverse=True)[:top_n]
        
        # 5. Format Output with Business Explanation & Feature Attribution
        results = []
        for pid, score, scores in ranked_items:
            prod = self.product_catalog.get(pid, {"id": pid, "title": f"Product {pid}", "price": 49.99, "rating": 4.5})
            
            # Determine dominant signal for narrative
            if scores["collab"] > scores["content"] and scores["collab"] > 0.6:
                reason = f"Personalized Collaborative match ({round(score*100, 1)}% confidence) based on shoppers with similar purchase history."
                rec_label = "Recommended For You"
            elif scores["content"] > 0.5:
                reason = f"Content Similarity match ({round(score*100, 1)}% confidence) aligned with your recently viewed category and features."
                rec_label = "Similar To Recently Viewed"
            else:
                reason = f"High-Velocity Bestseller ({round(score*100, 1)}% confidence) with top customer ratings."
                rec_label = "Trending Choice"
                
            results.append({
                "product": prod,
                "hybrid_score": round(float(score), 4),
                "explanation": {
                    "reason": reason,
                    "confidence": round(float(score), 4),
                    "important_features": [
                        {"feature": "Collaborative Shopper Signal", "impact": "High Positive", "value": f"{round(scores['collab']*100, 1)}%", "weight": round(float(scores['collab'] * self.collab_weight), 4)},
                        {"feature": "Content & Attribute Match", "impact": "High Positive", "value": f"{round(scores['content']*100, 1)}%", "weight": round(float(scores['content'] * self.content_weight), 4)},
                        {"feature": "Bestseller Popularity Velocity", "impact": "Moderate Positive", "value": f"{round(scores['popularity']*100, 1)}%", "weight": round(float(scores['popularity'] * self.popularity_weight), 4)}
                    ],
                    "recommendation": rec_label
                }
            })
        return results
