import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { CartItem, Product } from '../types';

interface CartState {
  items: CartItem[];
  subtotal: number;
  tax: number;
  delivery: number;
  discount: number;
  total: number;
  couponCode: string | null;
  isCartOpen: boolean;
}

const getInitialCart = (): CartItem[] => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('cart');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { return []; }
    }
  }
  return [];
};

const calculateTotals = (items: CartItem[], discount: number = 0) => {
  const subtotal = items.reduce((acc, item) => acc + item.product.price * item.quantity, 0);
  const tax = Math.round(subtotal * 0.08 * 100) / 100;
  const delivery = subtotal === 0 ? 0 : (subtotal >= 100 ? 0 : 10);
  const total = Math.round(Math.max(0, subtotal + tax + delivery - discount) * 100) / 100;
  return { subtotal: Math.round(subtotal * 100) / 100, tax, delivery, total };
};

const initialItems = getInitialCart();
const initialTotals = calculateTotals(initialItems);

const initialState: CartState = {
  items: initialItems,
  ...initialTotals,
  discount: 0,
  couponCode: null,
  isCartOpen: false,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    openCartDrawer: (state) => {
      state.isCartOpen = true;
    },
    closeCartDrawer: (state) => {
      state.isCartOpen = false;
    },
    toggleCartDrawer: (state) => {
      state.isCartOpen = !state.isCartOpen;
    },
    setCart: (state, action: PayloadAction<CartItem[]>) => {
      state.items = action.payload;
      const totals = calculateTotals(state.items, state.discount);
      state.subtotal = totals.subtotal;
      state.tax = totals.tax;
      state.delivery = totals.delivery;
      state.total = totals.total;
      if (typeof window !== 'undefined') {
        localStorage.setItem('cart', JSON.stringify(state.items));
      }
    },
    addToCart: (state, action: PayloadAction<{ product: Product; quantity: number }>) => {
      const { product, quantity } = action.payload;
      const existing = state.items.find((item) => item.product_id === product.id);
      if (existing) {
        existing.quantity += quantity;
      } else {
        state.items.push({
          id: Date.now(),
          product_id: product.id,
          quantity,
          product,
        });
      }
      const totals = calculateTotals(state.items, state.discount);
      state.subtotal = totals.subtotal;
      state.tax = totals.tax;
      state.delivery = totals.delivery;
      state.total = totals.total;
      state.isCartOpen = true; // Automatically slide out drawer for premium UX
      if (typeof window !== 'undefined') {
        localStorage.setItem('cart', JSON.stringify(state.items));
      }
    },
    updateQuantity: (state, action: PayloadAction<{ id: number; quantity: number }>) => {
      const { id, quantity } = action.payload;
      if (quantity <= 0) {
        state.items = state.items.filter((item) => item.id !== id && item.product_id !== id);
      } else {
        const existing = state.items.find((item) => item.id === id || item.product_id === id);
        if (existing) existing.quantity = quantity;
      }
      const totals = calculateTotals(state.items, state.discount);
      state.subtotal = totals.subtotal;
      state.tax = totals.tax;
      state.delivery = totals.delivery;
      state.total = totals.total;
      if (typeof window !== 'undefined') {
        localStorage.setItem('cart', JSON.stringify(state.items));
      }
    },
    removeFromCart: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter((item) => item.id !== action.payload && item.product_id !== action.payload);
      const totals = calculateTotals(state.items, state.discount);
      state.subtotal = totals.subtotal;
      state.tax = totals.tax;
      state.delivery = totals.delivery;
      state.total = totals.total;
      if (typeof window !== 'undefined') {
        localStorage.setItem('cart', JSON.stringify(state.items));
      }
    },
    applyCouponSuccess: (state, action: PayloadAction<{ code: string; discount_amount: number; final_total: number }>) => {
      state.couponCode = action.payload.code;
      state.discount = action.payload.discount_amount;
      state.total = action.payload.final_total;
    },
    clearCart: (state) => {
      state.items = [];
      state.subtotal = 0;
      state.tax = 0;
      state.delivery = 0;
      state.discount = 0;
      state.total = 0;
      state.couponCode = null;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('cart');
      }
    },
  },
});

export const { openCartDrawer, closeCartDrawer, toggleCartDrawer, setCart, addToCart, updateQuantity, removeFromCart, applyCouponSuccess, clearCart } = cartSlice.actions;
export default cartSlice.reducer;
