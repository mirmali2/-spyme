import * as Notifications from 'expo-notifications';
import { router } from 'expo-router';
import { Platform } from 'react-native';
import { api } from '../api/client';

Notifications.setNotificationHandler({
  handleNotification: async (notif) => {
    const isFire = notif.request.content.data?.type === 'fire';
    return {
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
      shouldShowBanner: true,
      shouldShowList: true,
      // Critical alerts bypass Do-Not-Disturb on iOS (requires entitlement)
      ...(isFire ? { priority: Notifications.AndroidNotificationPriority.MAX } : {}),
    };
  },
});

let listener: Notifications.Subscription | null = null;
let tapListener: Notifications.Subscription | null = null;

export async function registerPush() {
  const { status } = await Notifications.requestPermissionsAsync({
    ios: { allowAlert: true, allowBadge: true, allowSound: true, allowCriticalAlerts: true },
  });
  if (status !== 'granted') return;

  // Set up Android channel for max-importance fire alarm
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('fire-emergency', {
      name: 'Fire Emergency',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 1000, 300, 1000, 300, 1000, 300, 1000],
      sound: 'siren.mp3',
      bypassDnd: true,
      lockscreenVisibility: Notifications.AndroidNotificationVisibility.PUBLIC,
      enableVibrate: true,
      enableLights: true,
      lightColor: '#ff0000',
    });
  }

  const token = (await Notifications.getDevicePushTokenAsync()).data;
  await api.post('/api/v1/notify/register-token', {
    [Platform.OS === 'ios' ? 'apns_token' : 'fcm_token']: token,
  });

  // Listen for incoming notifications — fire events open the full-screen alarm
  listener?.remove();
  listener = Notifications.addNotificationReceivedListener((notif) => {
    const data = notif.request.content.data || {};
    if (data.type === 'fire') {
      router.push({
        pathname: '/fire-alert',
        params: {
          camera: notif.request.content.body ?? 'Camera',
          confidence: String(data.confidence ?? 0.9),
          eventId: String(data.event_id ?? ''),
        },
      });
    }
  });

  // Tap on notification → open the right screen
  tapListener?.remove();
  tapListener = Notifications.addNotificationResponseReceivedListener((resp) => {
    const data = resp.notification.request.content.data || {};
    if (data.type === 'fire') {
      router.push({ pathname: '/fire-alert', params: { eventId: String(data.event_id ?? '') } });
    } else if (data.event_id) {
      router.push(`/`);
    }
  });
}

export async function registerPhone(phone: string, emergency?: string) {
  await api.post('/api/v1/notify/register-phone', { phone_number: phone, emergency_contact: emergency });
}
