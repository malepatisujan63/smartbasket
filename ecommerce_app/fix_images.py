import sqlite3
import csv
import sys
import os

def fix_images():
    base_dir = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
    db_path = os.path.join(base_dir, "fast_ecommerce.db")
    csv_path = r"d:\3rd sem created files\AIML PROJECT\amazon_products.csv"
    
    print("Connecting to DB...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable WAL mode for fast updates
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    
    print("Reading CSV and building update list...")
    updates = []
    
    # Read the original CSV which has the real .jpg urls
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # We want to set imgUrl to the original .jpg link
            # We keep the alt column as whatever it is (the google search link)
            original_img_url = row['imgUrl']
            asin = row['asin']
            updates.append((original_img_url, asin))
            
    print(f"Total records to update: {len(updates)}")
    
    print("Executing updates in batches...")
    batch_size = 50000
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i+batch_size]
        cursor.executemany("UPDATE Products SET imgUrl = ? WHERE asin = ?", batch)
        conn.commit()
        print(f"Updated {min(i+batch_size, len(updates))} / {len(updates)}")
        
    conn.close()
    print("Finished updating images!")

if __name__ == "__main__":
    fix_images()
