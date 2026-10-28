'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Send, Bot, User, ShoppingCart, Award, CheckCircle2, AlertCircle, ArrowRight, RefreshCw, HelpCircle, ShieldCheck, Box, MessageSquare } from 'lucide-react';
import { aiAssistantApi } from '../services/api';
import { Product, AIAssistantChatResponse, ComparisonTableItem } from '../types';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { addToCart } from '../redux/cartSlice';
import { addToCompare } from '../redux/compareSlice';
import Link from 'next/link';

interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  data?: AIAssistantChatResponse;
  isLoading?: boolean;
}

export default function AIShoppingAssistant() {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const [isOpen, setIsOpen] = useState(false);
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQueries = [
    "Best AI laptop under $1,500 for developers",
    "Compare Sony vs Bose noise cancelling headphones",
    "What is the warranty and return policy?",
    "Recommend 5G smartphone with best camera under $800",
    "What comes inside the box for MacBook Pro?",
    "Summarize customer reviews and sentiment"
  ];

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome-msg',
          sender: 'ai',
          text: "### 👋 Hello! I'm your AJIO Personal Stylist & Shopping Assistant.\n\nI have real-time access to our entire **20,000+ fashion styles, footwear, watches & lifestyle catalog**, reviews, and Cash on Delivery details.\n\nHow can I help you discover the perfect style today?",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  }, [messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputQuery;
    if (!query.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const loadingMsg: ChatMessage = {
      id: `ai-loading-${Date.now()}`,
      sender: 'ai',
      text: '🤖 *Scanning 20,000+ products, specifications, and reviews using RAG Algorithm...*',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isLoading: true
    };

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    if (!textToSend) setInputQuery('');
    setIsLoading(true);

    try {
      const response = await aiAssistantApi.chat({
        query: query,
        user_id: user?.id,
      });

      setMessages((prev) => 
        prev.map((m) => 
          m.id === loadingMsg.id 
            ? {
                id: `ai-${Date.now()}`,
                sender: 'ai',
                text: response.data.message,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                data: response.data,
                isLoading: false
              }
            : m
        )
      );
    } catch (error) {
      setMessages((prev) => 
        prev.map((m) => 
          m.id === loadingMsg.id 
            ? {
                id: `ai-err-${Date.now()}`,
                sender: 'ai',
                text: "### ⚠️ System Notification\n\nI encountered a temporary connection issue while searching our AI database. Please try asking your question again or choose a suggested topic above.",
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                isLoading: false
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCart = (product: Product) => {
    dispatch(addToCart({ product, quantity: 1 }));
  };

  const handleAddToCompare = (product: Product) => {
    dispatch(addToCompare(product));
  };

  return (
    <>
      {/* Floating Action Button (Cart Assistant Symbol) */}
      <motion.button
        onClick={() => setIsOpen(true)}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-full bg-[#2c4152] text-white shadow-2xl hover:shadow-[#2c4152]/50 transition-all border border-[#d5a249]/40 backdrop-blur-md group"
        title="AJIO Personal Stylist & Shopping Assistant"
      >
        <div className="relative">
          <Bot className="w-6 h-6 text-[#d5a249] animate-pulse" />
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-[#2c4152] animate-ping" />
        </div>
        <span className="font-semibold text-sm tracking-wide group-hover:underline">AJIO Stylist</span>
        <Sparkles className="w-4 h-4 text-[#d5a249] animate-spin" style={{ animationDuration: '4s' }} />
      </motion.button>

      {/* Sleek iOS-Style Glassmorphic Modal / Drawer */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-end sm:p-6 bg-black/60 backdrop-blur-sm transition-opacity">
            <motion.div
              initial={{ opacity: 0, y: 100, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 100, scale: 0.95 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="w-full sm:w-[540px] md:w-[620px] h-[85vh] sm:h-[800px] max-h-[90vh] bg-white dark:bg-slate-900 rounded-t-3xl sm:rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden"
            >
              {/* Header */}
              <div className="px-6 py-4 bg-[#2c4152] text-white flex items-center justify-between border-b border-[#d5a249]/20">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-[#d5a249]/20 flex items-center justify-center shadow-lg border border-[#d5a249]/40">
                    <Bot className="w-6 h-6 text-[#d5a249]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-base tracking-tight text-white uppercase">AJIO AI Personal Stylist</h3>
                      <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-[#d5a249] text-[#172337] rounded-full">Pro</span>
                    </div>
                    <p className="text-xs text-slate-300">Connected to 20,000+ fashion styles & AI recs</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition-colors"
                  title="Close Assistant"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Suggested Query Pills */}
              <div className="px-4 py-3 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 overflow-x-auto whitespace-nowrap scrollbar-none flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-amber-500" /> Suggested:
                </span>
                {suggestedQueries.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(q)}
                    className="px-3 py-1.5 text-xs font-medium rounded-full bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all shadow-sm flex-shrink-0"
                  >
                    {q}
                  </button>
                ))}
              </div>

              {/* Chat Messages Area */}
              <div className="flex-1 p-6 overflow-y-auto space-y-6 bg-slate-50/50 dark:bg-slate-900/50">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.sender === 'ai' && (
                      <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                        <Bot className="w-5 h-5" />
                      </div>
                    )}

                    <div className={`max-w-[85%] space-y-3 ${msg.sender === 'user' ? 'order-1' : 'order-2'}`}>
                      <div
                        className={`p-4 rounded-2xl shadow-sm ${
                          msg.sender === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-none font-medium'
                            : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-tl-none font-normal'
                        }`}
                      >
                        <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed whitespace-pre-wrap">
                          {msg.text}
                        </div>
                        <div className={`mt-2 text-[10px] text-right ${msg.sender === 'user' ? 'text-blue-100' : 'text-slate-400'}`}>
                          {msg.timestamp}
                        </div>
                      </div>

                      {/* Render Rich AI Response Components (Top 5 Products & Comparison Table) */}
                      {msg.data && msg.data.recommended_products && msg.data.recommended_products.length > 0 && (
                        <div className="space-y-4 pt-2">
                          <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                            <Award className="w-4 h-4 text-amber-500" />
                            Top Recommended Products ({msg.data.recommended_products.length})
                          </h4>

                          <div className="grid grid-cols-1 gap-3">
                            {msg.data.recommended_products.map((prod, idx) => (
                              <div
                                key={prod.id}
                                className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-indigo-500 transition-all shadow-sm flex items-center gap-4"
                              >
                                <img
                                  src={prod.images?.[0] || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=200'}
                                  alt={prod.title}
                                  className="w-16 h-16 object-cover rounded-lg bg-slate-100 dark:bg-slate-700 flex-shrink-0"
                                />
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-1.5 mb-0.5">
                                    <span className="px-1.5 py-0.5 text-[10px] font-bold bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 rounded">
                                      Rank #{idx + 1}
                                    </span>
                                    {idx === 0 && (
                                      <span className="px-1.5 py-0.5 text-[10px] font-bold bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-300 rounded flex items-center gap-1">
                                        🏆 AI Winner
                                      </span>
                                    )}
                                  </div>
                                  <Link href={`/products/${prod.id}`}>
                                    <h5 className="font-semibold text-sm text-slate-900 dark:text-white truncate hover:text-indigo-600 transition-colors">
                                      {prod.title}
                                    </h5>
                                  </Link>
                                  <div className="flex items-center justify-between mt-1">
                                    <span className="font-bold text-indigo-600 dark:text-indigo-400 text-sm">
                                      ${prod.price.toLocaleString()}
                                    </span>
                                    <span className="text-xs text-slate-500 dark:text-slate-400">
                                      ⭐ {prod.rating} ({prod.reviews_count})
                                    </span>
                                  </div>
                                </div>
                                <div className="flex flex-col gap-1.5">
                                  <button
                                    onClick={() => handleAddToCart(prod)}
                                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs flex items-center gap-1 transition-all shadow-sm"
                                    title="Add to Cart"
                                  >
                                    <ShoppingCart className="w-3.5 h-3.5" /> Cart
                                  </button>
                                  <button
                                    onClick={() => handleAddToCompare(prod)}
                                    className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 font-medium text-[11px] transition-all text-center"
                                  >
                                    + Compare
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Render Retailer Policy / Info Box if available */}
                      {msg.data && msg.data.retailer_info && (
                        <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/50 flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2">
                            <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                            <div>
                              <span className="font-semibold text-slate-900 dark:text-white">Sold by {msg.data.retailer_info.name}</span>
                              <p className="text-slate-500 dark:text-slate-400">{msg.data.retailer_info.shipping_policy}</p>
                            </div>
                          </div>
                          <span className="px-2 py-1 rounded bg-indigo-600 text-white font-bold text-[10px]">Verified Seller</span>
                        </div>
                      )}
                    </div>

                    {msg.sender === 'user' && (
                      <div className="w-8 h-8 rounded-xl bg-slate-300 dark:bg-slate-700 text-slate-800 dark:text-slate-200 flex items-center justify-center flex-shrink-0 mt-1 shadow-md">
                        <User className="w-5 h-5" />
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex items-center gap-2"
                >
                  <input
                    type="text"
                    value={inputQuery}
                    onChange={(e) => setInputQuery(e.target.value)}
                    placeholder="Ask anything (e.g. 'Best laptop under $1500', 'What is the return policy?')..."
                    disabled={isLoading}
                    className="flex-1 px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 transition-all"
                  />
                  <button
                    type="submit"
                    disabled={!inputQuery.trim() || isLoading}
                    className="p-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:opacity-90 disabled:opacity-50 transition-all shadow-md flex-shrink-0"
                  >
                    {isLoading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </button>
                </form>
                <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-slate-400">
                  <span>⚡ Powered by AJIO AI Style & Inference Engine</span>
                  <Link href="/compare" onClick={() => setIsOpen(false)} className="text-indigo-600 dark:text-indigo-400 hover:underline">
                    View Comparison Matrix →
                  </Link>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
