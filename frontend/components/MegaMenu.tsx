'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { categoriesApi } from '../services/api';
import { Category, Brand } from '../types';
import { motion } from 'framer-motion';
import { X, Sparkles, ChevronRight, Laptop, Smartphone, Headphones, Tv, Gamepad2, Watch, Camera, Home, ShieldCheck, Zap, Shirt, Footprints } from 'lucide-react';

interface MegaMenuProps {
  onClose: () => void;
}

const MegaMenu: React.FC<MegaMenuProps> = ({ onClose }) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [catsRes, brandsRes] = await Promise.all([
          categoriesApi.getCategories(),
          categoriesApi.getBrands(),
        ]);
        setCategories(catsRes.data);
        setBrands(brandsRes.data);
      } catch (err) {
        console.error('Failed to load menu data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getCategoryIcon = (slug: string) => {
    switch (slug) {
      case 'fashion': return <Shirt className="w-5 h-5 text-rose-500" />;
      case 'shoes': return <Footprints className="w-5 h-5 text-amber-500" />;
      case 'beauty': return <Sparkles className="w-5 h-5 text-pink-500" />;
      case 'smart-watches': return <Watch className="w-5 h-5 text-teal-500" />;
      case 'laptops': return <Laptop className="w-5 h-5 text-blue-500" />;
      case 'mobiles': return <Smartphone className="w-5 h-5 text-emerald-500" />;
      case 'audio': return <Headphones className="w-5 h-5 text-purple-500" />;
      case 'furniture': return <Home className="w-5 h-5 text-indigo-500" />;
      case 'gaming': return <Gamepad2 className="w-5 h-5 text-amber-500" />;
      case 'televisions': return <Tv className="w-5 h-5 text-red-500" />;
      default: return <Zap className="w-5 h-5 text-[#d5a249]" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Menu Panel */}
      <motion.div
        initial={{ x: '-100%' }}
        animate={{ x: 0 }}
        exit={{ x: '-100%' }}
        transition={{ type: 'spring', damping: 28, stiffness: 300 }}
        className="relative w-full max-w-4xl bg-card border-r border-border text-foreground shadow-2xl flex flex-col max-h-screen overflow-y-auto z-10"
      >
        {/* Header */}
        <div className="bg-card/95 backdrop-blur-md p-6 border-b border-border flex items-center justify-between sticky top-0 z-10 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="bg-[#2c4152] p-2.5 rounded-2xl text-white shadow-md">
              <Sparkles className="w-6 h-6 fill-[#d5a249] text-[#d5a249]" />
            </div>
            <div>
              <h2 className="text-xl font-black tracking-tight flex items-center gap-1.5 text-foreground uppercase">
                AJIO <span className="bg-[#d5a249] text-[#172337] px-2 py-0.5 rounded text-xs font-black">LUXE</span> CATALOG
              </h2>
              <p className="text-xs text-muted-foreground font-semibold">Explore 20,000+ fashion styles, footwear & lifestyle categories</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 sm:p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Categories Grid */}
          <div className="md:col-span-2 space-y-4">
            <h3 className="text-sm font-black text-primary uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-secondary" /> Shop by Department
            </h3>
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-16 bg-muted/60 rounded-xl animate-shimmer" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {categories.map((cat) => (
                  <Link
                    key={cat.id}
                    href={`/products?category_slug=${cat.slug}`}
                    onClick={onClose}
                    className="flex items-center justify-between p-4 rounded-2xl bg-muted/50 border border-border hover:border-primary/40 hover:bg-card transition-all group shadow-sm hover:shadow-md"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="p-2.5 rounded-xl bg-card border border-border group-hover:scale-110 transition-transform shadow-inner">
                        {getCategoryIcon(cat.slug)}
                      </div>
                      <div>
                        <h4 className="text-sm font-extrabold text-foreground group-hover:text-primary transition-colors">{cat.name}</h4>
                        <p className="text-[11px] text-muted-foreground line-clamp-1 font-medium">{cat.description || 'AI curated electronics'}</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Brands & AI Spotlight */}
          <div className="space-y-6 border-t md:border-t-0 md:border-l border-border pt-6 md:pt-0 md:pl-8">
            <div>
              <h3 className="text-sm font-black text-secondary uppercase tracking-wider mb-4 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" /> Top Brands
              </h3>
              <div className="flex flex-wrap gap-2">
                {brands.slice(0, 10).map((b) => (
                  <Link
                    key={b.id}
                    href={`/products?brand_slug=${b.slug}`}
                    onClick={onClose}
                    className="px-3.5 py-1.5 rounded-xl bg-muted/80 border border-border hover:border-secondary/50 hover:bg-secondary/10 text-xs font-bold text-foreground hover:text-secondary transition-all shadow-sm"
                  >
                    {b.name}
                  </Link>
                ))}
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-gradient-to-br from-primary/10 via-secondary/10 to-transparent border border-primary/20 shadow-lg space-y-3">
              <div className="flex items-center gap-2 text-primary font-black text-xs uppercase">
                <Sparkles className="w-4 h-4 animate-spin text-secondary" /> Explainable AI Engine
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed font-semibold">
                Our hybrid recommendation engine uses TF-IDF vectorization and collaborative filtering to predict your preferences with 94%+ accuracy.
              </p>
              <Link
                href="/products"
                onClick={onClose}
                className="inline-block w-full text-center py-2.5 btn-orange-gradient text-xs uppercase font-black shadow-md"
              >
                Browse AI Matches
              </Link>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default MegaMenu;
