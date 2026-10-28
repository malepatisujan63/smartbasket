'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppSelector, useAppDispatch } from '../redux/hooks';
import { removeFromCompare, clearCompare } from '../redux/compareSlice';
import { X, GitCompare, Trash2, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function ProductComparisonBar() {
  const dispatch = useAppDispatch();
  const { items, isOpen } = useAppSelector((state) => state.compare);

  if (!isOpen || items.length === 0) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
        className="fixed bottom-6 left-6 right-28 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-4 flex items-center justify-between gap-4 max-w-4xl mx-auto"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center flex-shrink-0">
            <GitCompare className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              Product Comparison Matrix ({items.length}/5)
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Select up to 5 items to compare specs & AI scores
            </p>
          </div>
        </div>

        {/* Selected Items Thumbnails */}
        <div className="flex items-center gap-2 overflow-x-auto py-1">
          {items.map((prod) => (
            <div
              key={prod.id}
              className="relative group w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center flex-shrink-0 shadow-sm"
            >
              <img
                src={prod.images?.[0] || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100'}
                alt={prod.title}
                className="w-10 h-10 object-cover rounded-lg"
              />
              <button
                onClick={() => dispatch(removeFromCompare(prod.id))}
                className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-rose-500 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-md"
                title="Remove"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
          {Array.from({ length: 5 - items.length }).map((_, idx) => (
            <div
              key={`empty-${idx}`}
              className="w-12 h-12 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-800 flex items-center justify-center text-slate-300 dark:text-slate-700 text-xs font-bold"
            >
              +
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={() => dispatch(clearCompare())}
            className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/30 dark:hover:text-rose-400 text-slate-600 dark:text-slate-400 text-xs font-semibold transition-colors flex items-center gap-1"
            title="Clear All"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <Link
            href="/compare"
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-indigo-500/20 transition-all"
          >
            Compare Now <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
