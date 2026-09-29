import sqlite3
import os

def optimize_db():
    base_dir = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
    db_path = os.path.join(base_dir, "fast_ecommerce.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating indexes... this may take a few seconds.")
    # Index for the fallback feed (isBestSeller + reviews)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_bestseller_reviews ON Products(isBestSeller, reviews DESC)")
    
    # Index for category carousels (category_name + reviews)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_cat_reviews ON Products(category_name, reviews DESC)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    optimize_db()
