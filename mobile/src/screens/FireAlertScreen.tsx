import { Audio } from 'expo-av';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import React, { useEffect, useRef, useState } from 'react';
import { Animated, Easing, Pressable, Text, View, Vibration } from 'react-native';

interface Props {
  cameraName: string;
  confidence: number;
  eventId: string;
}

export default function FireAlertScreen({ cameraName, confidence, eventId }: Props) {
  const router = useRouter();
  const sound = useRef<Audio.Sound | null>(null);
  const flash = useRef(new Animated.Value(0)).current;
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    // Continuous strong vibration pattern (cannot be silenced)
    Vibration.vibrate([0, 1000, 300, 1000, 300, 1000], true);

    // Strong haptic burst every second
    const hapticTimer = setInterval(() => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }, 1000);

    // Counter
    const secTimer = setInterval(() => setSeconds(s => s + 1), 1000);

    // Siren sound — bypass mute switch with playsInSilentModeIOS
    (async () => {
      try {
        await Audio.setAudioModeAsync({
          playsInSilentModeIOS: true,
          staysActiveInBackground: true,
          shouldDuckAndroid: false,
        });
        const { sound: snd } = await Audio.Sound.createAsync(
          require('../../assets/siren.mp3'),
          { shouldPlay: true, isLooping: true, volume: 1.0 }
        );
        sound.current = snd;
      } catch (e) { /* missing siren.mp3 — fall back to haptics only */ }
    })();

    // Flashing red background
    Animated.loop(
      Animated.sequence([
        Animated.timing(flash, { toValue: 1, duration: 400, easing: Easing.linear, useNativeDriver: false }),
        Animated.timing(flash, { toValue: 0, duration: 400, easing: Easing.linear, useNativeDriver: false }),
      ])
    ).start();

    return () => {
      Vibration.cancel();
      clearInterval(hapticTimer);
      clearInterval(secTimer);
      sound.current?.unloadAsync();
    };
  }, []);

  const dismiss = () => {
    Vibration.cancel();
    sound.current?.stopAsync();
    router.back();
  };

  const bg = flash.interpolate({ inputRange: [0, 1], outputRange: ['#1a0000', '#7a0000'] });

  return (
    <Animated.View style={{ flex: 1, backgroundColor: bg, padding: 24, justifyContent: 'space-between' }}>
      {/* Top — emergency banner */}
      <View style={{ marginTop: 60 }}>
        <Text style={{ color: '#fff', fontSize: 14, fontWeight: '800', letterSpacing: 4, textAlign: 'center' }}>
          EMERGENCY ALERT
        </Text>
        <Text style={{ color: '#fff', fontSize: 11, opacity: 0.7, textAlign: 'center', marginTop: 4 }}>
          {String(Math.floor(seconds / 60)).padStart(2, '0')}:{String(seconds % 60).padStart(2, '0')} elapsed
        </Text>
      </View>

      {/* Middle — fire icon + message */}
      <View style={{ alignItems: 'center' }}>
        <Text style={{ fontSize: 140 }}>🔥</Text>
        <Text style={{ color: '#fff', fontSize: 38, fontWeight: '900', marginTop: 12, letterSpacing: -1 }}>
          FIRE DETECTED
        </Text>
        <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 17, marginTop: 12, textAlign: 'center', fontWeight: '600' }}>
          {cameraName}
        </Text>
        <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 14, marginTop: 6, textAlign: 'center' }}>
          Confidence: {Math.round(confidence * 100)}%
        </Text>
      </View>

      {/* Bottom — actions */}
      <View style={{ gap: 10, marginBottom: 20 }}>
        <Pressable
          onPress={() => router.push(`/live/${eventId}`)}
          style={{ backgroundColor: '#fff', borderRadius: 18, padding: 18, alignItems: 'center' }}
        >
          <Text style={{ color: '#7a0000', fontWeight: '800', fontSize: 16 }}>VIEW LIVE CAMERA</Text>
        </Pressable>

        <Pressable style={{ backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 18, padding: 16, alignItems: 'center' }}>
          <Text style={{ color: '#fff', fontWeight: '700', fontSize: 14 }}>📞 CALL FIRE DEPARTMENT (911)</Text>
        </Pressable>

        <Pressable onPress={dismiss} style={{ padding: 14, alignItems: 'center' }}>
          <Text style={{ color: 'rgba(255,255,255,0.6)', fontWeight: '600', fontSize: 12 }}>Dismiss alarm (false alarm)</Text>
        </Pressable>
      </View>
    </Animated.View>
  );
}
