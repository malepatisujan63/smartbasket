'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { ordersApi } from '../../services/api';
import { Order } from '../../types';
import { Package, Truck, Download, ChevronRight, CheckCircle2, Clock, AlertCircle, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

const OrdersPage: React.FC = () => {
  const router = useRouter();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const hasToken = typeof window !== 'undefined' && localStorage.getItem('access_token');
    if (!isAuthenticated && !hasToken) {
      router.push('/auth/login?redirect=/orders');
      return;
    }
    const fetchOrders = async () => {
      try {
        const res = await ordersApi.getUserOrders();
        setOrders(res.data);
        if (typeof window !== 'undefined') {
          localStorage.setItem('ajio_orders', JSON.stringify(res.data));
        }
      } catch (err) {
        console.error("Orders load error", err);
        if (typeof window !== 'undefined') {
          const cached = localStorage.getItem('ajio_orders');
          if (cached) {
            try { setOrders(JSON.parse(cached)); } catch (e) {}
          }
        }
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [isAuthenticated, router]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Delivered':
        return <span className="bg-[#03a685]/15 text-[#03a685] border border-[#03a685]/30 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Delivered</span>;
      case 'Out For Delivery':
      case 'Shipped':
        return <span className="bg-primary/15 text-primary border border-primary/30 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1"><Truck className="w-3.5 h-3.5" /> {status}</span>;
      default:
        return <span className="bg-amber-500/15 text-amber-500 border border-amber-500/30 px-3 py-1 rounded-full text-xs font-black flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="py-32 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto" />
        <p className="text-sm text-muted-foreground font-bold">Loading Your AJIO Orders...</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 pb-24 max-w-6xl mx-auto">
      <div className="border-b border-border pb-6">
        <h1 className="text-2xl sm:text-4xl font-black text-foreground tracking-tight flex items-center gap-2.5">
          <Package className="w-8 h-8 text-secondary" /> Your Orders & Tracking <span className="text-sm font-extrabold bg-[#d5a249]/15 text-[#d5a249] px-3 py-1 rounded-full">({orders.length})</span>
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground font-semibold mt-1">Track shipment timelines, delivery milestones and download verified Cash on Delivery PDF invoices</p>
      </div>

      {orders.length === 0 ? (
        <div className="py-24 text-center space-y-6 max-w-lg mx-auto bg-card border border-border rounded-3xl p-8 shadow-xl">
          <div className="w-20 h-20 rounded-full bg-muted text-secondary flex items-center justify-center mx-auto shadow-inner">
            <Package className="w-10 h-10 stroke-[1.5]" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-black text-foreground">No Past Orders Found</h2>
            <p className="text-xs text-muted-foreground font-semibold">
              When you place an order with Cash on Delivery, it will appear here with live tracking!
            </p>
          </div>
          <Link
            href="/products"
            className="inline-block px-8 py-4 btn-ajio text-xs uppercase font-black tracking-wider shadow-lg"
          >
            Start Shopping Now
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <motion.div
              layout
              key={order.id}
              className="bg-card border border-border rounded-3xl overflow-hidden shadow-md hover:shadow-xl transition-all group"
            >
              {/* Order Header */}
              <div className="bg-muted/40 p-5 sm:p-6 border-b border-border flex flex-wrap items-center justify-between gap-4 text-xs font-semibold">
                <div className="flex flex-wrap items-center gap-8">
                  <div>
                    <span className="text-muted-foreground uppercase font-black block text-[10px]">Order Placed</span>
                    <span className="text-foreground font-black">{new Date(order.created_at).toLocaleDateString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground uppercase font-black block text-[10px]">Total Amount</span>
                    <span className="text-secondary font-black text-sm">${order.total_amount.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground uppercase font-black block text-[10px]">Payment Method</span>
                    <span className="text-[#03a685] font-extrabold flex items-center gap-1">
                      <ShieldCheck className="w-4 h-4" /> 100% Cash on Delivery
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <a
                    href={ordersApi.downloadInvoice(order.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3.5 py-2 rounded-xl bg-card hover:bg-muted text-foreground font-bold flex items-center gap-1.5 transition-colors border border-border shadow-sm text-xs"
                  >
                    <Download className="w-3.5 h-3.5 text-secondary" /> Invoice PDF
                  </a>
                  <Link
                    href={`/orders/${order.id}`}
                    className="px-5 py-2.5 rounded-xl btn-ajio text-xs font-black uppercase tracking-wider flex items-center gap-1 shadow-md"
                  >
                    <span>Track Order</span>
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>

              {/* Order Content */}
              <div className="p-5 sm:p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="space-y-3 flex-1 w-full">
                  <div className="flex items-center gap-3">
                    {getStatusBadge(order.status)}
                    <span className="text-xs text-muted-foreground font-bold">Order #{order.order_number}</span>
                  </div>

                  {/* Items preview with product thumbnails and titles */}
                  <div className="space-y-3 pt-2">
                    {order.items?.map((item, idx) => {
                      const prodTitle = item.product?.title || item.product_title || `Product #${item.product_id}`;
                      const prodImg = item.product?.images?.[0] || 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=200&q=80';
                      const brandName = item.product?.brand?.name || 'AJIO LUXE';
                      return (
                        <div key={idx} className="flex items-center justify-between text-xs font-semibold bg-muted/30 p-3.5 rounded-2xl border border-border gap-4 hover:border-primary/40 transition-colors">
                          <div className="flex items-center gap-3.5 min-w-0">
                            <img
                              src={prodImg}
                              alt={prodTitle}
                              className="w-14 h-14 rounded-xl object-cover bg-card border border-border flex-shrink-0"
                            />
                            <div className="min-w-0">
                              <span className="text-[10px] font-black uppercase tracking-wider text-[#d5a249] block">{brandName}</span>
                              <Link href={`/products/${item.product_id}`} className="text-foreground font-extrabold hover:text-[#d5a249] transition-colors line-clamp-1">
                                {prodTitle}
                              </Link>
                              <span className="text-[11px] text-muted-foreground block mt-0.5">
                                Qty: {item.quantity} × ${(item.unit_price || (item.total_price / (item.quantity || 1))).toFixed(2)}
                              </span>
                            </div>
                          </div>
                          <span className="text-foreground font-black text-sm whitespace-nowrap ml-2">${item.total_price.toFixed(2)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrdersPage;
