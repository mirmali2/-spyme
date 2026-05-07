import React, { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import {
  MediaStream,
  RTCIceCandidate,
  RTCPeerConnection,
  RTCSessionDescription,
  RTCView,
} from 'react-native-webrtc';
import * as SecureStore from 'expo-secure-store';

interface Props {
  deviceId: string;
}

export default function LiveViewScreen({ deviceId }: Props) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [status, setStatus] = useState<'connecting' | 'live' | 'error'>('connecting');
  const pc = useRef<RTCPeerConnection | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function connect() {
      const apiUrl = (await SecureStore.getItemAsync('apiUrl') ?? '').replace(/^http/, 'ws');
      const token = await SecureStore.getItemAsync('accessToken') ?? '';

      ws.current = new WebSocket(`${apiUrl}/ws/viewer/${deviceId}?token=${token}`);

      pc.current = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.cloudflare.com:3478' },
          { urls: 'stun:stun.l.google.com:19302' },
        ],
      });

      pc.current.ontrack = (e) => {
        if (!cancelled) setStream(e.streams[0]);
        setStatus('live');
      };

      pc.current.onicecandidate = ({ candidate }) => {
        if (candidate && ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: 'ice-candidate', candidate }));
        }
      };

      ws.current.onopen = () => {
        ws.current!.send(JSON.stringify({ type: 'request-offer' }));
      };

      ws.current.onmessage = async (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'offer') {
          await pc.current!.setRemoteDescription(new RTCSessionDescription(msg));
          const answer = await pc.current!.createAnswer();
          await pc.current!.setLocalDescription(answer);
          ws.current!.send(JSON.stringify({ type: 'answer', sdp: answer.sdp }));
        } else if (msg.type === 'ice-candidate') {
          await pc.current!.addIceCandidate(new RTCIceCandidate(msg.candidate));
        } else if (msg.type === 'peer-disconnected') {
          setStatus('error');
        }
      };

      ws.current.onerror = () => setStatus('error');
    }

    connect();

    return () => {
      cancelled = true;
      pc.current?.close();
      ws.current?.close();
    };
  }, [deviceId]);

  return (
    <View style={styles.container}>
      {status === 'connecting' && <ActivityIndicator color="#fff" size="large" />}
      {status === 'error' && <Text style={styles.err}>Camera offline or unreachable</Text>}
      {stream && <RTCView streamURL={stream.toURL()} style={styles.video} objectFit="cover" />}
      {status === 'live' && <View style={styles.liveBadge}><Text style={styles.liveText}>LIVE</Text></View>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' },
  video: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 },
  liveBadge: { position: 'absolute', top: 20, left: 20, backgroundColor: '#e53e3e', borderRadius: 4, paddingHorizontal: 8, paddingVertical: 3 },
  liveText: { color: '#fff', fontSize: 11, fontWeight: '700', letterSpacing: 1 },
  err: { color: '#888', fontSize: 16 },
});
