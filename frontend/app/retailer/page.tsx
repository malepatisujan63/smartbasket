'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { retailersApi } from '../../services/api';
import { Product, Retailer } from '../../types';
import { Store, Package, DollarSign, Star, Users, TrendingUp, Plus, Edit, ShieldCheck, MessageSquare, Tag, CheckCircle2, AlertTriangle, ArrowRight, RefreshCw, X, Box } from 'lucide-react';
import Link from 'next/link';

export default function RetailerDashboardPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'products' | 'orders' | 'discounts'>('overview');
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [replyText, setReplyText] = useState<Record<number, string>>({});

  // New Product Form State
  const [newProduct, setNewProduct] = useState({
    title: '',
    price: '',
    stock: '50',
    description: '',
    marketing_description: '',
    category_id: 1,
    image_url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1000'
  });

  const fetchDashboard = async () => {
    setIsLoading(true);
    try {
      const res = await retailersApi.getDashboard();
      setDashboardData(res.data);
    } catch (err) {
      console.error('Failed to fetch retailer dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await retailersApi.createProduct({
        title: newProduct.title,
        price: parseFloat(newProduct.price) || 99.99,
        stock: parseInt(newProduct.stock) || 50,
        description: newProduct.description,
        marketing_description: newProduct.marketing_description,
        category_id: newProduct.category_id,
        images: [newProduct.image_url],
        specifications: { Processor: "AI Silicon Core Pro", Warranty: "2 Years Manufacturer" },
        features: ["Verified Retailer Direct Item", "Express Prime Fulfillment"]
      });
      setIsAddModalOpen(false);
      fetchDashboard();
      alert("✅ Product successfully added to your store!");
    } catch (err) {
      alert("Failed to create product. Please check your inputs.");
    }
  };

  const handleReplyReview = async (reviewId: number) => {
    const text = replyText[reviewId];
    if (!text || !text.trim()) return;
    try {
      await retailersApi.replyReview(reviewId, text);
      alert(`✅ Reply posted to review #${reviewId}`);
      setReplyText((prev) => ({ ...prev, [reviewId]: '' }));
    } catch (err) {
      alert("Failed to post reply.");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="font-semibold text-slate-700 dark:text-slate-300">Loading Retailer Portal & Store Analytics...</p>
      </div>
    );
  }

  const profile: Retailer = dashboardData?.profile || {};
  const stats = dashboardData?.statistics || {};
  const products: Product[] = dashboardData?.recent_products || [];
  const reviews = dashboardData?.recent_reviews || [];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-16">
      {/* Store Banner */}
      <div className="relative h-64 sm:h-80 w-full bg-slate-900 overflow-hidden">
        <img
          src={profile.store_banner || 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1600'}
          alt={profile.store_name}
          className="w-full h-full object-cover opacity-60"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />
        
        <div className="absolute bottom-6 left-4 sm:left-8 right-4 sm:right-8 max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div className="flex items-center gap-4">
            <img
              src={profile.store_logo || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=250'}
              alt={profile.store_name}
              className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover border-4 border-white dark:border-slate-800 shadow-xl bg-white"
            />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">{profile.store_name || 'Amazon-AI Retailer Hub'}</h1>
                {profile.verified_badge && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500 text-white flex items-center gap-1 shadow-md">
                    <ShieldCheck className="w-3.5 h-3.5" /> Verified Seller
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-300 mt-1 max-w-xl line-clamp-1">{profile.business_description || 'Authorized global distributor of high-performance merchandise.'}</p>
              <div className="flex items-center gap-4 mt-2 text-xs text-slate-300">
                <span>📍 {profile.location || 'Seattle, WA'}</span>
                <span>👥 {profile.followers_count?.toLocaleString() || '1,250'} Followers</span>
                <span>📅 {profile.years_of_selling || 5} Years Selling</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-5 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 text-white font-bold text-sm shadow-xl flex items-center justify-center gap-2 transition-all flex-shrink-0"
          >
            <Plus className="w-4 h-4" /> Add New Product
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-px overflow-x-auto">
          {[
            { id: 'overview', label: 'Dashboard Overview', icon: TrendingUp },
            { id: 'products', label: `My Store Products (${stats.total_products || products.length})`, icon: Package },
            { id: 'orders', label: 'Orders & Revenue', icon: DollarSign },
            { id: 'discounts', label: 'Discounts & Coupons', icon: Tag },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-5 py-3 font-bold text-sm rounded-t-2xl border-b-2 transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-950/20'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab 1: Dashboard Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Sales Revenue</p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">${(stats.total_revenue || 450000).toLocaleString()}</h3>
                  <span className="text-xs text-emerald-600 font-semibold mt-1 inline-block">↑ +18.4% this month</span>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                  <DollarSign className="w-6 h-6" />
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Store Products</p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">{stats.total_products || 50} Items</h3>
                  <span className="text-xs text-indigo-600 font-semibold mt-1 inline-block">Active in Catalog</span>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
                  <Package className="w-6 h-6" />
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Store Rating</p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">⭐ {stats.average_rating || 4.8} / 5.0</h3>
                  <span className="text-xs text-amber-600 font-semibold mt-1 inline-block">Verified Customer Score</span>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
                  <Star className="w-6 h-6" />
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Low Stock Alerts</p>
                  <h3 className="text-2xl font-black text-rose-600 dark:text-rose-400 mt-1">{stats.low_stock_items || 3} Items</h3>
                  <span className="text-xs text-rose-500 font-semibold mt-1 inline-block">Restock Recommended</span>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-600 flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6" />
                </div>
              </div>
            </div>

            {/* Customer Reviews & Reply Section */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                <div>
                  <h3 className="font-extrabold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-indigo-600" /> Recent Customer Reviews & Sentiment
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Reply directly to customer feedback to improve store reputation</p>
                </div>
              </div>

              <div className="space-y-4">
                {reviews.map((rev: any) => (
                  <div key={rev.id} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-slate-900 dark:text-white">{rev.user_name}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-300">
                          ⭐ {rev.rating}/5.0
                        </span>
                        <span className="text-xs text-slate-400">on <strong>{rev.product_title}</strong></span>
                      </div>
                      <span className="text-[11px] text-slate-400">{new Date(rev.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-sm text-slate-700 dark:text-slate-300 italic">"{rev.comment}"</p>

                    {/* Reply Input */}
                    <div className="flex items-center gap-2 pt-2">
                      <input
                        type="text"
                        value={replyText[rev.id] || ''}
                        onChange={(e) => setReplyText((prev) => ({ ...prev, [rev.id]: e.target.value }))}
                        placeholder="Write a public retailer reply to thank or assist the customer..."
                        className="flex-1 px-3 py-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      />
                      <button
                        onClick={() => handleReplyReview(rev.id)}
                        className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-all flex-shrink-0"
                      >
                        Reply
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: My Store Products */}
        {activeTab === 'products' && (
          <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
              <div>
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                  <Package className="w-5 h-5 text-indigo-600" /> My Store Inventory ({products.length} Products)
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">Manage stock levels, prices, and marketing copy for your exclusive store catalog</p>
              </div>
              <button
                onClick={() => setIsAddModalOpen(true)}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs flex items-center gap-1.5 transition-all"
              >
                <Plus className="w-3.5 h-3.5" /> Add Product
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[700px]">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-400 uppercase">
                    <th className="py-3 px-4">Product</th>
                    <th className="py-3 px-4">Price</th>
                    <th className="py-3 px-4">Stock Status</th>
                    <th className="py-3 px-4">Rating</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-sm">
                  {products.map((prod) => (
                    <tr key={prod.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                      <td className="py-4 px-4 flex items-center gap-3">
                        <img
                          src={prod.images?.[0] || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100'}
                          alt={prod.title}
                          className="w-12 h-12 rounded-xl object-cover bg-slate-100 dark:bg-slate-800"
                        />
                        <div>
                          <Link href={`/products/${prod.id}`} className="font-bold text-slate-900 dark:text-white hover:text-indigo-600 transition-colors line-clamp-1">
                            {prod.title}
                          </Link>
                          <span className="text-xs text-slate-400">SKU: {prod.sku || `SKU-RET-${String(prod.id).padStart(5, '0')}`}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 font-bold text-slate-900 dark:text-white">
                        ${prod.price.toLocaleString()}
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                          prod.stock > 15 ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300' : 'bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300'
                        }`}>
                          {prod.stock > 15 ? `In Stock (${prod.stock})` : `Low Stock (${prod.stock})`}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-amber-500 font-bold">
                        ⭐ {prod.rating} ({prod.reviews_count})
                      </td>
                      <td className="py-4 px-4 text-right">
                        <Link
                          href={`/products/${prod.id}`}
                          className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 hover:text-indigo-600 dark:hover:bg-indigo-950 text-slate-700 dark:text-slate-300 text-xs font-bold transition-all"
                        >
                          View / Edit
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Orders & Revenue */}
        {activeTab === 'orders' && (
          <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <DollarSign className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
            <h3 className="font-extrabold text-xl text-slate-900 dark:text-white mb-2">Real-Time Revenue & Order Fulfillment</h3>
            <p className="text-slate-500 dark:text-slate-400 max-w-lg mx-auto text-sm mb-6">
              All orders placed for your store products are dispatched automatically via <strong>Amazon-AI Prime Logistics</strong>. Cash on Delivery (COD) settlements are credited directly to your retailer bank account within 24 hours of delivery.
            </p>
            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/50 max-w-xl mx-auto border border-slate-200 dark:border-slate-700 flex items-center justify-around">
              <div>
                <span className="text-xs text-slate-400 font-semibold uppercase">Pending Dispatch</span>
                <h4 className="text-2xl font-black text-indigo-600 mt-1">14 Orders</h4>
              </div>
              <div className="h-10 w-px bg-slate-200 dark:bg-slate-700" />
              <div>
                <span className="text-xs text-slate-400 font-semibold uppercase">Completed COD</span>
                <h4 className="text-2xl font-black text-emerald-600 mt-1">${(profile.revenue || 450000).toLocaleString()}</h4>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Discounts */}
        {activeTab === 'discounts' && (
          <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            <h3 className="font-extrabold text-lg text-slate-900 dark:text-white flex items-center gap-2">
              <Tag className="w-5 h-5 text-indigo-600" /> Active Store Discount Codes
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-5 rounded-2xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/30 flex items-center justify-between">
                <div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-600 text-white">ACTIVE COUPON</span>
                  <h4 className="text-lg font-black text-slate-900 dark:text-white mt-2">AMAZONAI20</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">20% OFF on all store items above $100</p>
                </div>
                <button className="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 text-xs font-bold border border-slate-200 dark:border-slate-700 shadow-sm">
                  Edit
                </button>
              </div>
              <div className="p-5 rounded-2xl bg-slate-100 dark:bg-slate-800/50 border border-dashed border-slate-300 dark:border-slate-700 flex items-center justify-center text-center">
                <button
                  onClick={() => alert("🎟️ New coupon creation modal: Enter code and discount percentage.")}
                  className="font-bold text-sm text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" /> Create New Store Discount Code
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add New Product Modal */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 overflow-y-auto max-h-[90vh]"
            >
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 mb-6">
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                  <Plus className="w-5 h-5 text-indigo-600" /> Add Product to Your Store
                </h3>
                <button onClick={() => setIsAddModalOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateProduct} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Product Title</label>
                  <input
                    type="text"
                    required
                    value={newProduct.title}
                    onChange={(e) => setNewProduct({ ...newProduct, title: e.target.value })}
                    placeholder="e.g. Pro-Grade AI Ultrabook 16-inch (32GB, 1TB)"
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Price ($)</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={newProduct.price}
                      onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                      placeholder="999.99"
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Stock Quantity</label>
                    <input
                      type="number"
                      required
                      value={newProduct.stock}
                      onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                      placeholder="50"
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Image URL</label>
                  <input
                    type="url"
                    required
                    value={newProduct.image_url}
                    onChange={(e) => setNewProduct({ ...newProduct, image_url: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Marketing Description</label>
                  <textarea
                    rows={3}
                    value={newProduct.marketing_description}
                    onChange={(e) => setNewProduct({ ...newProduct, marketing_description: e.target.value })}
                    placeholder="Describe the key value proposition and AI benefits..."
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="pt-4 flex items-center justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-sm transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 text-white font-bold text-sm shadow-md transition-all"
                  >
                    Create Product
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
