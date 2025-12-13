/**
 * Fiber Maintenance Analytics - Mobile App Configuration
 */

// API Server URL (Tailscale IP)
export const API_URL = 'http://100.83.80.26:8000';

// App colors (matching desktop theme)
export const COLORS = {
  // Background colors
  background: '#0f172a',
  cardBackground: '#1e293b',
  surfaceBackground: '#334155',
  
  // Primary colors (gradient)
  primaryOrange: '#f97316',
  primaryPurple: '#a855f7',
  
  // Text colors
  textPrimary: '#ffffff',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
  
  // Status colors
  success: '#22c55e',
  warning: '#eab308',
  error: '#ef4444',
  info: '#3b82f6',
  
  // Grade colors
  gradeA: '#22c55e',
  gradeB: '#84cc16',
  gradeC: '#eab308',
  gradeD: '#f97316',
  gradeF: '#ef4444',
};

// API Endpoints
export const ENDPOINTS = {
  login: '/api/auth/login',
  tickets: '/api/tickets',
  ticketSearch: '/api/tickets/search',
  stats: '/api/stats',
  engineers: '/api/engineers',
  regions: '/api/regions',
  services: '/api/services',
  trends: '/api/trends',
  health: '/api/health',
};

// SLA Thresholds (in hours)
export const SLA = {
  response: 4,
  resolution: 24,
};

// Date format
export const DATE_FORMAT = 'YYYY-MM-DD';
export const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';
