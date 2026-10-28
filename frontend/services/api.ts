import axios from 'axios';
import { Product, Category, Brand, Retailer, User, Order, CartItem, WishlistItem, Review, DemandForecastResponse, CustomerChurnPrediction, InventoryIntelligenceItem, ReviewAnalyticsResponse, ComparisonResult, AIAssistantChatResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT Access Token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        if (typeof window !== 'undefined') {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            const res = await axios.post(`${API_BASE_URL}/api/auth/refresh?refresh_token=${refreshToken}`);
            const { access_token, refresh_token: newRefresh } = res.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', newRefresh);
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
        }
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// API Endpoints
export const authApi = {
  register: (data: any) => api.post('/api/auth/register', data),
  login: (data: any) => api.post('/api/auth/login', data),
  getMe: () => api.get<User>('/api/auth/me'),
  updateProfile: (data: any) => api.put<User>('/api/auth/profile', data),
  forgotPassword: (email: string) => api.post(`/api/auth/forgot-password?email=${encodeURIComponent(email)}`),
  getAddresses: () => api.get('/api/users/addresses'),
  createAddress: (data: any) => api.post('/api/users/addresses', data),
  deleteAddress: (id: number) => api.delete(`/api/users/addresses/${id}`),
};

export const productsApi = {
  getProducts: (params?: any) => api.get<Product[]>('/api/products', { params }),
  getProductDetail: (id: number) => api.get<Product>(`/api/products/${id}`),
  getRelated: (id: number) => api.get<Product[]>(`/api/products/${id}/related`),
  getFrequentlyBoughtTogether: (id: number) => api.get<Product[]>(`/api/products/${id}/frequently-bought-together`),
  createReview: (id: number, data: { rating: number; title: string; comment: string; pros?: string[]; cons?: string[] }) => api.post(`/api/products/${id}/reviews`, data),
  createProductAdmin: (data: any) => api.post<Product>('/api/products', data),
  getFeaturedProducts: () => api.get<Product[]>('/api/products?is_featured=true'),
};

export const categoriesApi = {
  getCategories: () => api.get<Category[]>('/api/categories'),
  getBrands: () => api.get<Brand[]>('/api/brands'),
};

export const cartApi = {
  getCart: () => api.get<CartItem[]>('/api/cart'),
  addToCart: (product_id: number, quantity: number = 1) => api.post<CartItem>('/api/cart/add', { product_id, quantity }),
  updateQuantity: (id: number, quantity: number) => api.put<CartItem>(`/api/cart/${id}`, { quantity }),
  removeItem: (id: number) => api.delete(`/api/cart/${id}`),
  applyCoupon: (code: string, cart_total: number) => api.post('/api/cart/apply-coupon', { code, cart_total }),
};

export const wishlistApi = {
  getWishlist: () => api.get<WishlistItem[]>('/api/wishlist'),
  toggleWishlist: (product_id: number) => api.post(`/api/wishlist/toggle/${product_id}`),
};

export const ordersApi = {
  createOrder: (data: { items: any[]; delivery_address_id: number; payment_method: string; coupon_code?: string }) => api.post<Order>('/api/orders', data),
  placeOrder: (data: { delivery_address: any; payment_method: string; coupon_code?: string }) => api.post<Order>('/api/orders', data),
  getUserOrders: () => api.get<Order[]>('/api/orders'),
  getOrderDetail: (id: number) => api.get<Order>(`/api/orders/${id}`),
  downloadInvoice: (id: number) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : '';
    return `${API_BASE_URL}/api/orders/${id}/invoice${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
  getAllOrdersAdmin: () => api.get<Order[]>('/api/admin/orders'),
  updateStatusAdmin: (id: number, statusStr: string, note?: string) => api.put<Order>(`/api/admin/orders/${id}/status?status_str=${encodeURIComponent(statusStr)}&note=${encodeURIComponent(note || '')}`),
};

export const usersApi = {
  getAddresses: () => api.get('/api/users/addresses'),
  createAddress: (data: any) => api.post('/api/users/addresses', data),
  deleteAddress: (id: number) => api.delete(`/api/users/addresses/${id}`),
  getNotifications: () => api.get('/api/users/notifications'),
  markAllRead: () => api.put('/api/users/notifications/read-all'),
  getAllUsersAdmin: () => api.get('/api/admin/users'),
};

export const recommendationsApi = {
  getPersonalized: (limit: number = 6, sessionId?: string, recentProductId?: number) => {
    let url = `/api/recommendation/personalized?limit=${limit}`;
    if (sessionId) url += `&session_id=${encodeURIComponent(sessionId)}`;
    if (recentProductId) url += `&recent_product_id=${recentProductId}`;
    return api.get(url);
  },
  getTrending: (limit: number = 8) => api.get(`/api/recommendation/trending?limit=${limit}`),
  getRecentlyViewed: (limit: number = 6, sessionId?: string) => {
    let url = `/api/recommendation/recently-viewed?limit=${limit}`;
    if (sessionId) url += `&session_id=${encodeURIComponent(sessionId)}`;
    return api.get(url);
  },
  getSearchSuggestions: (query?: string) => api.get('/api/search/suggestions', { params: { query } }),
  getRecommendations: (sessionId?: string) => {
    let url = `/api/recommendation/personalized?limit=4`;
    if (sessionId) url += `&session_id=${encodeURIComponent(sessionId)}`;
    return api.get(url);
  },
  getSimilarProducts: (id: number) => api.get<Product[]>(`/api/products/${id}/related`),
  getFrequentlyBoughtTogether: (id: number) => api.get<Product[]>(`/api/products/${id}/frequently-bought-together`),
};

export const analyticsApi = {
  trackEvent: (data: any) => api.post('/api/analytics/events', data),
  getUserHistory: (limit: number = 10, sessionId?: string) =>
    api.get('/api/analytics/user-history', { params: { limit, session_id: sessionId } }),
  getDashboardOverview: () => api.get('/api/dashboard/overview'),
  getDemandForecast: (days: number = 30) => api.get<DemandForecastResponse>(`/api/forecast/demand?days=${days}`),
  getChurnPredictions: () => api.get<CustomerChurnPrediction[]>('/api/churn/predictions'),
  getInventoryIntelligence: () => api.get<InventoryIntelligenceItem[]>('/api/inventory/intelligence'),
  getReviewsAnalytics: () => api.get<ReviewAnalyticsResponse>('/api/reviews/analytics'),
};

export const aiAssistantApi = {
  chat: (data: { query: string; user_id?: number; category_filter?: string; max_price?: number }) => api.post<AIAssistantChatResponse>('/api/ai-assistant/chat', data),
  compare: (product_ids: number[]) => api.post<ComparisonResult>('/api/ai-assistant/compare', { product_ids }),
};

export const retailersApi = {
  getAll: (params?: any) => api.get<Retailer[]>('/api/retailers', { params }),
  getDetail: (id: number) => api.get<Retailer>(`/api/retailers/${id}`),
  getDashboard: () => api.get<any>('/api/retailers/dashboard/me'),
  getProducts: (id: number, params?: any) => api.get<Product[]>(`/api/retailers/${id}/products`, { params }),
  createProduct: (data: any) => api.post<Product>('/api/retailers/products', data),
  updateProduct: (id: number, data: any) => api.put<Product>(`/api/retailers/products/${id}`, data),
  replyReview: (review_id: number, reply: string) => api.post(`/api/retailers/reviews/${review_id}/reply`, { reply }),
};

export const mlopsApi = {
  getModelStatus: () => api.get('/api/mlops/model/status'),
  getModelVersion: () => api.get('/api/mlops/model/version'),
  getSegmentation: () => api.get('/api/mlops/predict/segmentation'),
};
