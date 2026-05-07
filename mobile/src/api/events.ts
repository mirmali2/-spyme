import { api } from './client';

export interface SpymeEvent {
  id: string;
  device_id: string;
  type: 'motion' | 'person';
  confidence: number | null;
  triggered_at: string;
  clip_id: string | null;
}

export const getEvents = (deviceId?: string, limit = 50) =>
  api.get<SpymeEvent[]>('/api/v1/events', { params: { device_id: deviceId, limit } }).then(r => r.data);
