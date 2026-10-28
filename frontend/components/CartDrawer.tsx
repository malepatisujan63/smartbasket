'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../redux/store';
import { closeCartDrawer, updateQuantity, removeFromCart, applyCouponSuccess, clearCart } from '../redux/cartSlice';
import { cartApi } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, X, Trash2, Plus, Minus, ArrowRight, Tag, ShieldCheck, CheckCircle2, Sparkles, Truck } from 'lucide-react';

const CartDrawer: React.FC = () => {
  const router = useRouter();
  const dispatch = useDispatch();
  const { items, subtotal, tax, delivery, discount, total, couponCode, isCartOpen } = useSelector((state: RootState) => state.cart);

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

  const handleCheckout = () => {
    dispatch(closeCartDrawer());
    router.push('/checkout');
  };

  return (
    <AnimatePresence>
      {isCartOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          {/* Glassmorphic Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={() => dispatch(closeCartDrawer())}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
          />

          <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
            {/* Slide-out Drawer Panel */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              className="w-screen max-w-md bg-card border-l border-border text-foreground shadow-2xl flex flex-col h-full relative z-10"
            >
              {/* Header */}
              <div className="p-6 border-b border-border flex items-center justify-between bg-card/90 backdrop-blur-md sticky top-0 z-20">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold shadow-inner">
                    <ShoppingBag className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-lg font-extrabold tracking-tight text-foreground flex items-center gap-1.5">
                      Your Shopping Bag
                    </h2>
                    <p className="text-xs text-muted-foreground font-medium">
                      {items.reduce((acc, i) => acc + i.quantity, 0)} {items.reduce((acc, i) => acc + i.quantity, 0) === 1 ? 'item' : 'items'} in cart
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => dispatch(closeCartDrawer())}
                  className="p-2 rounded-full bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="Close cart drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Free Delivery Bar */}
              <div className="bg-gradient-to-r from-primary/10 via-secondary/10 to-accent/10 px-6 py-2.5 border-b border-border text-xs font-semibold flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-foreground">
                  <Truck className="w-4 h-4 text-secondary" />
                  {subtotal >= 100 ? (
                    <span className="text-accent font-bold">🎉 You unlocked FREE Cash on Delivery shipping!</span>
                  ) : (
                    <span>Add <strong className="text-secondary">${(100 - subtotal).toFixed(2)}</strong> more for FREE shipping</span>
                  )}
                </span>
              </div>

              {/* Cart Items List */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 divide-y divide-border/60 no-scrollbar">
                {items.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center py-16 space-y-4">
                    <div className="w-20 h-20 rounded-full bg-muted/60 flex items-center justify-center text-muted-foreground">
                      <ShoppingBag className="w-10 h-10 stroke-[1.5]" />
                    </div>
                    <div className="space-y-1">
                      <h3 className="text-base font-bold text-foreground">Your bag is empty</h3>
                      <p className="text-xs text-muted-foreground max-w-xs">
                        Explore our AI-curated catalog and discover premium electronics and smart devices.
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        dispatch(closeCartDrawer());
                        router.push('/products');
                      }}
                      className="px-6 py-2.5 btn-ajio text-xs uppercase tracking-wider font-bold shadow-md"
                    >
                      Start Shopping
                    </button>
                  </div>
                ) : (
                  items.map((item) => (
                    <motion.div
                      layout
                      key={item.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      className="pt-4 first:pt-0 flex gap-4 items-center group"
                    >
                      <Link
                        href={`/products/${item.product_id}`}
                        onClick={() => dispatch(closeCartDrawer())}
                        className="w-20 h-20 rounded-xl bg-muted overflow-hidden flex-shrink-0 border border-border shadow-sm relative group-hover:border-primary/50 transition-colors"
                      >
                        <img
                          src={item.product.images?.[0] || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=200&q=80'}
                          alt={item.product.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      </Link>

                      <div className="flex-1 min-w-0">
                        <span className="text-[10px] text-secondary font-bold uppercase tracking-wider block truncate">
                          {item.product.brand?.name || 'Amazon AI'}
                        </span>
                        <Link
                          href={`/products/${item.product_id}`}
                          onClick={() => dispatch(closeCartDrawer())}
                        >
                          <h4 className="text-xs font-bold text-foreground hover:text-primary transition-colors line-clamp-1">
                            {item.product.title}
                          </h4>
                        </Link>
                        <div className="flex items-baseline gap-1.5 mt-1">
                          <span className="text-sm font-black text-foreground">${item.product.price.toFixed(2)}</span>
                          {item.product.discount_percentage > 0 && (
                            <span className="text-[10px] text-muted-foreground line-through">
                              ${(item.product.price / (1 - item.product.discount_percentage / 100)).toFixed(2)}
                            </span>
                          )}
                        </div>

                        {/* Animated Quantity Controls */}
                        <div className="flex items-center justify-between mt-2 pt-1">
                          <div className="flex items-center gap-1.5 bg-muted/80 border border-border rounded-lg p-0.5">
                            <button
                              onClick={() => dispatch(updateQuantity({ id: item.id, quantity: item.quantity - 1 }))}
                              className="w-6 h-6 rounded flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-colors"
                            >
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="w-5 text-center text-xs font-bold text-foreground">{item.quantity}</span>
                            <button
                              onClick={() => dispatch(updateQuantity({ id: item.id, quantity: item.quantity + 1 }))}
                              className="w-6 h-6 rounded flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-colors"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>

                          <div className="flex items-center gap-3">
                            <span className="text-xs font-extrabold text-foreground">
                              ${(item.product.price * item.quantity).toFixed(2)}
                            </span>
                            <button
                              onClick={() => dispatch(removeFromCart(item.id))}
                              className="p-1.5 text-muted-foreground hover:text-red-500 transition-colors rounded-lg hover:bg-red-500/10"
                              title="Remove item"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>

              {/* Footer Summary & Checkout Button */}
              {items.length > 0 && (
                <div className="p-6 border-t border-border bg-card/95 backdrop-blur-lg space-y-4 shadow-2xl">
                  {/* Coupon Input */}
                  <div className="space-y-2">
                    <form onSubmit={handleApplyCoupon} className="flex gap-2">
                      <div className="relative flex-1">
                        <Tag className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <input
                          type="text"
                          value={inputCoupon}
                          onChange={(e) => setInputCoupon(e.target.value)}
                          placeholder="Promo code (e.g. WELCOME10)"
                          className="w-full bg-muted/60 border border-border rounded-xl pl-8 pr-3 py-2 text-xs font-bold uppercase text-foreground placeholder:text-muted-foreground placeholder:normal-case focus:outline-none focus:border-primary transition-colors"
                        />
                      </div>
                      <button
                        type="submit"
                        disabled={couponLoading}
                        className="px-4 py-2 bg-muted hover:bg-muted/80 text-foreground font-bold text-xs rounded-xl transition-all border border-border"
                      >
                        {couponLoading ? '...' : 'Apply'}
                      </button>
                    </form>
                    {couponError && <p className="text-[11px] text-red-500 font-semibold">{couponError}</p>}
                    {couponCode && (
                      <p className="text-[11px] text-accent font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Code &ldquo;{couponCode}&rdquo; applied! Saved ${discount.toFixed(2)}.
                      </p>
                    )}
                  </div>

                  {/* Live Price Updates */}
                  <div className="space-y-2 text-xs font-semibold pt-2 border-t border-border/60">
                    <div className="flex justify-between text-muted-foreground">
                      <span>Subtotal</span>
                      <span className="text-foreground">${subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-muted-foreground">
                      <span>Estimated Tax (8%)</span>
                      <span className="text-foreground">${tax.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-muted-foreground">
                      <span>Shipping</span>
                      <span className={delivery === 0 ? 'text-accent font-bold' : 'text-foreground'}>
                        {delivery === 0 ? 'FREE' : `$${delivery.toFixed(2)}`}
                      </span>
                    </div>
                    {discount > 0 && (
                      <div className="flex justify-between text-accent font-bold">
                        <span>Coupon Discount</span>
                        <span>-${discount.toFixed(2)}</span>
                      </div>
                    )}
                    <div className="pt-2 border-t border-border flex justify-between items-baseline text-base font-black text-foreground">
                      <span>Total</span>
                      <span className="text-xl text-secondary">${total.toFixed(2)}</span>
                    </div>
                  </div>

                  {/* Floating Checkout Button */}
                  <div className="space-y-2 pt-1">
                    <button
                      onClick={handleCheckout}
                      className="w-full py-3.5 btn-ajio flex items-center justify-center gap-2 text-sm tracking-wide uppercase font-black shadow-lg hover:scale-[1.01] transition-transform"
                    >
                      <span>Proceed to Checkout</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>

                    <div className="flex items-center justify-between px-1 text-[11px] text-muted-foreground font-medium">
                      <Link
                        href="/cart"
                        onClick={() => dispatch(closeCartDrawer())}
                        className="hover:text-primary transition-colors underline decoration-dotted"
                      >
                        View Full Bag
                      </Link>
                      <span className="flex items-center gap-1 text-accent font-bold">
                        <ShieldCheck className="w-3.5 h-3.5" /> Cash on Delivery Only
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default CartDrawer;
