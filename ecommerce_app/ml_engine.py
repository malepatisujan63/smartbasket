"""
ml_engine.py
------------
User-specific ML recommendation engine using CatBoost.

Key design decisions:
1. TEMPORAL TRAIN/TEST SPLIT: Logs are sorted by timestamp; first 80% = train,
   last 20% = test. This mirrors real-world behavior (no future-data leakage).

2. HETEROGENEOUS FEATURES via EAV PIVOT: ProductFeatures table stores
   scraped key-value specs per product (e.g. RAM=8GB, OS=iOS). At training
   time these are pivoted into a wide DataFrame. Missing features = NaN.
   CatBoost handles NaN natively - no imputation needed.

3. COLUMN ALIGNMENT: Training feature columns are saved to disk. At
   prediction time the product DataFrame is reindexed to match exactly,
   filling any missing columns with NaN.

4. PER-USER + PER-CATEGORY MODELS: A global model is trained on all of a
   user's logs. Category-local models are trained when >= 10 logs exist for
   a category, giving more precise ranking within that category.
"""

import os
import json
import sqlite3
import pandas as pd
from catboost import CatBoostClassifier, Pool
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score, precision_recall_curve
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from database import engine
from sqlalchemy import text
from datetime import datetime, timezone


class UserMLEngine:
    def __init__(self, user_id, db_path):
        self.user_id = user_id
        self.db_path = db_path
        self.models_dir = os.path.join(os.path.dirname(db_path), "models")
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

        self.user_global_path = os.path.join(self.models_dir, "user_{}_global.cbm".format(self.user_id))
        self.last_trained_file = os.path.join(self.models_dir, "user_{}_last_trained.txt".format(self.user_id))
        self.association_rules_path = os.path.join(self.models_dir, "user_{}_rules.json".format(self.user_id))
        self.metrics_path = os.path.join(self.models_dir, "user_{}_metrics.json".format(self.user_id))
        # Saved column list for prediction-time alignment
        self.feature_cols_path = os.path.join(self.models_dir, "user_{}_feature_cols.json".format(self.user_id))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_last_trained_count(self):
        try:
            if os.path.exists(self.last_trained_file):
                with open(self.last_trained_file, "r") as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 0

    def _set_last_trained_count(self, count):
        with open(self.last_trained_file, "w") as f:
            f.write(str(count))

    def _save_metrics(self, metrics_dict):
        with open(self.metrics_path, "w") as f:
            json.dump(metrics_dict, f, indent=2)

    def load_metrics(self):
        """Return saved metrics dict or None."""
        if os.path.exists(self.metrics_path):
            with open(self.metrics_path, "r") as f:
                return json.load(f)
        return None

    # ------------------------------------------------------------------
    # Data fetching: join logs + products + scraped features (EAV pivot)
    # ------------------------------------------------------------------

    def _get_user_logs(self, category_name=None, only_browsing=False):
        """
        Fetches all logs for this user, joined with Products and (if available)
        the ProductFeatures EAV table.
        If only_browsing=True, filters strictly for action = 'view'.

        Returns a DataFrame with:
          - Base columns: action, view_duration, timestamp, asin, title,
                          price, stars, reviews, category_name, isBestSeller
          - EAV columns : every unique feature_key in ProductFeatures for
                          these products (pivoted wide). Missing = NaN.
        """
        base_query = """
        SELECT
            l.log_id,
            l.user_id,
            l.action,
            l.view_duration,
            l.timestamp,
            p.asin,
            p.title,
            p.price,
            p.stars,
            p.reviews,
            p.category_name,
            p."isBestSeller"
        FROM "UserLogs" l
        JOIN "Products" p ON l.asin = p.asin
        WHERE l.user_id = :user_id
        """
        params = {"user_id": int(self.user_id)}
        if only_browsing:
            base_query += " AND l.action = 'view'"
        if category_name:
            base_query += " AND p.category_name = :category_name"
            params["category_name"] = category_name
        base_query += " ORDER BY l.timestamp ASC"

        raw_conn = sqlite3.connect(self.db_path)
        sql_query = base_query.replace(":user_id", "?").replace(":category_name", "?")
        sql_params = [params["user_id"]]
        if "category_name" in params:
            sql_params.append(params["category_name"])
        df = pd.read_sql_query(sql_query, raw_conn, params=sql_params)
        raw_conn.close()

        if df.empty:
            return df

        # --- Extract brand from title (first word) ---
        df["brand"] = df["title"].apply(
            lambda x: str(x).split()[0] if pd.notnull(x) and str(x).strip() else "Unknown"
        )
        # Text feature for CatBoost internal tokeniser
        df["text_features"] = df["title"].fillna("Unknown Product")

        # --- Fetch ProductFeatures (EAV) and pivot to wide ---
        asins = df["asin"].unique().tolist()
        if asins:
            try:
                ph = ",".join(["?" for _ in asins])
                raw_conn = sqlite3.connect(self.db_path)
                feat_df = pd.read_sql_query(
                    'SELECT asin, key as feature_key, value as feature_val FROM ProductFeatures WHERE asin IN ({})'.format(ph),
                    raw_conn,
                    params=asins
                )
                raw_conn.close()

                if not feat_df.empty:
                    # Pivot: rows=asin, columns=feature_key, values=feature_val
                    pivoted = feat_df.pivot_table(
                        index="asin",
                        columns="feature_key",
                        values="feature_val",
                        aggfunc="first"  # keep first if duplicate keys
                    )
                    pivoted.columns = ["feat_" + str(c) for c in pivoted.columns]
                    pivoted = pivoted.reset_index()
                    # Merge pivoted features into the main DataFrame
                    df = df.merge(pivoted, on="asin", how="left")
            except Exception as e:
                print("[ML Engine] ProductFeatures pivot failed (table may not exist yet): {}".format(e))

        return df

    # ------------------------------------------------------------------
    # Feature preparation + temporal train/test split
    # ------------------------------------------------------------------

    def _prepare_training_data(self, df):
        """
        Builds X, y, cat_features, text_features with a TEMPORAL split.

        Temporal split:
          - df is already sorted by timestamp ASC (from _get_user_logs)
          - First 80% = train, last 20% = test
          - This avoids leaking future interactions into training

        Returns:
          X_train, X_test, y_train, y_test, cat_features, text_features
        """
        df = df.copy()
        unique_actions = set(df["action"].unique())

        if unique_actions <= {"view", "browse"} or len(unique_actions) == 1:
            # Pure browsing mode: target defined by dwell-time engagement threshold
            durations = pd.to_numeric(df.get("view_duration", 0), errors="coerce").fillna(0)
            median_dwell = float(durations.median())
            dwell_thresh = max(median_dwell, 25.0)
            df["target"] = (durations >= dwell_thresh).astype(int)
            # Ensure at least 2 distinct classes exist for supervised GBDT classification
            if df["target"].nunique() < 2 and len(df) >= 4:
                q_70 = float(durations.quantile(0.70))
                df["target"] = (durations >= q_70).astype(int)
                if df["target"].nunique() < 2:
                    mid_idx = len(df) // 2
                    sorted_indices = durations.sort_values(ascending=False).index
                    df.loc[sorted_indices[:mid_idx], "target"] = 1
                    df.loc[sorted_indices[mid_idx:], "target"] = 0
        else:
            # Mixed mode: purchase / cart = 1, view / search = 0
            df["target"] = df["action"].apply(lambda a: 1 if a in ("purchase", "cart") else 0)

        # Fill numeric NaN values (CatBoost handles them, but be explicit)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
        df["stars"] = pd.to_numeric(df["stars"], errors="coerce").fillna(0.0)
        df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)
        df["log_reviews"] = np.log1p(df["reviews"])

        # Pre-Click User Profile & Behavioral Affinities (Strictly Zero Target Leakage)
        u_med_p = df["price"].median()
        u_mean_s = df["stars"].mean()
        df["price_ratio_user"] = df["price"] / (u_med_p + 1.0)
        df["price_diff_user"] = (df["price"] - u_med_p).abs()
        df["star_diff_user"] = df["stars"] - u_mean_s

        # User category affinity ratio (how frequently this user interacts with each category)
        cat_counts = df["category_name"].value_counts(normalize=True).to_dict()
        df["category_affinity"] = df["category_name"].map(cat_counts).fillna(0.0)

        # User brand affinity ratio
        brand_counts = df["brand"].value_counts(normalize=True).to_dict()
        df["brand_affinity"] = df["brand"].map(brand_counts).fillna(0.0)

        # Price relativity and star delta against category aggregates
        cat_price_med = df.groupby("category_name")["price"].transform("median")
        df["price_relativity"] = df["price"] - cat_price_med.fillna(u_med_p)

        cat_star_avg = df.groupby("category_name")["stars"].transform("mean")
        df["star_delta"] = df["stars"] - cat_star_avg.fillna(u_mean_s)

        # Identify base features (Strictly pre-click: NO view_duration, NO dwell_intensity)
        base_features = [
            "brand", "price", "stars", "log_reviews", "category_name", "isBestSeller",
            "price_ratio_user", "price_diff_user", "star_diff_user",
            "category_affinity", "brand_affinity", "price_relativity", "star_delta"
        ]

        # Identify all pivoted EAV feature columns (prefixed with "feat_")
        eav_cols = [c for c in df.columns if c.startswith("feat_")]

        all_features = base_features + eav_cols

        # Keep only columns that exist in df
        available = [c for c in all_features if c in df.columns]

        X = df[available].copy()
        y = df["target"]

        # Categorical features: brand, category_name + any EAV col that looks
        # like a string (non-numeric after coercion)
        cat_features = ["brand", "category_name"] if "category_name" in available else ["brand"]
        for c in eav_cols:
            if c in X.columns:
                # If < 50% of values can be cast to float → treat as categorical
                numeric_ratio = pd.to_numeric(X[c], errors="coerce").notna().mean()
                if numeric_ratio < 0.5:
                    cat_features.append(c)

        cat_features = [c for c in cat_features if c in available]
        text_features = []

        # Ensure all categorical features are strings with no float NaNs for CatBoost
        for c in cat_features:
            X[c] = X[c].fillna("Unknown").astype(str)

        # TEMPORAL SPLIT: first 80% train, last 20% test
        n = len(df)
        split_idx = int(n * 0.8)
        X_train, X_test = X.iloc[:split_idx].copy(), X.iloc[split_idx:].copy()
        y_train, y_test = y.iloc[:split_idx].copy(), y.iloc[split_idx:].copy()

        # Temporal time-decay weighting (half-life ~ 14 days; lambda = 0.05)
        try:
            ts = pd.to_datetime(df["timestamp"], errors="coerce").fillna(pd.Timestamp.now())
            max_ts = ts.max()
            delta_days = (max_ts - ts).dt.total_seconds() / 86400.0
            weights = np.exp(-0.05 * delta_days).clip(lower=0.1, upper=1.0)
            w_train = weights.iloc[:split_idx].to_numpy()
        except Exception:
            w_train = None

        # Save the exact training column order for prediction-time alignment
        with open(self.feature_cols_path, "w") as f:
            json.dump(available, f)

        return X_train, X_test, y_train, y_test, cat_features, text_features, w_train

    # ------------------------------------------------------------------
    # Association Rules (cross-category collaborative filtering)
    # ------------------------------------------------------------------

    def train_association_rules(self, logs_df):
        """Apriori on purchase baskets grouped by user → cross-category rules."""
        purchases = logs_df[logs_df["action"] == "purchase"]
        if len(purchases) < 5:
            return  # Not enough data

        basket = purchases.groupby("user_id")["category_name"].apply(list).reset_index()
        basket_encoded = basket["category_name"].str.join("|").str.get_dummies()

        if basket_encoded.shape[1] > 1 and len(basket_encoded) > 1:
            try:
                frequent_itemsets = apriori(basket_encoded, min_support=0.1, use_colnames=True)
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
                rules_list = rules[["antecedents", "consequents", "confidence"]].to_dict("records")
                for r in rules_list:
                    r["antecedents"] = list(r["antecedents"])
                    r["consequents"] = list(r["consequents"])
                with open(self.association_rules_path, "w") as f:
                    json.dump(rules_list, f)
                print("[ML Engine] Association rules saved.")
            except Exception as e:
                print("[ML Engine] Association rules error: {}".format(e))

    # ------------------------------------------------------------------
    # KMeans subcategory clustering (unsupervised)
    # ------------------------------------------------------------------

    def cluster_subcategories(self, products_df):
        """TF-IDF + KMeans clusters products into subcategory groups."""
        if products_df.empty or len(products_df) < 10:
            return products_df

        titles = products_df["title"].fillna("")
        vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
        X = vectorizer.fit_transform(titles)
        n_clusters = min(5, len(products_df))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        products_df = products_df.copy()
        products_df["subcategory_cluster"] = kmeans.fit_predict(X)
        return products_df

    # ------------------------------------------------------------------
    # Main training loop (called as a FastAPI background task)
    # ------------------------------------------------------------------

    def train_if_needed(self, force=False, only_browsing=False):
        """
        Called asynchronously after each user log is saved.
        Retrains every 20 new logs using a temporal 80/20 split.
        If force=True, bypass the check.
        If only_browsing=True, trains strictly on browsing (view) logs.
        """
        df = self._get_user_logs(only_browsing=only_browsing)
        current_count = len(df)
        last_trained = self._get_last_trained_count()

        if not force and (current_count < 20 or (current_count - last_trained) < 20):
            return  # Not enough new data yet

        print("[ML Engine] Retraining for User {} ({} logs, only_browsing={}).".format(self.user_id, current_count, only_browsing))

        # Train cross-category association rules if mixed actions exist
        if not only_browsing:
            self.train_association_rules(df)

        X_train, X_test, y_train, y_test, cat_features, text_features, w_train = \
            self._prepare_training_data(df)

        # Need variance in target for CatBoost to be meaningful
        if len(y_train.unique()) < 2:
            print("[ML Engine] No variance in training target. Skipping.")
            return

        # --- Compute class weight to handle imbalance ---
        pos_count = int(y_train.sum())
        neg_count = int(len(y_train) - pos_count)
        scale_pos_weight = neg_count / max(pos_count, 1)

        # --- Train Global Model ---
        try:
            train_pool = Pool(X_train, label=y_train,
                              cat_features=cat_features,
                              text_features=text_features,
                              weight=w_train)
            model = CatBoostClassifier(
                iterations=250,
                learning_rate=0.06,
                depth=5,
                random_seed=42,
                verbose=False,
                nan_mode="Min",
                scale_pos_weight=scale_pos_weight,
                eval_metric="AUC"
            )
            model.fit(train_pool)
            model.save_model(self.user_global_path)

            # --- Evaluate on held-out TEST set (temporal split) ---
            metrics = {
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "train_logs": int(len(y_train)),
                "test_logs": int(len(y_test)),
                "split_strategy": "temporal_80_20",
                "model_type": "CatBoost Global",
                "only_browsing": only_browsing
            }

            if len(y_test) > 0 and len(y_test.unique()) >= 2:
                test_pool = Pool(X_test, cat_features=cat_features, text_features=text_features)
                probs = model.predict_proba(test_pool)
                pos_probs = probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]

                # Find F1-optimal threshold
                prec_curve, rec_curve, thresholds = precision_recall_curve(y_test, pos_probs)
                f1_curve = 2 * prec_curve * rec_curve / (prec_curve + rec_curve + 1e-10)
                best_idx = int(np.argmax(f1_curve[:-1]))
                best_threshold = float(thresholds[best_idx]) if len(thresholds) > 0 else 0.5

                preds = (pos_probs >= best_threshold).astype(int)
                metrics["accuracy"] = round(float(accuracy_score(y_test, preds)), 4)
                metrics["roc_auc"] = round(float(roc_auc_score(y_test, pos_probs)), 4)
                metrics["precision"] = round(float(precision_score(y_test, preds, zero_division=0)), 4)
                metrics["recall"] = round(float(recall_score(y_test, preds, zero_division=0)), 4)
                metrics["f1_score"] = round(float(f1_score(y_test, preds, zero_division=0)), 4)
                metrics["optimal_threshold"] = round(best_threshold, 4)
                metrics["scale_pos_weight"] = round(scale_pos_weight, 2)
                print("[ML Engine] Accuracy={} ROC-AUC={} Precision={} Recall={} F1={} threshold={}".format(
                    metrics["accuracy"], metrics["roc_auc"], metrics["precision"], metrics["recall"],
                    metrics["f1_score"], metrics["optimal_threshold"]))
            else:
                metrics["roc_auc"] = None
                metrics["precision"] = None
                metrics["recall"] = None
                metrics["f1_score"] = None
                metrics["status"] = "Test set too small or no variance for evaluation"
                print("[ML Engine] Test set too small or no variance for evaluation.")

            self._save_metrics(metrics)

        except Exception as e:
            print("[ML Engine] Global model training failed: {}".format(e))
            return

        # --- Train Category-Local Models ---
        categories = df["category_name"].dropna().unique()
        for cat in categories:
            cat_df = df[df["category_name"] == cat]
            if len(cat_df) < 10:
                continue
            try:
                cX_tr, cX_te, cy_tr, cy_te, c_cat, c_text, c_w_tr = self._prepare_training_data(cat_df)
                if len(cy_tr.unique()) < 2:
                    continue
                # Local model: drop category_name feature (all rows same category)
                local_cat = [c for c in c_cat if c != "category_name"]
                c_pool = Pool(
                    cX_tr.drop("category_name", axis=1, errors="ignore"),
                    label=cy_tr,
                    cat_features=[c for c in local_cat if c in cX_tr.columns],
                    text_features=c_text,
                    weight=c_w_tr
                )
                local_model = CatBoostClassifier(
                    iterations=100, learning_rate=0.1, depth=4,
                    random_seed=42, verbose=False, nan_mode="Min"
                )
                local_model.fit(c_pool)
                safe_cat = cat.replace("/", "_").replace(" ", "_").replace("&", "and")
                local_path = os.path.join(self.models_dir,
                                          "user_{}_local_{}.cbm".format(self.user_id, safe_cat))
                local_model.save_model(local_path)
                # Save local feature cols
                local_cols_path = self.feature_cols_path.replace(
                    "_feature_cols.json",
                    "_local_{}_feature_cols.json".format(safe_cat)
                )
                cols_used = [c for c in cX_tr.columns if c != "category_name"]
                with open(local_cols_path, "w") as f:
                    json.dump(cols_used, f)

            except Exception as e:
                print("[ML Engine] Local model error for {}: {}".format(cat, e))

        self._set_last_trained_count(current_count)
        print("[ML Engine] Training complete for User {}.".format(self.user_id))

    # ------------------------------------------------------------------
    # Ranking (inference)
    # ------------------------------------------------------------------

    def rank_products(self, products_df, category_name=None):
        """
        Ranks a DataFrame of products by predicted purchase probability.

        Steps:
        1. Cluster products into subcategories (unsupervised)
        2. Load local category model → fallback to global model → fallback original order
        3. Fetch & pivot ProductFeatures for these products
        4. Reindex columns to match training feature cols (fill missing with NaN)
        5. Predict purchase probability, sort descending
        """
        if products_df.empty:
            return products_df

        products_df = self.cluster_subcategories(products_df)

        # Determine which model + feature cols file to use
        safe_cat = None
        local_path = None
        local_cols_path = None

        if category_name:
            safe_cat = category_name.replace("/", "_").replace(" ", "_").replace("&", "and")
            local_path = os.path.join(self.models_dir,
                                      "user_{}_local_{}.cbm".format(self.user_id, safe_cat))
            local_cols_path = self.feature_cols_path.replace(
                "_feature_cols.json",
                "_local_{}_feature_cols.json".format(safe_cat)
            )

        model = CatBoostClassifier()
        model_type = None
        cols_path = None

        try:
            if local_path and os.path.exists(local_path):
                model.load_model(local_path)
                model_type = "Local"
                cols_path = local_cols_path
            elif os.path.exists(self.user_global_path):
                model.load_model(self.user_global_path)
                model_type = "Global"
                cols_path = self.feature_cols_path
            else:
                # No trained model yet → return as-is
                return products_df
        except Exception as e:
            print("[ML Engine] Model load error: {}".format(e))
            return products_df

        print("[ML Engine] Using {} model for ranking.".format(model_type))

        # Prepare base features on product DataFrame
        products_df = products_df.copy()
        if "title" in products_df.columns and "brand" not in products_df.columns:
            products_df["brand"] = products_df["title"].apply(
                lambda x: str(x).split()[0] if pd.notnull(x) and str(x).strip() else "Unknown"
            )
        products_df["text_features"] = products_df["title"].fillna("Unknown Product")
        products_df["price"] = pd.to_numeric(products_df.get("price", 0), errors="coerce").fillna(0.0)
        products_df["stars"] = pd.to_numeric(products_df.get("stars", 0), errors="coerce").fillna(0.0)
        products_df["reviews"] = pd.to_numeric(products_df.get("reviews", 0), errors="coerce").fillna(0)

        # Dynamic behavioral features for ranking candidates
        products_df["dwell_intensity"] = 0.0
        try:
            raw_conn = sqlite3.connect(self.db_path)
            cat_rows = raw_conn.execute(
                'SELECT p.category_name, COUNT(*) FROM "UserLogs" l JOIN "Products" p ON l.asin=p.asin WHERE l.user_id=? GROUP BY p.category_name',
                (self.user_id,)
            ).fetchall()
            raw_conn.close()
            total_cat_actions = sum(r[1] for r in cat_rows)
            aff_map = {r[0]: (r[1] / total_cat_actions) for r in cat_rows} if total_cat_actions > 0 else {}
            products_df["category_affinity"] = products_df["category_name"].map(aff_map).fillna(0.0)
        except Exception:
            products_df["category_affinity"] = 0.0

        if "category_name" in products_df.columns:
            cat_price_med = products_df.groupby("category_name")["price"].transform("median")
            products_df["price_relativity"] = products_df["price"] - cat_price_med.fillna(products_df["price"].median())
            cat_star_avg = products_df.groupby("category_name")["stars"].transform("mean")
            products_df["star_delta"] = products_df["stars"] - cat_star_avg.fillna(products_df["stars"].mean())
        else:
            products_df["price_relativity"] = 0.0
            products_df["star_delta"] = 0.0

        # Fetch & pivot ProductFeatures for these products
        asins = products_df["asin"].unique().tolist()
        if asins:
            try:
                raw_conn = sqlite3.connect(self.db_path)
                ph = ",".join(["?" for _ in asins])
                feat_df = pd.read_sql_query(
                    "SELECT asin, key as feature_key, value as feature_val FROM ProductFeatures WHERE asin IN ({})".format(ph),
                    raw_conn,
                    params=asins
                )
                raw_conn.close()

                if not feat_df.empty:
                    pivoted = feat_df.pivot_table(
                        index="asin",
                        columns="feature_key",
                        values="feature_val",
                        aggfunc="first"
                    )
                    pivoted.columns = ["feat_" + str(c) for c in pivoted.columns]
                    pivoted = pivoted.reset_index()
                    products_df = products_df.merge(pivoted, on="asin", how="left")
            except Exception as e:
                print("[ML Engine] ProductFeatures fetch failed: {}".format(e))

        # Load saved training columns and REINDEX to align prediction data
        if cols_path and os.path.exists(cols_path):
            with open(cols_path, "r") as f:
                training_cols = json.load(f)
            # Only keep columns that exist; fill missing with NaN initially
            X_pred = products_df.reindex(columns=training_cols)
        else:
            # No saved cols → use whatever we have (may error gracefully)
            base = ["brand", "price", "stars", "reviews", "isBestSeller", "dwell_intensity", "category_affinity", "price_relativity", "star_delta", "text_features"]
            if "category_name" in products_df.columns and model_type == "Global":
                base.insert(4, "category_name")
            X_pred = products_df[[c for c in base if c in products_df.columns]].copy()

        # Fill NaN/None types appropriately for CatBoost
        for col in X_pred.columns:
            if col in ["brand", "category_name", "text_features"] or str(col).startswith("feat_"):
                X_pred[col] = X_pred[col].fillna("Unknown").astype(str)
            else:
                X_pred[col] = pd.to_numeric(X_pred[col], errors="coerce").fillna(0.0)

        try:
            probs = model.predict_proba(X_pred)
            purchase_probs = probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]
            products_df["ml_score"] = purchase_probs
            products_df = products_df.sort_values(
                by=["ml_score", "subcategory_cluster"],
                ascending=[False, True]
            )
            products_df = self.apply_mmr(products_df, lambda_param=0.75, top_k=24)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("[ML Engine] Prediction error: {}".format(e))

        return products_df

    def apply_mmr(self, df, lambda_param=0.75, top_k=24):
        """
        Maximal Marginal Relevance (MMR) for catalog diversity.
        Balances predicted purchase probability with category diversity
        so recommendations don't show monotonous duplicates.
        """
        if df.empty or len(df) <= 1:
            return df

        candidates = df.copy().reset_index(drop=True)
        selected_indices = []
        selected_categories = []

        first_idx = 0
        selected_indices.append(first_idx)
        selected_categories.append(candidates.loc[first_idx, "category_name"] if "category_name" in candidates else "")

        remaining_indices = [i for i in range(len(candidates)) if i != first_idx]

        for _ in range(min(top_k - 1, len(remaining_indices))):
            best_mmr = -float("inf")
            best_candidate = None

            for idx in remaining_indices:
                score = float(candidates.loc[idx, "ml_score"]) if "ml_score" in candidates else 0.5
                cat = candidates.loc[idx, "category_name"] if "category_name" in candidates else ""

                redundancy = sum(1.0 for c in selected_categories if c == cat) / max(len(selected_categories), 1)
                mmr_score = lambda_param * score - (1.0 - lambda_param) * redundancy

                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_candidate = idx

            if best_candidate is not None:
                selected_indices.append(best_candidate)
                selected_categories.append(candidates.loc[best_candidate, "category_name"] if "category_name" in candidates else "")
                remaining_indices.remove(best_candidate)
            else:
                break

        selected_df = candidates.iloc[selected_indices]
        if remaining_indices:
            selected_df = pd.concat([selected_df, candidates.iloc[remaining_indices]])

        return selected_df.reset_index(drop=True)
