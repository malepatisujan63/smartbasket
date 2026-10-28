'use client';

import React from 'react';
import Link from 'next/link';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../redux/store';
import { toggleWishlistItem, clearWishlist } from '../../redux/wishlistSlice';
import { addToCart } from '../../redux/cartSlice';
import ProductCard from '../../components/ProductCard';
import { Heart, Trash2, ShoppingCart, Sparkles, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const WishlistPage: React.FC = () => {
  const dispatch = useDispatch();
  const wishlistItems = useSelector((state: RootState) => state.wishlist.items);

  const handleMoveToCart = (product: any) => {
    dispatch(addToCart({ product, quantity: 1 }));
    dispatch(toggleWishlistItem(product));
  };

  if (wishlistItems.length === 0) {
    return (
      <div className="py-24 text-center space-y-6 max-w-lg mx-auto bg-card border border-border rounded-3xl p-8 shadow-xl">
        <div className="w-20 h-20 rounded-full bg-muted text-red-500 flex items-center justify-center mx-auto shadow-inner">
          <Heart className="w-10 h-10 stroke-[1.5]" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-black text-foreground">Your Wishlist is Empty</h2>
          <p className="text-xs text-muted-foreground font-semibold">
            Save your favorite AI recommendations here to monitor price drops and stock updates!
          </p>
        </div>
        <Link
          href="/products"
          className="inline-flex items-center gap-2 px-8 py-4 btn-orange-gradient text-xs uppercase font-black tracking-wider shadow-lg"
        >
          <span>Discover Products</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-20">
      <div className="flex items-center justify-between border-b border-border pb-6">
        <div>
          <h1 className="text-2xl sm:text-4xl font-black text-foreground tracking-tight flex items-center gap-2.5">
            <Heart className="w-8 h-8 text-red-500 fill-red-500" /> Your Wishlist <span className="text-sm font-extrabold bg-primary/10 text-primary px-3 py-1 rounded-full">({wishlistItems.length} Items)</span>
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground font-semibold mt-1">Manage your saved items and transfer them directly to your shopping bag</p>
        </div>
        <button
          onClick={() => {
            if (confirm('Clear all items from your wishlist?')) dispatch(clearWishlist());
          }}
          className="text-xs font-bold text-red-500 hover:underline flex items-center gap-1"
        >
          <Trash2 className="w-3.5 h-3.5" /> Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {wishlistItems.map((item) => (
          <motion.div layout key={item.id} className="relative flex flex-col justify-between">
            <ProductCard product={item.product} aiMatchScore={95} />
            <button
              onClick={() => handleMoveToCart(item.product)}
              className="w-full mt-3 py-3 btn-blue-gradient text-xs uppercase font-black tracking-wider shadow-md flex items-center justify-center gap-2"
            >
              <ShoppingCart className="w-4 h-4" /> Move to Bag
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default WishlistPage;
