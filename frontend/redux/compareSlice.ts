import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Product } from '../types';

interface CompareState {
  items: Product[];
  isOpen: boolean;
}

const getInitialCompare = (): Product[] => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('compare_items');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [];
      }
    }
  }
  return [];
};

const initialState: CompareState = {
  items: getInitialCompare(),
  isOpen: false,
};

const compareSlice = createSlice({
  name: 'compare',
  initialState,
  reducers: {
    addToCompare: (state, action: PayloadAction<Product>) => {
      const exists = state.items.some((p) => p.id === action.payload.id);
      if (!exists && state.items.length < 5) {
        state.items.push(action.payload);
        if (typeof window !== 'undefined') {
          localStorage.setItem('compare_items', JSON.stringify(state.items));
        }
      }
      state.isOpen = true;
    },
    removeFromCompare: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter((p) => p.id !== action.payload);
      if (typeof window !== 'undefined') {
        localStorage.setItem('compare_items', JSON.stringify(state.items));
      }
      if (state.items.length === 0) {
        state.isOpen = false;
      }
    },
    clearCompare: (state) => {
      state.items = [];
      state.isOpen = false;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('compare_items');
      }
    },
    toggleCompareBar: (state) => {
      state.isOpen = !state.isOpen;
    },
    openCompareBar: (state) => {
      if (state.items.length > 0) {
        state.isOpen = true;
      }
    },
  },
});

export const { addToCompare, removeFromCompare, clearCompare, toggleCompareBar, openCompareBar } = compareSlice.actions;
export default compareSlice.reducer;
