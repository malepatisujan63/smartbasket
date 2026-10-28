'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useDispatch, useSelector } from 'react-redux';
import { addToCart } from '../redux/cartSlice';
import { toggleWishlistItem } from '../redux/wishlistSlice';
import { RootState } from '../redux/store';
import { Product, PredictionExplanation } from '../types';
import { motion } from 'framer-motion';
import { Star, ShoppingBag, Heart, Sparkles, Check, AlertCircle, TrendingUp, Zap, ShieldCheck, Eye } from 'lucide-react';
import { trackEvent } from '../services/analytics';
import { cartApi } from '../services/api';

interface ProductCardProps {
  product: Product;
  explanation?: PredictionExplanation;
  aiMatchScore?: number;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, explanation, aiMatchScore = 95 }) => {
  const dispatch = useDispatch();
  const wishlistItems = useSelector((state: RootState) => state.wishlist.items);
  const isWishlisted = wishlistItems.some((item) => item.product_id === product.id);

  const [imgSrc, setImgSrc] = useState(
    product.images && product.images.length > 0
      ? product.images[0]
      : 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80'
  );

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dispatch(addToCart({ product, quantity: 1 }));
    trackEvent('cart_add', { productId: product.id, categoryId: product.category_id });
    if (typeof window !== 'undefined' && localStorage.getItem('access_token')) {
      cartApi.addToCart(product.id, 1).catch(() => {});
    }
  };

  const handleToggleWishlist = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dispatch(toggleWishlistItem(product));
    trackEvent('wishlist_add', { productId: product.id, categoryId: product.category_id });
  };

  const handleCardClick = () => {
    trackEvent('click', { productId: product.id, categoryId: product.category_id });
  };

  return (
    <motion.div
      whileHover={{ y: -8 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="group relative glass-card p-4 flex flex-col justify-between h-full hover-lift-glow bg-card/90 backdrop-blur-md"
    >
      {/* Top Badges */}
      <div className="absolute top-3.5 left-3.5 right-3.5 z-10 flex items-center justify-between pointer-events-none">
        {/* AI Match / Discount Badge */}
        <div className="flex flex-wrap items-center gap-1.5 pointer-events-auto">
          {explanation ? (
            <div className="flex flex-col gap-1 items-start">
              <span className="bg-gradient-to-r from-primary to-blue-600 text-white text-[10px] font-black px-2.5 py-1 rounded-full shadow-md flex items-center gap-1 border border-white/20">
                <Sparkles className="w-3 h-3 fill-secondary text-secondary" /> AI MATCH {aiMatchScore}%
              </span>
              {explanation.recommendation && (
                <span className="bg-secondary/90 text-white text-[9px] font-black px-2 py-0.5 rounded-full shadow-sm flex items-center gap-1 backdrop-blur-md border border-white/20">
                  <Zap className="w-2.5 h-2.5 text-amber-300" /> {explanation.recommendation}
                </span>
              )}
            </div>
          ) : product.discount_percentage > 0 ? (
            <span className="bg-red-500 text-white text-[10px] font-black px-2.5 py-0.5 rounded-full shadow-sm">
              -{product.discount_percentage}% OFF
            </span>
          ) : (
            <span className="bg-muted text-muted-foreground text-[10px] font-bold px-2 py-0.5 rounded-full border border-border">
              AI INDEXED
            </span>
          )}
        </div>

        {/* Wishlist Button */}
        <motion.button
          whileTap={{ scale: 0.8 }}
          whileHover={{ scale: 1.1 }}
          onClick={handleToggleWishlist}
          className={`p-2 rounded-full backdrop-blur-md transition-all pointer-events-auto shadow-md ${isWishlisted ? 'bg-red-500 text-white shadow-red-500/30' : 'bg-card/90 text-muted-foreground hover:text-red-500 border border-border'}`}
          title={isWishlisted ? 'Remove from Wishlist' : 'Add to Wishlist'}
        >
          <Heart className={`w-4 h-4 ${isWishlisted ? 'fill-white' : ''}`} />
        </motion.button>
      </div>

      {/* Product Image Link with Smooth Zoom */}
      <Link href={`/products/${product.id}`} onClick={handleCardClick} className="block relative aspect-square w-full rounded-2xl overflow-hidden bg-muted mb-3 border border-border/60 shadow-inner group-hover:border-primary/40 transition-colors">
        <img
          src={imgSrc}
          alt={product.title}
          onError={() => setImgSrc('https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80')}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Quick Stock Status Badge */}
        {product.stock <= 5 && product.stock > 0 && (
          <div className="absolute bottom-2.5 left-2.5 bg-amber-500 text-white font-black text-[9px] px-2.5 py-0.5 rounded-full flex items-center gap-1 shadow-md">
            <AlertCircle className="w-3 h-3" /> Only {product.stock} left!
          </div>
        )}
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-black/70 backdrop-blur-[2px] flex items-center justify-center font-black text-xs text-red-400 uppercase tracking-widest">
            Out of Stock
          </div>
        )}

        {/* Hover Quick View Overlay */}
        <div className="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <span className="p-2 rounded-xl bg-card/90 backdrop-blur-md text-foreground text-xs font-bold flex items-center gap-1 shadow-lg border border-border">
            <Eye className="w-3.5 h-3.5 text-primary" /> View
          </span>
        </div>
      </Link>

      {/* Product Information */}
      <div className="flex flex-col flex-1 justify-between">
        <div>
          {/* Category & Brand */}
          <div className="flex items-center justify-between text-[11px] text-muted-foreground font-bold mb-1">
            <span className="truncate max-w-[120px]">{product.category?.name || 'Fashion'}</span>
            <span className="text-[#d5a249] font-extrabold uppercase tracking-wider">{product.brand?.name || 'AJIO LUXE'}</span>
          </div>

          {/* Title */}
          <Link href={`/products/${product.id}`} onClick={handleCardClick}>
            <h3 className="text-sm font-extrabold text-foreground group-hover:text-primary transition-colors line-clamp-2 mb-2 leading-snug">
              {product.title}
            </h3>
          </Link>

          {/* Star Rating */}
          <div className="flex items-center gap-1.5 mb-2.5">
            <div className="flex items-center text-amber-400">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-3.5 h-3.5 ${i < Math.floor(product.rating) ? 'fill-amber-400 text-amber-400' : 'text-muted-foreground/30'}`}
                />
              ))}
            </div>
            <span className="text-xs font-black text-foreground">{product.rating}</span>
            <span className="text-[11px] text-muted-foreground font-semibold">({product.reviews_count})</span>
          </div>

          {/* Explainable AI Reason Snippet (if available) */}
          {explanation && (
            <div className="mb-3 p-2.5 rounded-xl bg-primary/5 border border-primary/20 text-[11px]">
              <div className="flex items-center justify-between gap-1 mb-1">
                <span className="flex items-center gap-1 text-primary font-black">
                  <Sparkles className="w-3 h-3 text-secondary" /> Why AI Recommends:
                </span>
                {explanation.recommendation && (
                  <span className="text-[9px] font-black text-secondary bg-secondary/15 px-2 py-0.5 rounded-full border border-secondary/20 truncate max-w-[140px]">
                    {explanation.recommendation}
                  </span>
                )}
              </div>
              <p className="line-clamp-2 text-muted-foreground text-[10px] leading-tight font-semibold">
                {explanation.reason}
              </p>
            </div>
          )}
        </div>

        {/* Price & Add to Cart */}
        <div className="pt-3 border-t border-border/80 flex items-center justify-between mt-2">
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg font-black text-foreground">${product.price.toFixed(2)}</span>
              {product.discount_percentage > 0 && (
                <span className="text-xs text-muted-foreground line-through font-semibold">
                  ${(product.price / (1 - product.discount_percentage / 100)).toFixed(2)}
                </span>
              )}
            </div>
            <span className="text-[10px] text-accent font-extrabold flex items-center gap-0.5 mt-0.5">
              <Check className="w-3 h-3 stroke-[3]" /> FREE COD Delivery
            </span>
          </div>

          <motion.button
            whileTap={{ scale: 0.92 }}
            whileHover={{ scale: 1.05 }}
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className={`p-2.5 px-3.5 rounded-lg font-black text-xs flex items-center gap-1.5 transition-all shadow-md ${product.stock === 0 ? 'bg-muted text-muted-foreground cursor-not-allowed' : 'btn-ajio uppercase tracking-wider'}`}
            title="Add to Bag & Open Cart Drawer"
          >
            <ShoppingBag className="w-4 h-4" />
            <span className="hidden sm:inline">Add to Bag</span>
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default ProductCard;
