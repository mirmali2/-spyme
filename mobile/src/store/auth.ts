import * as SecureStore from 'expo-secure-store';
import { create } from 'zustand';
import { api } from '../api/client';

interface AuthState {
  isLoggedIn: boolean;
  login: (email: string, password: string, apiUrl: string, signupName?: string) => Promise<void>;
  logout: () => Promise<void>;
  hydrate: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  isLoggedIn: false,

  hydrate: async () => {
    const token = await SecureStore.getItemAsync('accessToken');
    set({ isLoggedIn: !!token });
  },

  login: async (email, password, apiUrl, signupName) => {
    await SecureStore.setItemAsync('apiUrl', apiUrl);
    const path = signupName !== undefined ? '/api/v1/auth/register' : '/api/v1/auth/login';
    const body = signupName !== undefined
      ? { email, password, name: signupName }
      : { email, password };
    const res = await api.post(path, body, { baseURL: apiUrl });
    await SecureStore.setItemAsync('accessToken', res.data.access_token);
    await SecureStore.setItemAsync('refreshToken', res.data.refresh_token);
    set({ isLoggedIn: true });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('accessToken');
    await SecureStore.deleteItemAsync('refreshToken');
    set({ isLoggedIn: false });
  },
}));
