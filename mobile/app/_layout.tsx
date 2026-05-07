import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Stack, useRouter, useSegments } from 'expo-router';
import { useEffect } from 'react';
import { useAuth } from '../src/store/auth';
import { registerPush } from '../src/utils/push';

const qc = new QueryClient();

export default function RootLayout() {
  const { isLoggedIn, hydrate } = useAuth();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => { hydrate(); }, []);

  useEffect(() => {
    const inAuthScreen = segments[0] === 'login';
    if (!isLoggedIn && !inAuthScreen) router.replace('/login');
    if (isLoggedIn && inAuthScreen) router.replace('/');
    if (isLoggedIn) registerPush().catch(() => {});
  }, [isLoggedIn, segments]);

  return (
    <QueryClientProvider client={qc}>
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#0a0a0a' } }} />
    </QueryClientProvider>
  );
}
