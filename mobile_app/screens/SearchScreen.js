/**
 * Search Screen - Ticket Search
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../src/config';
import { searchTickets } from '../src/api';

export default function SearchScreen() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  
  const handleSearch = async () => {
    if (!query.trim()) {
      Alert.alert('Search', 'Please enter a ticket number or customer name');
      return;
    }
    
    setLoading(true);
    setSearched(true);
    
    try {
      const data = await searchTickets(query);
      setResults(data || []);
    } catch (error) {
      Alert.alert('Error', 'Failed to search tickets');
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'resolved':
      case 'closed':
        return COLORS.success;
      case 'in progress':
      case 'assigned':
        return COLORS.info;
      case 'pending':
        return COLORS.warning;
      default:
        return COLORS.textMuted;
    }
  };
  
  const renderTicket = ({ item }) => (
    <TouchableOpacity style={styles.ticketCard}>
      <View style={styles.ticketHeader}>
        <Text style={styles.ticketNumber}>{item.ticket_number || item.id}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status || 'Unknown'}</Text>
        </View>
      </View>
      
      <Text style={styles.ticketTitle} numberOfLines={2}>
        {item.issue_description || item.title || 'No description'}
      </Text>
      
      <View style={styles.ticketMeta}>
        <View style={styles.metaItem}>
          <Ionicons name="person-outline" size={14} color={COLORS.textMuted} />
          <Text style={styles.metaText}>{item.customer_name || 'N/A'}</Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="location-outline" size={14} color={COLORS.textMuted} />
          <Text style={styles.metaText}>{item.region || 'N/A'}</Text>
        </View>
      </View>
      
      <View style={styles.ticketMeta}>
        <View style={styles.metaItem}>
          <Ionicons name="build-outline" size={14} color={COLORS.textMuted} />
          <Text style={styles.metaText}>{item.assigned_engineer || 'Unassigned'}</Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="calendar-outline" size={14} color={COLORS.textMuted} />
          <Text style={styles.metaText}>{item.created_date?.split('T')[0] || 'N/A'}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
  
  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={20} color={COLORS.textMuted} />
          <TextInput
            style={styles.searchInput}
            placeholder="Ticket number or customer name..."
            placeholderTextColor={COLORS.textMuted}
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
          {query.length > 0 && (
            <TouchableOpacity onPress={() => setQuery('')}>
              <Ionicons name="close-circle" size={20} color={COLORS.textMuted} />
            </TouchableOpacity>
          )}
        </View>
        
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>
      
      {/* Results */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={COLORS.primaryOrange} />
        </View>
      ) : searched && results.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="search-outline" size={64} color={COLORS.textMuted} />
          <Text style={styles.emptyText}>No tickets found</Text>
          <Text style={styles.emptyHint}>Try a different search term</Text>
        </View>
      ) : !searched ? (
        <View style={styles.centerContainer}>
          <Ionicons name="ticket-outline" size={64} color={COLORS.textMuted} />
          <Text style={styles.emptyText}>Search Tickets</Text>
          <Text style={styles.emptyHint}>Enter a ticket number or customer name</Text>
        </View>
      ) : (
        <FlatList
          data={results}
          renderItem={renderTicket}
          keyExtractor={(item) => item.id?.toString() || item.ticket_number}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    paddingBottom: 8,
  },
  searchBar: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    paddingHorizontal: 12,
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    padding: 12,
    fontSize: 16,
    color: COLORS.textPrimary,
  },
  searchButton: {
    backgroundColor: COLORS.primaryOrange,
    borderRadius: 12,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  searchButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 18,
    color: COLORS.textPrimary,
    marginTop: 16,
  },
  emptyHint: {
    fontSize: 14,
    color: COLORS.textMuted,
    marginTop: 4,
  },
  listContent: {
    padding: 16,
    paddingTop: 8,
  },
  ticketCard: {
    backgroundColor: COLORS.cardBackground,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  ticketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  ticketNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryOrange,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#fff',
    textTransform: 'uppercase',
  },
  ticketTitle: {
    fontSize: 14,
    color: COLORS.textPrimary,
    marginBottom: 12,
  },
  ticketMeta: {
    flexDirection: 'row',
    marginTop: 4,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  metaText: {
    fontSize: 12,
    color: COLORS.textMuted,
    marginLeft: 4,
  },
});
