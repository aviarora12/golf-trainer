import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import api from '../services/api';

export default function HomeScreen({ navigation }) {
  const [swings, setSwings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSwings();
  }, []);

  const fetchSwings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/swings/user/all');
      setSwings(response.data || []);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Swings</Text>

      <TouchableOpacity
        style={styles.uploadBtn}
        onPress={() => navigation.navigate('Upload')}
      >
        <Text style={styles.uploadBtnText}>+ Upload Swing</Text>
      </TouchableOpacity>

      {loading ? (
        <ActivityIndicator size="large" color="#FF6B2B" />
      ) : (
        <FlatList
          data={swings}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.card}
              onPress={() => navigation.navigate('Report', { swingId: item.id })}
            >
              <Text style={styles.cardDate}>{new Date(item.upload_date).toLocaleDateString()}</Text>
              <Text style={styles.cardStatus}>{item.analysis_status}</Text>
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 16 },
  uploadBtn: { backgroundColor: '#FF6B2B', padding: 12, borderRadius: 8, marginBottom: 16, alignItems: 'center' },
  uploadBtnText: { color: '#fff', fontWeight: '600' },
  card: { padding: 12, borderRadius: 8, borderColor: '#e0e0e0', borderWidth: 1, marginBottom: 8 },
  cardDate: { fontSize: 14, fontWeight: '600' },
  cardStatus: { fontSize: 12, color: '#666', marginTop: 4 }
});
