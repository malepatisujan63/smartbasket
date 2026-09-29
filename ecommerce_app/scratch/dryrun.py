"""Full pipeline dry-run test — tests EVERY endpoint the website uses."""
import urllib.request, json, time, sys

BASE = "http://127.0.0.1:8000"
PASS = []; FAIL = []

def test(name, url, timeout=10):
    try:
        t = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "test"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            ms = int((time.time()-t)*1000)
            data = json.loads(body)
            PASS.append((name, ms, len(body)))
            return data
    except Exception as e:
        FAIL.append((name, str(e)))
        return None

def test_static(name, url, timeout=10):
    try:
        t = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "test"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            ms = int((time.time()-t)*1000)
            PASS.append((name, ms, len(body)))
            return True
    except Exception as e:
        FAIL.append((name, str(e)))
        return False

print("=" * 60)
print("  FULL PIPELINE DRY RUN")
print("=" * 60)

# 1. Static files
test_static("CSS:  google_glass.css",    f"{BASE}/static/css/google_glass.css")
test_static("JS:   categories.js",       f"{BASE}/static/js/categories.js")

# 2. Pages
test_static("PAGE: /",                   f"{BASE}/")
test_static("PAGE: /home",              f"{BASE}/home")
test_static("PAGE: /categories",        f"{BASE}/categories")
test_static("PAGE: /profile",           f"{BASE}/profile")
test_static("PAGE: /admin",             f"{BASE}/admin")

# 3. Categories API
cats_data = test("API:  /api/categories",            f"{BASE}/api/categories")
if cats_data:
    print(f"       -> {len(cats_data['categories'])} categories loaded")
    first_cat = cats_data['categories'][0]
else:
    first_cat = "Makeup"

# 4. Category products
prods = test("API:  /api/category_products/{cat}",  f"{BASE}/api/category_products/{urllib.request.quote(first_cat)}?user_id=0&page=1")
if prods:
    print(f"       -> ml={len(prods['ml_picks'])} std={len(prods['standard_results'])} has_more={prods['has_more']}")

# 5. Home feed
home = test("API:  /api/home_feed",                 f"{BASE}/api/home_feed?user_id=0")
if home:
    print(f"       -> {len(home['sections'])} sections")

# 6. Search
search = test("API:  /api/search",                  f"{BASE}/api/search?q=laptop&user_id=0")
if search:
    print(f"       -> {len(search['results'])} results")

# 7. Admin
admin = test("API:  /api/admin/stats",              f"{BASE}/api/admin/stats")
if admin:
    print(f"       -> {admin['users']['total']} users, {admin['products']['total']} products")

test("API:  /api/admin/users",      f"{BASE}/api/admin/users")
test("API:  /api/admin/daily_report", f"{BASE}/api/admin/daily_report")

# ── Results ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  PASSED: {len(PASS)} / {len(PASS)+len(FAIL)}")
print("=" * 60)
for name, ms, sz in PASS:
    print(f"  OK  {name:<42} {ms:>5}ms  {sz:>7} bytes")

if FAIL:
    print(f"\n  FAILED: {len(FAIL)}")
    print("-" * 60)
    for name, err in FAIL:
        print(f"  ❌  {name:<42} {err}")

print("=" * 60)
sys.exit(0 if not FAIL else 1)
