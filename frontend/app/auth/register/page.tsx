'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { loginSuccess } from '../../../redux/authSlice';
import { authApi } from '../../../services/api';
import { Sparkles, Lock, Mail, User, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

const RegisterPage: React.FC = () => {
  const router = useRouter();
  const dispatch = useDispatch();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await authApi.register({ full_name: fullName, email, password });
      dispatch(loginSuccess(res.data));
      router.push('/');
    } catch (err: any) {
      console.error("Register error", err);
      setError(err.response?.data?.detail || 'Failed to create account. Email may already be in use.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-card border border-border rounded-3xl p-8 sm:p-10 shadow-2xl relative overflow-hidden">
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
          <h2 className="text-xl sm:text-2xl font-black text-foreground pt-1">Create Your Account</h2>
          <p className="text-xs text-muted-foreground font-semibold">Join AJIO for exclusive fashion, footwear and AI personalized curation</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4 relative z-10">
          {error && (
            <div className="p-3.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-500 text-xs font-bold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-3.5">
            <div>
              <label className="text-xs font-extrabold text-foreground block mb-1.5">Your Full Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted-foreground">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-muted/60 border border-border rounded-xl pl-10 pr-4 py-3 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                  placeholder="First and Last Name"
                />
              </div>
            </div>

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
              <label className="text-xs font-extrabold text-foreground block mb-1.5">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted-foreground">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-muted/60 border border-border rounded-xl pl-10 pr-4 py-3 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                  placeholder="At least 6 characters"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-extrabold text-foreground block mb-1.5">Confirm Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted-foreground">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-muted/60 border border-border rounded-xl pl-10 pr-4 py-3 text-xs font-bold text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                  placeholder="Re-type password"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 btn-ajio text-xs uppercase font-black tracking-wider shadow-xl flex items-center justify-center gap-2 mt-2"
          >
            <span>{loading ? 'Creating Account...' : 'Create Your AJIO Account'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="pt-4 border-t border-border text-center text-xs text-muted-foreground font-semibold relative z-10">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-[#d5a249] font-black hover:underline ml-1">
            Sign In here
          </Link>
        </div>

        <div className="text-center text-[11px] text-muted-foreground font-bold flex items-center justify-center gap-1.5 pt-2 relative z-10">
          <ShieldCheck className="w-4 h-4 text-accent" /> Protected by 256-Bit Secure Authentication
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
