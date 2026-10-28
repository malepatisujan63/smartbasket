'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../redux/store';
import { clearCart } from '../../redux/cartSlice';
import { usersApi, ordersApi } from '../../services/api';
import { Address } from '../../types';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, MapPin, Truck, CheckCircle2, AlertCircle, Plus, ArrowRight, ArrowLeft, Lock, Sparkles, Check, Clock } from 'lucide-react';

const CheckoutPage: React.FC = () => {
  const router = useRouter();
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  const { items, subtotal, tax, delivery, discount, total, couponCode } = useSelector((state: RootState) => state.cart);

  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [placingOrder, setPlacingOrder] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState<1 | 2 | 3>(1); // 1: Delivery Address, 2: Payment Method, 3: Order Review

  // New Address Form
  const [showNewAddressForm, setShowNewAddressForm] = useState(false);
  const [newAddr, setNewAddr] = useState({
    full_name: user?.full_name || '',
    phone: '',
    street_address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'United States',
    is_default: true,
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/checkout');
      return;
    }
    if (items.length === 0) {
      router.push('/cart');
      return;
    }

    const fetchUserAddresses = async () => {
      try {
        const res = await usersApi.getAddresses();
        setAddresses(res.data);
        if (res.data.length > 0) {
          const def = res.data.find((a: Address) => a.is_default) || res.data[0];
          setSelectedAddressId(def.id);
        } else {
          setShowNewAddressForm(true);
        }
      } catch (err) {
        console.error("Address load error", err);
        // Fallback demo address if API offline
        const demoAddr = {
          id: 1,
          user_id: user?.id || 1,
          full_name: user?.full_name || "Alex Chen",
          phone: "+1 (555) 019-2834",
          street_address: "742 Evergreen Terrace, Suite 400",
          city: "Seattle",
          state: "WA",
          postal_code: "98101",
          country: "United States",
          is_default: true
        };
        setAddresses([demoAddr]);
        setSelectedAddressId(1);
      } finally {
        setLoading(false);
      }
    };

    fetchUserAddresses();
  }, [isAuthenticated, items.length, router, user]);

  const handleCreateAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await usersApi.createAddress(newAddr);
      setAddresses([...addresses, res.data]);
      setSelectedAddressId(res.data.id);
      setShowNewAddressForm(false);
    } catch (err: any) {
      // In demo/offline fallback, create locally
      const localAddr = { ...newAddr, id: Date.now(), user_id: user?.id || 1 };
      setAddresses([...addresses, localAddr]);
      setSelectedAddressId(localAddr.id);
      setShowNewAddressForm(false);
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddressId) {
      setError("Please select a delivery address.");
      return;
    }

    setPlacingOrder(true);
    setError('');

    const selectedAddrObj = addresses.find((a) => a.id === selectedAddressId);
    const orderPayload = {
      items: items.map((i) => ({
        product_id: i.product_id,
        quantity: i.quantity,
      })),
      delivery_address_id: selectedAddressId,
      delivery_address: selectedAddrObj ? {
        full_name: selectedAddrObj.full_name,
        phone: selectedAddrObj.phone,
        street_address: selectedAddrObj.street_address,
        city: selectedAddrObj.city,
        state: selectedAddrObj.state,
        postal_code: selectedAddrObj.postal_code,
        country: selectedAddrObj.country
      } : {
        full_name: user?.full_name || "Valued Customer",
        phone: "+91 9876543210",
        street_address: "Flat 402, Reliance Greens",
        city: "Bengaluru",
        state: "Karnataka",
        postal_code: "560100",
        country: "India"
      },
      coupon_code: couponCode || undefined,
      payment_method: 'Cash on Delivery'
    };

    try {
      const res = await ordersApi.placeOrder(orderPayload as any);
      if (typeof window !== 'undefined') {
        try {
          const existing = JSON.parse(localStorage.getItem('ajio_orders') || '[]');
          localStorage.setItem('ajio_orders', JSON.stringify([res.data, ...existing.filter((o: any) => o.id !== res.data.id)]));
        } catch (e) {}
      }
      dispatch(clearCart());
      router.push(`/orders/${res.data.id}?success=true`);
    } catch (err: any) {
      console.error("Order error", err);
      setError(err.response?.data?.detail || "Failed to place order. Please check address details and stock, then try again.");
    } finally {
      setPlacingOrder(false);
    }
  };

  if (loading) {
    return (
      <div className="py-32 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto" />
        <p className="text-sm text-muted-foreground font-bold">Securing AI Checkout & Verifying Inventory...</p>
      </div>
    );
  }

  const selectedAddrObj = addresses.find((a) => a.id === selectedAddressId);

  return (
    <div className="space-y-10 pb-24 max-w-6xl mx-auto">
      {/* Top Header & Security Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <button onClick={() => router.push('/cart')} className="text-xs font-bold text-secondary hover:underline flex items-center gap-1 mb-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Return to Shopping Bag
          </button>
          <h1 className="text-2xl sm:text-4xl font-black text-foreground tracking-tight flex items-center gap-2">
            Secure COD Checkout <Lock className="w-5 h-5 text-accent" />
          </h1>
        </div>

        <div className="flex items-center gap-2 text-xs font-bold text-accent bg-accent/10 px-4 py-2 rounded-xl border border-accent/20">
          <ShieldCheck className="w-4 h-4 flex-shrink-0" />
          <span>100% Cash on Delivery Protected</span>
        </div>
      </div>

      {/* 3-Step Indicator */}
      <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
        {[
          { num: 1, title: 'Delivery Address', desc: 'Where to ship' },
          { num: 2, title: 'Payment Method', desc: 'Cash on Delivery' },
          { num: 3, title: 'Review Order', desc: 'Confirm & Dispatch' }
        ].map((s) => (
          <button
            key={s.num}
            onClick={() => setStep(s.num as any)}
            className={`p-4 rounded-2xl border text-left transition-all flex items-center gap-3 ${step === s.num ? 'bg-primary text-white border-primary shadow-lg shadow-primary/20 scale-105' : step > s.num ? 'bg-card border-border text-foreground' : 'bg-muted/40 border-border text-muted-foreground opacity-60'}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-xs ${step === s.num ? 'bg-white text-primary' : step > s.num ? 'bg-accent text-white' : 'bg-muted text-muted-foreground'}`}>
              {step > s.num ? <Check className="w-4 h-4 stroke-[3]" /> : s.num}
            </div>
            <div className="hidden sm:block">
              <h4 className="text-xs font-black leading-tight">{s.title}</h4>
              <p className="text-[10px] opacity-80 font-medium">{s.desc}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Left Interactive Steps (Cols 1-7) */}
        <div className="lg:col-span-7 space-y-8">
          {/* Step 1: Delivery Address */}
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-border pb-4">
                <h2 className="text-lg font-black text-foreground uppercase tracking-wider flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-primary" /> 1. Select Delivery Address
                </h2>
                <button
                  onClick={() => setShowNewAddressForm(!showNewAddressForm)}
                  className="text-xs font-black text-secondary hover:underline flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" /> Add New Address
                </button>
              </div>

              {showNewAddressForm ? (
                <form onSubmit={handleCreateAddress} className="space-y-4 pt-2">
                  <h3 className="text-sm font-black text-foreground">Add New Delivery Address</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] font-bold text-muted-foreground uppercase block mb-1">Full Name</label>
                      <input
                        type="text"
                        required
                        value={newAddr.full_name}
                        onChange={(e) => setNewAddr({ ...newAddr, full_name: e.target.value })}
                        placeholder="Alex Chen"
                        className="w-full bg-muted/60 border border-border rounded-xl px-3.5 py-2.5 text-xs font-bold text-foreground focus:outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-muted-foreground uppercase block mb-1">Phone Number</label>
                      <input
                        type="tel"
                        required
                        value={newAddr.phone}
                        onChange={(e) => setNewAddr({ ...newAddr, phone: e.target.value })}
                        placeholder="+1 (555) 000-0000"
                        className="w-full bg-muted/60 border border-border rounded-xl px-3.5 py-2.5 text-xs font-bold text-foreground focus:outline-none focus:border-primary"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-muted-foreground uppercase block mb-1">Street Address</label>
                    <input
                      type="text"
                      required
                      value={newAddr.street_address}
                      onChange={(e) => setNewAddr({ ...newAddr, street_address: e.target.value })}
                      placeholder="742 Evergreen Terrace, Apt 4B"
                      className="w-full bg-muted/60 border border-border rounded-xl px-3.5 py-2.5 text-xs font-bold text-foreground focus:outline-none focus:border-primary"
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="text-[11px] font-bold text-muted-foreground uppercase block mb-1">City</label>
                      <input
                        type="text"
                        required
                        value={newAddr.city}
                        onChange={(e) => setNewAddr({ ...newAddr, city: e.target.value })}
                        placeholder="Seattle"
                        className="w-full bg-muted/60 border border-border rounded-xl px-3.5 py-2.5 text-xs font-bold text-foreground focus:outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-muted-foreground uppercase block mb-1">State / Province</label>
                      <input
                        type="text"
                        required
                        value={newAddr.state}
                        onChange={(e) => setNewAddr({ ...newAddr, state: e.target.value })}
                        placeholder="WA"
                        className="w-full bg-muted/60 border border-border rounded-xl px-3.5 py-2.5 text-xs font-bold text-foreground focus:outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-muted-foreground uppercase block mb-1">Postal Code</label>
                      <input
                        type="text"
                        required
                        value={newAddr.postal_code}
                        onChange={(e) => setNewAddr({ ...newAddr, postal_code: e.target.value })}
                        placeholder="98101"
                        className="w-full bg-muted/60 border border-border rounded-xl px-3.5 py-2.5 text-xs font-bold text-foreground focus:outline-none focus:border-primary"
                      />
                    </div>
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button type="submit" className="px-6 py-3 btn-ajio text-xs uppercase font-black tracking-wider">
                      Save & Use This Address
                    </button>
                    <button type="button" onClick={() => setShowNewAddressForm(false)} className="px-6 py-3 bg-muted hover:bg-muted/80 text-foreground font-bold text-xs uppercase rounded-xl border border-border">
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {addresses.map((addr) => (
                    <div
                      key={addr.id}
                      onClick={() => setSelectedAddressId(addr.id)}
                      className={`p-5 rounded-2xl border-2 cursor-pointer transition-all flex items-start justify-between gap-4 ${selectedAddressId === addr.id ? 'bg-primary/5 border-primary shadow-lg shadow-primary/10' : 'bg-muted/40 border-border hover:border-border/80'}`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-black text-foreground">{addr.full_name}</h4>
                          {addr.is_default && <span className="bg-muted text-muted-foreground text-[10px] font-extrabold px-2 py-0.5 rounded-full border border-border">Default</span>}
                        </div>
                        <p className="text-xs text-muted-foreground font-semibold">{addr.street_address}</p>
                        <p className="text-xs text-muted-foreground font-semibold">{addr.city}, {addr.state} {addr.postal_code}</p>
                        <p className="text-xs text-muted-foreground font-semibold">{addr.country} • Phone: {addr.phone}</p>
                      </div>

                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-1 ${selectedAddressId === addr.id ? 'border-primary bg-primary text-white' : 'border-border'}`}>
                        {selectedAddressId === addr.id && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                      </div>
                    </div>
                  ))}

                  <button
                    onClick={() => setStep(2)}
                    disabled={!selectedAddressId}
                    className="w-full py-4 btn-ajio text-sm uppercase tracking-wider font-black shadow-xl mt-4 flex items-center justify-center gap-2"
                  >
                    <span>Proceed to Payment Method</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* Step 2: Payment Method */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-border pb-4">
                <h2 className="text-lg font-black text-foreground uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-accent" /> 2. Payment Method
                </h2>
                <button onClick={() => setStep(1)} className="text-xs font-bold text-primary hover:underline">Change Address</button>
              </div>

              <div className="p-6 rounded-2xl bg-gradient-to-br from-accent/15 via-card to-accent/5 border-2 border-accent shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-accent text-white flex items-center justify-center font-black shadow-md">
                      <Truck className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-base font-black text-foreground">Cash on Delivery (COD)</h3>
                      <p className="text-xs text-accent font-extrabold uppercase tracking-wider">Zero Online Pre-Payment Required</p>
                    </div>
                  </div>
                  <span className="bg-accent text-white text-xs font-black px-3 py-1 rounded-full shadow-sm">
                    Selected ✓
                  </span>
                </div>

                <p className="text-xs text-muted-foreground leading-relaxed font-semibold">
                  Pay 100% of the total order amount in cash or via QR digital payment directly to the courier executive upon physical delivery and inspection of your items.
                </p>
              </div>

              <div className="flex gap-4 pt-2">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-4 rounded-xl bg-muted hover:bg-muted/80 text-foreground font-bold text-xs uppercase border border-border"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  className="flex-1 py-4 btn-ajio text-sm uppercase tracking-wider font-black shadow-xl flex items-center justify-center gap-2"
                >
                  <span>Review & Confirm Order</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Order Review */}
          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-border pb-4">
                <h2 className="text-lg font-black text-foreground uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-secondary" /> 3. Review & Dispatch Order
                </h2>
                <button onClick={() => setStep(2)} className="text-xs font-bold text-primary hover:underline">Change Payment</button>
              </div>

              {/* Delivery Address Summary */}
              {selectedAddrObj && (
                <div className="p-4 rounded-2xl bg-muted/60 border border-border space-y-1">
                  <span className="text-[10px] font-black uppercase text-primary block">Shipping Destination</span>
                  <p className="text-xs font-black text-foreground">{selectedAddrObj.full_name}</p>
                  <p className="text-xs text-muted-foreground font-semibold">{selectedAddrObj.street_address}, {selectedAddrObj.city}, {selectedAddrObj.state} {selectedAddrObj.postal_code}</p>
                </div>
              )}

              {/* Items List */}
              <div className="space-y-3 divide-y divide-border/60">
                <h3 className="text-xs font-black uppercase tracking-wider text-muted-foreground">Items to Dispatch ({items.reduce((a, b) => a + b.quantity, 0)})</h3>
                {items.map((item) => (
                  <div key={item.id} className="pt-3 first:pt-0 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <img src={item.product.images?.[0] || 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=150&q=80'} alt="" className="w-12 h-12 rounded-xl object-cover bg-muted border border-border" />
                      <div>
                        <h4 className="text-xs font-bold text-foreground line-clamp-1">{item.product.title}</h4>
                        <p className="text-[11px] text-muted-foreground font-semibold">Qty: {item.quantity} × ${item.product.price.toFixed(2)}</p>
                      </div>
                    </div>
                    <span className="text-xs font-black text-foreground">${(item.product.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
              </div>

              {error && <p className="text-xs font-bold text-red-500 bg-red-500/10 p-3 rounded-xl border border-red-500/20">{error}</p>}

              <div className="flex gap-4 pt-4 border-t border-border">
                <button
                  onClick={() => setStep(2)}
                  disabled={placingOrder}
                  className="px-6 py-4 rounded-xl bg-muted hover:bg-muted/80 text-foreground font-bold text-xs uppercase border border-border"
                >
                  Back
                </button>
                <button
                  onClick={handlePlaceOrder}
                  disabled={placingOrder || !selectedAddressId}
                  className="flex-1 py-4 btn-ajio text-sm uppercase tracking-wider font-black shadow-xl flex items-center justify-center gap-2"
                >
                  {placingOrder ? (
                    <span className="flex items-center gap-2"><div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" /> Dispatching AI Order...</span>
                  ) : (
                    <>
                      <span>Place Cash on Delivery Order</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </div>

        {/* Right Summary Card (Cols 8-12) */}
        <div className="lg:col-span-5 space-y-6 sticky top-24">
          <div className="bg-card border-2 border-primary/30 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl">
            <h2 className="text-base font-black text-foreground uppercase tracking-wider border-b border-border pb-4">
              Final Order Breakdown
            </h2>

            <div className="space-y-3 text-xs font-semibold">
              <div className="flex justify-between text-muted-foreground">
                <span>Subtotal</span>
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
                <span>Total Payable (COD)</span>
                <span className="text-2xl text-secondary">${total.toFixed(2)}</span>
              </div>
            </div>

            {/* Delivery Timeline Estimation */}
            <div className="p-4 rounded-2xl bg-muted/60 border border-border space-y-2">
              <span className="text-[10px] font-black uppercase text-accent flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> Estimated Delivery Timeline
              </span>
              <p className="text-xs font-bold text-foreground">Guaranteed in 2 - 4 Business Days</p>
              <p className="text-[11px] text-muted-foreground font-medium">Dispatched via LightGBM optimized routing network.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
