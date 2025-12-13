/**
 * Grade Card Component
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../src/config';

export default function GradeCard({ grade, label }) {
  const getGradeColor = () => {
    switch (grade?.toUpperCase()) {
      case 'A':
      case 'A+':
        return COLORS.gradeA;
      case 'B':
      case 'B+':
        return COLORS.gradeB;
      case 'C':
      case 'C+':
        return COLORS.gradeC;
      case 'D':
      case 'D+':
        return COLORS.gradeD;
      case 'F':
        return COLORS.gradeF;
      default:
        return COLORS.textMuted;
    }
  };
  
  const gradeColor = getGradeColor();
  
  return (
    <LinearGradient
      colors={[COLORS.cardBackground, COLORS.surfaceBackground]}
      style={styles.container}
    >
      <View style={[styles.gradeCircle, { borderColor: gradeColor }]}>
        <Text style={[styles.gradeText, { color: gradeColor }]}>
          {grade || 'N/A'}
        </Text>
      </View>
      <Text style={styles.label}>{label}</Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  gradeCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    marginBottom: 12,
  },
  gradeText: {
    fontSize: 36,
    fontWeight: 'bold',
  },
  label: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
});
