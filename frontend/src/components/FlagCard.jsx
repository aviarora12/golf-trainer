import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const SEVERITY_COLORS = {
  red: '#FF6B2B',
  yellow: '#FFA500',
  green: '#4ade80',
};

export default function FlagCard({ issue }) {
  const color = SEVERITY_COLORS[issue?.severity] || '#999';

  return (
    <View style={[styles.card, { borderLeftColor: color }]}>
      <Text style={[styles.name, { color }]}>{issue?.issue}</Text>
      <Text style={styles.description}>{issue?.description}</Text>
      {issue?.explanation ? <Text style={styles.explanation}>{issue.explanation}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    marginBottom: 8,
  },
  name: { fontSize: 14, fontWeight: '700' },
  description: { fontSize: 12, color: '#444', marginTop: 4 },
  explanation: { fontSize: 11, color: '#777', marginTop: 4 },
});
