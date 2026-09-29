import sys, asyncio, time
sys.path.insert(0, r'd:\3rd sem created files\AIML PROJECT\ecommerce_app')
from app import get_categories, get_category_products

async def test():
    # Test 1: categories (must be instant from file)
    t = time.time()
    cats = await get_categories()
    n = len(cats["categories"])
    ms = int((time.time()-t)*1000)
    print(f"[1] /api/categories -> {n} cats in {ms}ms")

    first = cats["categories"][0]

    # Test 2: category products page 1
    t = time.time()
    prods = await get_category_products(first, 0, 1)
    ml  = len(prods["ml_picks"])
    std = len(prods["standard_results"])
    ms  = int((time.time()-t)*1000)
    print(f"[2] /api/category_products/{first} -> ml={ml} std={std} in {ms}ms")
    print("ALL TESTS PASSED")

asyncio.run(test())
