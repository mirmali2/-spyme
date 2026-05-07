import { useLocalSearchParams } from 'expo-router';
import LiveViewScreen from '../../src/screens/LiveViewScreen';

export default function Live() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <LiveViewScreen deviceId={id!} />;
}
