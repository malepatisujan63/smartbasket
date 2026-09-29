import os
import csv
import json
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Set up paths
base_dir = r"d:\3rd sem created files\AIML PROJECT"
categories_dir = os.path.join(base_dir, "categories")
enriched_dir = os.path.join(base_dir, "enriched_data")
excel_dir = os.path.join(base_dir, "excel_exports")

if not os.path.exists(enriched_dir):
    os.makedirs(enriched_dir)
if not os.path.exists(excel_dir):
    os.makedirs(excel_dir)

# List of User-Agents to rotate and avoid blocking
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
]

def fetch_amazon_data(url):
    """Scrapes product features and top reviews from Amazon."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US, en;q=0.5',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    }
    
    data = {
        'specific_features': {},
        'positive_reviews': [],
        'negative_reviews': []
    }
    
    try:
        # Add a random sleep to avoid aggressive blocking
        time.sleep(random.uniform(1.0, 3.0))
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Extract Specific Features (e.g. from the 'Product Details' or technical specs table)
            details_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
            if details_table:
                for row in details_table.find_all('tr'):
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        key = th.text.strip().replace('\u200e', '')
                        value = td.text.strip().replace('\u200e', '')
                        data['specific_features'][key] = value
                        
            # Alternate feature extraction if table is different
            feature_bullets = soup.find('div', {'id': 'feature-bullets'})
            if feature_bullets and not data['specific_features']:
                ul = feature_bullets.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        text = li.text.strip()
                        if text:
                            data['specific_features'][f"feature_{len(data['specific_features'])}"] = text

            # 2. Extract Reviews
            reviews_div = soup.find_all('div', {'data-hook': 'review'})
            for review in reviews_div:
                rating_elem = review.find('i', {'data-hook': 'review-star-rating'})
                text_elem = review.find('span', {'data-hook': 'review-body'})
                
                if rating_elem and text_elem:
                    rating_text = rating_elem.text
                    rating_val = float(rating_text.split(' ')[0])
                    review_text = text_elem.text.strip()
                    
                    if rating_val >= 4.0:
                        if len(data['positive_reviews']) < 3: # Keep top 3 positive
                            data['positive_reviews'].append(review_text)
                    elif rating_val <= 2.0:
                        if len(data['negative_reviews']) < 3: # Keep top 3 negative
                            data['negative_reviews'].append(review_text)
                            
        else:
            print(f"Failed to fetch {url} - Status Code: {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        
    return data

def process_category(file_path):
    cat_name = os.path.basename(file_path)
    output_json = os.path.join(enriched_dir, cat_name.replace('.csv', '.json'))
    
    # Skip if already processed
    if os.path.exists(output_json):
        print(f"Skipping {cat_name}, already enriched.")
        return
        
    print(f"Enriching {cat_name}...")
    enriched_products = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Limit to first 20 products per category for the demo/test
        # Removing limit in production can take weeks due to Amazon blocking
        rows = [row for i, row in enumerate(reader) if i < 20]
        
    for row in rows:
        url = row.get('productURL')
        if url:
            scraped_data = fetch_amazon_data(url)
            row['specific_features'] = scraped_data['specific_features']
            row['positive_reviews'] = scraped_data['positive_reviews']
            row['negative_reviews'] = scraped_data['negative_reviews']
            
            # Combine features into a single text string for CatBoost
            feature_string = " ".join([f"{k} {v}" for k, v in scraped_data['specific_features'].items()])
            row['text_features'] = feature_string
            
        enriched_products.append(row)
        
    # Save to JSON (acts as a staging layer before MongoDB)
    with open(output_json, 'w', encoding='utf-8') as out_f:
        json.dump(enriched_products, out_f, indent=4)
        
    # Export to Excel
    try:
        df = pd.DataFrame(enriched_products)
        # Convert lists and dicts to string representations for Excel
        df['specific_features'] = df['specific_features'].apply(lambda x: str(x) if isinstance(x, dict) else x)
        df['positive_reviews'] = df['positive_reviews'].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
        df['negative_reviews'] = df['negative_reviews'].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
        
        excel_path = os.path.join(excel_dir, cat_name.replace('.csv', '.xlsx'))
        df.to_excel(excel_path, index=False)
        print(f"Exported {cat_name} to Excel.")
    except Exception as e:
        print(f"Failed to export Excel for {cat_name}: {e}")
        
    print(f"Finished enriching {cat_name}.")

def main():
    csv_files = [os.path.join(categories_dir, f) for f in os.listdir(categories_dir) if f.endswith('.csv')]
    
    print(f"Found {len(csv_files)} categories. Starting enrichment pipeline...")
    
    # Use ThreadPool to process multiple categories at once
    # Keep workers low (2-3) to avoid triggering Amazon's anti-bot mechanisms immediately
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(process_category, csv_files)
        
    print("Data Enrichment Complete. Data saved to the 'enriched_data' folder.")

if __name__ == "__main__":
    main()
