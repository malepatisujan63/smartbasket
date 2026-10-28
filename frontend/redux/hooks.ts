import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

// Type-safe redux hooks
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
