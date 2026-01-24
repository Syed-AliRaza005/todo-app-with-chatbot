'use client';

import { AuthProvider } from '@/hooks/useAuth';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState } from 'react';
import ChatWidget from '@/components/ChatWidget';

// Separate providers for public and protected routes
export default function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
        <ReactQueryDevtools initialIsOpen={false} />
        <ChatWidget />
      </AuthProvider>
    </QueryClientProvider>
  );
}

// Public providers (without auth) for public routes
export function PublicProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
      <ChatWidget />
    </QueryClientProvider>
  );
}