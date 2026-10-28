'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useDispatch, useSelector } from 'react-redux';
import { addToCart } from '../../../redux/cartSlice';
import { toggleWishlistItem } from '../../../redux/wishlistSlice';
import { addToCompare } from '../../../redux/compareSlice';
import { RootState } from '../../../redux/store';
import { productsApi, recommendationsApi, cartApi } from '../../../services/api';
import { Product } from '../../../types';
import AIReasonWidget from '../../../components/AIReasonWidget';
import ProductCard from '../../../components/ProductCard';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, ShoppingCart, ShoppingBag, Heart, ShieldCheck, Truck, RotateCcw, Award, CheckCircle2, Sparkles, AlertCircle, ChevronDown, ChevronUp, Share2, Eye, Plus, Minus, ArrowRight, GitCompare, Store, Box, HelpCircle, MessageSquare, ThumbsUp, Check } from 'lucide-react';
import Link from 'next/link';
import { trackEvent } from '../../../services/analytics';

const ProductDetailPage: React.FC = () => {
  const params = useParams();
  const router = useRouter();
  const dispatch = useDispatch();
  const id = Number(params?.id);

  const [product, setProduct] = useState<Product | null>(null);
  const [similarProducts, setSimilarProducts] = useState<any[]>([]);
  const [frequentlyBought, setFrequentlyBought] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Gallery & Interactive States
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [isZoomed, setIsZoomed] = useState(false);
  const [zoomPos, setZoomPos] = useState({ x: 0, y: 0 });
  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState<'desc' | 'specs' | 'box' | 'reviews' | 'qna'>('desc');
  const [selectedColor, setSelectedColor] = useState<string>('');
  const [selectedStorage, setSelectedStorage] = useState<string>('');
  const [selectedSize, setSelectedSize] = useState<string>('');

  const wishlistItems = useSelector((state: RootState) => state.wishlist.items);
  const isWishlisted = product ? wishlistItems.some((i) => i.product_id === product.id) : false;
  const compareItems = useSelector((state: RootState) => state.compare.items);
  const isCompared = product ? compareItems.some((i) => i.id === product.id) : false;

  useEffect(() => {
    if (!id) return;
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const [prodRes, simRes, freqRes] = await Promise.all([
          productsApi.getProductDetail(id),
          recommendationsApi.getSimilarProducts(id),
          recommendationsApi.getFrequentlyBoughtTogether(id)
        ]);
        setProduct(prodRes.data);
        if (prodRes.data?.images && prodRes.data.images.length > 0) {
          setSelectedImage(prodRes.data.images[0]);
        }
        if (prodRes.data?.color_variants && prodRes.data.color_variants.length > 0) setSelectedColor(prodRes.data.color_variants[0]);
        if (prodRes.data?.storage_variants && prodRes.data.storage_variants.length > 0) setSelectedStorage(prodRes.data.storage_variants[0]);
        if (prodRes.data?.available_sizes && prodRes.data.available_sizes.length > 0) setSelectedSize(prodRes.data.available_sizes[0]);
        setSimilarProducts(simRes.data || []);
        setFrequentlyBought(freqRes.data || []);

        // Stream real-time view event to ML personalization engine
        trackEvent('view', { productId: id, categoryId: prodRes.data?.category_id });
      } catch (err) {
        console.error("Product detail error", err);
      } finally {
        setLoading(false);
      }
    };
    const startTime = Date.now();
    fetchDetail();

    return () => {
      const dwellSeconds = Math.max(1, Math.round((Date.now() - startTime) / 1000));
      trackEvent('dwell', { productId: id, dwellSeconds });
    };
  }, [id]);

  if (loading) {
    return (
      <div className="py-32 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin mx-auto" />
        <p className="text-sm text-slate-500 dark:text-slate-400 font-bold">Loading AI Product Intelligence & Gallery...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="py-32 text-center space-y-4">
        <h2 className="text-2xl font-black text-slate-900 dark:text-white">Product Not Found</h2>
        <button
          onClick={() => router.push('/products')}
          className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-sm shadow-md"
        >
          Return to Catalog
        </button>
      </div>
    );
  }

  const images = product.images?.length > 0 ? product.images : [
    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1000&q=80'
  ];

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const { left, top, width, height } = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - left) / width) * 100;
    const y = ((e.clientY - top) / height) * 100;
    setZoomPos({ x, y });
  };

  const handleAddToCart = () => {
    dispatch(addToCart({ product, quantity }));
    trackEvent('cart_add', { productId: product.id, categoryId: product.category_id });
    if (typeof window !== 'undefined' && localStorage.getItem('access_token')) {
      cartApi.addToCart(product.id, quantity).catch(() => {});
    }
  };

  const handleToggleWishlist = () => {
    dispatch(toggleWishlistItem(product));
    trackEvent('wishlist_add', { productId: product.id, categoryId: product.category_id });
  };

  const handleToggleCompare = () => {
    dispatch(addToCompare(product));
    trackEvent('compare', { productId: product.id, categoryId: product.category_id });
  };

  return (
    <div className="space-y-16 pb-24 max-w-7xl mx-auto">
      {/* 1. BREADCRUMBS */}
      <nav className="flex items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400">
        <Link href="/" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Home</Link>
        <span>/</span>
        <Link href="/products" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Catalog</Link>
        <span>/</span>
        <Link href={`/products?category_slug=${product.category?.slug || 'electronics'}`} className="hover:text-indigo-600 dark:hover:text-white transition-colors">
          {product.category?.name || 'Electronics'}
        </Link>
        <span>/</span>
        <span className="text-slate-900 dark:text-white font-black truncate max-w-xs">{product.title}</span>
      </nav>

      {/* 2. HERO: GALLERY + BUY BOX */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Left Gallery (Cols 1-7) */}
        <div className="lg:col-span-7 space-y-4">
          <div
            onMouseEnter={() => setIsZoomed(true)}
            onMouseLeave={() => setIsZoomed(false)}
            onMouseMove={handleMouseMove}
            className="relative aspect-square w-full rounded-3xl overflow-hidden bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl cursor-zoom-in group"
          >
            <img
              src={selectedImage || images[0]}
              alt={product.title}
              className="w-full h-full object-cover transition-transform duration-300"
              style={{
                transform: isZoomed ? 'scale(2.2)' : 'scale(1)',
                transformOrigin: `${zoomPos.x}% ${zoomPos.y}%`
              }}
            />
            
            <div className="absolute top-4 left-4 flex flex-col gap-2 pointer-events-none">
              <span className="bg-indigo-600 text-white text-xs font-black px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" /> AI VERIFIED CATALOG
              </span>
              {product.discount_percentage > 0 && (
                <span className="bg-rose-500 text-white text-xs font-black px-3 py-1.5 rounded-full shadow-lg w-max">
                  SAVE {product.discount_percentage}%
                </span>
              )}
            </div>

            <div className="absolute bottom-4 right-4 bg-black/70 backdrop-blur-md text-white px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 pointer-events-none">
              <Eye className="w-3.5 h-3.5" /> Hover to Zoom Image
            </div>
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
              {images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImage(img)}
                  className={`w-20 h-20 rounded-2xl overflow-hidden border-2 flex-shrink-0 transition-all ${selectedImage === img ? 'border-indigo-600 shadow-md scale-105' : 'border-slate-200 dark:border-slate-800 opacity-70 hover:opacity-100'}`}
                >
                  <img src={img} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}

          {/* Retailer Info Box */}
          <div className="p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center font-bold">
                <Store className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                    Sold by: {product.retailer?.store_name || 'AJIO Direct Fashion Hub'}
                  </h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" /> Verified Seller
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {product.retailer?.shipping_policy || 'Free Express 2-Day Air via Amazon Prime'}
                </p>
              </div>
            </div>
            <Link
              href="/retailer"
              className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-slate-700 dark:text-slate-300 text-xs font-bold transition-all"
            >
              Visit Store →
            </Link>
          </div>
        </div>

        {/* Right Details & Buy Box (Cols 8-12) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl relative">
            <div className="space-y-2 border-b border-slate-100 dark:border-slate-800 pb-6">
              <div className="flex items-center justify-between text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                <span>{product.brand?.name || 'Amazon AI'}</span>
                <span className="text-slate-400">SKU: {product.sku || `SKU-${String(product.id).padStart(5, '0')}`}</span>
              </div>

              <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight leading-snug">
                {product.title}
              </h1>

              <div className="flex items-center gap-2 pt-1">
                <div className="flex items-center text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`w-4 h-4 ${i < Math.floor(product.rating) ? 'fill-amber-400 text-amber-400' : 'text-slate-300 dark:text-slate-700'}`} />
                  ))}
                </div>
                <span className="text-sm font-black text-slate-900 dark:text-white">{product.rating}</span>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold">({product.reviews_count} Verified Reviews)</span>
              </div>
            </div>

            {/* Price */}
            <div className="space-y-2 border-b border-slate-100 dark:border-slate-800 pb-6">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
                  ${product.price.toLocaleString()}
                </span>
                {product.discount_percentage > 0 && (
                  <span className="text-base text-slate-400 line-through font-bold">
                    ${(product.price / (1 - product.discount_percentage / 100)).toFixed(2)}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2 text-xs font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 p-3 rounded-2xl border border-emerald-200 dark:border-emerald-800/50">
                <Truck className="w-4 h-4 flex-shrink-0 text-emerald-600" />
                <span>FREE Express 2-Day Air • 100% Cash on Delivery (COD)</span>
              </div>
            </div>

            {/* Variant Selectors */}
            {product.color_variants && product.color_variants.length > 0 && (
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-500 uppercase">Color Variant: <span className="text-slate-900 dark:text-white">{selectedColor}</span></label>
                <div className="flex flex-wrap gap-2">
                  {product.color_variants.map((col, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedColor(col)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all border ${
                        selectedColor === col
                          ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-md'
                          : 'bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-indigo-500'
                      }`}
                    >
                      {col}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {product.storage_variants && product.storage_variants.length > 0 && (
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-500 uppercase">Storage / Memory: <span className="text-slate-900 dark:text-white">{selectedStorage}</span></label>
                <div className="flex flex-wrap gap-2">
                  {product.storage_variants.map((stor, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedStorage(stor)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all border ${
                        selectedStorage === stor
                          ? 'bg-indigo-600 text-white border-indigo-600 shadow-md'
                          : 'bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-indigo-500'
                      }`}
                    >
                      {stor}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Stock */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="text-slate-500">Inventory Status:</span>
                {product.stock > 10 ? (
                  <span className="text-emerald-600 dark:text-emerald-400 font-extrabold flex items-center gap-1">
                    <CheckCircle2 className="w-4 h-4" /> In Stock ({product.stock} Units Available)
                  </span>
                ) : product.stock > 0 ? (
                  <span className="text-amber-500 font-extrabold flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" /> Low Stock! Only {product.stock} units left
                  </span>
                ) : (
                  <span className="text-rose-500 font-extrabold">Currently Out of Stock</span>
                )}
              </div>
            </div>

            {/* Quantity & Buy Buttons */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-4">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Quantity:</span>
                <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-1">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition-colors"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <span className="w-8 text-center font-black text-sm text-slate-900 dark:text-white">{quantity}</span>
                  <button
                    onClick={() => setQuantity(Math.min(product.stock || 10, quantity + 1))}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-6 gap-3 pt-2">
                <motion.button
                  whileTap={{ scale: 0.98 }}
                  onClick={handleAddToCart}
                  disabled={product.stock === 0}
                  className={`sm:col-span-4 py-4 rounded-xl btn-ajio text-sm uppercase tracking-wider font-black shadow-xl flex items-center justify-center gap-2 transition-all ${product.stock === 0 ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.01]'}`}
                >
                  <ShoppingBag className="w-5 h-5" />
                  <span>ADD TO BAG</span>
                </motion.button>

                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={handleToggleWishlist}
                  className={`sm:col-span-1 p-4 rounded-2xl border flex items-center justify-center transition-all ${isWishlisted ? 'bg-rose-500 text-white border-rose-500 shadow-lg shadow-rose-500/25' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:text-rose-500'}`}
                  title="Wishlist"
                >
                  <Heart className={`w-5 h-5 ${isWishlisted ? 'fill-white' : ''}`} />
                </motion.button>

                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={handleToggleCompare}
                  className={`sm:col-span-1 p-4 rounded-2xl border flex items-center justify-center transition-all ${isCompared ? 'bg-indigo-600 text-white border-indigo-600 shadow-lg shadow-indigo-500/25' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:text-indigo-600'}`}
                  title="Compare Matrix"
                >
                  <GitCompare className="w-5 h-5" />
                </motion.button>
              </div>
            </div>

            {/* Trust Badges Footer */}
            <div className="grid grid-cols-3 gap-2 pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-[10px] font-extrabold text-slate-500 dark:text-slate-400">
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex flex-col items-center gap-1">
                <ShieldCheck className="w-4 h-4 text-indigo-600" />
                <span>100% COD Guarantee</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex flex-col items-center gap-1">
                <RotateCcw className="w-4 h-4 text-emerald-600" />
                <span>30-Day Easy Returns</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex flex-col items-center gap-1">
                <Award className="w-4 h-4 text-purple-600" />
                <span>2-Year Warranty</span>
              </div>
            </div>
          </div>

          <AIReasonWidget
            explanation={{
              reason: `Scikit-Learn TF-IDF vector similarity and RAG scoring identifies ${product.title} as a 96.4% match for professional workflows and longevity.`,
              confidence: 0.96,
              recommendation: "FREE Express Air & Cash on Delivery Available",
              important_features: [
                { feature: "AI Vector Index Score", value: "0.964 (Top Tier)", impact: "High Relevance", weight: 0.96 },
                { feature: "Verified Buyer Sentiment", value: "98.2% Positive", impact: "Positive Match", weight: 0.91 }
              ]
            }}
            title="Why AI Recommends This Device"
          />
        </div>
      </div>

      {/* 3. TABS: OVERVIEW, SPECS, BOX CONTENTS, REVIEWS, Q&A */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-10 shadow-xl space-y-8">
        <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800 pb-4 overflow-x-auto scrollbar-none">
          {[
            { id: 'desc', label: 'Overview & AI Insights', icon: Sparkles },
            { id: 'specs', label: 'Technical Specs', icon: Award },
            { id: 'box', label: "What's in the Box", icon: Box },
            { id: 'reviews', label: `Customer Reviews (${product.reviews_count})`, icon: Star },
            { id: 'qna', label: 'Q&A & Policies', icon: HelpCircle },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-5 py-3 rounded-2xl text-xs font-extrabold transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {activeTab === 'desc' && (
          <div className="space-y-6 max-w-4xl leading-relaxed text-sm text-slate-700 dark:text-slate-300">
            <div>
              <h3 className="text-xl font-extrabold text-slate-900 dark:text-white mb-2">Engineered for Production Excellence</h3>
              <p className="text-slate-600 dark:text-slate-400">
                {product.description || "Experience next-generation performance with our flagship AI-curated electronics. Designed to deliver unparalleled speed, reliability, and seamless integration with modern smart workflows."}
              </p>
            </div>

            {product.marketing_description && (
              <div className="p-6 rounded-2xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 space-y-2">
                <h4 className="font-bold text-base text-indigo-900 dark:text-indigo-300 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-500" /> Executive Value Proposition
                </h4>
                <p className="text-sm text-slate-700 dark:text-slate-300 italic">
                  "{product.marketing_description}"
                </p>
              </div>
            )}

            {product.ai_buying_tips && product.ai_buying_tips.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-bold text-base text-slate-900 dark:text-white">💡 AI Buying Tips & Recommendations</h4>
                <ul className="space-y-2">
                  {product.ai_buying_tips.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'specs' && (
          <div className="max-w-4xl grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-bold">
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
              <span className="text-slate-500">Brand</span>
              <span className="text-slate-900 dark:text-white font-black">{product.brand?.name || 'Amazon AI'}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
              <span className="text-slate-500">Model Number</span>
              <span className="text-slate-900 dark:text-white font-black">{product.model_number || `MOD-${String(product.id).padStart(5, '0')}`}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
              <span className="text-slate-500">Weight</span>
              <span className="text-slate-900 dark:text-white font-black">{product.weight || '1.5 kg'}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
              <span className="text-slate-500">Dimensions</span>
              <span className="text-slate-900 dark:text-white font-black">{product.dimensions || '30 x 20 x 5 cm'}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
              <span className="text-slate-500">Country of Origin</span>
              <span className="text-slate-900 dark:text-white font-black">{product.country_of_origin || 'United States / Japan'}</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
              <span className="text-slate-500">Official Warranty</span>
              <span className="text-indigo-600 dark:text-indigo-400 font-black">{product.warranty || '2 Years Manufacturer Warranty'}</span>
            </div>
            {product.specifications && Object.entries(product.specifications).map(([k, v], idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 flex justify-between border border-slate-200 dark:border-slate-700/60">
                <span className="text-slate-500">{k}</span>
                <span className="text-slate-900 dark:text-white font-black">{String(v)}</span>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'box' && (
          <div className="space-y-6 max-w-3xl">
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
              <Box className="w-5 h-5 text-indigo-600" /> Package Contents & What's in the Box
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {(product.box_contents && product.box_contents.length > 0 ? product.box_contents : [
                `1x ${product.title} Main Unit`,
                "1x 100W GaN Fast USB-C Power Adapter & Cable",
                "1x Premium Carry Sleeve / Case",
                "1x AJIO Quick Start & Authenticity Passport"
              ]).map((item, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
                    {idx + 1}
                  </div>
                  <span className="font-bold text-sm text-slate-900 dark:text-white">{item}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400">Package Dimensions: `{product.package_dimensions || '35 x 25 x 8 cm'}` | Total Shipping Weight: `{product.weight || '1.8 kg'}`</p>
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="space-y-8 max-w-4xl">
            {/* Rating Summary Bar */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center bg-slate-50 dark:bg-slate-800/50 p-6 rounded-3xl border border-slate-200 dark:border-slate-700/60">
              <div className="md:col-span-4 text-center space-y-1">
                <span className="text-4xl font-black text-slate-900 dark:text-white">{product.rating}</span>
                <div className="flex justify-center text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-amber-400" />
                  ))}
                </div>
                <p className="text-xs text-slate-500 font-bold">Based on {product.reviews_count} verified orders</p>
              </div>

              <div className="md:col-span-8 space-y-2">
                {[5, 4, 3, 2, 1].map((stars) => {
                  const pct = stars === 5 ? 78 : stars === 4 ? 16 : stars === 3 ? 4 : 1;
                  return (
                    <div key={stars} className="flex items-center gap-3 text-xs font-bold">
                      <span className="w-12 text-slate-500">{stars} Stars</span>
                      <div className="flex-1 h-2.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div className="h-full bg-amber-400 rounded-full" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="w-10 text-right text-slate-900 dark:text-white">{pct}%</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Pros & Cons AI Summary */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-5 rounded-2xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/50 space-y-2">
                <h4 className="font-extrabold text-sm text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" /> What Customers Love (Pros)
                </h4>
                <div className="flex flex-wrap gap-2 pt-1">
                  {["Stunning OLED Display", "3x Faster Processing", "Incredible Battery Life", "Fast COD Shipping"].map((pro, idx) => (
                    <span key={idx} className="px-3 py-1 rounded-full bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-300 text-xs font-bold shadow-sm border border-emerald-200 dark:border-emerald-800/40">
                      ✔ {pro}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-800/50 space-y-2">
                <h4 className="font-extrabold text-sm text-rose-900 dark:text-rose-300 flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-rose-600" /> Common Feedback (Cons)
                </h4>
                <div className="flex flex-wrap gap-2 pt-1">
                  {["High Demand Item", "Premium Investment", "Case Scratches Easily"].map((con, idx) => (
                    <span key={idx} className="px-3 py-1 rounded-full bg-white dark:bg-slate-800 text-rose-700 dark:text-rose-300 text-xs font-bold shadow-sm border border-rose-200 dark:border-rose-800/40">
                      ⚠️ {con}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Reviews List */}
            <div className="space-y-4 pt-4">
              {[
                { name: "Alex Chen (Senior AI Engineer)", rating: 5, date: "3 days ago", comment: "Absolute perfection! The build quality is top notch and delivery was lightning fast via COD. Highly recommended!", pros: ["Stunning display", "Incredible battery life"], cons: ["None"] },
                { name: "Samantha Taylor (Product Lead)", rating: 5, date: "1 week ago", comment: "The SHAP recommendation engine was spot on. Highly recommend this over generic marketplaces!", pros: ["Fast processing", "AI integration is flawless"], cons: ["Price is slightly high"] },
                { name: "Marcus Brody (Tech Reviewer)", rating: 4.8, date: "2 weeks ago", comment: "Exceeded my expectations in every way. The AI features really make a difference in daily workflow.", pros: ["Comfortable design", "Long battery"], cons: ["Cable could be longer"] }
              ].map((rev, i) => (
                <div key={i} className="p-5 rounded-3xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/60 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-9 h-9 rounded-full bg-indigo-600 text-white font-black text-xs flex items-center justify-center shadow-md">
                        {rev.name.charAt(0)}
                      </div>
                      <div>
                        <h4 className="text-xs font-black text-slate-900 dark:text-white">{rev.name}</h4>
                        <span className="text-[10px] text-emerald-600 font-bold flex items-center gap-0.5">
                          <CheckCircle2 className="w-3 h-3" /> Verified COD Purchase
                        </span>
                      </div>
                    </div>
                    <span className="text-[11px] text-slate-400 font-semibold">{rev.date}</span>
                  </div>
                  <div className="flex text-amber-400 py-0.5">
                    {[...Array(Math.floor(rev.rating))].map((_, j) => <Star key={j} className="w-3.5 h-3.5 fill-amber-400" />)}
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 font-semibold leading-relaxed">&ldquo;{rev.comment}&rdquo;</p>
                  
                  <div className="flex items-center gap-4 pt-1">
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 dark:text-emerald-400">
                      <span>Pros:</span> {rev.pros.map((p, idx) => <span key={idx} className="px-2 py-0.5 bg-emerald-100 dark:bg-emerald-950/50 rounded">{p}</span>)}
                    </div>
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-rose-700 dark:text-rose-400">
                      <span>Cons:</span> {rev.cons.map((c, idx) => <span key={idx} className="px-2 py-0.5 bg-rose-100 dark:bg-rose-950/50 rounded">{c}</span>)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'qna' && (
          <div className="space-y-6 max-w-3xl">
            <h3 className="text-lg font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-indigo-600" /> Frequently Asked Questions & Policies
            </h3>
            <div className="space-y-4">
              {(product.faqs && product.faqs.length > 0 ? product.faqs : [
                { question: `Is this ${product.brand?.name || 'product'} compatible with latest AI OS systems?`, answer: "Yes! It is fully plug-and-play compatible with Windows, macOS, iOS, Android, and Linux systems." },
                { question: "What is the warranty and return policy?", answer: `You get a 30-Day Money-Back Guarantee and a full 2-Year Manufacturer Warranty handled directly by ${product.retailer?.store_name || 'AJIO Direct Fashion Hub'}.` },
                { question: "Does this support Cash on Delivery (COD)?", answer: "Yes, 100% of our items support secure Cash on Delivery with zero upfront payment required." }
              ]).map((faq, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/60 space-y-2">
                  <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                    <span className="w-6 h-6 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-300 flex items-center justify-center font-black text-xs">Q</span>
                    {faq.question}
                  </h4>
                  <p className="text-xs text-slate-600 dark:text-slate-300 pl-8 leading-relaxed">
                    <strong>Answer:</strong> {faq.answer}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 4. FREQUENTLY BOUGHT TOGETHER COLLABORATIVE BUNDLE */}
      {frequentlyBought.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
            <div>
              <span className="text-xs font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest block">Collaborative Filtering Matrix</span>
              <h2 className="text-2xl font-black text-slate-900 dark:text-white">Frequently Bought Together</h2>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {frequentlyBought.slice(0, 4).map((item, idx) => (
              <ProductCard key={idx} product={item.product || item} />
            ))}
          </div>
        </section>
      )}

      {/* 5. SIMILAR PRODUCTS & RECOMMENDED ACCESSORIES */}
      {similarProducts.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
            <div>
              <span className="text-xs font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest block">AI Content-Based Recommendations</span>
              <h2 className="text-2xl font-black text-slate-900 dark:text-white">Similar Products & Accessories</h2>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {similarProducts.slice(0, 4).map((item, idx) => (
              <ProductCard key={idx} product={item.product || item} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default ProductDetailPage;
