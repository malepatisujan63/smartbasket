"""
apply_sqlite_pragmas.py
Run once to permanently bake performance settings into fast_ecommerce.db.
"""
import sqlite3
import os
import sys

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fast_ecommerce.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

settings = [
    ("PRAGMA journal_mode=WAL",         "journal_mode"),
    ("PRAGMA wal_autocheckpoint=1000",  "wal_autocheckpoint"),
    ("PRAGMA synchronous=NORMAL",       "synchronous"),
    ("PRAGMA cache_size=-131072",       "cache_size"),      # 128 MB
    ("PRAGMA temp_store=MEMORY",        "temp_store"),
    ("PRAGMA mmap_size=5368709120",     "mmap_size"),       # 5 GB
    ("PRAGMA busy_timeout=5000",        "busy_timeout"),
    ("PRAGMA optimize",                 None),
]

print("Applying PRAGMAs to:", db_path)
for sql, name in settings:
    c.execute(sql)
    if name:
        c.execute(f"PRAGMA {name}")
        val = c.fetchone()
        print(f"  OK  {name}: {val}")

# Create composite indexes for the most common query patterns
indexes = [
    ("idx_products_cat_reviews",
     "CREATE INDEX IF NOT EXISTS idx_products_cat_reviews ON Products(category_name, reviews DESC)"),
    ("idx_products_bestseller_reviews",
     "CREATE INDEX IF NOT EXISTS idx_products_bestseller_reviews ON Products(isBestSeller DESC, reviews DESC)"),
    ("idx_products_stars",
     "CREATE INDEX IF NOT EXISTS idx_products_stars ON Products(stars DESC)"),
    ("idx_products_boughtlastmonth",
     "CREATE INDEX IF NOT EXISTS idx_products_boughtlastmonth ON Products(boughtInLastMonth DESC)"),
    ("idx_userlogs_user_action",
     "CREATE INDEX IF NOT EXISTS idx_userlogs_user_action ON UserLogs(user_id, action)"),
    ("idx_userlogs_user_ts",
     "CREATE INDEX IF NOT EXISTS idx_userlogs_user_ts ON UserLogs(user_id, timestamp DESC)"),
    ("idx_userlogs_asin",
     "CREATE INDEX IF NOT EXISTS idx_userlogs_asin ON UserLogs(asin)"),
]

print("\nCreating composite indexes...")
for name, sql in indexes:
    c.execute(sql)
    print(f"  OK  {name}")

conn.commit()
conn.close()
print("\nDONE! Database is now at maximum performance.")
