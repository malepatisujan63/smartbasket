# -*- coding: utf-8 -*-
"""
force_retrain_all.py - Force-retrains all CatBoost models + evaluates NCF
Run: venv\\Scripts\\python.exe scratch\\force_retrain_all.py
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')  # Fix Windows cp1252 console issue

sys.path.insert(0, r"d:\3rd sem created files\AIML PROJECT\ecommerce_app")
os.chdir(r"d:\3rd sem created files\AIML PROJECT\ecommerce_app")

import json
import sqlite3
import numpy as np

DB_PATH = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app\fast_ecommerce.db"

# -- 1. Get all users --
db = sqlite3.connect(DB_PATH)
cur = db.cursor()
cur.execute("SELECT user_id, username, ab_group FROM Users ORDER BY user_id")
users = cur.fetchall()
cur.execute("SELECT user_id, COUNT(*) FROM UserLogs GROUP BY user_id")
log_counts = {row[0]: row[1] for row in cur.fetchall()}
db.close()

print("=" * 65)
print("FORCE RETRAINING ALL CatBoost MODELS (with imbalance fixes)")
print("=" * 65)

from ml_engine import UserMLEngine

results = []

for user_id, username, ab_group in users:
    n_logs = log_counts.get(user_id, 0)
    print(f"\n[User {user_id}: {username}] Group={ab_group} | Logs={n_logs}")

    if n_logs < 20:
        print("  -> Skipping: fewer than 20 logs")
        results.append({
            "user_id": user_id, "username": username,
            "status": "SKIPPED (< 20 logs)", "roc_auc": "N/A",
            "precision": "N/A", "recall": "N/A", "f1": "N/A",
            "threshold": "N/A", "scale_pos_weight": "N/A",
            "train_logs": 0, "test_logs": 0
        })
        continue

    try:
        engine = UserMLEngine(user_id=user_id, db_path=DB_PATH)
        engine._set_last_trained_count(0)  # Force retrain
        engine.train_if_needed()

        metrics = engine.load_metrics()
        if metrics:
            roc    = metrics.get('roc_auc', 'N/A')
            prec   = metrics.get('precision', 'N/A')
            rec    = metrics.get('recall', 'N/A')
            f1     = metrics.get('f1_score', 'N/A')
            thresh = metrics.get('optimal_threshold', 'N/A')
            spw    = metrics.get('scale_pos_weight', 'N/A')
            tr_l   = metrics.get('train_logs', '?')
            te_l   = metrics.get('test_logs', '?')

            print(f"  [OK] Trained successfully")
            print(f"       ROC-AUC  : {roc}")
            print(f"       Precision: {prec}")
            print(f"       Recall   : {rec}")
            print(f"       F1 Score : {f1}")
            print(f"       Threshold: {thresh}")
            print(f"       scale_pos_weight: {spw}")
            print(f"       Train logs: {tr_l}  |  Test logs: {te_l}")

            if roc is None:
                note = "Test set has no positive labels (all views, no purchases)"
            elif isinstance(f1, float) and f1 > 0:
                note = "Good - model predicting positives correctly"
            elif roc is not None and isinstance(roc, float) and roc > 0.7:
                note = "AUC good but threshold issue - check positive label count"
            else:
                note = "Needs more interaction data"
            print(f"       Note: {note}")

            results.append({
                "user_id": user_id, "username": username,
                "status": "TRAINED", "roc_auc": roc,
                "precision": prec, "recall": rec, "f1": f1,
                "threshold": thresh, "scale_pos_weight": spw,
                "train_logs": tr_l, "test_logs": te_l
            })
        else:
            print("  [WARN] No metrics file found after training")
            results.append({
                "user_id": user_id, "username": username,
                "status": "NO METRICS", "roc_auc": "N/A",
                "precision": "N/A", "recall": "N/A", "f1": "N/A",
                "threshold": "N/A", "scale_pos_weight": "N/A",
                "train_logs": "?", "test_logs": "?"
            })
    except Exception as e:
        import traceback
        print(f"  [ERROR] {e}")
        traceback.print_exc()
        results.append({
            "user_id": user_id, "username": username,
            "status": f"ERROR: {e}", "roc_auc": "ERR",
            "precision": "ERR", "recall": "ERR", "f1": "ERR",
            "threshold": "ERR", "scale_pos_weight": "ERR",
            "train_logs": "?", "test_logs": "?"
        })

# -- 2. NCF Evaluation --
print("\n" + "=" * 65)
print("NCF MODEL -- EVALUATION (Hit@10 / NDCG@10)")
print("=" * 65)

ncf_result = {}
try:
    from ncf_engine import NCFEngine

    ncf = NCFEngine(r"d:\3rd sem created files\AIML PROJECT\ecommerce_app")
    if not ncf.load():
        print("  [WARN] NCF model not found. Train via admin panel first.")
        ncf_result = {"status": "NOT LOADED"}
    else:
        print(f"  Loaded: {len(ncf.user_map)} users | {len(ncf.item_map)} items")

        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        cur.execute(
            "SELECT user_id, asin, action FROM UserLogs "
            "WHERE action IN ('view','cart','purchase') ORDER BY rowid ASC"
        )
        rows = cur.fetchall()
        db.close()

        positives = [(r[0], r[1]) for r in rows if r[2] in ('cart', 'purchase')]
        print(f"  Total positive interactions (cart+purchase): {len(positives)}")

        if len(positives) < 5:
            print("  [WARN] Too few positive interactions for evaluation.")
            ncf_result = {"status": "INSUFFICIENT DATA", "positives": len(positives)}
        else:
            split_idx = int(len(positives) * 0.8)
            test_positives = positives[split_idx:]
            train_positives = positives[:split_idx]
            print(f"  Train positives: {len(train_positives)} | Test positives: {len(test_positives)}")

            items_all = list(ncf.item_map.keys())
            hits_at_10 = 0
            ndcg_sum = 0.0
            hits_at_5 = 0
            evaluated = 0

            for user_id, pos_asin in test_positives:
                # NCF map keys are strings (JSON coercion) — cast both sides
                uid_str = str(user_id)
                if uid_str not in ncf.user_map or pos_asin not in ncf.item_map:
                    continue
                user_interacted = {r[1] for r in rows if r[0] == user_id}
                negatives = [a for a in items_all if a not in user_interacted and a != pos_asin]
                if len(negatives) < 99:
                    continue
                sample_neg = list(np.random.choice(negatives, 99, replace=False))
                candidates = [pos_asin] + sample_neg

                # rank_items_for_user expects the raw user_id as stored in user_map
                scores = ncf.rank_items_for_user(uid_str, candidates)
                if not scores:
                    continue

                ranked = [s[0] for s in scores]
                if pos_asin in ranked[:10]:
                    hits_at_10 += 1
                    rank = ranked.index(pos_asin) + 1
                    ndcg_sum += 1.0 / np.log2(rank + 1)
                if pos_asin in ranked[:5]:
                    hits_at_5 += 1
                evaluated += 1

            if evaluated > 0:
                hit10 = round(hits_at_10 / evaluated, 4)
                hit5  = round(hits_at_5 / evaluated, 4)
                ndcg  = round(ndcg_sum / evaluated, 4)
                print(f"  Hit@5   : {hit5}  ({hits_at_5}/{evaluated})")
                print(f"  Hit@10  : {hit10}  ({hits_at_10}/{evaluated})")
                print(f"  NDCG@10 : {ndcg}")
                if hit10 < 0.3:
                    note = "Below 0.3 -- needs more data or more training epochs"
                elif hit10 < 0.5:
                    note = "Moderate -- acceptable for sparse data"
                else:
                    note = "Good performance"
                print(f"  Note: {note}")
                ncf_result = {
                    "status": "EVALUATED", "evaluated": evaluated,
                    "hit_at_5": hit5, "hit_at_10": hit10, "ndcg_at_10": ndcg,
                    "note": note
                }
            else:
                print("  [WARN] No test cases evaluable (users/items not in NCF map)")
                ncf_result = {"status": "NO EVALUABLE CASES"}

except Exception as e:
    import traceback
    print(f"  [ERROR] NCF eval failed: {e}")
    traceback.print_exc()
    ncf_result = {"status": f"ERROR: {e}"}

# -- 3. Model file inventory --
print("\n" + "=" * 65)
print("MODEL FILE INVENTORY")
print("=" * 65)
models_dir = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app\models"
print(f"\n  {'File':<55} {'Size':>10}")
print("  " + "-" * 67)
for f in sorted(os.listdir(models_dir)):
    path = os.path.join(models_dir, f)
    size_kb = os.path.getsize(path) / 1024
    print(f"  {f:<55} {size_kb:>8.1f} KB")

# -- 4. Final summary table --
print("\n" + "=" * 65)
print("FINAL RESULTS SUMMARY")
print("=" * 65)
print(f"\n  {'User':<20} {'Status':<12} {'AUC':>7} {'Prec':>7} {'Rec':>7} {'F1':>7} {'Thresh':>8}")
print("  " + "-" * 72)
for r in results:
    print(f"  {r['username']:<20} {r['status']:<12} "
          f"{str(r['roc_auc']):>7} {str(r['precision']):>7} "
          f"{str(r['recall']):>7} {str(r['f1']):>7} {str(r['threshold']):>8}")

print(f"\n  NCF: {ncf_result}")
print("\nDone.")
