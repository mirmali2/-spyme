import { useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';
import { Alert, Pressable, Text, TextInput, View } from 'react-native';
import { api } from '../api/client';

export default function PairScreen() {
  const [name, setName] = useState('');
  const [platform, setPlatform] = useState<'windows' | 'macos'>('windows');
  const qc = useQueryClient();

  const create = async () => {
    if (!name) return;
    try {
      const res = await api.post('/api/v1/devices', { name, platform });
      const tokenRes = await api.post(`/api/v1/devices/${res.data.id}/pair`);
      qc.invalidateQueries({ queryKey: ['devices'] });
      Alert.alert(
        'Device created',
        `Pairing token (valid 10 min):\n\n${tokenRes.data.token}\n\nEnter this on your laptop's SPYME app.`
      );
    } catch (e: any) {
      Alert.alert('Failed', e.message);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: '#0a0a0a', padding: 24 }}>
      <Text style={{ color: '#fff', fontSize: 24, fontWeight: '700', marginBottom: 8 }}>Add Camera</Text>
      <Text style={{ color: '#555', fontSize: 13, marginBottom: 32 }}>
        Name your laptop and we'll generate a one-time pairing token.
      </Text>

      <Text style={{ color: '#666', fontSize: 11, marginBottom: 6, letterSpacing: 0.5 }}>NAME</Text>
      <TextInput
        value={name}
        onChangeText={setName}
        placeholder="Bedroom Laptop"
        placeholderTextColor="#333"
        style={{ backgroundColor: '#1a1a1a', color: '#fff', borderRadius: 12, padding: 14, marginBottom: 16 }}
      />

      <Text style={{ color: '#666', fontSize: 11, marginBottom: 6, letterSpacing: 0.5 }}>PLATFORM</Text>
      <View style={{ flexDirection: 'row', gap: 8, marginBottom: 24 }}>
        {(['windows', 'macos'] as const).map(p => (
          <Pressable
            key={p}
            onPress={() => setPlatform(p)}
            style={{ flex: 1, backgroundColor: platform === p ? '#e53e3e' : '#1a1a1a', padding: 12, borderRadius: 10, alignItems: 'center' }}
          >
            <Text style={{ color: '#fff', fontWeight: '600', textTransform: 'capitalize' }}>{p}</Text>
          </Pressable>
        ))}
      </View>

      <Pressable onPress={create} style={{ backgroundColor: '#e53e3e', borderRadius: 14, padding: 16, alignItems: 'center' }}>
        <Text style={{ color: '#fff', fontWeight: '700' }}>Generate Pairing Token</Text>
      </Pressable>
    </View>
  );
}
