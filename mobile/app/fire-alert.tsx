import { useLocalSearchParams } from 'expo-router';
import FireAlertScreen from '../src/screens/FireAlertScreen';

export default function FireAlert() {
  const { camera, confidence, eventId } = useLocalSearchParams<{ camera: string; confidence: string; eventId: string }>();
  return (
    <FireAlertScreen
      cameraName={camera ?? 'Unknown Camera'}
      confidence={parseFloat(confidence ?? '0.9')}
      eventId={eventId ?? ''}
    />
  );
}
