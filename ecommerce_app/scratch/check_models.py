import sqlite3, json, os, sys

BASE = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
db = sqlite3.connect(os.path.join(BASE, "fast_ecommerce.db"))
cur = db.cursor()

print("=" * 60)
print("USER STATS")
print("=" * 60)
cur.execute("SELECT user_id, username, ab_group, is_admin FROM Users ORDER BY user_id")
users = cur.fetchall()
for u in users:
    cur2 = db.cursor()
    cur2.execute("SELECT action, COUNT(*) FROM UserLogs WHERE user_id=? GROUP BY action", (u[0],))
    actions = dict(cur2.fetchall())
    total = sum(actions.values()) if actions else 0
    view = actions.get("view", 0)
    cart = actions.get("cart", 0)
    purchase = actions.get("purchase", 0)
    print("  User %d (%s) | Group=%s | TotalLogs=%d | View=%d Cart=%d Purchase=%d" % (
        u[0], u[1], u[2], total, view, cart, purchase))

print()
cur.execute("SELECT COUNT(*) FROM Products")
print("Total Products: %d" % cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM UserLogs")
print("Total UserLogs: %d" % cur.fetchone()[0])

print()
print("=" * 60)
print("MODEL FILES")
print("=" * 60)
models_dir = os.path.join(BASE, "models")
if os.path.exists(models_dir):
    for f in sorted(os.listdir(models_dir)):
        path = os.path.join(models_dir, f)
        size = os.path.getsize(path)
        print("  %s  (%d bytes)" % (f, size))

print()
print("=" * 60)
print("METRICS")
print("=" * 60)
if os.path.exists(models_dir):
    for f in sorted(os.listdir(models_dir)):
        if f.endswith("_metrics.json"):
            with open(os.path.join(models_dir, f)) as mf:
                m = json.load(mf)
            print("  [%s]" % f)
            for k, v in m.items():
                print("    %s: %s" % (k, v))

print()
print("=" * 60)
print("NCF MODEL")
print("=" * 60)
ncf_map = os.path.join(BASE, "ncf_mappings.json")
ncf_model = os.path.join(BASE, "ncf_model.pth")
if os.path.exists(ncf_model):
    print("  ncf_model.pth: %d bytes" % os.path.getsize(ncf_model))
if os.path.exists(ncf_map):
    with open(ncf_map) as f:
        m = json.load(f)
    print("  Trained on: %d users, %d items" % (len(m["user_map"]), len(m["item_map"])))
    print("  User IDs in map:", list(m["user_map"].keys()))

db.close()
print("\nDone.")
