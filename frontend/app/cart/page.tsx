'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../redux/store';
import { updateQuantity, removeFromCart, applyCouponSuccess, clearCart } from '../../redux/cartSlice';
import { cartApi } from '../../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Trash2, Plus, Minus, ArrowRight, Tag, ShieldCheck, CheckCircle2, Sparkles, Truck, ArrowLeft } from 'lucide-react';

const CartPage: React.FC = () => {
  const router = useRouter();
  const dispatch = useDispatch();
  const { items, subtotal, tax, delivery, discount, total, couponCode } = useSelector((state: RootState) => state.cart);

  const [inputCoupon, setInputCoupon] = useState('');
  const [couponError, setCouponError] = useState('');
  const [couponLoading, setCouponLoading] = useState(false);

  const handleApplyCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputCoupon.trim()) return;
    setCouponLoading(true);
    setCouponError('');
    try {
      const res = await cartApi.applyCoupon(inputCoupon.trim(), subtotal);
      dispatch(applyCouponSuccess(res.data));
      setInputCoupon('');
    } catch (err: any) {
      setCouponError(err.response?.data?.detail || 'Invalid or expired coupon code');
    } finally {
      setCouponLoading(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="py-24 max-w-4xl mx-auto text-center space-y-6">
        <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center mx-auto text-muted-foreground shadow-inner">
          <ShoppingBag className="w-12 h-12 stroke-[1.5]" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl sm:text-3xl font-black text-foreground">Your Shopping Bag is Empty</h1>
          <p className="text-sm text-muted-foreground font-semibold max-w-md mx-auto">
            Discover our AI-curated electronics, workstations, and smart home appliances with 100% Cash on Delivery protection.
          </p>
        </div>
        <Link
          href="/products"
          className="inline-flex items-center gap-2 px-8 py-4 btn-ajio text-sm uppercase tracking-wider font-black shadow-xl"
        >
          <span>Explore AJIO Catalog</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-10 pb-24">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <button onClick={() => router.push('/products')} className="text-xs font-bold text-secondary hover:underline flex items-center gap-1 mb-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Continue Shopping
          </button>
          <h1 className="text-2xl sm:text-4xl font-black text-foreground tracking-tight flex items-center gap-2">
            Shopping Bag <span className="text-sm font-extrabold bg-primary/10 text-primary px-3 py-1 rounded-full">({items.reduce((a, b) => a + b.quantity, 0)} items)</span>
          </h1>
        </div>
        <button
          onClick={() => {
            if (confirm('Clear all items from your bag?')) dispatch(clearCart());
          }}
          className="text-xs font-extrabold text-red-500 hover:underline self-start sm:self-center"
        >
          Empty Bag
        </button>
      </div>

      {/* Main Layout: Cart Items + Summary Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Cart Items List (Cols 1-7) */}
        <div className="lg:col-span-7 space-y-4">
          {items.map((item) => (
            <motion.div
              layout
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-card border border-border rounded-3xl p-5 sm:p-6 shadow-md hover:shadow-lg transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 group"
            >
              <div className="flex items-center gap-4 flex-1">
                <Link
                  href={`/products/${item.product_id}`}
                  className="w-24 h-24 rounded-2xl bg-muted overflow-hidden flex-shrink-0 border border-border shadow-inner relative group-hover:border-primary/50 transition-colors"
                >
                  <img
                    src={item.product.images?.[0] || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=300&q=80'}
                    alt={item.product.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </Link>

                <div className="space-y-1">
                  <span className="text-[10px] font-black text-secondary uppercase tracking-wider block">
                    {item.product.brand?.name || 'Amazon AI Flagship'}
                  </span>
                  <Link href={`/products/${item.product_id}`}>
                    <h3 className="text-sm font-extrabold text-foreground hover:text-primary transition-colors line-clamp-2">
                      {item.product.title}
                    </h3>
                  </Link>
                  <p className="text-xs text-muted-foreground font-semibold">Unit Price: ${item.product.price.toFixed(2)}</p>
                  <span className="inline-block text-[10px] font-extrabold text-accent bg-accent/10 px-2 py-0.5 rounded-full mt-1">
                    ✓ Eligible for Cash on Delivery
                  </span>
                </div>
              </div>

              {/* Quantity Controls & Price */}
              <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto pt-4 sm:pt-0 border-t sm:border-t-0 border-border gap-4">
                <div className="flex items-center gap-1.5 bg-muted border border-border rounded-xl p-1">
                  <button
                    onClick={() => dispatch(updateQuantity({ id: item.id, quantity: item.quantity - 1 }))}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-colors font-bold"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <span className="w-8 text-center text-xs font-black text-foreground">{item.quantity}</span>
                  <button
                    onClick={() => dispatch(updateQuantity({ id: item.id, quantity: item.quantity + 1 }))}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-colors font-bold"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                <div className="text-right flex items-center gap-4">
                  <span className="text-lg font-black text-foreground">
                    ${(item.product.price * item.quantity).toFixed(2)}
                  </span>
                  <button
                    onClick={() => dispatch(removeFromCart(item.id))}
                    className="p-2 text-muted-foreground hover:text-red-500 transition-colors rounded-xl hover:bg-red-500/10"
                    title="Remove item"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Premium Order Summary Card (Cols 8-12) */}
        <div className="lg:col-span-5 space-y-6 sticky top-24">
          <div className="bg-card border-2 border-primary/30 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

            <h2 className="text-lg font-black text-foreground uppercase tracking-wider border-b border-border pb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-secondary" /> Order Summary
            </h2>

            {/* Free Shipping Banner */}
            <div className="p-3.5 rounded-2xl bg-muted/60 border border-border text-xs font-semibold flex items-center gap-2">
              <Truck className="w-5 h-5 text-secondary flex-shrink-0" />
              {subtotal >= 100 ? (
                <span className="text-accent font-extrabold">🎉 You unlocked FREE Priority COD Shipping!</span>
              ) : (
                <span className="text-foreground">Add <strong className="text-secondary">${(100 - subtotal).toFixed(2)}</strong> more for FREE shipping</span>
              )}
            </div>

            {/* Coupon Box */}
            <div className="space-y-2 pt-2">
              <form onSubmit={handleApplyCoupon} className="flex gap-2">
                <div className="relative flex-1">
                  <Tag className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    value={inputCoupon}
                    onChange={(e) => setInputCoupon(e.target.value)}
                    placeholder="Promo code (e.g. WELCOME10)"
                    className="w-full bg-muted/80 border border-border rounded-xl pl-9 pr-3 py-2.5 text-xs font-bold uppercase text-foreground placeholder:text-muted-foreground placeholder:normal-case focus:outline-none focus:border-primary"
                  />
                </div>
                <button
                  type="submit"
                  disabled={couponLoading}
                  className="px-5 py-2.5 bg-muted hover:bg-muted/80 text-foreground font-black text-xs uppercase tracking-wider rounded-xl transition-all border border-border"
                >
                  {couponLoading ? '...' : 'Apply'}
                </button>
              </form>
              {couponError && <p className="text-xs text-red-500 font-bold">{couponError}</p>}
              {couponCode && (
                <p className="text-xs text-accent font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Promo code &ldquo;{couponCode}&rdquo; applied (-${discount.toFixed(2)})
                </p>
              )}
            </div>

            {/* Price Breakdown */}
            <div className="space-y-3 text-sm font-semibold pt-4 border-t border-border">
              <div className="flex justify-between text-muted-foreground">
                <span>Subtotal ({items.reduce((a, b) => a + b.quantity, 0)} items)</span>
                <span className="text-foreground font-bold">${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Estimated Tax (8%)</span>
                <span className="text-foreground font-bold">${tax.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Priority Shipping</span>
                <span className={delivery === 0 ? 'text-accent font-extrabold' : 'text-foreground font-bold'}>
                  {delivery === 0 ? 'FREE' : `$${delivery.toFixed(2)}`}
                </span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between text-accent font-extrabold">
                  <span>Coupon Discount</span>
                  <span>-${discount.toFixed(2)}</span>
                </div>
              )}
              <div className="pt-4 border-t border-border flex justify-between items-baseline text-lg font-black text-foreground">
                <span>Total Payable</span>
                <span className="text-2xl text-secondary">${total.toFixed(2)}</span>
              </div>
            </div>

            {/* Checkout Button */}
            <div className="space-y-3 pt-2">
              <button
                onClick={() => router.push('/checkout')}
                className="w-full py-4 btn-ajio text-sm uppercase tracking-wider font-black shadow-xl flex items-center justify-center gap-2 group hover:scale-[1.01] transition-transform"
              >
                <span>Proceed to Secure Checkout</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>

              <div className="p-3 rounded-2xl bg-muted/60 border border-border text-center text-xs font-bold text-accent flex items-center justify-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                <span>100% Cash on Delivery (COD) Protection</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
