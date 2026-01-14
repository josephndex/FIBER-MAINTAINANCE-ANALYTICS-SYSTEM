"""
Configuration settings for Fiber Maintenance Analytics System
"""
import os
import sys

# App Settings
APP_TITLE = "Fiber Maintenance Analytics System"
APP_ICON = "fiber_app"
PAGE_LAYOUT = "wide"

# Developer Info
DEVELOPER_NAME = "Joseph Nderitu"
DEVELOPER_EMAIL = "josephnderito16@gmail.com"

# Data Settings - Use user's AppData folder for writable storage
# This avoids permission issues when installed to Program Files
if sys.platform == "win32":
    APP_DATA = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'FiberMaintenanceAnalytics')
else:
    APP_DATA = os.path.join(os.path.expanduser('~'), '.fiber_analytics')

DATA_DIR = os.path.join(APP_DATA, "data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except PermissionError:
    # Fallback to temp directory if still no permission
    DATA_DIR = os.path.join(os.environ.get('TEMP', '/tmp'), 'fiber_analytics_data')
    os.makedirs(DATA_DIR, exist_ok=True)

# Theme Colors - STUNNING Orange/Purple palette
THEME_COLORS = {
    'primary': '#f97316',       # Stunning orange
    'secondary': '#a855f7',     # Beautiful purple
    'accent': '#667eea',        # Electric blue
    'gradient_start': '#f97316',
    'gradient_mid': '#a855f7',
    'gradient_end': '#667eea',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'dark': '#0f172a',
    'darker': '#1a0d2e',
    'card_bg': '#1e293b',
    'text_primary': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'border': 'rgba(168, 85, 247, 0.2)',
    'glow_orange': 'rgba(249, 115, 22, 0.4)',
    'glow_purple': 'rgba(168, 85, 247, 0.3)',
    'light': '#f8f9fa'
}

# SLA Settings
SLA_TARGET_HOURS = 24  # 24-hour SLA target
SLA_THRESHOLDS = {
    'excellent': 98,
    'good': 95,
    'warning': 90,
    'danger': 85
}

# Performance Grade Thresholds (based on MTTR in hours)
PERFORMANCE_GRADES = {
    'A+': 2,
    'A': 4,
    'B': 6,
    'C': 8,
    'D': 10,
    'F': float('inf')
}

# Engineer names to exclude from analysis (non-field engineers)
EXCLUDED_ENGINEERS = [
    "ROLLOUT PARTNERS",
    "DUNCAN NDEGWA - PM",
    "CHEGE KENNEDY",
    "TIMOTHY GITAU",
    "WRIGHT OSEKO",
    "FIRESIDE ROLLOUT TEAM",
    "CAPACITY OPTIMIZATION TEAM"
]

# Dispatcher name mappings for standardization
DISPATCHER_MAPPING = {
    'BRIAN WAHISI': 'WAKHISI',
    'JUDITH': 'JUDITH O',
    'BRIAN WAKHISI': 'WAKHISI'
}

# Cluster name mappings
CLUSTER_MAPPING = {
    "CHANGAMWE CLUSTER": "MAZERAS-MARIAKANI"
}

# Alarm detection keywords
ALARM_ROOT_CAUSES = ["UCA", "SOC AUTO-RESOLVED"]
ALARM_CAUSE_KEYWORD = "ALARM"

# Database configurations
DB_CONFIGS = {
    1: "Production DB 1",
    2: "Production DB 2", 
    3: "CRQ DB 1",
    4: "CRQ DB 2",
    5: "OSP DB 1",
    6: "OSP DB 2"
}

# Default date format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Chart dimensions
CHART_HEIGHT = 600
CHART_WIDTH = 1200

# Color scales
COLOR_SCALES = {
    'sequential': 'Viridis',
    'diverging': 'RdYlGn',
    'qualitative': 'Plotly'
}
