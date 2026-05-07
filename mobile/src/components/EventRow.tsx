import React from 'react';
import { Text, View } from 'react-native';
import { SpymeEvent } from '../api/events';

export function EventRow({ event }: { event: SpymeEvent }) {
  const isPerson = event.type === 'person';
  const time = new Date(event.triggered_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const date = new Date(event.triggered_at).toLocaleDateString([], { month: 'short', day: 'numeric' });

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: '#141414', borderRadius: 12, padding: 14 }}>
      <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: isPerson ? '#e53e3e22' : '#ecc94b22', justifyContent: 'center', alignItems: 'center', marginRight: 12 }}>
        <Text style={{ fontSize: 16 }}>{isPerson ? '🧍' : '👁️'}</Text>
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ color: '#fff', fontSize: 14, fontWeight: '600' }}>
          {isPerson ? 'Person detected' : 'Motion detected'}
        </Text>
        {event.confidence !== null && (
          <Text style={{ color: '#555', fontSize: 11 }}>Confidence: {Math.round(event.confidence * 100)}%</Text>
        )}
      </View>
      <Text style={{ color: '#444', fontSize: 11, textAlign: 'right' }}>{date}{'\n'}{time}</Text>
    </View>
  );
}
