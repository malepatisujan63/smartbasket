'use client';

import React, { useState, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { loginSuccess } from '../../../redux/authSlice';
import { authApi } from '../../../services/api';
import { Sparkles, Lock, Mail, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

const LoginContent: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const dispatch = useDispatch();
  const redirectUrl = searchParams.get('redirect') || '/';

  const [email, setEmail] = useState('admin@amazon-ai.com');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await authApi.login({ email, password });
      dispatch(loginSuccess(res.data));
      router.push(redirectUrl);
    } catch (err: any) {
      console.error("Login error", err);
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (role: 'admin' | 'customer') => {
    if (role === 'admin') {
      setEmail('admin@amazon-ai.com');
      setPassword('admin123');
    } else {
      setEmail('john.doe@gmail.com');
      setPassword('password123');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-card border border-border rounded-3xl p-8 sm:p-10 shadow-2xl relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute -top-12 -right-12 w-48 h-48 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-secondary/10 rounded-full blur-3xl pointer-events-none" />

        <div className="text-center space-y-2 relative z-10">
          <Link href="/" className="inline-flex items-center gap-2 group mx-auto">
            <span className="text-3xl font-black tracking-tight text-[#2c4152] dark:text-white uppercase">
              AJIO
            </span>
            <span className="text-xs bg-[#d5a249] text-[#172337] font-black px-1.5 py-0.5 rounded tracking-widest uppercase">
              LUXE
            </span>
          </Link>
          <h2 className="text-xl sm:text-2xl font-black text-foreground pt-1">Sign In to Your Account</h2>
          <p className="text-xs text-muted-foreground font-semibold">Access personalized recommendations, shopping bag & order tracking</p>
        </div>

        {/* Quick Demo Buttons */}
        <div className="p-4 rounded-2xl bg-muted/60 border border-border space-y-2.5 text-xs relative z-10">
          <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest block text-center">Quick Demo Credentials</span>
          <div className="grid grid-cols-2 gap-2.5">
            <button
              type="button"
              onClick={() => fillDemo('admin')}
              className="py-2 px-3 bg-primary/15 hover:bg-primary/25 text-primary border border-primary/30 font-extrabold rounded-xl transition-all shadow-sm"
            >
              Fill Admin Account
            </button>
            <button
              type="button"
              onClick={() => fillDemo('customer')}
              className="py-2 px-3 bg-secondary/15 hover:bg-secondary/25 text-secondary border border-secondary/30 font-extrabold rounded-xl transition-all shadow-sm"
            >
              Fill Customer Account
            </button>
          </div>
        </div>

        <form onSubmit={handleLogin} className="space-y-5 relative z-10">
          {error && (
            <div className="p-3.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-500 text-xs font-bold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="text-xs font-extrabold text-foreground block mb-1.5">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted-foreground">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-muted/60 border border-border rounded-xl pl-10 pr-4 py-3 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-extrabold text-foreground block">Password</label>
                <Link href="/auth/forgot-password" className="text-[11px] font-bold text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted-foreground">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-muted/60 border border-border rounded-xl pl-10 pr-4 py-3 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 btn-ajio text-xs uppercase font-black tracking-wider shadow-xl flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Signing in...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="pt-4 border-t border-border text-center text-xs text-muted-foreground font-semibold relative z-10">
          New to AJIO?{' '}
          <Link href="/auth/register" className="text-[#d5a249] font-black hover:underline ml-1">
            Create your AJIO account
          </Link>
        </div>

        <div className="text-center text-[11px] text-muted-foreground font-bold flex items-center justify-center gap-1.5 pt-2 relative z-10">
          <ShieldCheck className="w-4 h-4 text-accent" /> Protected by 256-Bit Secure Authentication
        </div>
      </div>
    </div>
  );
};

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="py-24 text-center text-sm font-bold text-muted-foreground animate-pulse">Loading Authentication...</div>}>
      <LoginContent />
    </Suspense>
  );
}
