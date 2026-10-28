import api from './api';

// Persistent Client Session Token for Real-time In-Session Behavioral Personalization
export const getSessionId = (): string => {
  if (typeof window === 'undefined') return 'server_session';
  let sessionId = localStorage.getItem('amazon_ai_session_id');
  if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).substring(2, 15) + '_' + Date.now().toString(36);
    localStorage.setItem('amazon_ai_session_id', sessionId);
  }
  return sessionId;
};

export interface TrackEventPayload {
  productId?: number;
  categoryId?: number;
  query?: string;
  dwellSeconds?: number;
  metadata?: Record<string, any>;
}

/**
 * Streams real-time user touchpoints (views, clicks, searches, cart additions, wishlist adds)
 * into the AI Analytics & Personalization pipeline.
 */
export const trackEvent = async (
  eventType: 'view' | 'click' | 'search' | 'cart_add' | 'wishlist_add' | 'compare' | 'dwell',
  payload: TrackEventPayload = {}
): Promise<void> => {
  try {
    const sessionId = getSessionId();
    const eventBody = {
      event_type: eventType,
      product_id: payload.productId,
      category_id: payload.categoryId,
      query: payload.query,
      metadata_json: {
        session_id: sessionId,
        dwell_seconds: payload.dwellSeconds,
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : 'browser',
        path: typeof window !== 'undefined' ? window.location.pathname : '',
        timestamp: new Date().toISOString(),
        ...(payload.metadata || {}),
      },
    };

    // Use sendBeacon if available for quick non-blocking flush on unload/click
    if (eventType === 'click' && typeof navigator !== 'undefined' && navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(eventBody)], { type: 'application/json' });
      navigator.sendBeacon('http://localhost:8000/api/analytics/events', blob);
      return;
    }

    // Standard asynchronous API dispatch
    await api.post('/api/analytics/events', eventBody);
  } catch (err) {
    // Fail silently in client to never disrupt user experience
    console.debug('Telemetry event non-critical log:', err);
  }
};
