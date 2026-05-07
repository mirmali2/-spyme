import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { Device, armDevice, disarmDevice } from '../api/devices';
import { useQueryClient } from '@tanstack/react-query';

export function DeviceCard({ device }: { device: Device }) {
  const router = useRouter();
  const qc = useQueryClient();

  const toggleArm = async () => {
    device.is_armed ? await disarmDevice(device.id) : await armDevice(device.id);
    qc.invalidateQueries({ queryKey: ['devices'] });
  };

  const isOnline = device.last_seen
    ? Date.now() - new Date(device.last_seen).getTime() < 60_000
    : false;

  return (
    <Pressable
      onPress={() => router.push(`/live/${device.id}`)}
      style={{ width: 180, backgroundColor: '#1a1a1a', borderRadius: 16, padding: 16 }}
    >
      {/* Status dot */}
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
        <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: isOnline ? '#48bb78' : '#555', marginRight: 6 }} />
        <Text style={{ color: '#888', fontSize: 11 }}>{isOnline ? 'Online' : 'Offline'}</Text>
      </View>

      <Text style={{ color: '#fff', fontSize: 15, fontWeight: '600', marginBottom: 4 }} numberOfLines={1}>
        {device.name}
      </Text>
      <Text style={{ color: '#555', fontSize: 11, marginBottom: 16 }}>{device.platform}</Text>

      {device.battery_pct !== null && (
        <Text style={{ color: '#888', fontSize: 11, marginBottom: 4 }}>🔋 {device.battery_pct}%</Text>
      )}

      <Pressable
        onPress={toggleArm}
        style={{ marginTop: 8, backgroundColor: device.is_armed ? '#e53e3e22' : '#48bb7822', borderRadius: 8, padding: 8, alignItems: 'center' }}
      >
        <Text style={{ color: device.is_armed ? '#e53e3e' : '#48bb78', fontSize: 12, fontWeight: '600' }}>
          {device.is_armed ? 'ARMED' : 'DISARMED'}
        </Text>
      </Pressable>
    </Pressable>
  );
}
