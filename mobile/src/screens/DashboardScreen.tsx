import { useQuery } from '@tanstack/react-query';
import React from 'react';
import { FlatList, Pressable, RefreshControl, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { getDevices } from '../api/devices';
import { getEvents } from '../api/events';
import { DeviceCard } from '../components/DeviceCard';
import { EventRow } from '../components/EventRow';

export default function DashboardScreen() {
  const router = useRouter();
  const devices = useQuery({ queryKey: ['devices'], queryFn: getDevices, refetchInterval: 15_000 });
  const events = useQuery({ queryKey: ['events'], queryFn: () => getEvents(undefined, 20), refetchInterval: 10_000 });

  return (
    <View style={{ flex: 1, backgroundColor: '#0a0a0a' }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', margin: 20 }}>
        <Text style={{ color: '#fff', fontSize: 22, fontWeight: '700' }}>SPYME</Text>
        <Pressable onPress={() => router.push('/pair')} style={{ backgroundColor: '#1a1a1a', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8 }}>
          <Text style={{ color: '#fff', fontSize: 13, fontWeight: '600' }}>+ Add</Text>
        </Pressable>
      </View>

      {/* Device list */}
      <Text style={{ color: '#888', fontSize: 12, marginLeft: 20, marginBottom: 8, letterSpacing: 1 }}>
        CAMERAS
      </Text>
      <FlatList
        horizontal
        data={devices.data ?? []}
        keyExtractor={d => d.id}
        renderItem={({ item }) => <DeviceCard device={item} />}
        contentContainerStyle={{ paddingHorizontal: 16, gap: 12 }}
        showsHorizontalScrollIndicator={false}
      />

      {/* Recent events */}
      <Text style={{ color: '#888', fontSize: 12, marginLeft: 20, marginTop: 24, marginBottom: 8, letterSpacing: 1 }}>
        RECENT ALERTS
      </Text>
      <FlatList
        data={events.data ?? []}
        keyExtractor={e => e.id}
        renderItem={({ item }) => <EventRow event={item} />}
        refreshControl={<RefreshControl refreshing={events.isFetching} onRefresh={() => events.refetch()} tintColor="#fff" />}
        contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
      />
    </View>
  );
}
