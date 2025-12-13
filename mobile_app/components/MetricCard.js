/**
 * Metric Card Component
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '../src/config';

export default function MetricCard({ title, value, icon, trend }) {
  const getTrendColor = () => {
    switch (trend) {
      case 'good':
        return COLORS.success;
      case 'bad':
        return COLORS.error;
      case 'neutral':
        return COLORS.warning;
      default:
        return COLORS.textMuted;
    }
  };
  
  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>{icon}</Text>
      </View>
      <Text style={[styles.value, trend && { color: getTrendColor() }]}>
        {value}
      </Text>
      <Text style={styles.title}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '48%',
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    padding: 16,
    margin: '1%',
    alignItems: 'center',
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.surfaceBackground,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  icon: {
    fontSize: 20,
  },
  value: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  title: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginTop: 4,
    textAlign: 'center',
  },
});
