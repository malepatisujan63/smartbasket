'use client';

import React, { useEffect, useState } from 'react';
import { useAppSelector, useAppDispatch } from '../../redux/hooks';
import { removeFromCompare, clearCompare } from '../../redux/compareSlice';
import { addToCart } from '../../redux/cartSlice';
import { aiAssistantApi } from '../../services/api';
import { ComparisonResult, Product } from '../../types';
import { GitCompare, Trophy, Award, Zap, Battery, Monitor, ShoppingCart, Trash2, ArrowLeft, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import Link from 'next/link';

export default function ComparePage() {
  const dispatch = useAppDispatch();
  const { items } = useAppSelector((state) => state.compare);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchComparison = async () => {
      if (items.length === 0) {
        setResult(null);
        return;
      }
      setIsLoading(true);
      try {
        const res = await aiAssistantApi.compare(items.map((p) => p.id));
        setResult(res.data);
      } catch (err) {
        console.error('Failed to fetch comparison matrix:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchComparison();
  }, [items]);

  if (items.length === 0) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center max-w-md mx-auto">
        <div className="w-20 h-20 rounded-3xl bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-6 shadow-xl">
          <GitCompare className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Your Comparison Matrix is Empty</h2>
        <p className="text-slate-500 dark:text-slate-400 mb-8 text-sm leading-relaxed">
          Select up to 5 products from our 20,000+ catalog while browsing by clicking the <strong>"+ Compare"</strong> button on any product card or AI recommendation!
        </p>
        <Link
          href="/products"
          className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-sm shadow-lg shadow-indigo-500/30 hover:opacity-90 transition-all flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" /> Browse Catalog
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-500" /> AI Matrix Engine
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              Side-by-Side Product Comparison ({items.length}/5)
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Evaluating specifications, price-to-performance ratio, and verified review sentiment.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => dispatch(clearCompare())}
              className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40 dark:hover:text-rose-400 text-slate-700 dark:text-slate-300 font-semibold text-xs transition-all flex items-center gap-1.5"
            >
              <Trash2 className="w-4 h-4" /> Clear Matrix
            </button>
            <Link
              href="/products"
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition-all"
            >
              + Add More Products
            </Link>
          </div>
        </div>

        {/* AI Recommendation Awards Banner */}
        {result?.awards && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {result.awards.overall_winner && (
              <div className="p-5 rounded-3xl bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent border-2 border-amber-500/30 dark:border-amber-500/40 relative overflow-hidden shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-amber-500/30">
                  <Trophy className="w-6 h-6" />
                </div>
                <div className="min-w-0">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
                    🏆 Overall AI Winner
                  </span>
                  <Link href={`/products/${result.awards.overall_winner.id}`}>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white truncate hover:text-indigo-600 transition-colors">
                      {result.awards.overall_winner.title}
                    </h4>
                  </Link>
                  <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 mt-0.5">
                    ${result.awards.overall_winner.price.toLocaleString()} | ⭐ {result.awards.overall_winner.rating}
                  </p>
                </div>
              </div>
            )}

            {result.awards.best_value && (
              <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent border border-emerald-500/30 relative overflow-hidden shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-emerald-500/30">
                  <Award className="w-6 h-6" />
                </div>
                <div className="min-w-0">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                    💰 Best Value Pick
                  </span>
                  <Link href={`/products/${result.awards.best_value.id}`}>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white truncate hover:text-indigo-600 transition-colors">
                      {result.awards.best_value.title}
                    </h4>
                  </Link>
                  <p className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mt-0.5">
                    ${result.awards.best_value.price.toLocaleString()}
                  </p>
                </div>
              </div>
            )}

            {result.awards.best_performance && (
              <div className="p-5 rounded-3xl bg-gradient-to-br from-blue-500/10 via-blue-500/5 to-transparent border border-blue-500/30 relative overflow-hidden shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/30">
                  <Zap className="w-6 h-6" />
                </div>
                <div className="min-w-0">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                    ⚡ Best Performance
                  </span>
                  <Link href={`/products/${result.awards.best_performance.id}`}>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white truncate hover:text-indigo-600 transition-colors">
                      {result.awards.best_performance.title}
                    </h4>
                  </Link>
                  <p className="text-xs font-semibold text-blue-600 dark:text-blue-400 mt-0.5">
                    ⭐ {result.awards.best_performance.rating}/5.0 Rating
                  </p>
                </div>
              </div>
            )}

            {result.awards.best_display && (
              <div className="p-5 rounded-3xl bg-gradient-to-br from-purple-500/10 via-purple-500/5 to-transparent border border-purple-500/30 relative overflow-hidden shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-purple-500/30">
                  <Monitor className="w-6 h-6" />
                </div>
                <div className="min-w-0">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400">
                    🖥️ Best Display / Specs
                  </span>
                  <Link href={`/products/${result.awards.best_display.id}`}>
                    <h4 className="font-bold text-sm text-slate-900 dark:text-white truncate hover:text-indigo-600 transition-colors">
                      {result.awards.best_display.title}
                    </h4>
                  </Link>
                  <p className="text-xs font-semibold text-purple-600 dark:text-purple-400 mt-0.5">
                    OLED Liquid Retina
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Comparison Matrix Table */}
        {isLoading ? (
          <div className="p-16 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="font-semibold text-slate-700 dark:text-slate-300">Generating AI Comparison Matrix...</p>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/50">
                  <th className="py-6 px-6 text-sm font-bold text-slate-500 dark:text-slate-400 w-48 sticky left-0 bg-slate-50 dark:bg-slate-800/90 z-10">
                    Specification
                  </th>
                  {items.map((prod) => (
                    <th key={prod.id} className="py-6 px-6 min-w-[240px] max-w-[280px] align-top">
                      <div className="relative group">
                        <button
                          onClick={() => dispatch(removeFromCompare(prod.id))}
                          className="absolute -top-2 -right-2 p-1.5 rounded-full bg-slate-200 dark:bg-slate-700 hover:bg-rose-500 hover:text-white text-slate-600 dark:text-slate-300 transition-colors shadow-sm"
                          title="Remove"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                        <Link href={`/products/${prod.id}`}>
                          <img
                            src={prod.images?.[0] || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300'}
                            alt={prod.title}
                            className="w-full h-40 object-cover rounded-2xl bg-slate-100 dark:bg-slate-800 mb-4 shadow-sm group-hover:scale-[1.02] transition-transform"
                          />
                          <span className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                            {prod.brand?.name || 'Brand'}
                          </span>
                          <h3 className="font-bold text-base text-slate-900 dark:text-white mt-1 line-clamp-2 group-hover:text-indigo-600 transition-colors">
                            {prod.title}
                          </h3>
                        </Link>
                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-lg font-black text-slate-900 dark:text-white">
                            ${prod.price.toLocaleString()}
                          </span>
                          <span className="px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 text-xs font-bold">
                            ⭐ {prod.rating}
                          </span>
                        </div>
                        <button
                          onClick={() => dispatch(addToCart({ product: prod, quantity: 1 }))}
                          className="w-full mt-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-indigo-500/20 transition-all"
                        >
                          <ShoppingCart className="w-3.5 h-3.5" /> Add to Cart
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-sm">
                {/* Price & Value */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-bold text-slate-700 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    Price & Discount
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6 text-slate-900 dark:text-white font-semibold">
                      ${prod.price.toLocaleString()}
                      {prod.discount_percentage > 0 && (
                        <span className="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300">
                          -{prod.discount_percentage}% OFF
                        </span>
                      )}
                    </td>
                  ))}
                </tr>

                {/* Processor / CPU */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-bold text-slate-700 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    Processor / Core
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6 text-slate-600 dark:text-slate-300">
                      {prod.specifications?.Processor || prod.specifications?.CPU || prod.specifications?.Sensor || 'AI Silicon Core Pro'}
                    </td>
                  ))}
                </tr>

                {/* RAM / Memory */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-bold text-slate-700 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    RAM / Memory
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6 text-slate-600 dark:text-slate-300">
                      {prod.specifications?.RAM || prod.specifications?.Memory || 'Unified AI Memory'}
                    </td>
                  ))}
                </tr>

                {/* Display / Panel */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-bold text-slate-700 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    Display / Panel
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6 text-slate-600 dark:text-slate-300">
                      {prod.specifications?.Display || prod.specifications?.Panel || prod.specifications?.Resolution || 'Liquid Retina OLED (120Hz)'}
                    </td>
                  ))}
                </tr>

                {/* Battery / Power */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-bold text-slate-700 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    Battery / Power
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6 text-slate-600 dark:text-slate-300">
                      {prod.specifications?.['Battery Life'] || prod.specifications?.Battery || prod.specifications?.Power || 'Up to 24 Hours Ultra Mode'}
                    </td>
                  ))}
                </tr>

                {/* Warranty */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <td className="py-4 px-6 font-bold text-slate-700 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    Official Warranty
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6 text-slate-600 dark:text-slate-300">
                      {prod.warranty || '2 Years Manufacturer Warranty'}
                    </td>
                  ))}
                </tr>

                {/* AI Identified Pros */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 bg-emerald-50/30 dark:bg-emerald-950/10">
                  <td className="py-4 px-6 font-bold text-emerald-700 dark:text-emerald-400 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    ✨ AI Identified Pros
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6">
                      <ul className="space-y-1">
                        {(prod.features || ['High reliability & speed', 'Aerospace aluminum build']).slice(0, 3).map((feat, idx) => (
                          <li key={idx} className="text-xs text-emerald-800 dark:text-emerald-300 flex items-start gap-1.5 font-medium">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                            <span>{feat}</span>
                          </li>
                        ))}
                      </ul>
                    </td>
                  ))}
                </tr>

                {/* AI Identified Cons */}
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 bg-rose-50/30 dark:bg-rose-950/10">
                  <td className="py-4 px-6 font-bold text-rose-700 dark:text-rose-400 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    ⚠️ Considerations
                  </td>
                  {items.map((prod) => (
                    <td key={prod.id} className="py-4 px-6">
                      <ul className="space-y-1">
                        <li className="text-xs text-rose-800 dark:text-rose-300 flex items-start gap-1.5 font-medium">
                          <AlertCircle className="w-3.5 h-3.5 text-rose-500 flex-shrink-0 mt-0.5" />
                          <span>{prod.price > 1000 ? 'Premium flagship investment' : 'High demand item - limited stock'}</span>
                        </li>
                      </ul>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
