import sqlite3, os

db = sqlite3.connect(r"d:\3rd sem created files\AIML PROJECT\ecommerce_app\fast_ecommerce.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM ProductFeatures")
print("ProductFeatures count:", c.fetchone()[0])
c.execute("PRAGMA index_list(ProductFeatures)")
print("ProductFeatures indexes:", c.fetchall())
db.close()
