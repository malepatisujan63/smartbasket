import os
import json
import sqlite3
import psycopg2
from pymongo import MongoClient

# This script migrates data from the local SQLite database and JSON staging files
# into the advanced Multi-Database Architecture (PostgreSQL & MongoDB)

base_dir = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
sqlite_db_path = os.path.join(base_dir, "fast_ecommerce.db")
enriched_dir = r"d:\3rd sem created files\AIML PROJECT\enriched_data"

# PostgreSQL Connection (for Relational Data: Users, Logs, Core Products)
PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "admin"
PG_PASS = "adminpassword"
PG_DB = "ecommerce_db"

# MongoDB Connection (for Dynamic Schema: Features, Reviews)
MONGO_URI = "mongodb://admin:adminpassword@localhost:27017/"
MONGO_DB_NAME = "ecommerce_nosql"

def setup_postgres():
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB
        )
        cursor = conn.cursor()
        
        # Create Tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserLogs (
            log_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES Users(user_id),
            asin VARCHAR(255),
            action VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            search_query TEXT,
            view_duration INTEGER DEFAULT 0
        )
        """)
        
        conn.commit()
        print("PostgreSQL setup complete.")
        return conn
    except Exception as e:
        print(f"PostgreSQL connection failed (Ensure Docker container is running): {e}")
        return None

def setup_mongodb():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info() # Trigger connection test
        db = client[MONGO_DB_NAME]
        print("MongoDB setup complete.")
        return db
    except Exception as e:
        print(f"MongoDB connection failed (Ensure Docker container is running): {e}")
        return None

def migrate_data(pg_conn, mongo_db):
    if not pg_conn or not mongo_db:
        print("Migration aborted due to missing database connections.")
        return
        
    print("Starting migration...")
    
    # 1. Migrate SQLite Users & Logs to PostgreSQL
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    pg_cursor = pg_conn.cursor()
    
    try:
        sqlite_cursor.execute("SELECT user_id, username, password FROM Users")
        users = sqlite_cursor.fetchall()
        for u in users:
            pg_cursor.execute(
                "INSERT INTO Users (user_id, username, password) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING", 
                (u[0], u[1], u[2])
            )
            
        sqlite_cursor.execute("SELECT log_id, user_id, asin, action, timestamp, search_query, view_duration FROM UserLogs")
        logs = sqlite_cursor.fetchall()
        for l in logs:
            pg_cursor.execute(
                "INSERT INTO UserLogs (log_id, user_id, asin, action, timestamp, search_query, view_duration) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (log_id) DO NOTHING",
                (l[0], l[1], l[2], l[3], l[4], l[5], l[6])
            )
        pg_conn.commit()
        print("Relational data migrated to PostgreSQL.")
    except Exception as e:
        print(f"Error migrating to PostgreSQL: {e}")
        pg_conn.rollback()
        
    # 2. Migrate Enriched JSON Data to MongoDB
    products_collection = mongo_db["products"]
    
    if os.path.exists(enriched_dir):
        json_files = [f for f in os.listdir(enriched_dir) if f.endswith('.json')]
        total_imported = 0
        for j_file in json_files:
            file_path = os.path.join(enriched_dir, j_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if data:
                        # Use ASIN as the MongoDB _id
                        for item in data:
                            item['_id'] = item.pop('asin', None)
                            if item['_id']:
                                try:
                                    products_collection.insert_one(item)
                                    total_imported += 1
                                except Exception as e: # Catch duplicate key errors
                                    pass
                except Exception as e:
                    print(f"Error reading {j_file}: {e}")
                    
        print(f"Migrated {total_imported} enriched products to MongoDB.")
    else:
        print("Enriched data directory not found. Please run data_enrichment.py first.")
        
    sqlite_conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    pg_conn = setup_postgres()
    mongo_db = setup_mongodb()
    migrate_data(pg_conn, mongo_db)
    if pg_conn:
        pg_conn.close()
