import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator, StyleSheet } from 'react-native';
import api from '../services/api';

export default function ReportScreen({ route }) {
  const { swingId } = route.params;
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const pollReport = async () => {
      try {
        while (!cancelled) {
          const statusResponse = await api.get(`/swings/${swingId}/status`);

          if (statusResponse.data.status === 'complete') {
            const reportResponse = await api.get(`/swings/${swingId}/report`);
            if (!cancelled) setAnalysis(reportResponse.data);
            break;
          }

          if (statusResponse.data.status === 'failed') break;

          await new Promise((r) => setTimeout(r, 2000));
        }
      } catch (error) {
        console.error(error);
      }
      if (!cancelled) setLoading(false);
    };

    pollReport();
    return () => {
      cancelled = true;
    };
  }, [swingId]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#FF6B2B" />
        <Text style={styles.loadingText}>Analyzing your swing...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Analysis Report</Text>

      <View style={styles.heatmapPlaceholder}>
        <Text>Heatmap visualization</Text>
      </View>

      <Text style={styles.sectionTitle}>Key Findings</Text>
      {analysis?.flagged_issues?.map((issue, idx) => (
        <View key={idx} style={styles.issueCard}>
          <Text style={[styles.issueName, { color: issue.severity === 'red' ? '#FF6B2B' : '#FFA500' }]}>
            {issue.issue}
          </Text>
          <Text style={styles.issueDesc}>{issue.description}</Text>
        </View>
      ))}

      <Text style={styles.sectionTitle}>Metrics</Text>
      <View style={styles.metricsGrid}>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Spine Angle</Text>
          <Text style={styles.metricValue}>{analysis?.spine_angle_setup_deg?.toFixed(1)}°</Text>
        </View>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Hip Turn</Text>
          <Text style={styles.metricValue}>{analysis?.hip_turn_top_deg?.toFixed(1)}°</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 16 },
  loadingText: { marginTop: 8, color: '#666' },
  heatmapPlaceholder: { height: 200, backgroundColor: '#f0f0f0', borderRadius: 8, justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  sectionTitle: { fontSize: 16, fontWeight: '600', marginTop: 16, marginBottom: 8 },
  issueCard: { backgroundColor: '#f9f9f9', padding: 12, borderRadius: 8, marginBottom: 8 },
  issueName: { fontSize: 14, fontWeight: '700' },
  issueDesc: { fontSize: 12, color: '#666', marginTop: 4 },
  metricsGrid: { flexDirection: 'row', gap: 8 },
  metric: { flex: 1, backgroundColor: '#f9f9f9', padding: 12, borderRadius: 8 },
  metricLabel: { fontSize: 12, color: '#666' },
  metricValue: { fontSize: 18, fontWeight: '700', color: '#FF6B2B', marginTop: 4 }
});
