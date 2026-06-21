import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function DrillCard({ drill }) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.name}>{drill?.name}</Text>
        <Text style={styles.difficulty}>{drill?.difficulty}</Text>
      </View>
      <Text style={styles.description}>{drill?.description}</Text>
      {drill?.reps_sets ? <Text style={styles.reps}>{drill.reps_sets}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#eee',
    marginBottom: 8,
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  name: { fontSize: 14, fontWeight: '700', color: '#222' },
  difficulty: { fontSize: 11, color: '#FF6B2B', textTransform: 'capitalize' },
  description: { fontSize: 12, color: '#555', marginTop: 4 },
  reps: { fontSize: 12, color: '#888', marginTop: 6, fontWeight: '600' },
});
