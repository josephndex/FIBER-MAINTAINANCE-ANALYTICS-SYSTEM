/**
 * API Client for Fiber Maintenance Analytics Mobile App
 */

import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_URL, ENDPOINTS } from './config';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';

// Add auth token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await logout();
    }
    return Promise.reject(error);
  }
);

// Auth functions
export async function login(username, password) {
  const response = await api.post(ENDPOINTS.login, { username, password });
  const { token, user } = response.data;
  
  await SecureStore.setItemAsync(TOKEN_KEY, token);
  await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
  
  return user;
}

export async function logout() {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
  await SecureStore.deleteItemAsync(USER_KEY);
}

export async function getStoredUser() {
  const userData = await SecureStore.getItemAsync(USER_KEY);
  return userData ? JSON.parse(userData) : null;
}

export async function isAuthenticated() {
  const token = await SecureStore.getItemAsync(TOKEN_KEY);
  return !!token;
}

// Data fetching functions
export async function getStats(startDate, endDate) {
  const response = await api.get(ENDPOINTS.stats, {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

export async function getTickets(params = {}) {
  const response = await api.get(ENDPOINTS.tickets, { params });
  return response.data;
}

export async function searchTickets(query) {
  const response = await api.get(ENDPOINTS.ticketSearch, {
    params: { q: query },
  });
  return response.data;
}

export async function getEngineerStats(startDate, endDate) {
  const response = await api.get(ENDPOINTS.engineers, {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

export async function getRegionalStats(startDate, endDate) {
  const response = await api.get(ENDPOINTS.regions, {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

export async function getServiceStats(startDate, endDate) {
  const response = await api.get(ENDPOINTS.services, {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

export async function getTrends(startDate, endDate) {
  const response = await api.get(ENDPOINTS.trends, {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

export async function checkHealth() {
  const response = await api.get(ENDPOINTS.health);
  return response.data;
}

export default api;
