'use client';

import React, { useEffect, useState, useMemo, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { productsApi, categoriesApi } from '../../services/api';
import { Product, Category, Brand } from '../../types';
import ProductCard from '../../components/ProductCard';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, SlidersHorizontal, X, ArrowUpDown, Sparkles, Filter, Check, ChevronDown, Tag, RefreshCw, Zap } from 'lucide-react';

const ProductsCatalogContent: React.FC = () => {
  const searchParams = useSearchParams();
  const router = useRouter();

  const searchVal = searchParams.get('search') || '';
  const categorySlug = searchParams.get('category_slug') || '';
  const brandSlug = searchParams.get('brand_slug') || '';
  const sortByVal = searchParams.get('sort_by') || 'featured';

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters State
  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [inStockOnly, setInStockOnly] = useState<boolean>(false);
  const [minRating, setMinRating] = useState<number>(0);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  useEffect(() => {
    const fetchCatalogData = async () => {
      setLoading(true);
      try {
        const [prodRes, catRes, brandRes] = await Promise.all([
          productsApi.getProducts({
            search: searchVal || undefined,
            category_slug: categorySlug || undefined,
            brand_slug: brandSlug || undefined,
            sort_by: sortByVal,
            limit: 48,
          }),
          categoriesApi.getCategories(),
          categoriesApi.getBrands(),
        ]);
        setProducts(prodRes.data);
        setCategories(catRes.data);
        setBrands(brandRes.data);
      } catch (err) {
        console.error('Catalog fetch error', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCatalogData();
  }, [searchVal, categorySlug, brandSlug, sortByVal]);

  // Client-side filtering
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      if (minPrice && p.price < Number(minPrice)) return false;
      if (maxPrice && p.price > Number(maxPrice)) return false;
      if (inStockOnly && p.stock <= 0) return false;
      if (minRating > 0 && p.rating < minRating) return false;
      return true;
    });
  }, [products, minPrice, maxPrice, inStockOnly, minRating]);

  const handleClearFilters = () => {
    setMinPrice('');
    setMaxPrice('');
    setInStockOnly(false);
    setMinRating(0);
    router.push('/products');
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-card via-muted to-card border border-border rounded-2xl p-6 sm:p-8 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-1.5 bg-[#d5a249]/15 text-[#172337] dark:text-[#d5a249] px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5 text-[#d5a249]" /> AJIO Curated Catalog
          </div>
          <h1 className="text-2xl sm:text-4xl font-black text-[#2c4152] dark:text-white tracking-tight uppercase">
            {categorySlug ? `${categories.find((c) => c.slug === categorySlug)?.name || 'Department'} Collection` : searchVal ? `Search results for "${searchVal}"` : 'AJIO All Products Collection'}
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground font-semibold mt-1">
            Showing {filteredProducts.length} items with instant Cash on Delivery guarantee & personalized AI ranking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Mobile Filter Trigger */}
          <button
            onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
            className="md:hidden px-4 py-2.5 rounded-xl bg-card border border-border text-foreground font-bold text-xs flex items-center gap-2 shadow-sm"
          >
            <Filter className="w-4 h-4 text-secondary" />
            <span>Filters</span>
          </button>

          {/* Sort By Dropdown */}
          <div className="relative flex items-center gap-2 bg-card border border-border rounded-xl px-3.5 py-2 shadow-sm">
            <ArrowUpDown className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-bold text-muted-foreground hidden sm:inline">Sort:</span>
            <select
              value={sortByVal}
              onChange={(e) => {
                const params = new URLSearchParams(searchParams.toString());
                params.set('sort_by', e.target.value);
                router.push(`/products?${params.toString()}`);
              }}
              className="bg-transparent text-xs font-extrabold text-foreground focus:outline-none cursor-pointer"
            >
              <option value="featured" className="bg-card text-foreground">Featured & AI Recommended</option>
              <option value="price_asc" className="bg-card text-foreground">Price: Low to High</option>
              <option value="price_desc" className="bg-card text-foreground">Price: High to Low</option>
              <option value="reviews" className="bg-card text-foreground">Customer Rating</option>
              <option value="newest" className="bg-card text-foreground">Newest Arrivals</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Sidebar Filters & Product Results */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        {/* Sidebar Filters (Desktop) */}
        <aside className={`md:col-span-3 space-y-6 bg-card border border-border rounded-3xl p-6 shadow-lg ${mobileFilterOpen ? 'block' : 'hidden md:block'}`}>
          <div className="flex items-center justify-between pb-4 border-b border-border">
            <h3 className="text-sm font-black text-foreground uppercase tracking-wider flex items-center gap-1.5">
              <SlidersHorizontal className="w-4 h-4 text-primary" /> Filter Catalog
            </h3>
            <button
              onClick={handleClearFilters}
              className="text-[11px] text-secondary hover:underline font-extrabold uppercase tracking-wider"
            >
              Reset All
            </button>
          </div>

          {/* Categories Filter */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-black text-muted-foreground uppercase tracking-wider">Department</h4>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1 no-scrollbar">
              <button
                onClick={() => router.push('/products')}
                className={`w-full text-left px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${!categorySlug ? 'bg-primary text-white font-black shadow-md' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
              >
                All Departments
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => router.push(`/products?category_slug=${cat.slug}`)}
                  className={`w-full text-left px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${categorySlug === cat.slug ? 'bg-primary text-white font-black shadow-md' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div className="space-y-3 pt-4 border-t border-border">
            <h4 className="text-xs font-black text-muted-foreground uppercase tracking-wider">Price Range ($)</h4>
            <div className="flex items-center gap-2">
              <input
                type="number"
                placeholder="Min"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                className="w-full bg-muted/60 border border-border rounded-xl px-3 py-2 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
              />
              <span className="text-muted-foreground">-</span>
              <input
                type="number"
                placeholder="Max"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="w-full bg-muted/60 border border-border rounded-xl px-3 py-2 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          {/* Rating Filter */}
          <div className="space-y-2.5 pt-4 border-t border-border">
            <h4 className="text-xs font-black text-muted-foreground uppercase tracking-wider">Minimum Rating</h4>
            <div className="space-y-1">
              {[4, 3, 2, 1].map((stars) => (
                <button
                  key={stars}
                  onClick={() => setMinRating(minRating === stars ? 0 : stars)}
                  className={`w-full flex items-center justify-between px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${minRating === stars ? 'bg-amber-500/15 text-amber-500 border border-amber-500/30 font-black' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
                >
                  <span>★ {stars}.0 & Up</span>
                  {minRating === stars && <Check className="w-3.5 h-3.5 text-amber-500" />}
                </button>
              ))}
            </div>
          </div>

          {/* In Stock Only Toggle */}
          <div className="pt-4 border-t border-border flex items-center justify-between">
            <span className="text-xs font-bold text-foreground">In Stock Only</span>
            <input
              type="checkbox"
              checked={inStockOnly}
              onChange={(e) => setInStockOnly(e.target.checked)}
              className="w-4 h-4 rounded text-primary focus:ring-primary accent-primary cursor-pointer"
            />
          </div>
        </aside>

        {/* Product Results Grid */}
        <main className="md:col-span-9 space-y-6">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-96 bg-card rounded-2xl border border-border animate-shimmer" />
              ))}
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="bg-card border border-border rounded-3xl p-12 text-center space-y-4 shadow-xl">
              <div className="w-16 h-16 rounded-2xl bg-muted/80 flex items-center justify-center mx-auto text-muted-foreground">
                <Search className="w-8 h-8 stroke-[1.5]" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-black text-foreground">No matching products found</h3>
                <p className="text-xs text-muted-foreground max-w-md mx-auto">
                  Try adjusting your price range, clearing filter keywords, or exploring other categories.
                </p>
              </div>
              <button
                onClick={handleClearFilters}
                className="px-6 py-2.5 btn-orange-gradient text-xs uppercase font-black tracking-wider shadow-md inline-block"
              >
                Reset All Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map((prod) => (
                <ProductCard key={prod.id} product={prod} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

const ProductsPage: React.FC = () => {
  return (
    <Suspense fallback={<div className="py-24 text-center text-sm font-bold text-muted-foreground animate-pulse">Loading AI Catalog...</div>}>
      <ProductsCatalogContent />
    </Suspense>
  );
};

export default ProductsPage;
