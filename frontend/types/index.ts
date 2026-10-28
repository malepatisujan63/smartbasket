export interface Category {
  id: number;
  name: string;
  slug: string;
  icon?: string;
  description?: string;
  parent_id?: number;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  logo?: string;
  description?: string;
}

export interface Retailer {
  id: number;
  user_id?: number;
  store_name: string;
  store_slug: string;
  store_logo?: string;
  store_banner?: string;
  business_description?: string;
  verified_badge: boolean;
  rating: number;
  location: string;
  followers_count: number;
  years_of_selling: number;
  contact_email?: string;
  contact_phone?: string;
  shipping_policy: string;
  return_policy: string;
  total_sales: number;
  revenue: number;
  created_at: string;
}

export interface Inventory {
  sku: string;
  quantity: number;
  warehouse_location: string;
  status: 'In Stock' | 'Low Stock' | 'Out of Stock' | 'Critical Low Stock' | string;
}

export interface FAQItem {
  question: string;
  answer: string;
}

export interface QNAItem {
  question: string;
  answer: string;
  user?: string;
  date?: string;
}

export interface Product {
  id: number;
  title: string;
  description?: string;
  marketing_description?: string;
  price: number;
  discount_percentage: number;
  rating: number;
  reviews_count: number;
  stock: number;
  brand_id?: number;
  category_id?: number;
  retailer_id?: number;
  images: string[];
  gallery_images?: string[];
  specifications?: Record<string, any>;
  features?: string[];
  country_of_origin?: string;
  warranty?: string;
  model_number?: string;
  sku?: string;
  weight?: string;
  dimensions?: string;
  color_variants?: string[];
  storage_variants?: string[];
  available_sizes?: string[];
  material?: string;
  manufacturing_date?: string;
  shipping_info?: string;
  delivery_estimate?: string;
  return_policy?: string;
  box_contents?: string[];
  package_dimensions?: string;
  faqs?: FAQItem[];
  qna?: QNAItem[];
  related_products?: number[];
  frequently_bought_together?: number[];
  accessories?: number[];
  ai_buying_tips?: string[];
  category?: Category;
  brand?: Brand;
  retailer?: Retailer;
  inventory?: Inventory;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: 'customer' | 'admin' | 'retailer' | string;
  profile_picture?: string;
  is_active: boolean;
  browsing_history?: number[];
  recently_viewed?: number[];
  favorite_categories?: string[];
  preferred_brands?: string[];
  created_at: string;
}

export interface Review {
  id: number;
  product_id: number;
  user_id: number;
  user_name?: string;
  rating: number;
  title?: string;
  comment?: string;
  pros?: string[];
  cons?: string[];
  verified_purchase?: boolean;
  review_images?: string[];
  helpful_votes: number;
  created_at: string;
  user?: User;
}

export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  product: Product;
}

export interface WishlistItem {
  id: number;
  product_id: number;
  product: Product;
}

export interface Address {
  id: number;
  full_name: string;
  phone: string;
  street_address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface OrderItem {
  id?: number;
  order_id?: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  product?: Product;
  product_title?: string;
}

export interface OrderTimelineEvent {
  status: 'Pending' | 'Packed' | 'Shipped' | 'Out For Delivery' | 'Delivered' | string;
  timestamp: string;
  note: string;
}

export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  total_amount: number;
  tax: number;
  delivery_charge: number;
  status: string;
  payment_method: string;
  delivery_address?: Record<string, any>;
  timeline?: OrderTimelineEvent[];
  created_at: string;
  items: OrderItem[];
}

// AI & ML Explanation Types
export interface ExplanationFeature {
  feature: string;
  impact: string;
  value: any;
  weight: number;
}

export interface PredictionExplanation {
  reason: string;
  confidence: number;
  important_features: ExplanationFeature[];
  recommendation: string;
}

export interface RecommendationItem {
  product: Product;
  explanation: PredictionExplanation;
}

export interface CustomerChurnPrediction {
  user_id: number;
  user_email: string;
  churn_probability: number;
  risk_level: 'High' | 'Medium' | 'Low' | string;
  clv_score: number;
  segment_name: string;
  explanation: PredictionExplanation;
}

export interface ForecastDataPoint {
  date: string;
  predicted_revenue: number;
  predicted_orders: number;
  confidence_upper: number;
  confidence_lower: number;
}

export interface DemandForecastItem {
  product_id: number;
  product_title: string;
  current_stock: number;
  thirty_day_demand: number;
  trend: 'Increasing' | 'Stable' | 'Decreasing' | string;
  restock_recommended: boolean;
  explanation: PredictionExplanation;
}

export interface DemandForecastResponse {
  forecast_timeline: ForecastDataPoint[];
  product_demand: DemandForecastItem[];
  summary: {
    expected_30d_revenue: number;
    expected_30d_orders: number;
    growth_rate_vs_last_month: string;
  };
}

export interface InventoryIntelligenceItem {
  product_id: number;
  sku: string;
  title: string;
  category: string;
  quantity: number;
  warehouse: string;
  daily_velocity: string;
  days_until_stockout: number;
  status: string;
  ai_recommendation: string;
}

export interface ReviewAnalyticsResponse {
  total_reviews: number;
  average_rating: number;
  sentiment_breakdown: Record<string, number>;
  recent_reviews: Review[];
}

// Comparison & AI Assistant Types
export interface ComparisonTableItem {
  id: number;
  title: string;
  brand: string;
  price: string;
  rating: string;
  processor?: string;
  ram?: string;
  storage?: string;
  display?: string;
  battery?: string;
  camera?: string;
  warranty?: string;
  pros: string[];
  cons: string[];
}

export interface ComparisonResult {
  products: Product[];
  comparison_table: ComparisonTableItem[];
  awards: {
    overall_winner?: Product;
    best_value?: Product;
    best_performance?: Product;
    best_battery?: Product;
    best_display?: Product;
  };
}

export interface AIAssistantChatResponse {
  message: string;
  recommended_products: Product[];
  comparison_table: ComparisonTableItem[];
  winner?: Product;
  accessories: Product[];
  retailer_info?: {
    name: string;
    rating: number;
    verified: boolean;
    shipping_policy: string;
  };
}
