import React, { useState } from 'react';
import { View, TouchableOpacity, Text, ActivityIndicator, StyleSheet, Alert } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import api from '../services/api';

export default function UploadScreen({ navigation }) {
  const [loading, setLoading] = useState(false);

  const pickVideo = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({ type: 'video/*' });

      // expo-document-picker v11+ returns { canceled, assets: [...] }
      if (result.canceled) return;
      const asset = result.assets ? result.assets[0] : result;
      if (asset && asset.uri) {
        uploadVideo(asset.uri, asset.name);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick video');
    }
  };

  const uploadVideo = async (videoUri, name) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: videoUri,
        type: 'video/mp4',
        name: name || 'swing.mp4',
      });

      const response = await api.post('/swings/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      navigation.replace('Report', { swingId: response.data.swing_id });
    } catch (error) {
      Alert.alert('Error', 'Upload failed');
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Upload Your Swing</Text>
      <Text style={styles.subtitle}>Landscape, full swing, 8-12 seconds</Text>

      <TouchableOpacity
        style={styles.btn}
        onPress={pickVideo}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Pick Video</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 8 },
  subtitle: { fontSize: 13, color: '#666', marginBottom: 32 },
  btn: { backgroundColor: '#FF6B2B', padding: 14, borderRadius: 8, alignItems: 'center' },
  btnText: { color: '#fff', fontWeight: '600' }
});
