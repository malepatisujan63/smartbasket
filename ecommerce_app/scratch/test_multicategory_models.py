import os
import sys

# Ensure current application directory is in sys.path
APP_DIR = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import json
import sqlite3
import random
import time
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, precision_recall_curve

from ml_engine import UserMLEngine
from ncf_engine import NCFEngine

DB_PATH = os.path.join(APP_DIR, "fast_ecommerce.db")

def run_multicategory_experiment():
    print("=" * 70)
    print("STEP 1: Selecting Diverse Categories & Generating Realistic Logs")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create or get test user 'multicat_eval_user'
    cursor.execute("SELECT user_id FROM Users WHERE username = 'multicat_eval_user'")
    row = cursor.fetchone()
    need_insert = True
    if row:
        test_user_id = row[0]
        cursor.execute("SELECT COUNT(*) FROM UserLogs WHERE user_id = ?", (test_user_id,))
        cnt = cursor.fetchone()[0]
        if cnt >= 100:
            print(f"User 'multicat_eval_user' (ID: {test_user_id}) already has {cnt} logs. Reusing existing logs.")
            need_insert = False
        else:
            cursor.execute("DELETE FROM UserLogs WHERE user_id = ?", (test_user_id,))
            conn.commit()
            print(f"Using existing user 'multicat_eval_user' (ID: {test_user_id}) - previous logs cleared.")
    else:
        cursor.execute("INSERT INTO Users (username, password, ab_group, is_admin) VALUES ('multicat_eval_user', 'evalpass123', 'A', 0)")
        conn.commit()
        test_user_id = cursor.lastrowid
        print(f"Created new test user 'multicat_eval_user' (ID: {test_user_id}).")

    # 2. Select 5 diverse, popular categories
    target_categories = [
        "Toys & Games",
        "Men's Shoes",
        "Girls' Clothing",
        "Women's Handbags",
        "Men's Clothing"
    ]
    
    category_products = {}
    for cat in target_categories:
        cursor.execute("""
            SELECT asin, title, price, stars, reviews, category_name 
            FROM Products 
            WHERE category_name = ? AND price > 0 AND stars > 0 
            LIMIT 50
        """, (cat,))
        prods = cursor.fetchall()
        category_products[cat] = prods

    if need_insert:
        conversion_rates = {
            "Toys & Games": 0.35,
            "Men's Shoes": 0.32,
            "Girls' Clothing": 0.18,
            "Women's Handbags": 0.08,
            "Men's Clothing": 0.20
        }
        logs_to_insert = []
        base_time = datetime.now() - timedelta(days=14)
        current_time = base_time
        
        for cat, prods in category_products.items():
            target_conv = conversion_rates[cat]
            for i in range(30):
                prod = random.choice(prods)
                asin = prod[0]
                price = prod[2]
                stars = prod[3]
                
                star_factor = (stars / 5.0)
                rand_val = random.random()
                
                if rand_val < (target_conv * star_factor):
                    action = "purchase"
                    view_duration = random.randint(35, 160)
                elif rand_val < (target_conv * 1.5):
                    action = "cart"
                    view_duration = random.randint(20, 80)
                else:
                    action = "view"
                    view_duration = random.randint(5, 50)
                    
                current_time += timedelta(minutes=random.randint(15, 180))
                logs_to_insert.append((
                    test_user_id,
                    asin,
                    action,
                    current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    None,
                    view_duration
                ))

        cursor.executemany("""
            INSERT INTO UserLogs (user_id, asin, action, timestamp, search_query, view_duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, logs_to_insert)
        conn.commit()
        print(f"\n[OK] Inserted {len(logs_to_insert)} multi-category logs for User {test_user_id}.")
    conn.close()

    # =========================================================================
    # STEP 2: Train Global CatBoost & Local CatBoost Models
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Training Global CatBoost & Category-Local CatBoost Models")
    print("=" * 70)
    
    ml_engine = UserMLEngine(test_user_id, DB_PATH)
    models_dir = ml_engine.models_dir
    global_model_file = ml_engine.user_global_path
    
    if not os.path.exists(global_model_file):
        ml_engine.train_if_needed(force=True)
    else:
        print("Models already trained on disk. Skipping training.")
        
    has_global = os.path.exists(global_model_file)
    print(f"Global CatBoost Model exists: {has_global} ({os.path.basename(global_model_file)})")
    
    local_model_files = [f for f in os.listdir(models_dir) if f.startswith(f"user_{test_user_id}_local_") and f.endswith(".cbm")]
    print(f"Found {len(local_model_files)} Category-Local CatBoost Models:")
    for lmf in local_model_files:
        print(f"  - {lmf}")

    # =========================================================================
    # STEP 3: Train Neural Collaborative Filtering (NCF / NeuMF)
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 3: Evaluating Neural Collaborative Filtering (NCF NeuMF)")
    print("=" * 70)
    
    ncf = NCFEngine(base_dir=models_dir)
    if not os.path.exists(os.path.join(models_dir, "ncf_model.pth")):
        ncf_trained = ncf.train(epochs=3, batch_size=256, neg_ratio=4)
    else:
        ncf_trained = ncf.load()
        print("Loaded pre-trained NCF NeuMF model from disk.")
    print(f"NCF NeuMF ready: {ncf_trained}")

    # =========================================================================
    # STEP 4: Rigorous Accuracy & Performance Testing
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 4: Rigorous Accuracy Testing of All Three Models")
    print("=" * 70)

    # 4.1 Global CatBoost Evaluation
    df = ml_engine._get_user_logs()
    X_tr, X_te, y_tr, y_te, cat_features, text_features, w_tr = ml_engine._prepare_training_data(df)
    
    from catboost import CatBoostClassifier, Pool
    global_cb = CatBoostClassifier()
    global_cb.load_model(global_model_file)
    
    test_pool = Pool(X_te, cat_features=cat_features, text_features=text_features)
    test_probs = global_cb.predict_proba(test_pool)[:, 1]
    
    # Evaluate at optimal threshold
    prec_c, rec_c, thrs = precision_recall_curve(y_te, test_probs)
    f1_c = 2 * prec_c * rec_c / (prec_c + rec_c + 1e-10)
    opt_thr_idx = int(np.argmax(f1_c[:-1])) if len(thrs) > 0 else 0
    opt_thr = float(thrs[opt_thr_idx]) if len(thrs) > 0 else 0.5
    
    y_pred_opt = (test_probs >= opt_thr).astype(int)
    y_pred_def = (test_probs >= 0.50).astype(int)
    
    global_acc = accuracy_score(y_te, y_pred_opt)
    global_prec = precision_score(y_te, y_pred_opt, zero_division=0)
    global_rec = recall_score(y_te, y_pred_opt, zero_division=0)
    global_f1 = f1_score(y_te, y_pred_opt, zero_division=0)
    global_auc = roc_auc_score(y_te, test_probs) if len(np.unique(y_te)) > 1 else 0.5
    
    print("\n--- GLOBAL CATBOOST ACCURACY METRICS (Across All Categories) ---")
    print(f"Test Samples (Temporal 20%): {len(y_te)} (Positive buys/carts: {int(y_te.sum())}, Negative views: {int(len(y_te) - y_te.sum())})")
    print(f"Optimal Decision Threshold (tau*): {opt_thr:.4f}")
    print(f"Accuracy at tau*: {global_acc * 100:.2f}%")
    print(f"Accuracy at default 0.50: {accuracy_score(y_te, y_pred_def) * 100:.2f}%")
    print(f"Precision: {global_prec * 100:.2f}%")
    print(f"Recall: {global_rec * 100:.2f}%")
    print(f"F1-Score: {global_f1:.4f}")
    print(f"ROC-AUC: {global_auc:.4f}")

    # 4.2 Category-Local CatBoost vs Global CatBoost Comparison
    print("\n--- CATEGORY-LOCAL CATBOOST VS GLOBAL CATBOOST COMPARISON ---")
    local_results = []
    
    for cat in target_categories:
        cat_df = df[df["category_name"] == cat]
        if len(cat_df) < 10:
            continue
            
        safe_cat = cat.replace("/", "_").replace(" ", "_").replace("&", "and")
        local_path = os.path.join(models_dir, f"user_{test_user_id}_local_{safe_cat}.cbm")
        
        if not os.path.exists(local_path):
            print(f"No local model file for {cat}")
            continue
            
        cX_tr, cX_te, cy_tr, cy_te, c_cat, c_text, _ = ml_engine._prepare_training_data(cat_df)
        if len(cy_te) == 0:
            continue
            
        local_model = CatBoostClassifier()
        local_model.load_model(local_path)
        
        # Local evaluation
        local_cols_path = ml_engine.feature_cols_path.replace(
            "_feature_cols.json",
            "_local_{}_feature_cols.json".format(safe_cat)
        )
        if os.path.exists(local_cols_path):
            with open(local_cols_path, "r") as f:
                l_cols = json.load(f)
        else:
            l_cols = [c for c in cX_tr.columns if c != "category_name"]
            
        l_df = cX_te.reindex(columns=l_cols)
        l_cat = [c for c in c_cat if c != "category_name" and c in l_df.columns]
        for c in l_cat:
            l_df[c] = l_df[c].fillna("Unknown").astype(str)
            
        l_pool = Pool(
            l_df,
            cat_features=l_cat,
            text_features=c_text
        )
        l_probs = local_model.predict_proba(l_pool)[:, 1]
        l_preds = (l_probs >= 0.5).astype(int)
        
        l_acc = accuracy_score(cy_te, l_preds)
        l_auc = roc_auc_score(cy_te, l_probs) if len(np.unique(cy_te)) > 1 else 0.5
        
        # Global evaluation on the exact same category test slice with aligned features
        g_df = cX_te.reindex(columns=X_tr.columns)
        for c in cat_features:
            g_df[c] = g_df[c].fillna("Unknown").astype(str)
        for c in X_tr.columns:
            if c not in cat_features and c not in text_features:
                g_df[c] = pd.to_numeric(g_df[c], errors="coerce").fillna(0.0).astype(float)
                
        g_pool = Pool(g_df, cat_features=cat_features, text_features=text_features)
        g_probs = global_cb.predict_proba(g_pool)[:, 1]
        g_preds = (g_probs >= 0.5).astype(int)
        
        g_acc = accuracy_score(cy_te, g_preds)
        g_auc = roc_auc_score(cy_te, g_probs) if len(np.unique(cy_te)) > 1 else 0.5
        
        local_results.append({
            "category": cat,
            "samples": len(cy_te),
            "positives": int(cy_te.sum()),
            "local_accuracy": l_acc,
            "local_auc": l_auc,
            "global_accuracy": g_acc,
            "global_auc": g_auc,
        })
        print(f"Category: [{cat}] (Test Slice N={len(cy_te)}, Positives={int(cy_te.sum())})")
        print(f"   Local CatBoost  -> Accuracy: {l_acc * 100:.1f}%, AUC: {l_auc:.4f}")
        print(f"   Global CatBoost -> Accuracy: {g_acc * 100:.1f}%, AUC: {g_auc:.4f}")

    # 4.3 NCF (Neural Collaborative Filtering) Evaluation
    print("\n--- NCF NEUMF COLLABORATIVE FILTERING EVALUATION ---")
    user_prods = df[df["action"].isin(["cart", "purchase"])]["asin"].unique().tolist()
    print(f"User {test_user_id} converted ASINs count: {len(user_prods)}")
    
    candidate_asins = [prod[0] for prods in category_products.values() for prod in prods]
    ranked_tuples = ncf.rank_items_for_user(test_user_id, candidate_asins)
    ncf_recs = [asin for asin, score in ranked_tuples[:20]] if ranked_tuples else []
    print(f"NCF Top-10 Recommended ASINs: {ncf_recs[:10]}")
    
    hit_10 = any(asin in user_prods for asin in ncf_recs[:10])
    hit_20 = any(asin in user_prods for asin in ncf_recs[:20])
    
    mrr = 0.0
    for rank, asin in enumerate(ncf_recs, 1):
        if asin in user_prods:
            mrr = 1.0 / rank
            break
            
    print(f"NCF Hit@10: {'YES (Hit!)' if hit_10 else 'NO'}")
    print(f"NCF Hit@20: {'YES (Hit!)' if hit_20 else 'NO'}")
    print(f"NCF Mean Reciprocal Rank (MRR): {mrr:.4f}")

    # Save test results summary to json
    results_summary = {
        "test_user_id": test_user_id,
        "total_test_logs": len(df),
        "global_catboost": {
            "accuracy": global_acc,
            "precision": global_prec,
            "recall": global_rec,
            "f1": global_f1,
            "roc_auc": global_auc,
            "optimal_threshold": opt_thr
        },
        "category_local_comparisons": local_results,
        "ncf_metrics": {
            "hit_at_10": hit_10,
            "hit_at_20": hit_20,
            "mrr": mrr,
            "recommended_count": len(ncf_recs)
        }
    }
    
    out_path = os.path.join(models_dir, "multicategory_model_accuracy_benchmark.json")
    with open(out_path, "w") as f:
        json.dump(results_summary, f, indent=2)
    print(f"\n[SUCCESS] Benchmark results saved to: {out_path}")

if __name__ == "__main__":
    run_multicategory_experiment()
