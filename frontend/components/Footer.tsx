'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, ArrowUp, ShieldCheck, Cpu, Heart, CheckCircle2, Lock } from 'lucide-react';

const Footer: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="bg-card text-muted-foreground border-t border-border mt-24">
      {/* Back to top button */}
      <button
        onClick={scrollToTop}
        className="w-full bg-[#2c4152] hover:bg-[#1f2e3a] text-white font-black py-3.5 text-xs uppercase tracking-widest transition-colors flex items-center justify-center gap-2 border-b border-border shadow-inner"
      >
        <ArrowUp className="w-4 h-4 text-[#d5a249]" /> Back to top of AJIO
      </button>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        {/* Main Columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pb-14 border-b border-border">
          <div>
            <h4 className="text-foreground font-black text-sm uppercase tracking-wider mb-4">Get to Know Us</h4>
            <ul className="space-y-3 text-xs font-semibold text-muted-foreground">
              <li><Link href="/" className="hover:text-primary transition-colors">About AJIO Platform</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Careers in Fashion & AI</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Press Releases & Style Research</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">AJIO RecSys & SHAP Explainability</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-foreground font-black text-sm uppercase tracking-wider mb-4">Make Money with Us</h4>
            <ul className="space-y-3 text-xs font-semibold text-muted-foreground">
              <li><Link href="/" className="hover:text-primary transition-colors">Sell on AJIO Marketplace</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Supply to AJIO Logistics</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Become an Affiliate Partner</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Advertise Your Styles</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-foreground font-black text-sm uppercase tracking-wider mb-4">AJIO Payment Services</h4>
            <ul className="space-y-3 text-xs font-semibold text-muted-foreground">
              <li className="flex items-center gap-1.5 text-accent font-extrabold">
                <CheckCircle2 className="w-4 h-4" /> Cash on Delivery (COD Exclusive)
              </li>
              <li><Link href="/" className="hover:text-primary transition-colors">AJIO Luxe Rewards Card</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Shop with Points & Coupons</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Reload Your Account Balance</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-foreground font-black text-sm uppercase tracking-wider mb-4">Let Us Help You</h4>
            <ul className="space-y-3 text-xs font-semibold text-muted-foreground">
              <li><Link href="/profile" className="hover:text-primary transition-colors">Your Account & Profile</Link></li>
              <li><Link href="/orders" className="hover:text-primary transition-colors">Your Orders & Tracking</Link></li>
              <li><Link href="/wishlist" className="hover:text-primary transition-colors">Your Wishlist</Link></li>
              <li><Link href="/cart" className="hover:text-primary transition-colors">Shopping Cart & COD Checkout</Link></li>
              <li><Link href="/" className="hover:text-primary transition-colors">Help & Customer Service</Link></li>
            </ul>
          </div>
        </div>

        {/* Brand & Tech Stack Disclaimer */}
        <div className="pt-10 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3.5">
            <div className="bg-[#2c4152] p-2.5 rounded-xl text-white shadow-lg border border-[#d5a249]/30">
              <span className="text-xl font-black tracking-tight text-white font-sans uppercase">
                AJIO
              </span>
            </div>
            <div>
              <span className="text-lg font-black tracking-tight text-foreground flex items-center gap-1.5 uppercase">
                AJIO <span className="text-[#d5a249] text-xs font-black bg-[#d5a249]/15 px-1.5 py-0.5 rounded">LUXE</span>
              </span>
              <p className="text-xs text-muted-foreground font-bold">Fashion, Footwear & AI Retail Sales Intelligence Platform</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 text-xs text-foreground font-extrabold">
            <span className="flex items-center gap-1.5 bg-muted px-3.5 py-2 rounded-xl border border-border shadow-sm">
              <Cpu className="w-4 h-4 text-[#2c4152] dark:text-[#d5a249]" /> Scikit-Learn • XGBoost
            </span>
            <span className="flex items-center gap-1.5 bg-muted px-3.5 py-2 rounded-xl border border-border shadow-sm">
              <ShieldCheck className="w-4 h-4 text-[#03a685]" /> SHAP Explainability
            </span>
            <span className="flex items-center gap-1.5 bg-muted px-3.5 py-2 rounded-xl border border-border shadow-sm">
              <Lock className="w-4 h-4 text-[#d5a249]" /> 100% Cash on Delivery
            </span>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-border text-center text-muted-foreground text-xs font-medium">
          <p>© 2026 AJIO Retail Intelligence Platform. High-Fashion & E-Commerce Powered by Next.js 15, React 19, and FastAPI.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
