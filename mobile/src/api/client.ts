import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

export const api = axios.create({ baseURL: '' });

api.interceptors.request.use(async (config) => {
  const base = await SecureStore.getItemAsync('apiUrl') ?? '';
  const token = await SecureStore.getItemAsync('accessToken') ?? '';
  config.baseURL = base;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  r => r,
  async (err) => {
    if (err.response?.status === 401) {
      const refresh = await SecureStore.getItemAsync('refreshToken');
      if (refresh) {
        try {
          const base = await SecureStore.getItemAsync('apiUrl') ?? '';
          const res = await axios.post(`${base}/api/v1/auth/refresh`, null, { params: { token: refresh } });
          await SecureStore.setItemAsync('accessToken', res.data.access_token);
          err.config.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api.request(err.config);
        } catch (_) {}
      }
    }
    return Promise.reject(err);
  }
);
