'use client';

import React from 'react';
import { PredictionExplanation } from '../types';
import { Sparkles, ShieldCheck, TrendingUp, Cpu, CheckCircle2, AlertTriangle, ArrowUpRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface AIReasonWidgetProps {
  explanation: PredictionExplanation;
  title?: string;
  type?: 'recommendation' | 'churn' | 'demand';
}

const AIReasonWidget: React.FC<AIReasonWidgetProps> = ({ explanation, title = "Why AI Recommends This For You", type = 'recommendation' }) => {
  if (!explanation) return null;

  const confidencePercent = Math.round((explanation.confidence || 0.95) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-gradient-to-br from-card via-card to-primary/5 border-2 border-primary/30 rounded-3xl p-6 shadow-xl relative overflow-hidden"
    >
      {/* Background AI Glow */}
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-secondary/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-border/80 mb-4 gap-3 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-primary to-blue-600 text-white shadow-lg shadow-primary/25">
            <Sparkles className="w-5 h-5 fill-white" />
          </div>
          <div>
            <h4 className="text-sm sm:text-base font-black text-foreground tracking-tight flex items-center gap-1.5">
              {title}
            </h4>
            <p className="text-[11px] text-primary font-extrabold uppercase tracking-wider">
              {type === 'recommendation' ? 'Scikit-Learn TF-IDF RecSys' : type === 'churn' ? 'XGBoost SHAP Churn Model' : 'LightGBM Forecasting'}
            </p>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center">
          <span className="text-[10px] text-muted-foreground font-extrabold uppercase tracking-widest">AI Confidence</span>
          <span className="text-base sm:text-lg font-black text-accent flex items-center gap-1">
            {confidencePercent}% <CheckCircle2 className="w-4 h-4 stroke-[2.5]" />
          </span>
        </div>
      </div>

      {/* Primary Reason */}
      <div className="mb-5 bg-muted/60 p-4 rounded-2xl border border-border relative z-10">
        <p className="text-xs sm:text-sm text-foreground font-bold leading-relaxed">
          &ldquo;{explanation.reason}&rdquo;
        </p>
        {explanation.recommendation && (
          <div className="mt-2.5 text-xs font-black text-secondary flex items-center gap-1">
            <ArrowUpRight className="w-4 h-4" /> Action: {explanation.recommendation}
          </div>
        )}
      </div>

      {/* SHAP Important Features Table */}
      {explanation.important_features && explanation.important_features.length > 0 && (
        <div className="space-y-2.5 relative z-10">
          <h5 className="text-xs font-black text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-secondary" /> Key Feature Drivers (SHAP Explainability)
          </h5>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {explanation.important_features.map((feat, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-card border border-border flex items-center justify-between shadow-sm">
                <div>
                  <span className="text-xs font-extrabold text-foreground block">{feat.feature}</span>
                  <span className="text-[11px] text-muted-foreground">Value: <strong className="text-foreground">{feat.value}</strong></span>
                </div>
                <div className="text-right">
                  <span className={`text-[10px] font-black px-2.5 py-1 rounded-full ${feat.impact?.includes('Positive') || feat.impact?.includes('Low Risk') ? 'bg-accent/15 text-accent border border-accent/30' : 'bg-red-500/15 text-red-500 border border-red-500/30'}`}>
                    {feat.impact}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Note */}
      <div className="mt-5 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] text-muted-foreground font-semibold relative z-10">
        <span className="flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-accent" /> Transparent Explainable AI Policy
        </span>
        <span>Model Updated: Live Session</span>
      </div>
    </motion.div>
  );
};

export default AIReasonWidget;
