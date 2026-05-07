import React, { useState } from 'react';
import { ActivityIndicator, Alert, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { useAuth } from '../store/auth';
import { useGoogleSignIn } from '../api/google';

type Mode = 'signin' | 'signup';

export default function LoginScreen() {
  const login = useAuth(s => s.login);
  const setLoggedIn = useAuth.setState;

  const [mode, setMode] = useState<Mode>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [apiUrl, setApiUrl] = useState('https://api.spyme.app');
  const [loading, setLoading] = useState(false);
  const [storeWith, setStoreWith] = useState<'spyme_cloud' | 'google_drive'>('spyme_cloud');

  const { request, promptAsync } = useGoogleSignIn(storeWith, () => {
    setLoggedIn({ isLoggedIn: true });
  });

  const submit = async () => {
    if (!email || !password) return;
    setLoading(true);
    try {
      await login(email, password, apiUrl, mode === 'signup' ? name : undefined);
    } catch {
      Alert.alert(mode === 'signup' ? 'Sign up failed' : 'Login failed', 'Check your input.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={{ flexGrow: 1, backgroundColor: '#0a0a0a', padding: 28, paddingTop: 70 }}>
      <Text style={{ color: '#fff', fontSize: 36, fontWeight: '900', letterSpacing: 4 }}>SPYME</Text>
      <Text style={{ color: '#555', fontSize: 13, marginTop: 4, marginBottom: 36 }}>
        Your space. Your surveillance.
      </Text>

      {/* Mode toggle */}
      <View style={{ flexDirection: 'row', backgroundColor: '#141414', borderRadius: 14, padding: 4, marginBottom: 28 }}>
        {(['signin', 'signup'] as Mode[]).map(m => (
          <Pressable
            key={m}
            onPress={() => setMode(m)}
            style={{
              flex: 1, padding: 11, borderRadius: 10, alignItems: 'center',
              backgroundColor: mode === m ? '#e53e3e' : 'transparent',
            }}
          >
            <Text style={{ color: mode === m ? '#fff' : '#666', fontWeight: '700', fontSize: 13 }}>
              {m === 'signin' ? 'Sign In' : 'Create Account'}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* Google sign-in — primary CTA */}
      <Pressable
        disabled={!request}
        onPress={() => promptAsync()}
        style={{
          backgroundColor: '#fff', borderRadius: 14, padding: 14,
          flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10,
        }}
      >
        <Text style={{ fontSize: 18 }}>G</Text>
        <Text style={{ color: '#000', fontWeight: '700', fontSize: 15 }}>
          Continue with Google
        </Text>
      </Pressable>

      {/* Drive option */}
      <Pressable
        onPress={() => setStoreWith(s => s === 'google_drive' ? 'spyme_cloud' : 'google_drive')}
        style={{ flexDirection: 'row', alignItems: 'center', marginTop: 14, padding: 12, backgroundColor: '#0d0d0d', borderRadius: 10, borderWidth: 1, borderColor: storeWith === 'google_drive' ? '#4285F4' : '#1a1a1a' }}
      >
        <View style={{
          width: 18, height: 18, borderRadius: 4, marginRight: 10,
          backgroundColor: storeWith === 'google_drive' ? '#4285F4' : 'transparent',
          borderWidth: 1.5, borderColor: storeWith === 'google_drive' ? '#4285F4' : '#444',
          justifyContent: 'center', alignItems: 'center',
        }}>
          {storeWith === 'google_drive' && <Text style={{ color: '#fff', fontSize: 11, fontWeight: '900' }}>✓</Text>}
        </View>
        <View style={{ flex: 1 }}>
          <Text style={{ color: '#fff', fontSize: 12, fontWeight: '600' }}>Store clips in MY Google Drive</Text>
          <Text style={{ color: '#666', fontSize: 10, marginTop: 1 }}>Privacy-first · your videos stay in your cloud</Text>
        </View>
      </Pressable>

      {/* Divider */}
      <View style={{ flexDirection: 'row', alignItems: 'center', marginVertical: 26 }}>
        <View style={{ flex: 1, height: 1, backgroundColor: '#222' }} />
        <Text style={{ color: '#555', marginHorizontal: 14, fontSize: 11 }}>OR EMAIL</Text>
        <View style={{ flex: 1, height: 1, backgroundColor: '#222' }} />
      </View>

      {/* Email/password fields */}
      {mode === 'signup' && (
        <Field label="NAME" value={name} onChange={setName} placeholder="Your name" />
      )}
      <Field label="EMAIL" value={email} onChange={setEmail} placeholder="you@example.com" />
      <Field label="PASSWORD" value={password} onChange={setPassword} placeholder="••••••••" secure />
      <Field label="SERVER URL" value={apiUrl} onChange={setApiUrl} placeholder="https://api.spyme.app" />

      <Pressable
        onPress={submit}
        disabled={loading}
        style={{ backgroundColor: '#e53e3e', borderRadius: 14, padding: 16, alignItems: 'center', marginTop: 10 }}
      >
        {loading ? <ActivityIndicator color="#fff" /> :
          <Text style={{ color: '#fff', fontWeight: '700', fontSize: 15 }}>
            {mode === 'signup' ? 'Create Account' : 'Sign In'}
          </Text>
        }
      </Pressable>

      <Text style={{ color: '#444', fontSize: 10, textAlign: 'center', marginTop: 18, lineHeight: 15 }}>
        By continuing you agree to use SPYME only in spaces you own.{'\n'}
        We do not record audio. Cameras show a visible monitoring indicator.
      </Text>
    </ScrollView>
  );
}

function Field({ label, value, onChange, placeholder, secure = false }: {
  label: string; value: string; onChange: (s: string) => void; placeholder: string; secure?: boolean;
}) {
  return (
    <View style={{ marginBottom: 14 }}>
      <Text style={{ color: '#666', fontSize: 10, letterSpacing: 1, marginBottom: 6 }}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChange}
        placeholder={placeholder}
        placeholderTextColor="#333"
        secureTextEntry={secure}
        autoCapitalize="none"
        style={{ backgroundColor: '#1a1a1a', color: '#fff', borderRadius: 12, padding: 14, fontSize: 14 }}
      />
    </View>
  );
}
