"""
populate_features.py
--------------------
Extracts and populates structured EAV product features into ProductFeatures table.
Provides the heterogeneous features required by ml_engine.py EAV pivot.
"""
import sqlite3
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fast_ecommerce.db")

KEYWORD_SPECS = [
    ("connectivity", ["Wireless", "Bluetooth", "USB-C", "Wi-Fi", "Wired"]),
    ("material", ["Leather", "Cotton", "Stainless Steel", "Wood", "Ceramic", "Aluminum", "Plastic"]),
    ("style", ["Vintage", "Modern", "Casual", "Formal", "Sport", "Classic"]),
    ("feature", ["Waterproof", "Rechargeable", "Portable", "Organic", "Ergonomic", "Gaming", "Noise Cancelling"]),
    ("color", ["Black", "White", "Blue", "Red", "Silver", "Gold", "Pink", "Green"])
]

def derive_features_for_product(asin, title, price, stars, reviews, is_bestseller, category_name):
    features = []
    title_str = str(title) if title else ""
    
    # 1. Price tier
    try:
        p = float(price) if price else 0.0
        if p > 100:
            features.append((asin, "price_tier", "Premium ($100+)"))
        elif p >= 30:
            features.append((asin, "price_tier", "Mid-Range ($30-$100)"))
        elif p > 0:
            features.append((asin, "price_tier", "Budget (<$30)"))
    except:
        pass

    # 2. Rating tier
    try:
        s = float(stars) if stars else 0.0
        if s >= 4.5:
            features.append((asin, "rating_tier", "Top Rated (4.5+)"))
        elif s >= 4.0:
            features.append((asin, "rating_tier", "Highly Rated (4.0-4.4)"))
        elif s > 0:
            features.append((asin, "rating_tier", "Average (below 4.0)"))
    except:
        pass

    # 3. Popularity
    try:
        r = int(reviews) if reviews else 0
        if r >= 1000:
            features.append((asin, "popularity", "Very Popular (1000+ reviews)"))
        elif r >= 100:
            features.append((asin, "popularity", "Popular (100+ reviews)"))
        else:
            features.append((asin, "popularity", "Niche (<100 reviews)"))
    except:
        pass

    # 4. Bestseller status
    if is_bestseller:
        features.append((asin, "badge", "Best Seller"))

    # 5. Keyword specs derived from title
    for spec_name, keywords in KEYWORD_SPECS:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', title_str, re.IGNORECASE):
                features.append((asin, spec_name, kw))
                break

    return features

def main():
    print("Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists with key and value columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProductFeatures (
            feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            UNIQUE(asin, key)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_asin ON ProductFeatures(asin)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_key ON ProductFeatures(key)")

    # Fetch all asins that users have interacted with in UserLogs
    cursor.execute("SELECT DISTINCT asin FROM UserLogs")
    logged_asins = [r[0] for r in cursor.fetchall() if r[0]]
    print(f"Found {len(logged_asins)} distinct products in UserLogs.")

    # Also fetch top 5000 products from UserLogs
    cursor.execute("""
        SELECT asin, title, price, stars, reviews, isBestSeller, category_name
        FROM Products
        WHERE asin IN (SELECT DISTINCT asin FROM UserLogs)
        LIMIT 5000
    """)
    rows = cursor.fetchall()

    # Grab bestsellers using existing composite index (instant <5ms)
    cursor.execute("""
        SELECT asin, title, price, stars, reviews, isBestSeller, category_name
        FROM Products
        WHERE isBestSeller = 1
        ORDER BY reviews DESC
        LIMIT 3000
    """)
    rows += cursor.fetchall()

    seen_asins = set()
    all_features = []
    for r in rows:
        asin, title, price, stars, reviews, is_bs, cat = r
        if asin in seen_asins:
            continue
        seen_asins.add(asin)
        feats = derive_features_for_product(asin, title, price, stars, reviews, is_bs, cat)
        all_features.extend(feats)

    print(f"Inserting {len(all_features)} features for {len(seen_asins)} products...")
    cursor.executemany("""
        INSERT OR REPLACE INTO ProductFeatures (asin, key, value)
        VALUES (?, ?, ?)
    """, all_features)

    conn.commit()
    cnt = cursor.execute("SELECT COUNT(*) FROM ProductFeatures").fetchone()[0]
    print(f"Done! Total ProductFeatures rows: {cnt}")
    conn.close()

if __name__ == "__main__":
    main()
