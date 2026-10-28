'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../redux/store';
import { productsApi, recommendationsApi, categoriesApi } from '../services/api';
import { Product, Category } from '../types';
import ProductCard from '../components/ProductCard';
import AIReasonWidget from '../components/AIReasonWidget';
import { motion } from 'framer-motion';
import { Sparkles, TrendingUp, ShieldCheck, Zap, ArrowRight, CheckCircle2, Cpu, Award, Truck, ShoppingBag, Layers, Activity, Star, History } from 'lucide-react';
import { getSessionId } from '../services/analytics';

const HomePage: React.FC = () => {
  const router = useRouter();
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);

  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [aiRecommendations, setAiRecommendations] = useState<any[]>([]);
  const [recentlyViewed, setRecentlyViewed] = useState<any[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const sessionId = getSessionId();
        const [featRes, recRes, catRes, recentRes] = await Promise.all([
          productsApi.getFeaturedProducts(),
          recommendationsApi.getRecommendations(sessionId),
          categoriesApi.getCategories(),
          recommendationsApi.getRecentlyViewed(4, sessionId)
        ]);
        setFeaturedProducts(featRes.data);
        setAiRecommendations(recRes.data);
        setCategories(catRes.data);
        setRecentlyViewed(recentRes.data || []);
      } catch (err) {
        console.error("Home data fetch failed", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHomeData();
  }, [isAuthenticated]);

  // Demo fallback products if API is empty during initial setup
  const displayFeatured = featuredProducts.length > 0 ? featuredProducts : [
    {
      id: 1,
      title: "MacBook Pro M3 Max 16-Inch Space Black",
      description: "Apple M3 Max chip with 16‑core CPU, 40‑core GPU, 48GB Unified Memory, 1TB SSD Storage. Extreme AI development workstation.",
      price: 3499.00,
      stock: 4,
      category_id: 1,
      brand_id: 1,
      rating: 4.9,
      reviews_count: 142,
      is_featured: true,
      discount_percentage: 10,
      images: ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80"],
      created_at: new Date().toISOString(),
      category: { id: 1, name: "Computers", slug: "computers" },
      brand: { id: 1, name: "Apple", slug: "apple" }
    },
    {
      id: 2,
      title: "Sony WH-1000XM5 Wireless Noise-Canceling Headphones",
      description: "Industry-leading noise cancellation with two processors and 8 microphones. 30-hour battery life with quick charging.",
      price: 399.99,
      stock: 12,
      category_id: 2,
      brand_id: 2,
      rating: 4.8,
      reviews_count: 389,
      is_featured: true,
      discount_percentage: 15,
      images: ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80"],
      created_at: new Date().toISOString(),
      category: { id: 2, name: "Audio", slug: "audio" },
      brand: { id: 2, name: "Sony", slug: "sony" }
    },
    {
      id: 3,
      title: "Samsung 65-Inch 4K Neo QLED Smart AI TV",
      description: "Quantum Matrix Technology with Mini LEDs and Neural Quantum Processor 4K with 4K AI Upscaling.",
      price: 1899.99,
      stock: 7,
      category_id: 3,
      brand_id: 3,
      rating: 4.7,
      reviews_count: 94,
      is_featured: true,
      discount_percentage: 20,
      images: ["https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=600&q=80"],
      created_at: new Date().toISOString(),
      category: { id: 3, name: "TV & Home", slug: "tv" },
      brand: { id: 3, name: "Samsung", slug: "samsung" }
    },
    {
      id: 4,
      title: "Apple iPhone 15 Pro Max 512GB Natural Titanium",
      description: "Forged in titanium and featuring the groundbreaking A17 Pro chip, a customizable Action button, and a more versatile Pro camera system.",
      price: 1399.00,
      stock: 3,
      category_id: 4,
      brand_id: 1,
      rating: 4.9,
      reviews_count: 512,
      is_featured: true,
      discount_percentage: 5,
      images: ["https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=600&q=80"],
      created_at: new Date().toISOString(),
      category: { id: 4, name: "Smartphones", slug: "smartphones" },
      brand: { id: 1, name: "Apple", slug: "apple" }
    }
  ];

  const displayRecs = aiRecommendations.length > 0 ? aiRecommendations : [
    {
      product: displayFeatured[0],
      explanation: {
        reason: "Matched via Scikit-Learn TF-IDF vector similarity with your high-end computing browsing history.",
        confidence: 0.96,
        recommendation: "Priority Fulfillment Available",
        important_features: [
          { feature: "AI Workstation Specs", value: "M3 Max / 48GB RAM", impact: "High Relevance (+0.42)" },
          { feature: "Peer Cluster Preference", value: "Software Engineers", impact: "Positive Match (+0.35)" }
        ]
      }
    },
    {
      product: displayFeatured[1],
      explanation: {
        reason: "Frequently paired with professional laptops in collaborative filtering matrix.",
        confidence: 0.92,
        recommendation: "Bundle Discount Eligible",
        important_features: [
          { feature: "Noise Cancellation", value: "WH-1000XM5 Dual Chip", impact: "High Relevance (+0.38)" },
          { feature: "Return Rate Risk", value: "0.4% (Ultra Low)", impact: "Positive Match (+0.28)" }
        ]
      }
    }
  ];

  return (
    <div className="space-y-20 pb-24">
      {/* 1. PREMIUM SAAS LANDING HERO SECTION */}
      <section className="relative pt-8 sm:pt-14 pb-16 overflow-hidden">
        {/* Background Glass & Gradient Shapes */}
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[800px] h-[450px] bg-gradient-to-tr from-primary/20 via-blue-500/10 to-secondary/15 rounded-full blur-[120px] pointer-events-none -z-10" />
        <div className="absolute top-1/3 -right-32 w-96 h-96 bg-secondary/10 rounded-full blur-[100px] pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column: Hero Typography Hierarchy */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left z-10">
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#d5a249]/15 text-[#1a2733] dark:text-[#d5a249] border border-[#d5a249]/30 font-black text-xs uppercase tracking-wider shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#d5a249] animate-spin" />
                <span>AJIOMANIA FASHION & LIFESTYLE SALE IS LIVE • 50-90% OFF</span>
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="text-4xl sm:text-6xl lg:text-[62px] font-black tracking-tight text-[#2c4152] dark:text-white leading-[1.08] uppercase"
              >
                Iconic Fashion <br className="hidden sm:inline" />
                <span className="text-[#d5a249]">
                  Curated by AI.
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="text-base sm:text-lg text-muted-foreground font-medium max-w-2xl mx-auto lg:mx-0 leading-relaxed"
              >
                Discover over 20,000+ top fashion apparel, luxury footwear, smart gadgets & beauty collections. Engineered with Scikit-Learn TF-IDF recommendations and 100% Cash on Delivery protection.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="flex flex-wrap items-center justify-center lg:justify-start gap-4 pt-2"
              >
                <Link
                  href="/products"
                  className="px-8 py-4 btn-ajio text-sm uppercase tracking-wider font-black shadow-xl flex items-center gap-2 group hover:scale-105 transition-all"
                >
                  <span>Explore AJIO Catalog</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  href="/products?sort_by=reviews"
                  className="px-8 py-4 rounded-lg bg-card hover:bg-muted border border-border text-foreground text-sm uppercase tracking-wider font-extrabold shadow-sm hover:shadow-md transition-all flex items-center gap-2"
                >
                  <Award className="w-4 h-4 text-[#d5a249]" />
                  <span>Deals of the Day (COD)</span>
                </Link>
              </motion.div>

              {/* Trust Indicators */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.5 }}
                className="pt-8 border-t border-border/80 grid grid-cols-3 gap-4 text-left max-w-lg mx-auto lg:mx-0"
              >
                <div>
                  <h4 className="text-xl sm:text-2xl font-black text-foreground flex items-center gap-1">
                    20,000+ <CheckCircle2 className="w-4 h-4 text-[#03a685]" />
                  </h4>
                  <p className="text-[11px] text-muted-foreground font-bold uppercase tracking-wider">Live Products</p>
                </div>
                <div>
                  <h4 className="text-xl sm:text-2xl font-black text-foreground flex items-center gap-1">
                    100% <ShieldCheck className="w-4 h-4 text-[#2c4152] dark:text-[#d5a249]" />
                  </h4>
                  <p className="text-[11px] text-muted-foreground font-bold uppercase tracking-wider">COD Delivery</p>
                </div>
                <div>
                  <h4 className="text-xl sm:text-2xl font-black text-foreground flex items-center gap-1">
                    AI-Driven <Zap className="w-4 h-4 text-[#d5a249]" />
                  </h4>
                  <p className="text-[11px] text-muted-foreground font-bold uppercase tracking-wider">Personalized Recs</p>
                </div>
              </motion.div>
            </div>

            {/* Right Column: Floating 3D Parallax Cards Showcase */}
            <div className="lg:col-span-5 relative min-h-[420px] flex items-center justify-center">
              {/* Background Glass Circle */}
              <div className="absolute w-80 h-80 rounded-full bg-gradient-to-tr from-primary/10 to-secondary/10 border border-border/60 shadow-inner -z-0" />

              {/* Main Floating Featured Product Card */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.7 }}
                className="w-full max-w-sm z-10 elevation-floating animate-float"
              >
                <div className="p-1 rounded-[28px] bg-gradient-to-br from-primary/40 via-border to-secondary/40 shadow-2xl">
                  <div className="bg-card rounded-[24px] p-5 shadow-inner">
                    <div className="flex items-center justify-between mb-3">
                      <span className="bg-primary/10 text-primary text-[10px] font-black px-2.5 py-1 rounded-full uppercase tracking-wider flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-secondary" /> AI TOP MATCH
                      </span>
                      <span className="text-xs font-black text-accent flex items-center gap-1">
                        ★ 4.9 (512 reviews)
                      </span>
                    </div>

                    <div className="aspect-video w-full rounded-2xl overflow-hidden bg-muted mb-4 border border-border relative group">
                      <img
                        src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80"
                        alt="MacBook Pro M3 Max"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute bottom-2 left-2 bg-black/70 backdrop-blur-md text-white font-black text-[10px] px-2.5 py-1 rounded-lg">
                        Scikit-Learn TF-IDF Indexed
                      </div>
                    </div>

                    <h3 className="text-base font-black text-foreground mb-1 leading-snug">
                      MacBook Pro M3 Max 16-Inch Workstation
                    </h3>
                    <p className="text-xs text-muted-foreground font-medium mb-4 line-clamp-2">
                      Engineered for high-throughput AI vector calculations, LLM local inference, and production software engineering.
                    </p>

                    <div className="flex items-center justify-between pt-3 border-t border-border">
                      <div>
                        <span className="text-[10px] text-muted-foreground uppercase font-bold block">Exclusive COD Price</span>
                        <span className="text-xl font-black text-foreground">$3,499.00</span>
                      </div>
                      <Link
                        href="/products/1"
                        className="px-4 py-2.5 btn-orange-gradient text-xs font-black uppercase rounded-xl shadow-md"
                      >
                        Quick View
                      </Link>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Floating Secondary Badge Card (Top Right) */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="absolute -top-6 -right-4 sm:-right-8 bg-card/95 backdrop-blur-xl border border-border p-3.5 rounded-2xl shadow-xl z-20 animate-float-delayed hidden sm:flex items-center gap-3 max-w-[220px]"
              >
                <div className="w-10 h-10 rounded-xl bg-accent/15 text-accent flex items-center justify-center font-black flex-shrink-0">
                  <Truck className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-black text-foreground leading-tight">Cash on Delivery</h4>
                  <p className="text-[10px] text-muted-foreground font-semibold">Pay 100% at your doorstep</p>
                </div>
              </motion.div>

              {/* Floating SHAP AI Badge (Bottom Left) */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
                className="absolute -bottom-6 -left-4 sm:-left-8 bg-card/95 backdrop-blur-xl border border-border p-3.5 rounded-2xl shadow-xl z-20 animate-float hidden sm:flex items-center gap-3 max-w-[240px]"
              >
                <div className="w-10 h-10 rounded-xl bg-secondary/15 text-secondary flex items-center justify-center font-black flex-shrink-0">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-black text-foreground leading-tight">XGBoost SHAP Enabled</h4>
                  <p className="text-[10px] text-muted-foreground font-semibold">Transparent recommendation weights</p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* 1.5 AJIO SIGNATURE CIRCULAR CATEGORY NAVIGATION STRIP */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        <div className="border-y border-border/80 py-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-black uppercase tracking-widest text-[#2c4152] dark:text-[#d5a249] flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#d5a249]" /> Explore Top Departments
            </h3>
            <Link href="/products" className="text-xs font-black text-[#d5a249] hover:underline uppercase tracking-wider flex items-center gap-1">
              View All 20 Categories <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="flex items-center justify-between gap-6 sm:gap-8 overflow-x-auto no-scrollbar py-2">
            {[
              { name: "Men's Fashion", slug: "fashion", img: "https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?auto=format&fit=crop&w=300&q=80", tag: "MIN 60% OFF" },
              { name: "Women's Wear", slug: "fashion", img: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=300&q=80", tag: "TRENDING" },
              { name: "Footwear", slug: "shoes", img: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=300&q=80", tag: "UP TO 70% OFF" },
              { name: "Smart Watches", slug: "smart-watches", img: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=300&q=80", tag: "AJIO EXCLUSIVE" },
              { name: "Beauty & Care", slug: "beauty", img: "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=300&q=80", tag: "BEST DEALS" },
              { name: "Audio Gear", slug: "audio", img: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=300&q=80", tag: "TOP PICKS" },
              { name: "Smartphones", slug: "mobiles", img: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=300&q=80", tag: "5G READY" },
              { name: "Laptops", slug: "laptops", img: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=300&q=80", tag: "AI POWERED" },
            ].map((cat, idx) => (
              <Link key={idx} href={`/products?category_slug=${cat.slug}`} className="flex flex-col items-center flex-shrink-0 group text-center space-y-2">
                <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full overflow-hidden border-2 border-border group-hover:border-[#d5a249] transition-all p-1 shadow-md bg-card group-hover:scale-105">
                  <img src={cat.img} alt={cat.name} className="w-full h-full object-cover rounded-full" />
                </div>
                <span className="text-xs font-black text-foreground group-hover:text-[#d5a249] transition-colors">{cat.name}</span>
                <span className="text-[9px] bg-[#d5a249]/15 text-[#b8860b] dark:text-[#d5a249] font-black px-2 py-0.5 rounded-full">{cat.tag}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 2. EXPLAINABLE AI RECSYS SHOWCASE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-primary/10 via-card to-secondary/10 border border-border rounded-3xl p-6 sm:p-10 shadow-xl">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8 border-b border-border pb-6">
            <div>
              <div className="inline-flex items-center gap-1.5 bg-secondary/15 text-secondary px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider mb-2">
                <Sparkles className="w-3.5 h-3.5" /> Real-Time Multi-Touch Hybrid RecSys Active
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
                AI Personalized Recommendations
              </h2>
              <p className="text-xs sm:text-sm text-muted-foreground font-semibold max-w-2xl mt-1">
                Dynamically adapted to your real-time in-session clickstream, cart items, brand preferences, and collaborative shopper patterns.
              </p>
            </div>
            <Link
              href="/products"
              className="px-5 py-2.5 rounded-xl bg-card hover:bg-muted border border-border text-foreground text-xs uppercase font-extrabold tracking-wider transition-all flex items-center gap-1.5 shadow-sm whitespace-nowrap"
            >
              <span>View Full AI Storefront</span>
              <ArrowRight className="w-3.5 h-3.5 text-primary" />
            </Link>
          </div>

          {/* Recommended Cards & Explanations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {displayRecs.map((item, idx) => (
              <div key={idx} className="flex flex-col gap-4">
                <ProductCard
                  product={item.product || displayFeatured[0]}
                  explanation={item.explanation}
                  aiMatchScore={Math.round((item.explanation?.confidence || 0.95) * 100)}
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 2.5 REAL-TIME RECENTLY VIEWED SECTION */}
      {recentlyViewed && recentlyViewed.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-primary/10 text-primary">
                <History className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xl font-black text-foreground tracking-tight">
                  Recently Viewed in Your Active Session
                </h3>
                <p className="text-xs text-muted-foreground font-semibold">
                  Live interaction history streamed to your AI personalization profile
                </p>
              </div>
            </div>
            <span className="text-[11px] font-black uppercase text-accent bg-accent/10 px-3 py-1 rounded-full border border-accent/20">
              Live Session Synced
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {recentlyViewed.map((item: any, idx: number) => {
              const prod = item.product || item;
              return (
                <ProductCard
                  key={prod.id || idx}
                  product={prod}
                  explanation={item.explanation}
                />
              );
            })}
          </div>
        </section>
      )}

      {/* 3. FEATURED PRODUCTS GRID */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border pb-4">
          <div>
            <span className="text-xs font-black text-primary uppercase tracking-widest block mb-1">
              Curated For Excellence
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
              Featured Flagship Devices
            </h2>
          </div>
          <Link
            href="/products?sort_by=newest"
            className="text-xs font-black text-secondary hover:underline uppercase tracking-wider flex items-center gap-1"
          >
            <span>Browse All {featuredProducts.length || displayFeatured.length} Flagships</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-96 bg-card rounded-2xl border border-border animate-shimmer" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {displayFeatured.slice(0, 4).map((prod) => (
              <ProductCard key={prod.id} product={prod} />
            ))}
          </div>
        )}
      </section>

      {/* 4. DEPARTMENTS GRID */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
            Explore AI Catalog by Department
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground font-semibold">
            Discover precision-indexed electronics, high-throughput workstations, and smart home automation systems.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {(categories.length > 0 ? categories : [
            { id: 1, name: "Computers & Laptops", slug: "computers-laptops", description: "M3 Max & AI Workstations" },
            { id: 2, name: "Smartphones & Tablets", slug: "smartphones-tablets", description: "iPhone 15 & iPad Pro" },
            { id: 3, name: "Audio & Headphones", slug: "audio-headphones", description: "Sony XM5 & AirPods" },
            { id: 4, name: "TV & Home Theater", slug: "tv-home-theater", description: "Samsung Neo QLED 8K" },
            { id: 5, name: "Smart Home AI", slug: "smart-home-ai", description: "HomePod & Alexa AI" },
            { id: 6, name: "Gaming & Wearables", slug: "gaming", description: "PS5 & Apple Watch" }
          ]).map((cat, idx) => (
            <Link
              key={cat.id || idx}
              href={`/products?category_slug=${cat.slug}`}
              className="glass-card p-5 text-center flex flex-col items-center justify-center gap-3 hover-lift-glow group bg-card"
            >
              <div className="w-12 h-12 rounded-2xl bg-muted group-hover:bg-primary/10 text-primary flex items-center justify-center transition-colors shadow-sm">
                <Layers className="w-6 h-6 group-hover:scale-110 transition-transform" />
              </div>
              <div>
                <h3 className="text-xs font-black text-foreground group-hover:text-primary transition-colors line-clamp-1">{cat.name}</h3>
                <p className="text-[10px] text-muted-foreground font-medium line-clamp-1 mt-0.5">{cat.description || "AI Curated"}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 5. CASH ON DELIVERY TRUST GUARANTEE BANNER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-slate-900 via-primary/90 to-slate-900 text-white rounded-3xl p-8 sm:p-12 shadow-2xl border border-primary/30 flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-secondary/15 rounded-full blur-3xl pointer-events-none" />

          <div className="space-y-4 max-w-2xl relative z-10 text-center md:text-left">
            <div className="inline-flex items-center gap-2 bg-secondary text-white px-3.5 py-1 rounded-full text-xs font-black uppercase tracking-wider shadow-md">
              <Truck className="w-4 h-4" /> 100% Risk-Free Guarantee
            </div>
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight leading-tight">
              Pay Nothing Online. <br />
              <span className="text-secondary">Cash on Delivery</span> Across All Orders.
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 font-medium leading-relaxed">
              We believe in total transparency. Inspect your AI-recommended electronics at your doorstep before making any payment. Zero hidden fees, zero pre-payment risk.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-4 relative z-10 w-full md:w-auto">
            <Link
              href="/products"
              className="w-full sm:w-auto px-8 py-4 btn-orange-gradient text-sm uppercase tracking-wider font-black shadow-xl text-center whitespace-nowrap"
            >
              Shop COD Now
            </Link>
            <Link
              href="/orders"
              className="w-full sm:w-auto px-6 py-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 text-sm font-bold text-center transition-colors whitespace-nowrap"
            >
              Track Your Shipment
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
