'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../redux/store';
import { logout } from '../redux/authSlice';
import { toggleTheme } from '../redux/themeSlice';
import { openCartDrawer } from '../redux/cartSlice';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ShoppingCart, Heart, User, Menu, Sun, Moon, Sparkles, ChevronDown, LogOut, ShieldAlert, Package, Sliders, Bell, CheckCircle2, Zap } from 'lucide-react';
import FloatingSearchBar from './FloatingSearchBar';
import MegaMenu from './MegaMenu';

const Navbar: React.FC = () => {
  const router = useRouter();
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const cartItems = useSelector((state: RootState) => state.cart.items);
  const wishlistItems = useSelector((state: RootState) => state.wishlist.items);
  const themeMode = useSelector((state: RootState) => state.theme.mode);

  const [megaMenuOpen, setMegaMenuOpen] = useState(false);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) setScrolled(true);
      else setScrolled(false);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    dispatch(logout());
    setAccountMenuOpen(false);
    router.push('/');
  };

  const totalCartCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <header className={`sticky top-0 z-40 transition-all duration-500 ${scrolled ? 'glass-nav py-2.5 shadow-lg' : 'bg-background/95 backdrop-blur-sm py-4 border-b border-border/40'}`}>
      {/* Top Banner Notice - AJIO Style */}
      <div className="bg-[#2c4152] text-white px-4 py-1.5 text-xs font-bold text-center flex items-center justify-center gap-2 shadow-sm tracking-wide">
        <span className="text-[#d5a249] font-black uppercase text-[11px] tracking-wider">AJIOMANIA SALE:</span>
        <span className="hidden sm:inline">FLAT 50% - 90% OFF | USE CODE: <strong className="text-[#d5a249]">AJIO500</strong></span>
        <span className="bg-[#d5a249] text-[#172337] px-2.5 py-0.5 rounded text-[10px] uppercase font-black tracking-wider ml-1 shadow-sm">
          100% Cash On Delivery
        </span>
      </div>

      {/* Main Nav Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4 pt-2">
        {/* Brand Logo & Mega Menu Trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMegaMenuOpen(!megaMenuOpen)}
            className="p-2.5 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted/80 transition-all flex items-center gap-2 font-bold text-sm border border-transparent hover:border-border"
            aria-label="Open Category Menu"
          >
            <Menu className="w-5 h-5 text-[#2c4152] dark:text-[#d5a249]" />
            <span className="hidden sm:inline font-extrabold uppercase text-xs tracking-wider">Menu</span>
          </button>

          <Link href="/" className="flex items-center gap-2 group">
            <span className="text-2xl sm:text-3xl font-black tracking-tight text-[#2c4152] dark:text-white font-sans uppercase">
              AJIO
            </span>
            <span className="text-[10px] bg-[#d5a249] text-[#172337] font-black px-1.5 py-0.5 rounded tracking-widest uppercase">
              LUXE
            </span>
          </Link>
        </div>

        {/* Floating AI Search Bar */}
        <div className="flex-1 max-w-2xl mx-4">
          <FloatingSearchBar />
        </div>

        {/* Right Navigation Icons */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Theme Toggle */}
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => dispatch(toggleTheme())}
            className="p-2.5 rounded-xl bg-card border border-border text-muted-foreground hover:text-secondary hover:border-secondary/40 transition-all shadow-sm hover:shadow-md"
            title={`Switch to ${themeMode === 'light' ? 'Dark' : 'Light'} Mode`}
          >
            {themeMode === 'light' ? <Moon className="w-5 h-5 text-primary" /> : <Sun className="w-5 h-5 text-secondary" />}
          </motion.button>

          {/* Notifications Icon */}
          <div className="relative">
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className="p-2.5 rounded-xl bg-card border border-border text-muted-foreground hover:text-primary hover:border-primary/40 transition-all shadow-sm hover:shadow-md relative"
              title="AI System Notifications"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-accent animate-ping" />
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-accent" />
            </motion.button>

            <AnimatePresence>
              {notificationsOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-72 bg-card border border-border rounded-2xl shadow-2xl p-4 z-50 backdrop-blur-xl"
                >
                  <div className="flex items-center justify-between pb-2 border-b border-border mb-3">
                    <span className="text-xs font-black uppercase tracking-wider text-foreground flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-secondary" /> AI Live Intelligence
                    </span>
                    <span className="text-[10px] bg-accent/20 text-accent font-bold px-2 py-0.5 rounded-full border border-accent/30">
                      100% Active
                    </span>
                  </div>
                  <div className="space-y-2.5 text-xs">
                    <div className="p-2 rounded-xl bg-muted/60 border border-border/60">
                      <p className="font-bold text-foreground">RecSys TF-IDF Matrix Updated</p>
                      <p className="text-[11px] text-muted-foreground mt-0.5">Catalog indexed with 94.2% peer similarity accuracy.</p>
                    </div>
                    <div className="p-2 rounded-xl bg-muted/60 border border-border/60">
                      <p className="font-bold text-foreground">Cash on Delivery Guaranteed</p>
                      <p className="text-[11px] text-muted-foreground mt-0.5">Zero pre-payment required across all 50 states.</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Wishlist */}
          <Link
            href="/wishlist"
            className="relative p-2.5 rounded-xl bg-card border border-border text-muted-foreground hover:text-red-500 hover:border-red-500/40 transition-all flex items-center gap-1.5 shadow-sm hover:shadow-md"
          >
            <Heart className="w-5 h-5" />
            <span className="hidden lg:inline text-xs font-extrabold text-foreground">Wishlist</span>
            {wishlistItems.length > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1.5 -right-1.5 bg-red-500 text-white text-[10px] font-black w-5 h-5 rounded-full flex items-center justify-center shadow-md animate-pulse"
              >
                {wishlistItems.length}
              </motion.span>
            )}
          </Link>

          {/* Cart Icon -> Opens Slide-out Drawer */}
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => dispatch(openCartDrawer())}
            className="relative p-2 px-3.5 rounded-xl bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/30 hover:border-primary text-primary transition-all flex items-center gap-2.5 shadow-sm hover:shadow-md group"
            title="Open Shopping Cart Drawer"
          >
            <ShoppingCart className="w-5 h-5 text-secondary group-hover:scale-110 transition-transform" />
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-[10px] text-muted-foreground font-bold leading-none uppercase">Bag</span>
              <span className="text-xs font-black text-foreground leading-none mt-0.5">
                ${cartItems.reduce((acc, item) => acc + item.product.price * item.quantity, 0).toFixed(0)}
              </span>
            </div>
            <span className="bg-secondary text-white text-xs font-black w-5 h-5 rounded-full flex items-center justify-center shadow-md ml-0.5">
              {totalCartCount}
            </span>
          </motion.button>

          {/* Account & Lists */}
          <div className="relative">
            <button
              onClick={() => setAccountMenuOpen(!accountMenuOpen)}
              className="flex items-center gap-2 p-1.5 px-3 rounded-xl bg-card border border-border hover:border-primary/50 transition-all shadow-sm hover:shadow-md"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-blue-600 flex items-center justify-center text-white font-black text-xs shadow-inner">
                {isAuthenticated && user?.full_name ? user.full_name.charAt(0).toUpperCase() : <User className="w-4 h-4" />}
              </div>
              <div className="hidden xl:flex flex-col text-left">
                <span className="text-[10px] text-muted-foreground font-extrabold leading-none uppercase">
                  {isAuthenticated ? `Hello, ${user?.full_name?.split(' ')[0]}` : 'Hello, Sign in'}
                </span>
                <span className="text-xs font-black text-foreground leading-none mt-0.5 flex items-center gap-1">
                  Account <ChevronDown className="w-3 h-3 text-muted-foreground" />
                </span>
              </div>
            </button>

            {/* Account Dropdown */}
            <AnimatePresence>
              {accountMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-64 bg-card border border-border rounded-2xl shadow-2xl p-3.5 z-50 backdrop-blur-2xl"
                >
                  {!isAuthenticated ? (
                    <div className="p-3.5 bg-muted/60 rounded-xl border border-border/80 text-center mb-3">
                      <p className="text-xs text-foreground font-bold mb-2.5">Access personalized AI recommendations & order tracking</p>
                      <Link
                        href="/auth/login"
                        onClick={() => setAccountMenuOpen(false)}
                        className="block w-full py-2.5 btn-blue-gradient text-xs uppercase tracking-wider text-center shadow-md font-black"
                      >
                        Sign in to Account
                      </Link>
                      <p className="text-[10px] text-muted-foreground mt-2 font-medium">
                        New customer? <Link href="/auth/register" onClick={() => setAccountMenuOpen(false)} className="text-secondary hover:underline font-bold">Start here.</Link>
                      </p>
                    </div>
                  ) : (
                    <div className="p-2.5 mb-2 border-b border-border">
                      <p className="text-xs font-black text-foreground">{user?.full_name}</p>
                      <p className="text-[11px] text-muted-foreground truncate">{user?.email}</p>
                      {user?.role === 'admin' && (
                        <span className="inline-block mt-1.5 bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">
                          AI Admin Hub Access
                        </span>
                      )}
                    </div>
                  )}

                  <div className="space-y-1">
                    <Link
                      href="/profile"
                      onClick={() => setAccountMenuOpen(false)}
                      className="flex items-center gap-2.5 p-2 rounded-xl text-xs font-bold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                    >
                      <User className="w-4 h-4 text-primary" /> Your Profile & Addresses
                    </Link>
                    <Link
                      href="/orders"
                      onClick={() => setAccountMenuOpen(false)}
                      className="flex items-center gap-2.5 p-2 rounded-xl text-xs font-bold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                    >
                      <Package className="w-4 h-4 text-secondary" /> Your Orders & Tracking
                    </Link>
                    <Link
                      href="/wishlist"
                      onClick={() => setAccountMenuOpen(false)}
                      className="flex items-center gap-2.5 p-2 rounded-xl text-xs font-bold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                    >
                      <Heart className="w-4 h-4 text-red-500" /> Your Wishlist ({wishlistItems.length})
                    </Link>

                    {user?.role === 'admin' && (
                      <Link
                        href="/admin"
                        onClick={() => setAccountMenuOpen(false)}
                        className="flex items-center gap-2.5 p-2.5 rounded-xl text-xs font-black text-purple-600 dark:text-purple-300 bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 transition-all mt-2"
                      >
                        <ShieldAlert className="w-4 h-4 text-purple-500" /> Launch AI Admin Hub
                      </Link>
                    )}

                    {isAuthenticated && (
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2.5 p-2 rounded-xl text-xs font-bold text-red-500 hover:bg-red-500/10 transition-colors mt-2 border-t border-border/80 pt-2"
                      >
                        <LogOut className="w-4 h-4" /> Sign out
                      </button>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Sub Navigation Bar - AJIO Fashion & Lifestyle Categories */}
      <div className="bg-card border-t border-border/80 px-4 py-2.5 text-xs font-bold text-foreground flex items-center gap-7 overflow-x-auto no-scrollbar max-w-7xl mx-auto uppercase tracking-wider">
        <Link href="/products?category_slug=fashion" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Men
        </Link>
        <Link href="/products?category_slug=fashion" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Women
        </Link>
        <Link href="/products?category_slug=shoes" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Footwear
        </Link>
        <Link href="/products?category_slug=beauty" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Beauty
        </Link>
        <Link href="/products?category_slug=smart-watches" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Watches
        </Link>
        <Link href="/products?category_slug=electronics" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Tech & Audio
        </Link>
        <Link href="/products?category_slug=laptops" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Laptops
        </Link>
        <Link href="/products?category_slug=furniture" className="hover:text-[#d5a249] transition-colors whitespace-nowrap font-extrabold">
          Home & Luxe
        </Link>
        <Link href="/products?sort_by=reviews" className="text-[#03a685] hover:underline transition-colors whitespace-nowrap font-black flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-[#d5a249]" /> Deals (Min 50% Off)
        </Link>
        <Link href="/products" className="text-[#d5a249] hover:underline transition-colors whitespace-nowrap font-black ml-auto">
          AI Recommendations
        </Link>
        {user?.role === 'admin' && (
          <Link href="/admin" className="text-purple-600 dark:text-purple-400 font-black hover:underline whitespace-nowrap flex items-center gap-1">
            <Sliders className="w-3.5 h-3.5" /> Admin Hub
          </Link>
        )}
      </div>

      {/* Mega Menu Overlay */}
      {megaMenuOpen && <MegaMenu onClose={() => setMegaMenuOpen(false)} />}
    </header>
  );
};

export default Navbar;
