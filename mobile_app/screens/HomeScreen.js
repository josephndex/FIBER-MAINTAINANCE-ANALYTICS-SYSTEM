/**
 * Home Screen - Dashboard Overview
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { COLORS } from '../src/config';
import { getStats } from '../src/api';
import MetricCard from '../components/MetricCard';
import GradeCard from '../components/GradeCard';

export default function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  
  // Get date range (last 90 days)
  const getDateRange = () => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 90);
    return {
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    };
  };
  
  const fetchData = async () => {
    try {
      const { startDate, endDate } = getDateRange();
      const data = await getStats(startDate, endDate);
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Failed to load data');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };
  
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primaryOrange} />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }
  
  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorEmoji}>⚠️</Text>
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.errorHint}>Pull down to retry</Text>
      </View>
    );
  }
  
  // Calculate metrics from stats
  const totalTickets = stats?.total_tickets || 0;
  const avgResponseTime = stats?.avg_response_time || 0;
  const avgResolutionTime = stats?.avg_resolution_time || 0;
  const slaCompliance = stats?.sla_compliance || 0;
  const overallGrade = stats?.overall_grade || 'N/A';
  
  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor={COLORS.primaryOrange}
          colors={[COLORS.primaryOrange]}
        />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard</Text>
        <Text style={styles.headerSubtitle}>Last 90 days overview</Text>
      </View>
      
      {/* Overall Grade */}
      <GradeCard grade={overallGrade} label="Overall Performance" />
      
      {/* Key Metrics */}
      <Text style={styles.sectionTitle}>Key Metrics</Text>
      
      <View style={styles.metricsGrid}>
        <MetricCard
          title="Total Tickets"
          value={totalTickets.toLocaleString()}
          icon="🎫"
        />
        <MetricCard
          title="Avg Response"
          value={`${avgResponseTime.toFixed(1)}h`}
          icon="⏱️"
          trend={avgResponseTime <= 4 ? 'good' : 'bad'}
        />
        <MetricCard
          title="Avg Resolution"
          value={`${avgResolutionTime.toFixed(1)}h`}
          icon="✅"
          trend={avgResolutionTime <= 24 ? 'good' : 'bad'}
        />
        <MetricCard
          title="SLA Compliance"
          value={`${slaCompliance.toFixed(1)}%`}
          icon="📊"
          trend={slaCompliance >= 80 ? 'good' : slaCompliance >= 60 ? 'neutral' : 'bad'}
        />
      </View>
      
      {/* Status Breakdown */}
      {stats?.status_breakdown && (
        <>
          <Text style={styles.sectionTitle}>Status Breakdown</Text>
          <View style={styles.statusContainer}>
            {Object.entries(stats.status_breakdown).map(([status, count]) => (
              <View key={status} style={styles.statusItem}>
                <Text style={styles.statusCount}>{count}</Text>
                <Text style={styles.statusLabel}>{status}</Text>
              </View>
            ))}
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    padding: 16,
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 16,
    color: COLORS.textSecondary,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
    padding: 32,
  },
  errorEmoji: {
    fontSize: 48,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 18,
    color: COLORS.textPrimary,
    marginBottom: 8,
  },
  errorHint: {
    color: COLORS.textMuted,
  },
  header: {
    marginBottom: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginTop: 24,
    marginBottom: 12,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -6,
  },
  statusContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    padding: 16,
  },
  statusItem: {
    width: '50%',
    paddingVertical: 8,
  },
  statusCount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  statusLabel: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
});
