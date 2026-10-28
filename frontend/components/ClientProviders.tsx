'use client';

import React, { useState, useEffect } from 'react';
import { Provider } from 'react-redux';
import { store } from '../redux/store';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { setTheme } from '../redux/themeSlice';

const ThemeSync: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useAppDispatch();
  const { mode } = useAppSelector((state) => state.theme);

  useEffect(() => {
    // 1. Initial sync with DOM
    if (mode === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    }

    // 2. Listen to OS preference changes if no manual override is saved
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleOSChange = (e: MediaQueryListEvent) => {
      const saved = localStorage.getItem('theme');
      if (!saved) {
        dispatch(setTheme(e.matches ? 'dark' : 'light'));
      }
    };

    if (mediaQuery?.addEventListener) {
      mediaQuery.addEventListener('change', handleOSChange);
      return () => mediaQuery.removeEventListener('change', handleOSChange);
    }
  }, [mode, dispatch]);

  return <>{children}</>;
};

interface ClientProvidersProps {
  children: React.ReactNode;
}

const ClientProviders: React.FC<ClientProvidersProps> = ({ children }) => {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  }));

  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeSync>
          {children}
        </ThemeSync>
      </QueryClientProvider>
    </Provider>
  );
};

export default ClientProviders;
