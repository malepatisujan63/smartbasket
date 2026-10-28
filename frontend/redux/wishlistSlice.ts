import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { WishlistItem, Product } from '../types';

interface WishlistState {
  items: WishlistItem[];
}

const getInitialWishlist = (): WishlistItem[] => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('wishlist');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { return []; }
    }
  }
  return [];
};

const initialState: WishlistState = {
  items: getInitialWishlist(),
};

const wishlistSlice = createSlice({
  name: 'wishlist',
  initialState,
  reducers: {
    setWishlist: (state, action: PayloadAction<WishlistItem[]>) => {
      state.items = action.payload;
      if (typeof window !== 'undefined') {
        localStorage.setItem('wishlist', JSON.stringify(state.items));
      }
    },
    toggleWishlistItem: (state, action: PayloadAction<Product>) => {
      const product = action.payload;
      const existingIndex = state.items.findIndex((item) => item.product_id === product.id);
      if (existingIndex >= 0) {
        state.items.splice(existingIndex, 1);
      } else {
        state.items.push({
          id: Date.now(),
          product_id: product.id,
          product,
        });
      }
      if (typeof window !== 'undefined') {
        localStorage.setItem('wishlist', JSON.stringify(state.items));
      }
    },
    clearWishlist: (state) => {
      state.items = [];
      if (typeof window !== 'undefined') {
        localStorage.removeItem('wishlist');
      }
    },
  },
});

export const { setWishlist, toggleWishlistItem, clearWishlist } = wishlistSlice.actions;
export default wishlistSlice.reducer;
