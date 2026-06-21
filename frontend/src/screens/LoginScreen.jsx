import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import api from '../services/api';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const sendMagicLink = async () => {
    if (!email) {
      Alert.alert('Enter your email');
      return;
    }
    setLoading(true);
    try {
      await api.post('/auth/signup', { email });
      setSent(true);
    } catch (error) {
      Alert.alert('Error', 'Could not send magic link');
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>SwingCheck</Text>
      <Text style={styles.subtitle}>AI golf swing analysis</Text>

      {sent ? (
        <Text style={styles.sentText}>
          Check your email for a sign-in link.
        </Text>
      ) : (
        <>
          <TextInput
            style={styles.input}
            placeholder="you@example.com"
            autoCapitalize="none"
            keyboardType="email-address"
            value={email}
            onChangeText={setEmail}
          />
          <TouchableOpacity style={styles.btn} onPress={sendMagicLink} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Send Magic Link</Text>}
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center', backgroundColor: '#fff' },
  title: { fontSize: 32, fontWeight: '800', textAlign: 'center', color: '#FF6B2B' },
  subtitle: { fontSize: 14, color: '#666', textAlign: 'center', marginBottom: 32 },
  input: { borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 8, padding: 12, marginBottom: 16 },
  btn: { backgroundColor: '#FF6B2B', padding: 14, borderRadius: 8, alignItems: 'center' },
  btnText: { color: '#fff', fontWeight: '600' },
  sentText: { fontSize: 15, color: '#333', textAlign: 'center' }
});
