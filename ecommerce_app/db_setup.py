import os
import csv
import glob
from database import SessionLocal, init_db, Product

def setup_database():
    base_dir = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
    categories_dir = r"d:\3rd sem created files\AIML PROJECT\categories"
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    # Initialize the database schema (Creates tables if they don't exist)
    init_db()
    
    db = SessionLocal()
    
    # Check if we already imported (if table is not empty)
    count = db.query(Product).count()
    if count > 0:
        print(f"Products table already has {count} rows. Skipping import.")
        db.close()
        return

    # Import CSV files
    print("Importing CSV files into database. This might take a minute...")
    csv_files = glob.glob(os.path.join(categories_dir, "*.csv"))
    
    total_imported = 0
    for file_path in csv_files:
        cat_name = os.path.basename(file_path).replace('.csv', '')
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products_to_add = []
            for row in reader:
                products_to_add.append(Product(
                    asin=row['asin'],
                    title=row['title'],
                    imgUrl=row['imgUrl'],
                    productURL=row['productURL'],
                    stars=float(row['stars']) if row['stars'] else 0.0,
                    reviews=int(row['reviews']) if row['reviews'] else 0,
                    price=float(row['price']) if row['price'] else 0.0,
                    listPrice=float(row['listPrice']) if row['listPrice'] else 0.0,
                    category_id=row['category_id'],
                    isBestSeller=1 if row['isBestSeller'] == 'True' else 0,
                    boughtInLastMonth=int(row['boughtInLastMonth']) if row['boughtInLastMonth'] else 0,
                    alt=row['alt'],
                    category_name=cat_name
                ))
            
            # Bulk save for performance
            try:
                # Merge will act like INSERT OR IGNORE / ON CONFLICT DO UPDATE
                for p in products_to_add:
                    db.merge(p)
                db.commit()
                total_imported += len(products_to_add)
                print(f"Imported {len(products_to_add)} records from {cat_name}")
            except Exception as e:
                db.rollback()
                print(f"Error importing {cat_name}: {e}")

    db.close()
    print(f"Database setup complete. Total products imported: {total_imported}")

if __name__ == "__main__":
    setup_database()
