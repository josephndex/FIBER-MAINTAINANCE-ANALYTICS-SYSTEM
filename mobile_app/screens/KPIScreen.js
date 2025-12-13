/**
 * KPI Screen - Key Performance Indicators
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { LineChart, BarChart } from 'react-native-chart-kit';
import { COLORS } from '../src/config';
import { getStats, getEngineerStats } from '../src/api';

const screenWidth = Dimensions.get('window').width - 32;

export default function KPIScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState(null);
  const [engineers, setEngineers] = useState([]);
  
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
      const [statsData, engineerData] = await Promise.all([
        getStats(startDate, endDate),
        getEngineerStats(startDate, endDate),
      ]);
      setStats(statsData);
      setEngineers(engineerData?.slice(0, 5) || []);
    } catch (err) {
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
      </View>
    );
  }
  
  // Prepare chart data
  const chartConfig = {
    backgroundColor: COLORS.cardBackground,
    backgroundGradientFrom: COLORS.cardBackground,
    backgroundGradientTo: COLORS.cardBackground,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(249, 115, 22, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(148, 163, 184, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: COLORS.primaryOrange,
    },
  };
  
  // Mock trend data (replace with real data from API)
  const trendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        data: [65, 78, 82, 88],
      },
    ],
  };
  
  // Engineer performance data
  const engineerChartData = {
    labels: engineers.map(e => e.name?.split(' ')[0] || 'N/A').slice(0, 5),
    datasets: [
      {
        data: engineers.map(e => e.tickets_resolved || 0).slice(0, 5),
      },
    ],
  };
  
  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          tintColor={COLORS.primaryOrange}
        />
      }
    >
      {/* SLA Trend */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>SLA Compliance Trend</Text>
        <LineChart
          data={trendData}
          width={screenWidth - 32}
          height={200}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
        />
      </View>
      
      {/* Top Engineers */}
      {engineers.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Top Engineers</Text>
          <BarChart
            data={engineerChartData}
            width={screenWidth - 32}
            height={200}
            chartConfig={{
              ...chartConfig,
              color: (opacity = 1) => `rgba(168, 85, 247, ${opacity})`,
            }}
            style={styles.chart}
            showValuesOnTopOfBars
          />
        </View>
      )}
      
      {/* KPI Cards */}
      <View style={styles.kpiGrid}>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiValue}>{stats?.avg_response_time?.toFixed(1) || 0}h</Text>
          <Text style={styles.kpiLabel}>Avg Response Time</Text>
          <View style={[styles.kpiIndicator, { backgroundColor: stats?.avg_response_time <= 4 ? COLORS.success : COLORS.error }]} />
        </View>
        
        <View style={styles.kpiCard}>
          <Text style={styles.kpiValue}>{stats?.avg_resolution_time?.toFixed(1) || 0}h</Text>
          <Text style={styles.kpiLabel}>Avg Resolution Time</Text>
          <View style={[styles.kpiIndicator, { backgroundColor: stats?.avg_resolution_time <= 24 ? COLORS.success : COLORS.error }]} />
        </View>
        
        <View style={styles.kpiCard}>
          <Text style={styles.kpiValue}>{stats?.first_call_resolution?.toFixed(1) || 0}%</Text>
          <Text style={styles.kpiLabel}>First Call Resolution</Text>
          <View style={[styles.kpiIndicator, { backgroundColor: COLORS.info }]} />
        </View>
        
        <View style={styles.kpiCard}>
          <Text style={styles.kpiValue}>{stats?.customer_satisfaction?.toFixed(1) || 0}</Text>
          <Text style={styles.kpiLabel}>CSAT Score</Text>
          <View style={[styles.kpiIndicator, { backgroundColor: COLORS.success }]} />
        </View>
      </View>
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
  card: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 16,
  },
  chart: {
    borderRadius: 12,
  },
  kpiGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -6,
  },
  kpiCard: {
    width: '48%',
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    padding: 16,
    margin: '1%',
    position: 'relative',
    overflow: 'hidden',
  },
  kpiValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  kpiLabel: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginTop: 4,
  },
  kpiIndicator: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: 4,
    height: '100%',
  },
});
