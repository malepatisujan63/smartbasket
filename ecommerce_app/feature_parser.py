"""
feature_parser.py
-----------------
Reads enriched product JSON files (produced by data_enrichment.py) and
inserts their scraped features into the ProductFeatures EAV table.

Run once after data_enrichment.py has populated the enriched_data folder:
    python feature_parser.py
"""
import os
import json
import sqlite3

BASE_DIR = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
ENRICHED_DIR = r"d:\3rd sem created files\AIML PROJECT\enriched_data"
DB_PATH = os.path.join(BASE_DIR, "fast_ecommerce.db")


def parse_and_store():
    if not os.path.exists(ENRICHED_DIR):
        print("enriched_data directory not found. Run data_enrichment.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the ProductFeatures table if it doesn't exist yet
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProductFeatures (
            feature_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            asin        TEXT NOT NULL,
            feature_key TEXT NOT NULL,
            feature_val TEXT,
            UNIQUE (asin, feature_key)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_asin ON ProductFeatures(asin)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_key  ON ProductFeatures(feature_key)")

    json_files = [f for f in os.listdir(ENRICHED_DIR) if f.endswith(".json")]
    total_inserted = 0

    for jf in json_files:
        fpath = os.path.join(ENRICHED_DIR, jf)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as e:
            print("Error reading {}: {}".format(jf, e))
            continue

        rows = []
        for product in products:
            asin = product.get("asin") or product.get("_id")
            if not asin:
                continue
            features = product.get("specific_features", {})
            if isinstance(features, dict):
                for key, val in features.items():
                    rows.append((asin, str(key).strip(), str(val).strip()))

        if rows:
            cursor.executemany(
                """INSERT OR REPLACE INTO ProductFeatures (asin, feature_key, feature_val)
                   VALUES (?, ?, ?)""",
                rows
            )
            total_inserted += len(rows)

    conn.commit()
    conn.close()
    print("Inserted/updated {} feature rows into ProductFeatures.".format(total_inserted))


if __name__ == "__main__":
    parse_and_store()
