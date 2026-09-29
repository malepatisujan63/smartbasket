import sqlite3

db_path = r'd:\3rd sem created files\AIML PROJECT\ecommerce_app\fast_ecommerce.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_products_isBestSeller ON Products(isBestSeller);",
    "CREATE INDEX IF NOT EXISTS idx_products_boughtInLastMonth ON Products(boughtInLastMonth);",
    "CREATE INDEX IF NOT EXISTS idx_products_stars ON Products(stars);",
    "CREATE INDEX IF NOT EXISTS idx_products_reviews ON Products(reviews);"
]

for idx in indexes:
    print(f"Executing: {idx}")
    cur.execute(idx)

conn.commit()
conn.close()
print("Indexes created successfully.")
