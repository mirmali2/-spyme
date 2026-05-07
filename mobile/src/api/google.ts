import * as Google from 'expo-auth-session/providers/google';
import * as WebBrowser from 'expo-web-browser';
import { useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';
import { api } from './client';

WebBrowser.maybeCompleteAuthSession();

export interface GoogleConfig {
  expoClientId: string;     // for Expo Go testing
  iosClientId: string;
  androidClientId: string;
  webClientId: string;      // backend-side audience verification
}

const CONFIG: GoogleConfig = {
  expoClientId: process.env.EXPO_PUBLIC_GOOGLE_EXPO_CLIENT_ID ?? '',
  iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID ?? '',
  androidClientId: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID ?? '',
  webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID ?? '',
};

/**
 * useGoogleSignIn — call from a component.
 *   Returns { request, promptAsync, signInToBackend }.
 *   storageProvider:
 *     - 'spyme_cloud'  → only basic profile scope (default, easiest)
 *     - 'google_drive' → also requests drive.file scope to store clips in user's Drive
 */
export function useGoogleSignIn(
  storageProvider: 'spyme_cloud' | 'google_drive' = 'spyme_cloud',
  onAuth?: (jwt: { access_token: string; refresh_token: string }) => void,
) {
  const scopes = storageProvider === 'google_drive'
    ? ['profile', 'email', 'https://www.googleapis.com/auth/drive.file']
    : ['profile', 'email'];

  const [request, response, promptAsync] = Google.useAuthRequest({
    iosClientId: CONFIG.iosClientId,
    androidClientId: CONFIG.androidClientId,
    webClientId: CONFIG.webClientId,
    scopes,
  });

  useEffect(() => {
    if (response?.type === 'success') {
      const { authentication, params } = response;
      const idToken = authentication?.idToken ?? params.id_token;
      const refreshToken = authentication?.refreshToken;
      if (!idToken) return;

      (async () => {
        const apiUrl = await SecureStore.getItemAsync('apiUrl');
        const res = await api.post('/api/v1/auth/google', {
          id_token: idToken,
          client_id: CONFIG.webClientId,
          refresh_token: refreshToken,
          storage_provider: storageProvider,
        }, { baseURL: apiUrl ?? '' });

        await SecureStore.setItemAsync('accessToken', res.data.access_token);
        await SecureStore.setItemAsync('refreshToken', res.data.refresh_token);
        onAuth?.(res.data);
      })();
    }
  }, [response]);

  return { request, promptAsync, response };
}
