import csv
import os
import urllib.parse
import re

def sanitize_filename(name):
    # Remove invalid characters for Windows filenames
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def main():
    base_dir = r"d:\3rd sem created files\AIML PROJECT"
    categories_file = os.path.join(base_dir, "amazon_categories.csv")
    products_file = os.path.join(base_dir, "amazon_products.csv")
    output_dir = os.path.join(base_dir, "categories")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Read categories
    categories = {}
    with open(categories_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories[row['id']] = row['category_name']
            
    # Keep track of file handles to avoid opening/closing files millions of times
    file_handles = {}
    writers = {}
    
    print("Starting processing...")
    
    with open(products_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['alt']
        
        count = 0
        for row in reader:
            cat_id = row['category_id']
            cat_name = categories.get(cat_id, "Unknown_Category_{}".format(cat_id))
            
            # Generate the new image search URL
            title = row.get('title', '')
            search_query = urllib.parse.quote(title)
            google_img_url = "https://www.google.com/search?tbm=isch&q={}".format(search_query)
            
            # Replace imgUrl and set alt
            row['imgUrl'] = google_img_url
            row['alt'] = google_img_url
            
            if cat_id not in file_handles:
                safe_name = sanitize_filename(cat_name)
                out_path = os.path.join(output_dir, "{}.csv".format(safe_name))
                
                try:
                    fh = open(out_path, 'w', encoding='utf-8', newline='')
                    writer = csv.DictWriter(fh, fieldnames=fieldnames)
                    writer.writeheader()
                    file_handles[cat_id] = fh
                    writers[cat_id] = writer
                except Exception as e:
                    print("Error opening file for category {}: {}".format(cat_name, e))
                    continue
                    
            writers[cat_id].writerow(row)
            
            count += 1
            if count % 100000 == 0:
                print("Processed {} rows...".format(count))
                
    # Close all files
    for fh in file_handles.values():
        fh.close()
        
    print("Finished processing {} rows. Files saved to {}".format(count, output_dir))

if __name__ == '__main__':
    main()
