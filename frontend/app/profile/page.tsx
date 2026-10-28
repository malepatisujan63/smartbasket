'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import Link from 'next/link';
import { usersApi, ordersApi } from '../../services/api';
import { Address, Order } from '../../types';
import { User, MapPin, Plus, Trash2, CheckCircle2, ShieldCheck, Mail, Phone, Lock, Package, ChevronRight, Truck, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

const ProfilePage: React.FC = () => {
  const router = useRouter();
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  // New Address Form
  const [fullName, setFullName] = useState(user?.full_name || 'Alex Morgan');
  const [phone, setPhone] = useState('+1 (555) 234-5678');
  const [street, setStreet] = useState('');
  const [city, setCity] = useState('');
  const [stateName, setStateName] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [country, setCountry] = useState('United States');
  const [isDefault, setIsDefault] = useState(true);

  useEffect(() => {
    const hasToken = typeof window !== 'undefined' && localStorage.getItem('access_token');
    if (!isAuthenticated && !hasToken) {
      router.push('/auth/login?redirect=/profile');
      return;
    }
    const fetchUserData = async () => {
      try {
        const [addrRes, ordersRes] = await Promise.allSettled([
          usersApi.getAddresses(),
          ordersApi.getUserOrders(),
        ]);
        if (addrRes.status === 'fulfilled') {
          setAddresses(addrRes.value.data);
        }
        if (ordersRes.status === 'fulfilled') {
          setOrders(ordersRes.value.data);
          if (typeof window !== 'undefined') {
            localStorage.setItem('ajio_orders', JSON.stringify(ordersRes.value.data));
          }
        } else if (typeof window !== 'undefined') {
          const cached = localStorage.getItem('ajio_orders');
          if (cached) {
            try { setOrders(JSON.parse(cached)); } catch (e) {}
          }
        }
      } catch (err) {
        console.error("Profile data error", err);
      } finally {
        setLoading(false);
      }
    };
    fetchUserData();
  }, [isAuthenticated, router]);

  const handleAddAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        full_name: fullName,
        phone,
        street_address: street,
        city,
        state: stateName,
        postal_code: postalCode,
        country,
        is_default: isDefault || addresses.length === 0
      };
      const res = await usersApi.createAddress(payload);
      setAddresses([...addresses, res.data]);
      setShowAddForm(false);
      setStreet('');
      setCity('');
      setStateName('');
      setPostalCode('');
    } catch (err) {
      console.error("Add address error", err);
    }
  };

  const handleDeleteAddress = async (id: number) => {
    try {
      await usersApi.deleteAddress(id);
      setAddresses(addresses.filter((a) => a.id !== id));
    } catch (err) {
      console.error("Delete address error", err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Delivered':
        return <span className="bg-[#03a685]/15 text-[#03a685] border border-[#03a685]/30 px-2.5 py-0.5 rounded-full text-[11px] font-black flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Delivered</span>;
      case 'Out For Delivery':
      case 'Shipped':
        return <span className="bg-primary/15 text-primary border border-primary/30 px-2.5 py-0.5 rounded-full text-[11px] font-black flex items-center gap-1"><Truck className="w-3.5 h-3.5" /> {status}</span>;
      default:
        return <span className="bg-amber-500/15 text-amber-500 border border-amber-500/30 px-2.5 py-0.5 rounded-full text-[11px] font-black flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="py-32 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto" />
        <p className="text-sm text-muted-foreground font-bold">Loading Your Profile & Addresses...</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 pb-24 max-w-6xl mx-auto">
      <div className="border-b border-border pb-6">
        <h1 className="text-2xl sm:text-4xl font-black text-foreground tracking-tight flex items-center gap-2.5">
          <User className="w-8 h-8 text-secondary" /> Account Profile & Security
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground font-semibold mt-1">Manage personal information and saved Cash on Delivery destinations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        {/* Left: Account Details */}
        <div className="md:col-span-4 space-y-6">
          <div className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl relative overflow-hidden">
            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-primary to-blue-600 flex items-center justify-center text-white font-black text-4xl shadow-lg mx-auto">
              {user?.full_name?.charAt(0).toUpperCase() || 'A'}
            </div>
            <div className="text-center space-y-1.5">
              <h2 className="text-xl font-black text-foreground">{user?.full_name}</h2>
              <p className="text-xs text-muted-foreground font-semibold flex items-center justify-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-primary" /> {user?.email}
              </p>
              <span className="inline-block mt-2 bg-secondary/15 text-secondary border border-secondary/30 text-[10px] font-black px-3.5 py-1 rounded-full uppercase tracking-wider">
                {user?.role === 'admin' ? 'AI Administrator' : 'Verified COD Customer'}
              </span>
            </div>
            <div className="pt-6 border-t border-border text-xs space-y-3 font-semibold">
              <div className="flex justify-between text-muted-foreground">
                <span>Account Status</span>
                <span className="text-accent font-extrabold flex items-center gap-1"><CheckCircle2 className="w-4 h-4" /> Active</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Payment Mode</span>
                <span className="text-secondary font-extrabold">Cash on Delivery</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Security Protocol</span>
                <span className="text-primary font-extrabold flex items-center gap-1"><Lock className="w-3.5 h-3.5" /> 256-Bit Encrypted</span>
              </div>
            </div>
          </div>

          {/* Orders Summary Card */}
          <div className="bg-card border border-border rounded-3xl p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-black text-foreground flex items-center gap-2">
                <Package className="w-4 h-4 text-[#d5a249]" /> Your Orders
              </h3>
              <span className="bg-[#d5a249]/15 text-[#d5a249] text-[10px] font-black px-2.5 py-0.5 rounded-full">
                {orders.length} Total
              </span>
            </div>
            <p className="text-xs text-muted-foreground font-semibold">
              Track live fulfillment timelines and view invoice receipts for all your Cash on Delivery orders.
            </p>
            <Link
              href="/orders"
              className="w-full py-2.5 btn-ajio text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1.5 shadow-md"
            >
              <span>View All Orders & Tracking</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Right: Orders & Saved Delivery Addresses */}
        <div className="md:col-span-8 space-y-8">
          {/* Recent Orders Section */}
          <div className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <h2 className="text-lg font-black text-foreground flex items-center gap-2">
                  <Package className="w-5 h-5 text-primary" /> Recent Orders & Live Tracking
                </h2>
                <p className="text-xs text-muted-foreground font-semibold mt-0.5">
                  Shipment status & milestones for your Cash on Delivery orders
                </p>
              </div>
              <Link
                href="/orders"
                className="px-4 py-2 rounded-xl btn-ajio text-xs font-black uppercase tracking-wider flex items-center gap-1 shadow-sm"
              >
                <span>All Orders ({orders.length})</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {orders.length === 0 ? (
              <div className="text-center py-10 space-y-4 bg-muted/20 rounded-2xl border border-dashed border-border p-6">
                <Package className="w-10 h-10 text-muted-foreground mx-auto stroke-[1.5]" />
                <div className="space-y-1">
                  <h3 className="text-sm font-black text-foreground">No Orders Placed Yet</h3>
                  <p className="text-xs text-muted-foreground font-semibold max-w-sm mx-auto">
                    Explore top AJIO fashion collections and enjoy effortless 100% Cash on Delivery on every order.
                  </p>
                </div>
                <Link
                  href="/products"
                  className="inline-block px-6 py-2.5 btn-ajio text-xs uppercase font-black tracking-wider shadow-md"
                >
                  Explore Trends
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {orders.slice(0, 3).map((order) => (
                  <div
                    key={order.id}
                    className="p-5 rounded-2xl bg-muted/30 border border-border space-y-4 hover:border-primary/40 transition-colors shadow-sm"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3 text-xs border-b border-border/60 pb-3 font-semibold">
                      <div className="flex items-center gap-3">
                        <span className="font-black text-foreground">Order #{order.order_number}</span>
                        {getStatusBadge(order.status)}
                      </div>
                      <div className="flex items-center gap-4 text-xs font-bold">
                        <span className="text-muted-foreground text-[11px]">{new Date(order.created_at).toLocaleDateString()}</span>
                        <span className="text-secondary font-black text-sm">${order.total_amount.toFixed(2)}</span>
                      </div>
                    </div>

                    {/* Order items preview */}
                    <div className="space-y-2.5">
                      {order.items?.map((item, idx) => {
                        const prodTitle = item.product?.title || item.product_title || `Product #${item.product_id}`;
                        const prodImg = item.product?.images?.[0] || 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=200&q=80';
                        const brandName = item.product?.brand?.name || 'AJIO LUXE';
                        return (
                          <div key={idx} className="flex items-center justify-between text-xs font-semibold gap-3 bg-card p-2.5 rounded-xl border border-border">
                            <div className="flex items-center gap-3 min-w-0">
                              <img
                                src={prodImg}
                                alt={prodTitle}
                                className="w-12 h-12 rounded-lg object-cover bg-muted border border-border flex-shrink-0"
                              />
                              <div className="min-w-0">
                                <span className="text-[9px] font-black uppercase text-[#d5a249] block">{brandName}</span>
                                <Link href={`/products/${item.product_id}`} className="text-foreground font-black hover:text-[#d5a249] transition-colors truncate block">
                                  {prodTitle}
                                </Link>
                                <span className="text-[10px] text-muted-foreground block">
                                  Qty: {item.quantity} × ${(item.unit_price || (item.total_price / (item.quantity || 1))).toFixed(2)}
                                </span>
                              </div>
                            </div>
                            <span className="text-foreground font-black whitespace-nowrap">${item.total_price.toFixed(2)}</span>
                          </div>
                        );
                      })}
                    </div>

                    <div className="flex items-center justify-between pt-2">
                      <span className="text-[11px] text-[#03a685] font-extrabold flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5" /> 100% Cash on Delivery
                      </span>
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/orders/${order.id}`}
                          className="px-4 py-2 rounded-xl btn-ajio text-xs font-black uppercase tracking-wider flex items-center gap-1 shadow-sm"
                        >
                          <span>Track Order</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Saved Delivery Addresses */}
          <div className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <h2 className="text-lg font-black text-foreground flex items-center gap-2">
                <MapPin className="w-5 h-5 text-primary" /> Saved Delivery Addresses
              </h2>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="px-4 py-2.5 btn-ajio text-xs uppercase font-black tracking-wider shadow flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Add New Address
              </button>
            </div>

            {showAddForm && (
              <form onSubmit={handleAddAddress} className="bg-muted/40 p-6 rounded-2xl border border-border space-y-4">
                <h3 className="text-xs font-black text-primary uppercase tracking-wider">Add Delivery Destination</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-semibold">
                  <div>
                    <label className="text-muted-foreground block mb-1">Full Name</label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="text-muted-foreground block mb-1">Phone Number</label>
                    <input
                      type="text"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="text-muted-foreground block mb-1">Street Address</label>
                    <input
                      type="text"
                      required
                      value={street}
                      onChange={(e) => setStreet(e.target.value)}
                      placeholder="e.g. 123 Tech Avenue, Suite 400"
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="text-muted-foreground block mb-1">City</label>
                    <input
                      type="text"
                      required
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      placeholder="e.g. Seattle"
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="text-muted-foreground block mb-1">State / Province</label>
                    <input
                      type="text"
                      required
                      value={stateName}
                      onChange={(e) => setStateName(e.target.value)}
                      placeholder="e.g. WA"
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="text-muted-foreground block mb-1">Postal Code</label>
                    <input
                      type="text"
                      required
                      value={postalCode}
                      onChange={(e) => setPostalCode(e.target.value)}
                      placeholder="e.g. 98101"
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="text-muted-foreground block mb-1">Country</label>
                    <input
                      type="text"
                      required
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      className="w-full bg-card border border-border rounded-xl px-3.5 py-2.5 text-foreground font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <input
                    type="checkbox"
                    checked={isDefault}
                    onChange={(e) => setIsDefault(e.target.checked)}
                    className="w-4 h-4 text-primary rounded focus:ring-primary accent-primary cursor-pointer"
                  />
                  <span className="text-xs text-foreground font-bold">Set as Default Delivery Address</span>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    className="px-6 py-3 btn-ajio text-xs uppercase font-black tracking-wider shadow-md"
                  >
                    Save Address
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="px-6 py-3 bg-card hover:bg-muted text-foreground font-bold text-xs uppercase rounded-xl border border-border"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}

            {addresses.length === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-8 font-semibold">No saved addresses found. Click &ldquo;Add New Address&rdquo; above!</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {addresses.map((addr) => (
                  <div key={addr.id} className="p-5 rounded-2xl bg-muted/30 border border-border relative space-y-2 text-xs shadow-sm">
                    {addr.is_default && (
                      <span className="absolute top-3.5 right-3.5 bg-primary/15 text-primary border border-primary/30 text-[10px] font-black px-2.5 py-0.5 rounded-full uppercase">
                        Default
                      </span>
                    )}
                    <h3 className="font-black text-foreground text-sm">{addr.full_name}</h3>
                    <p className="text-muted-foreground font-semibold">{addr.street_address}</p>
                    <p className="text-muted-foreground font-semibold">{addr.city}, {addr.state} {addr.postal_code}</p>
                    <p className="text-muted-foreground font-semibold">{addr.country}</p>
                    <p className="text-foreground pt-1 font-bold">Phone: {addr.phone}</p>

                    <div className="pt-3 border-t border-border flex justify-end">
                      <button
                        onClick={() => handleDeleteAddress(addr.id)}
                        className="text-red-500 hover:text-red-400 text-xs font-extrabold flex items-center gap-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" /> Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
