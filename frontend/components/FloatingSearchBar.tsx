'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { recommendationsApi } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sparkles, TrendingUp, ArrowRight, X, Tag, Zap } from 'lucide-react';
import { trackEvent } from '../services/analytics';

const FloatingSearchBar: React.FC = () => {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<{
    trending_searches: string[];
    popular_categories: any[];
    product_suggestions: any[];
  }>({
    trending_searches: [],
    popular_categories: [],
    product_suggestions: [],
  });
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const fetchSuggestions = async () => {
      setLoading(true);
      try {
        const res = await recommendationsApi.getSearchSuggestions(query);
        setSuggestions(res.data);
      } catch (err) {
        console.error('Search error', err);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(() => {
      if (isOpen) fetchSuggestions();
    }, 250);

    return () => clearTimeout(timer);
  }, [query, isOpen]);

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (query.trim()) {
      trackEvent('search', { query: query.trim() });
      setIsOpen(false);
      router.push(`/products?search=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleSelectQuery = (term: string) => {
    trackEvent('search', { query: term });
    setQuery(term);
    setIsOpen(false);
    router.push(`/products?search=${encodeURIComponent(term)}`);
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <form onSubmit={handleSearchSubmit} className="relative flex items-center">
        {/* Search Input */}
        <div className="relative w-full flex items-center bg-card border-2 border-border hover:border-primary/50 focus-within:border-primary rounded-2xl shadow-sm hover:shadow-md transition-all duration-300">
          <div className="pl-4 text-primary flex items-center gap-1.5">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder="Search AJIO for styles, sneakers, electronics, watches..."
            className="w-full bg-transparent py-3 px-3.5 text-xs sm:text-sm text-foreground placeholder-muted-foreground font-semibold focus:outline-none"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="p-1.5 mr-1 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            type="submit"
            className="btn-ajio px-5 py-3 rounded-r-xl transition-all flex items-center gap-1.5 text-xs sm:text-sm shadow-md font-bold tracking-wide"
          >
            <span>Search</span>
          </button>
        </div>
      </form>

      {/* Autocomplete Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="absolute left-0 right-0 mt-2.5 bg-card border border-border rounded-2xl shadow-2xl p-5 z-50 backdrop-blur-2xl max-h-[80vh] overflow-y-auto"
          >
            {loading && <div className="text-center py-6 text-xs font-bold text-muted-foreground animate-pulse">AI is indexing catalog vector space...</div>}

            {!loading && (
              <div className="space-y-6">
                {/* Product Suggestions */}
                {suggestions.product_suggestions.length > 0 && (
                  <div>
                    <h4 className="text-xs font-black text-primary uppercase tracking-wider mb-3 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-secondary" /> Instant AI Product Matches
                    </h4>
                    <div className="space-y-2">
                      {suggestions.product_suggestions.map((prod) => (
                        <motion.div
                          whileHover={{ x: 4 }}
                          key={prod.id}
                          onClick={() => {
                            setIsOpen(false);
                            router.push(`/products/${prod.id}`);
                          }}
                          className="flex items-center justify-between p-2.5 rounded-xl bg-muted/50 hover:bg-muted border border-border/60 hover:border-primary/40 cursor-pointer transition-all group"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-11 h-11 rounded-lg bg-card overflow-hidden flex items-center justify-center flex-shrink-0 border border-border">
                              <img src={prod.image || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=200&q=80'} alt="" className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                            </div>
                            <div className="text-left">
                              <p className="text-xs font-extrabold text-foreground group-hover:text-primary transition-colors line-clamp-1">{prod.title}</p>
                              <p className="text-[10px] text-muted-foreground font-semibold">{prod.category} • ★ {prod.rating}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-black text-secondary">${prod.price.toFixed(2)}</span>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trending Searches */}
                {suggestions.trending_searches.length > 0 && (
                  <div>
                    <h4 className="text-xs font-black text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-secondary" /> Trending in AI Retail
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {suggestions.trending_searches.map((term, i) => (
                        <motion.button
                          whileTap={{ scale: 0.95 }}
                          whileHover={{ scale: 1.05 }}
                          key={i}
                          type="button"
                          onClick={() => handleSelectQuery(term)}
                          className="px-3.5 py-1.5 rounded-xl bg-muted/80 hover:bg-primary/10 border border-border hover:border-primary/50 text-xs font-bold text-foreground hover:text-primary transition-all flex items-center gap-1.5 shadow-sm"
                        >
                          <Search className="w-3 h-3 text-muted-foreground" />
                          <span>{term}</span>
                        </motion.button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Popular Categories */}
                {suggestions.popular_categories.length > 0 && !query && (
                  <div>
                    <h4 className="text-xs font-black text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-1.5">
                      <Tag className="w-3.5 h-3.5 text-primary" /> Popular Departments
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                      {suggestions.popular_categories.map((cat) => (
                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          key={cat.id}
                          onClick={() => {
                            setIsOpen(false);
                            router.push(`/products?category_slug=${cat.slug}`);
                          }}
                          className="p-3 rounded-xl bg-muted/50 hover:bg-muted border border-border/60 hover:border-primary/40 cursor-pointer text-xs font-extrabold text-foreground hover:text-primary transition-all flex items-center justify-between group shadow-sm"
                        >
                          <span>{cat.name}</span>
                          <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-primary" />
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FloatingSearchBar;
