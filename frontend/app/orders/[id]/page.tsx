'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ordersApi } from '../../../services/api';
import { Order } from '../../../types';
import Confetti from '../../../components/Confetti';
import { Package, Truck, CheckCircle2, Clock, MapPin, Download, ShieldCheck, ArrowLeft, Sparkles, Check } from 'lucide-react';
import { motion } from 'framer-motion';

const OrderTrackingPage: React.FC = () => {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const orderId = Number(params?.id);
  const isNewSuccess = searchParams.get('success') === 'true';

  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orderId) return;
    const fetchDetail = async () => {
      try {
        const res = await ordersApi.getOrderDetail(orderId);
        setOrder(res.data);
      } catch (err) {
        console.error("Tracking load error", err);
        // Fallback demo order if API offline
        setOrder({
          id: orderId,
          user_id: 1,
          order_number: `ORD-${orderId}-2026`,
          status: 'Processing',
          total_amount: 3499.00,
          tax: 279.92,
          delivery_charge: 0,
          payment_method: 'COD',
          created_at: new Date().toISOString(),
          items: [
            {
              id: 1,
              order_id: orderId,
              product_id: 1,
              quantity: 1,
              unit_price: 3499.00,
              total_price: 3499.00,
              product_title: "MacBook Pro M3 Max 16-Inch Space Black"
            }
          ],
          delivery_address: {
            id: 1,
            user_id: 1,
            full_name: "Alex Chen",
            phone: "+1 (555) 019-2834",
            street_address: "742 Evergreen Terrace, Suite 400",
            city: "Seattle",
            state: "WA",
            postal_code: "98101",
            country: "United States",
            is_default: true
          }
        });
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [orderId]);

  if (loading) {
    return (
      <div className="py-32 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto" />
        <p className="text-sm text-muted-foreground font-bold">Loading Order Tracking Timeline & Invoice...</p>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="py-32 text-center space-y-4">
        <h2 className="text-2xl font-black text-foreground">Order Not Found</h2>
        <button onClick={() => router.push('/orders')} className="px-6 py-3 btn-ajio text-xs uppercase font-black">
          Back to Orders
        </button>
      </div>
    );
  }

  const steps = [
    { title: "Order Placed", desc: "AI Fulfillment Indexed", done: true },
    { title: "Processing", desc: "Packed at AI Warehouse", done: ['Processing', 'Shipped', 'Out For Delivery', 'Delivered'].includes(order.status) },
    { title: "Shipped", desc: "On the way to destination", done: ['Shipped', 'Out For Delivery', 'Delivered'].includes(order.status) },
    { title: "Out For Delivery", desc: "Courier executive dispatched", done: ['Out For Delivery', 'Delivered'].includes(order.status) },
    { title: "Delivered", desc: "Cash collected upon arrival", done: order.status === 'Delivered' }
  ];

  return (
    <div className="space-y-10 pb-24 max-w-6xl mx-auto">
      {/* Trigger Confetti on New Order Success! */}
      {isNewSuccess && <Confetti />}

      {/* Success Banner if newly placed */}
      {isNewSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-accent/20 via-card to-accent/10 border-2 border-accent shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-6"
        >
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-accent text-white flex items-center justify-center font-black flex-shrink-0 shadow-lg">
              <Check className="w-8 h-8 stroke-[3]" />
            </div>
            <div>
              <span className="text-[10px] font-black uppercase tracking-widest text-accent block mb-0.5">Order Confirmed!</span>
              <h2 className="text-xl sm:text-2xl font-black text-foreground">Thank you for your order!</h2>
              <p className="text-xs text-muted-foreground font-semibold max-w-lg mt-1">
                Your Cash on Delivery order <strong className="text-foreground">#{order.order_number}</strong> has been logged in our AI fulfillment network.
              </p>
            </div>
          </div>
          <Link
            href="/products"
            className="px-6 py-3.5 btn-ajio text-xs uppercase font-black tracking-wider shadow-lg whitespace-nowrap"
          >
            Continue Shopping
          </Link>
        </motion.div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <button onClick={() => router.push('/orders')} className="text-xs text-secondary hover:underline font-bold flex items-center gap-1 mb-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to All Orders
          </button>
          <h1 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
            Order #{order.order_number}
          </h1>
          <p className="text-xs text-muted-foreground font-semibold">Placed on {new Date(order.created_at).toLocaleString()}</p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={ordersApi.downloadInvoice(order.id)}
            target="_blank"
            rel="noreferrer"
            className="px-5 py-3 rounded-xl btn-ajio font-black text-xs uppercase tracking-wider flex items-center gap-1.5 shadow-md"
          >
            <Download className="w-4 h-4" /> Download PDF Invoice
          </a>
        </div>
      </div>

      {/* Visual Tracking Timeline */}
      <div className="bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
        <h3 className="text-sm font-black text-secondary uppercase tracking-wider flex items-center gap-1.5">
          <Truck className="w-4 h-4" /> Live Shipment Timeline
        </h3>

        <div className="relative pt-6 pb-2">
          {/* Progress bar line */}
          <div className="hidden sm:block absolute top-10 left-10 right-10 h-1.5 bg-muted rounded-full -z-0 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-secondary to-accent transition-all duration-1000 rounded-full"
              style={{ width: order.status === 'Delivered' ? '100%' : order.status === 'Out For Delivery' ? '75%' : order.status === 'Shipped' ? '50%' : '25%' }}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-6 relative z-10">
            {steps.map((step, idx) => (
              <div key={idx} className="flex sm:flex-col items-center sm:text-center gap-3 sm:gap-2">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-xs shadow-md transition-all ${step.done ? 'bg-secondary text-white scale-110 shadow-secondary/30' : 'bg-muted text-muted-foreground border border-border'}`}>
                  {step.done ? <Check className="w-5 h-5 stroke-[3]" /> : idx + 1}
                </div>
                <div>
                  <h4 className={`text-xs font-black ${step.done ? 'text-foreground' : 'text-muted-foreground'}`}>{step.title}</h4>
                  <p className="text-[10px] text-muted-foreground font-semibold">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left: Ordered Items */}
        <div className="md:col-span-7 bg-card border border-border rounded-3xl p-6 sm:p-8 space-y-4 shadow-xl">
          <h3 className="text-base font-black text-foreground border-b border-border pb-4">
            Items in this Shipment ({order.items?.reduce((a, b) => a + b.quantity, 0)} items)
          </h3>
          <div className="divide-y divide-border/60">
            {order.items?.map((item, idx) => {
              const prodTitle = item.product?.title || item.product_title || `Product #${item.product_id}`;
              const prodImg = item.product?.images?.[0] || 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=200&q=80';
              const brandName = item.product?.brand?.name || 'AJIO LUXE';
              return (
                <div key={idx} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3.5 min-w-0">
                    <img
                      src={prodImg}
                      alt={prodTitle}
                      className="w-16 h-16 rounded-xl object-cover bg-muted border border-border flex-shrink-0"
                    />
                    <div className="min-w-0">
                      <span className="text-[10px] font-black uppercase tracking-wider text-[#d5a249] block">{brandName}</span>
                      <Link href={`/products/${item.product_id}`} className="text-xs font-bold text-foreground hover:text-[#d5a249] transition-colors line-clamp-2">
                        {prodTitle}
                      </Link>
                      <p className="text-[11px] text-muted-foreground font-semibold mt-0.5">
                        Qty: {item.quantity} × ${(item.unit_price || (item.total_price / (item.quantity || 1))).toFixed(2)}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm font-black text-foreground whitespace-nowrap ml-2">${item.total_price.toFixed(2)}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Delivery Address & Summary */}
        <div className="md:col-span-5 space-y-6">
          <div className="bg-card border border-border rounded-3xl p-6 space-y-4 shadow-xl">
            <h3 className="text-xs font-black text-foreground uppercase tracking-wider flex items-center gap-1.5 border-b border-border pb-3">
              <MapPin className="w-4 h-4 text-primary" /> Delivery Destination
            </h3>
            {order.delivery_address && (
              <div className="text-xs space-y-1 font-semibold text-muted-foreground">
                <p className="text-foreground font-black text-sm">{order.delivery_address.full_name}</p>
                <p>{order.delivery_address.street_address}</p>
                <p>{order.delivery_address.city}, {order.delivery_address.state} {order.delivery_address.postal_code}</p>
                <p>{order.delivery_address.country}</p>
                <p className="text-muted-foreground pt-1">Phone: {order.delivery_address.phone}</p>
              </div>
            )}
          </div>

          <div className="bg-card border-2 border-primary/30 rounded-3xl p-6 space-y-3 shadow-xl text-xs font-semibold">
            <h3 className="text-xs font-black text-foreground uppercase tracking-wider border-b border-border pb-3">
              Payment & Total Amount
            </h3>
            <div className="flex justify-between text-muted-foreground">
              <span>Subtotal Amount</span>
              <span className="text-foreground font-bold">${(order.items?.reduce((acc, item) => acc + item.total_price, 0) || order.total_amount).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Estimated Tax (8%)</span>
              <span className="text-foreground font-bold">${(order.tax || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Shipping & Handling</span>
              <span className="text-foreground font-bold">${(order.delivery_charge || 0).toFixed(2)}</span>
            </div>
            <div className="pt-3 border-t border-border flex justify-between items-baseline text-base font-black text-foreground">
              <span>Total Payable</span>
              <span className="text-xl text-secondary">${order.total_amount.toFixed(2)}</span>
            </div>
            <div className="pt-2 flex items-center justify-center gap-1.5 text-accent font-extrabold bg-accent/10 p-3 rounded-xl border border-accent/20">
              <ShieldCheck className="w-4 h-4" /> Cash on Delivery (COD) Protected
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderTrackingPage;
