"""
Fiber Maintenance Analytics System - Main Application
A comprehensive Streamlit dashboard for fiber maintenance analysis
"""
import streamlit as st
from datetime import datetime, timedelta
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT, DEVELOPER_NAME

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)

# Import auth after page config
from auth import check_authentication, get_current_user, logout, get_auth_manager, log_page_visit

# Get current user (will be None if not authenticated)
current_user = get_current_user()
auth_manager = get_auth_manager()

# Custom CSS for STUNNING dark theme - OPTIMIZED for multi-user performance
# Reduced animations to prevent client-side CPU overhead
st.markdown("""
<style>
    /* ============================================== */
    /* 🌟 STUNNING DARK THEME - PREMIUM DESIGN 🌟     */
    /* Performance optimized: reduced animations     */
    /* ============================================== */
    
    /* Static gradient background (removed animation for performance) */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1a0d2e 50%, #0f172a 100%);
        background-attachment: fixed;
    }
    
    /* Subtle static overlay effect (removed animation) */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(249, 115, 22, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(168, 85, 247, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(102, 126, 234, 0.02) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* METRIC CARDS - Glassmorphism effect */
    .stMarkdown div[style*="background: white"],
    .stMarkdown div[style*="background:white"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.6) 100%) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Fix text visibility - WHITE text on dark background */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #f1f5f9 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Main title with gradient text */
    .stMarkdown h1 {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 50%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Section headers - static gradient border */
    .stMarkdown h3 {
        color: #a78bfa !important;
        font-weight: 700 !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, #f97316, #a855f7, transparent) 1;
        position: relative;
    }
    
    /* General text in markdown blocks */
    .stMarkdown > div > p {
        color: #e2e8f0 !important;
    }
    
    /* Streamlit native elements */
    .stRadio label, .stSelectbox label, .stMultiSelect label,
    .stDateInput label, .stNumberInput label, .stTextInput label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }
    
    .stRadio div[role="radiogroup"] label {
        color: #e2e8f0 !important;
    }
    
    /* ============================================== */
    /* 🎨 STUNNING METRIC CARDS (optimized)          */
    /* ============================================== */
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(249, 115, 22, 0.2);
        border-radius: 16px;
        padding: 1.5rem !important;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: transform 0.3s ease, border-color 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    /* Static gradient border (removed animation) */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #f97316, #a855f7, #667eea);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(168, 85, 247, 0.4);
    }
    
    [data-testid="stMetric"] label {
        color: #a78bfa !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        text-shadow: 0 0 30px rgba(249, 115, 22, 0.3);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
        filter: drop-shadow(0 0 5px currentColor);
    }
    
    /* ============================================== */
    /* 📊 STUNNING CHARTS & CONTAINERS               */
    /* ============================================== */
    
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        padding: 1rem 1.5rem !important;
        font-weight: 600;
        color: #f1f5f9 !important;
    }
    
    [data-testid="stExpander"] summary:hover {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 50%, #667eea 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 50px rgba(249, 115, 22, 0.3),
            0 10px 30px rgba(168, 85, 247, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
        );
        animation: headerShine 4s ease-in-out infinite;
    }
    
    @keyframes headerShine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .main-header h1, .main-header p {
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    /* Info boxes with glow */
    .info-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid;
        border-image: linear-gradient(180deg, #f97316, #a855f7) 1;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .info-box:hover {
        transform: translateX(5px);
        box-shadow: 0 15px 40px rgba(249, 115, 22, 0.15);
    }
    
    .info-box, .info-box * {
        color: #e2e8f0 !important;
    }
    
    .info-box strong {
        color: #f97316 !important;
        text-shadow: 0 0 10px rgba(249, 115, 22, 0.3);
    }
    
    /* Grade badges with glow effects */
    .grade-badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        color: white !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .grade-badge:hover {
        transform: scale(1.1);
    }
    
    .grade-a-plus { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 5px 20px rgba(16, 185, 129, 0.4);
    }
    .grade-a { 
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        box-shadow: 0 5px 20px rgba(34, 197, 94, 0.4);
    }
    .grade-b { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        box-shadow: 0 5px 20px rgba(245, 158, 11, 0.4);
    }
    .grade-c { 
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        box-shadow: 0 5px 20px rgba(249, 115, 22, 0.4);
    }
    .grade-d { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 5px 20px rgba(239, 68, 68, 0.4);
    }
    .grade-f { 
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        box-shadow: 0 5px 20px rgba(220, 38, 38, 0.4);
    }
    
    /* ============================================== */
    /* 📑 STUNNING TABS                               */
    /* ============================================== */
    
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 16px;
        padding: 0.5rem;
        gap: 0.5rem;
        border: 1px solid rgba(168, 85, 247, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #a78bfa !important;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        color: #f97316 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    /* ============================== */
    /* BEAUTIFUL SIDEBAR STYLING      */
    /* Orange & Purple Theme          */
    /* ============================== */
    
    /* Sidebar base styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1033 0%, #0f172a 50%, #1a0d2e 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar navigation container */
    section[data-testid="stSidebar"] nav {
        padding: 0.5rem 0;
    }
    
    /* Navigation links - default state */
    section[data-testid="stSidebar"] nav a {
        display: block;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0.5rem;
        border-radius: 12px;
        text-decoration: none;
        color: #c4b5fd !important;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: transparent;
        border: 1px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    /* Navigation links - hover state */
    section[data-testid="stSidebar"] nav a:hover {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%) !important;
        border-color: rgba(249, 115, 22, 0.3);
        color: #f97316 !important;
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.2);
    }
    
    /* Navigation links - active/selected state */
    section[data-testid="stSidebar"] nav a[aria-current="page"],
    section[data-testid="stSidebar"] nav a[data-selected="true"],
    section[data-testid="stSidebar"] nav a.active,
    section[data-testid="stSidebar"] nav span[data-baseweb="link"][aria-current="page"] {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        color: white !important;
        font-weight: 700;
        border: none;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4), 0 4px 10px rgba(168, 85, 247, 0.3);
        transform: scale(1.02);
    }
    
    section[data-testid="stSidebar"] nav a[aria-current="page"]::before,
    section[data-testid="stSidebar"] nav a[data-selected="true"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 45%, rgba(255,255,255,0.1) 50%, transparent 55%);
        background-size: 200% 200%;
        animation: shimmer-sidebar 3s ease-in-out infinite;
    }
    
    @keyframes shimmer-sidebar {
        0% { background-position: -200% -200%; }
        100% { background-position: 200% 200%; }
    }
    
    /* Selected link icon/emoji styling */
    section[data-testid="stSidebar"] nav a[aria-current="page"] span,
    section[data-testid="stSidebar"] nav a[data-selected="true"] span {
        color: white !important;
        filter: drop-shadow(0 0 3px rgba(255,255,255,0.5));
    }
    
    /* Streamlit navigation specific selectors */
    [data-testid="stSidebarNav"] {
        padding: 1rem 0;
    }
    
    [data-testid="stSidebarNav"] li {
        margin: 0.2rem 0;
    }
    
    [data-testid="stSidebarNav"] li > div > a {
        padding: 0.75rem 1.25rem !important;
        margin: 0.15rem 0.75rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        background: transparent !important;
    }
    
    [data-testid="stSidebarNav"] li > div > a:hover {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%) !important;
        transform: translateX(4px);
    }
    
    [data-testid="stSidebarNav"] li > div > a[aria-current="page"] {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.35), 0 3px 10px rgba(168, 85, 247, 0.25) !important;
    }
    
    /* Sidebar dividers with gradient */
    section[data-testid="stSidebar"] hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #f97316, #a855f7, transparent);
        margin: 1rem 0.5rem;
        opacity: 0.5;
    }
    
    /* Sidebar buttons with orange/purple theme */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4), 0 4px 10px rgba(168, 85, 247, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"],
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
        border: 1px solid #a855f7 !important;
        color: #a855f7 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    /* Sidebar select boxes */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: #f97316 !important;
        box-shadow: 0 0 10px rgba(249, 115, 22, 0.2);
    }
    
    /* Sidebar date inputs */
    section[data-testid="stSidebar"] .stDateInput > div > div {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    
    section[data-testid="stSidebar"] .stDateInput > div > div:hover {
        border-color: #a855f7 !important;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.2);
    }
    
    /* Sidebar section headers */
    section[data-testid="stSidebar"] h3 {
        background: linear-gradient(90deg, #f97316, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        font-size: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Caption styling in sidebar */
    section[data-testid="stSidebar"] .stCaption p {
        color: #6b7280 !important;
        font-size: 0.8rem;
    }
    
    /* Success/Info messages in sidebar */
    section[data-testid="stSidebar"] .stSuccess {
        background: linear-gradient(135deg, #10b98120 0%, #10b98110 100%) !important;
        border: 1px solid #10b981 !important;
        border-radius: 10px;
    }
    
    section[data-testid="stSidebar"] .stInfo {
        background: linear-gradient(135deg, #3b82f620 0%, #3b82f610 100%) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 10px;
    }
    
    /* ============================== */
    /* END SIDEBAR STYLING            */
    /* ============================== */
    
    /* ============================================== */
    /* 🔘 STUNNING BUTTONS                            */
    /* ============================================== */
    
    .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 25px rgba(249, 115, 22, 0.3),
            0 4px 15px rgba(168, 85, 247, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(249, 115, 22, 0.4),
            0 8px 25px rgba(168, 85, 247, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4);
    }
    
    /* ============================================== */
    /* 📋 STUNNING DATA TABLES                        */
    /* ============================================== */
    
    .dataframe {
        border-radius: 16px !important;
        overflow: hidden;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stDataFrame"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 16px;
        border: 1px solid rgba(168, 85, 247, 0.2);
        overflow: hidden;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stDataFrame"] table {
        border-collapse: separate;
        border-spacing: 0;
    }
    
    [data-testid="stDataFrame"] th {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%) !important;
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 1rem !important;
        border-bottom: 2px solid rgba(168, 85, 247, 0.3) !important;
    }
    
    [data-testid="stDataFrame"] td {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #e2e8f0 !important;
        padding: 0.75rem !important;
        border-bottom: 1px solid rgba(71, 85, 105, 0.3) !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stDataFrame"] tr:hover td {
        background: rgba(249, 115, 22, 0.1) !important;
    }
    
    /* ============================================== */
    /* 📝 STUNNING INPUTS                             */
    /* ============================================== */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 2px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: #f97316 !important;
        box-shadow: 
            0 0 0 3px rgba(249, 115, 22, 0.2),
            0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 2px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #a855f7 !important;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.2);
    }
    
    /* Multi-select */
    .stMultiSelect > div > div {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 2px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 12px !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* ============================================== */
    /* 🔔 STUNNING ALERTS                             */
    /* ============================================== */
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.15);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.15);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(234, 88, 12, 0.1) 100%) !important;
        border: 1px solid rgba(249, 115, 22, 0.4) !important;
        border-left: 4px solid #f97316 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.15);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
    }
    
    /* ============================================== */
    /* 📈 STUNNING PROGRESS BARS                      */
    /* ============================================== */
    
    .stProgress > div > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 10px !important;
        overflow: hidden;
        height: 12px !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #f97316 0%, #a855f7 50%, #667eea 100%) !important;
        border-radius: 10px !important;
        animation: progressGlow 2s ease-in-out infinite;
    }
    
    @keyframes progressGlow {
        0%, 100% { box-shadow: 0 0 10px rgba(249, 115, 22, 0.5); }
        50% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.6); }
    }
    
    /* ============================================== */
    /* 🎛️ STUNNING SLIDERS                           */
    /* ============================================== */
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #f97316 0%, #a855f7 100%) !important;
    }
    
    .stSlider > div > div > div > div {
        background: white !important;
        border: 3px solid #a855f7 !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    
    /* ============================================== */
    /* 🃏 STUNNING CARDS (Custom)                     */
    /* ============================================== */
    
    .metric-card, .stat-card, .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 
            0 15px 40px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before, .stat-card::before, .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #f97316, #a855f7, #667eea);
    }
    
    .metric-card:hover, .stat-card:hover, .kpi-card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 
            0 25px 60px rgba(249, 115, 22, 0.2),
            0 15px 40px rgba(168, 85, 247, 0.15);
        border-color: rgba(249, 115, 22, 0.4);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2.5rem;
        color: #6b7280;
        border-top: 2px solid transparent;
        border-image: linear-gradient(90deg, transparent, #f97316, #a855f7, transparent) 1;
        margin-top: 3rem;
        background: linear-gradient(180deg, transparent 0%, rgba(15, 23, 42, 0.5) 100%);
    }
    
    /* ============================================== */
    /* ✨ ADDITIONAL STUNNING EFFECTS                 */
    /* ============================================== */
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ea580c 0%, #7c3aed 100%);
    }
    
    /* Selection color */
    ::selection {
        background: rgba(249, 115, 22, 0.4);
        color: white;
    }
    
    /* Tooltip styling */
    [data-baseweb="tooltip"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Checkbox styling */
    .stCheckbox > label > div[data-testid="stCheckbox"] {
        border-color: #a855f7 !important;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"][aria-checked="true"] {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        border-color: transparent !important;
    }
    
    /* Radio buttons */
    .stRadio > div > label > div:first-child {
        border-color: #a855f7 !important;
    }
    
    .stRadio > div > label[data-baseweb="radio"] > div:first-child > div {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
    }
    
    /* Date picker */
    .stDateInput > div > div {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 2px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Number input spinners */
    .stNumberInput button {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        border: none !important;
        color: white !important;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 2px dashed rgba(168, 85, 247, 0.4) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #f97316 !important;
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%) !important;
    }
    
    /* Spinner/Loading animation */
    .stSpinner > div {
        border-top-color: #f97316 !important;
        border-right-color: #a855f7 !important;
    }
    
    /* Column containers */
    [data-testid="column"] {
        transition: all 0.3s ease;
    }
    
    /* Make charts look better */
    .js-plotly-plot, .plotly {
        border-radius: 16px !important;
        overflow: hidden;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Create navigation pages
login_page = st.Page("pages/0_Login.py", title="Login")
intro_page = st.Page("pages/00_Introduction.py", title="Introduction")
home_page = st.Page("pages/1_Home.py", title="Home")
kpi_page = st.Page("pages/2_KPI_Dashboard.py", title="KPI Dashboard")
cluster_page = st.Page("pages/3_Cluster_Analysis.py", title="Cluster Analysis")
engineer_page = st.Page("pages/4_Engineer_Performance.py", title="Engineer Performance")
regional_page = st.Page("pages/5_Regional_Analysis.py", title="Regional Analysis")
service_page = st.Page("pages/6_Service_Analysis.py", title="Service Analysis")
trends_page = st.Page("pages/7_Trends.py", title="Trends")
sla_page = st.Page("pages/8_SLA_Analysis.py", title="SLA Analysis")
challenges_page = st.Page("pages/9_Challenges.py", title="Challenges")
recurring_page = st.Page("pages/10_Recurring_Issues.py", title="Recurring Issues")
admin_page = st.Page("pages/11_Admin.py", title="Admin")
noc_entries_page = st.Page("pages/12_NOC Entries.py", title="NOC Entries")
ceo_dashboard_page = st.Page("pages/13_CEO_Dashboard.py", title="CEO Dashboard")
reports_page = st.Page("pages/14_Reports.py", title="Reports")
predictions_page = st.Page("pages/15_Predictions.py", title="Predictions")
ticket_search_page = st.Page("pages/16_Ticket_Search.py", title="Ticket Search")
help_page = st.Page("pages/17_❓_Help.py", title="Help")
comparison_page = st.Page("pages/18_Comparison.py", title="Comparison")
advanced_predictions_page = st.Page("pages/19_Advanced_Predictions.py", title="Advanced Predictions")
dispatcher_page = st.Page("pages/20_Dispatcher_Performance.py", title="Dispatcher Performance")
suggestions_page = st.Page("pages/21_Suggestions.py", title="Suggestions")


def show_welcome_screen():
    """Display a stunning full-screen welcome with floating orbs and dismiss button"""
    user = st.session_state.get('user')
    if not st.session_state.get('welcome_shown', False) and user:
        st.session_state.welcome_shown = True
        
        user_name = user.get('full_name', user.get('username', 'User'))
        position = user.get('position', 'Staff')
        
        # Use components.html for proper rendering
        import streamlit.components.v1 as components
        
        welcome_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                @keyframes float {{
                    0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                    25% {{ transform: translateY(-20px) rotate(5deg); }}
                    50% {{ transform: translateY(-10px) rotate(-5deg); }}
                    75% {{ transform: translateY(-25px) rotate(3deg); }}
                }}
                @keyframes pulse-glow {{
                    0%, 100% {{ box-shadow: 0 0 60px rgba(249, 115, 22, 0.6), 0 0 120px rgba(168, 85, 247, 0.4); }}
                    50% {{ box-shadow: 0 0 100px rgba(249, 115, 22, 0.8), 0 0 180px rgba(168, 85, 247, 0.6); }}
                }}
                @keyframes slideUp {{
                    from {{ transform: translateY(50px); opacity: 0; }}
                    to {{ transform: translateY(0); opacity: 1; }}
                }}
                @keyframes glow-text {{
                    0%, 100% {{ text-shadow: 0 0 20px rgba(249, 115, 22, 0.5), 0 0 40px rgba(168, 85, 247, 0.3); }}
                    50% {{ text-shadow: 0 0 40px rgba(249, 115, 22, 0.8), 0 0 60px rgba(168, 85, 247, 0.5); }}
                }}
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    background: radial-gradient(ellipse at center, #1a0d2e 0%, #0f172a 50%, #0a0a0f 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    overflow: hidden;
                }}
                .orb {{
                    position: absolute;
                    border-radius: 50%;
                    filter: blur(1px);
                    animation: float 6s ease-in-out infinite;
                }}
                .orb-1 {{
                    width: 300px; height: 300px;
                    background: radial-gradient(circle, rgba(249, 115, 22, 0.4) 0%, transparent 70%);
                    top: 10%; left: 10%;
                }}
                .orb-2 {{
                    width: 400px; height: 400px;
                    background: radial-gradient(circle, rgba(168, 85, 247, 0.35) 0%, transparent 70%);
                    top: 60%; right: 5%;
                    animation-delay: -2s;
                }}
                .orb-3 {{
                    width: 250px; height: 250px;
                    background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
                    bottom: 10%; left: 20%;
                    animation-delay: -4s;
                }}
                .welcome-content {{
                    position: relative;
                    z-index: 10;
                    text-align: center;
                    animation: slideUp 0.8s ease;
                    padding: 2rem;
                }}
                .welcome-icon {{ font-size: 4rem; margin-bottom: 1rem; animation: float 3s ease-in-out infinite; }}
                .welcome-title {{
                    font-size: 3rem;
                    font-weight: 900;
                    background: linear-gradient(135deg, #f97316 0%, #ec4899 30%, #a855f7 60%, #667eea 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.5rem;
                    animation: glow-text 3s ease-in-out infinite;
                }}
                .welcome-name {{
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: #f1f5f9;
                    margin-bottom: 0.3rem;
                }}
                .welcome-position {{
                    font-size: 1.1rem;
                    color: #a78bfa;
                    margin-bottom: 1.5rem;
                }}
                .dismiss-btn {{
                    background: linear-gradient(135deg, #f97316 0%, #a855f7 100%);
                    border: none;
                    padding: 0.8rem 2.5rem;
                    font-size: 1rem;
                    font-weight: 700;
                    color: white;
                    border-radius: 50px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    animation: pulse-glow 2s ease-in-out infinite;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                .dismiss-btn:hover {{
                    transform: scale(1.05);
                }}
                .crafted-by {{
                    margin-top: 1.5rem;
                    color: #64748b;
                    font-size: 0.85rem;
                }}
                .crafted-by .name {{
                    color: #f97316;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            
            <div class="welcome-content">
                <div class="welcome-icon">🔥</div>
                <h1 class="welcome-title">Welcome to FIRESIDE</h1>
                <p class="welcome-name">{user_name}</p>
                <p class="welcome-position">Logged in as {position}</p>
                <button class="dismiss-btn" onclick="window.parent.document.querySelector('iframe').style.display='none'">
                    Enter Dashboard
                </button>
                <div class="crafted-by">
                    Crafted with passion by <span class="name">Joseph Nderitu</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        components.html(welcome_html, height=600)


# Create navigation - Login is default if not authenticated
if check_authentication():
    # Show welcome screen on first load after login
    show_welcome_screen()
    
    pg = st.navigation(pages=[
        home_page,
        intro_page,
        ceo_dashboard_page,
        kpi_page,
        cluster_page,
        engineer_page,
        dispatcher_page,
        regional_page,
        service_page,
        trends_page,
        sla_page,
        challenges_page,
        recurring_page,
        reports_page,
        predictions_page,
        advanced_predictions_page,
        ticket_search_page,
        comparison_page,
        suggestions_page,
        help_page,
        admin_page,
        noc_entries_page
    ])
else:
    pg = st.navigation(pages=[login_page])

# Sidebar configuration - only show if authenticated
if check_authentication():
    with st.sidebar:
        # User info section
        if current_user:
            st.markdown(f"""
            <div style='text-align: center; padding: 0.5rem; background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); 
                        border-radius: 10px; margin-bottom: 1rem; border: 1px solid #667eea40;'>
                <p style='margin: 0; font-size: 0.85rem; color: #a78bfa;'>Logged in as</p>
                <p style='margin: 0; font-weight: 600; color: #e2e8f0;'>{current_user.get('full_name', current_user.get('username', 'User'))}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='color: #667eea; margin-bottom: 0.5rem;'>Fiber Analytics</h2>
            <p style='color: #6b7280; font-size: 0.9rem;'>Maintenance Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Date range selector
        st.markdown("### Date Range")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=90),
                key="start_date_input"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                key="end_date_input"
            )
        
        # Database config selector
        db_options = {
            1: "Remote Server (NDERITU)",
            2: "Local Server (localhost)"
        }
        db_config = st.selectbox(
            "Database Server",
            options=[1, 2],
            format_func=lambda x: db_options[x],
            index=1,  # Default to Local Server
            key="db_config_input",
            help="Select database: Remote (external server) or Local (localhost)"
        )
        
        # Load data button
        if st.button("Load Data", use_container_width=True, type="primary"):
            # Clear existing data to force reload
            if 'df' in st.session_state:
                del st.session_state['df']
            st.session_state['data_loaded'] = True
            st.session_state['loaded_start_date'] = start_date.strftime("%Y-%m-%d")
            st.session_state['loaded_end_date'] = end_date.strftime("%Y-%m-%d 23:59:59")
            st.session_state['loaded_db_config'] = db_config
            
            # Log data load action
            if current_user:
                auth_manager = get_auth_manager()
                auth_manager.log_activity(
                    current_user.get('id'),
                    current_user.get('username', 'Unknown'),
                    "DATA_LOAD",
                    "main",
                    f"Loaded data from {start_date} to {end_date} using DB config {db_config}"
                )
            
            st.toast("Starting data load...")
            st.rerun()
        
        # Show loading indicator if data is being loaded
        if st.session_state.get('data_loaded') and ('df' not in st.session_state or st.session_state.get('df') is None):
            st.info("Data loading in progress...")
        
        # Clear data button
        if 'df' in st.session_state and st.session_state.get('df') is not None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", use_container_width=True, type="secondary", help="Reload data with current settings"):
                    # Force refresh - clear and reload
                    if 'df' in st.session_state:
                        del st.session_state['df']
                    st.session_state['data_loaded'] = True
                    st.toast("Refreshing data...")
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear", use_container_width=True, type="secondary", help="Clear loaded data"):
                    del st.session_state['df']
                    st.session_state['data_loaded'] = False
                    st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("KPIs", use_container_width=True, type="secondary"):
                try:
                    st.switch_page("pages/2_KPI_Dashboard.py")
                except:
                    st.rerun()
        with col2:
            if st.button("Trends", use_container_width=True, type="secondary"):
                try:
                    st.switch_page("pages/7_Trends.py")
                except:
                    st.rerun()
        
        st.markdown("---")
        
        # Data status
        if 'df' in st.session_state and st.session_state['df'] is not None and not st.session_state['df'].empty:
            df = st.session_state['df']
            st.success(f"{len(df):,} records loaded")
            if 'date_range' in st.session_state:
                st.caption(st.session_state.get('date_range', ''))
        else:
            st.info("No data loaded yet")
        
        st.markdown("---")
        
        # Logout button
        if st.button("Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.caption(f"© 2025 {DEVELOPER_NAME}")
        st.caption("All rights reserved")

# Run the selected page
pg.run()
