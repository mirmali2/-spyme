import { api } from './client';

export interface Device {
  id: string;
  name: string;
  platform: string;
  is_armed: boolean;
  last_seen: string | null;
  battery_pct: number | null;
  storage_free_mb: number | null;
}

export const getDevices = () => api.get<Device[]>('/api/v1/devices').then(r => r.data);
export const getDevice = (id: string) => api.get<Device>(`/api/v1/devices/${id}`).then(r => r.data);
export const armDevice = (id: string) => api.patch(`/api/v1/devices/${id}`, { is_armed: true });
export const disarmDevice = (id: string) => api.patch(`/api/v1/devices/${id}`, { is_armed: false });
export const pairDevice = (id: string) => api.post<{ token: string; expires_in_seconds: number }>(`/api/v1/devices/${id}/pair`).then(r => r.data);
