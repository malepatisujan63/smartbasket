'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Sparkles, Mail, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSubmitted(true);
    }, 1000);
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 group mx-auto">
            <div className="bg-gradient-to-br from-orange-500 to-amber-600 p-2.5 rounded-xl text-slate-950 shadow-md">
              <Sparkles className="w-6 h-6 fill-slate-950" />
            </div>
            <span className="text-2xl font-black tracking-tight text-white flex items-center gap-1">
              AMAZON<span className="text-orange-500">.AI</span>
            </span>
          </Link>
          <h2 className="text-xl font-black text-white">Password Assistance</h2>
          <p className="text-xs text-slate-400">Enter the email address associated with your account</p>
        </div>

        {submitted ? (
          <div className="space-y-4 text-center py-4">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-base font-black text-white">Check Your Email</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              If an account exists for <strong className="text-orange-400">{email}</strong>, we have dispatched a password recovery link with instructions.
            </p>
            <Link
              href="/auth/login"
              className="block w-full py-3 bg-gradient-to-r from-orange-500 to-amber-600 text-slate-950 font-black text-xs uppercase rounded-xl mt-4"
            >
              Return to Sign In
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-orange-500"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-slate-950 font-black text-xs uppercase tracking-wider rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <span>{loading ? 'Sending Link...' : 'Continue'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        <div className="pt-4 border-t border-slate-800 text-center text-xs text-slate-400">
          Remember your password?{' '}
          <Link href="/auth/login" className="text-orange-400 font-bold hover:underline">
            Sign In here
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
