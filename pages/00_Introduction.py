"""
Introduction Page - Welcome new users to FIRESIDE
Shows system features and guides new users through the platform
"""
import streamlit as st
import sys
sys.path.insert(0, '..')

from config import APP_TITLE, DEVELOPER_NAME
from auth import (
    check_authentication, get_current_user, log_page_visit, 
    get_position_display_name, POSITIONS, get_allowed_pages
)

# NOTE: Do NOT use st.set_page_config here - it's handled by main.py

# Custom CSS for STUNNING Introduction page
st.markdown("""
<style>
    /* Animated background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1a0d2e, #0f172a, #1e1033);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating orbs background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 40% 60%, rgba(102, 126, 234, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 70% 30%, rgba(249, 115, 22, 0.05) 0%, transparent 35%);
        pointer-events: none;
        z-index: 0;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1033 0%, #0f172a 50%, #1a0d2e 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* STUNNING Hero Section */
    .intro-hero {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 50%, #667eea 100%);
        padding: 4rem 3rem;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 
            0 30px 80px rgba(249, 115, 22, 0.35),
            0 15px 40px rgba(168, 85, 247, 0.25),
            inset 0 1px 0 rgba(255,255,255,0.2);
        animation: heroFloat 6s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .intro-hero::before {
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
        animation: heroShine 4s ease-in-out infinite;
    }
    
    @keyframes heroShine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    @keyframes heroFloat {
        0%, 100% { 
            transform: translateY(0); 
            box-shadow: 0 30px 80px rgba(249, 115, 22, 0.35), 0 15px 40px rgba(168, 85, 247, 0.25);
        }
        50% { 
            transform: translateY(-8px); 
            box-shadow: 0 40px 100px rgba(249, 115, 22, 0.4), 0 20px 50px rgba(168, 85, 247, 0.3);
        }
    }
    
    .intro-hero h1 {
        color: white !important;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 0.75rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
    }
    
    .intro-hero p {
        color: rgba(255,255,255,0.97) !important;
        font-size: 1.3rem;
        margin: 0;
        position: relative;
        z-index: 1;
        font-weight: 500;
    }
    
    .welcome-name {
        color: #fde047 !important;
        font-weight: 800;
        font-size: 1.6rem;
        text-shadow: 0 0 20px rgba(253, 224, 71, 0.5);
    }
    
    /* STUNNING Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(168, 85, 247, 0.2);
        height: 100%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #f97316, #a855f7);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 
            0 25px 60px rgba(249, 115, 22, 0.2),
            0 15px 40px rgba(168, 85, 247, 0.15);
        border-color: #f97316;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.25rem;
        filter: drop-shadow(0 0 15px rgba(249, 115, 22, 0.4));
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .feature-title {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .feature-desc {
        color: #94a3b8 !important;
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 500;
    }
    
    .position-info {
        background: linear-gradient(135deg, #7c3aed20 0%, #a855f740 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #7c3aed60;
        margin: 2rem 0;
    }
    
    .position-title {
        color: #a855f7 !important;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .access-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .access-list li {
        color: #e2e8f0;
        padding: 0.5rem 0;
        border-bottom: 1px solid #475569;
        display: flex;
        align-items: center;
    }
    
    .access-list li:last-child {
        border-bottom: none;
    }
    
    .access-check {
        color: #10b981;
        margin-right: 0.75rem;
        font-size: 1.2rem;
    }
    
    .step-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #f97316;
        margin-bottom: 1rem;
    }
    
    .step-number {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 1rem;
    }
    
    .step-title {
        color: #e2e8f0 !important;
        font-size: 1.1rem;
        font-weight: 600;
        display: inline;
    }
    
    .step-desc {
        color: #94a3b8;
        margin-top: 0.5rem;
        padding-left: 3.5rem;
    }
    
    .cta-container {
        background: linear-gradient(135deg, #f97316 0%, #dc2626 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.4);
    }
    
    .cta-title {
        color: white !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .cta-desc {
        color: rgba(255,255,255,0.9) !important;
        margin-bottom: 1.5rem;
    }
    
    .signature {
        background: linear-gradient(90deg, #f97316, #ea580c, #f97316);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        font-weight: 600;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not check_authentication():
    st.warning("Please log in to view this page")
    try:
        st.switch_page("pages/0_Login.py")
    except:
        st.rerun()
    st.stop()

# Get current user
user = get_current_user()
log_page_visit("00_Introduction.py")

# User info
user_name = user.get('full_name', user.get('username', 'User'))
position = user.get('position', 'NOC')
position_display = get_position_display_name(position)
allowed_pages = get_allowed_pages(user)

# Hero Section
st.markdown(f"""
<div class='intro-hero'>
    <h1>🎉 Welcome to FIRESIDE</h1>
    <p>Fiber Maintenance Analytics System</p>
    <p class='welcome-name'>Hello, {user_name}!</p>
    <p style='margin-top: 0.5rem; color: rgba(255,255,255,0.8);'>You're logged in as <strong>{position_display}</strong></p>
</div>
""", unsafe_allow_html=True)

# Introduction text
st.markdown("""
<div style='text-align: center; padding: 1rem 0 2rem 0;'>
    <p style='color: #e2e8f0; font-size: 1.1rem;'>
        FIRESIDE is your comprehensive platform for fiber network maintenance analytics. 
        Track performance, analyze trends, and make data-driven decisions.
    </p>
</div>
""", unsafe_allow_html=True)

# Key Features Section
st.markdown("### 🚀 Key Features")

col1, col2, col3, col4 = st.columns(4)

features = [
    {"icon": "📊", "title": "Real-time Dashboards", "desc": "Monitor KPIs, SLA metrics, and performance indicators in real-time"},
    {"icon": "👷", "title": "Engineer Analytics", "desc": "Track engineer performance, workload, and resolution times"},
    {"icon": "🏢", "title": "Cluster Analysis", "desc": "Compare performance across different clusters and regions"},
    {"icon": "📈", "title": "Trend Forecasting", "desc": "AI-powered predictions for ticket volumes and SLA breaches"}
]

for col, feature in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class='feature-card'>
            <div class='feature-icon'>{feature['icon']}</div>
            <div class='feature-title'>{feature['title']}</div>
            <div class='feature-desc'>{feature['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

# More features
col5, col6, col7, col8 = st.columns(4)

features2 = [
    {"icon": "🔍", "title": "Ticket Search", "desc": "Search and filter through all tickets with advanced criteria"},
    {"icon": "📋", "title": "Reports", "desc": "Generate comprehensive reports for stakeholders"},
    {"icon": "⚙️", "title": "Service Analysis", "desc": "Deep dive into service-level performance metrics"},
    {"icon": "🌍", "title": "Regional Views", "desc": "Geographic analysis of network performance"}
]

for col, feature in zip([col5, col6, col7, col8], features2):
    with col:
        st.markdown(f"""
        <div class='feature-card'>
            <div class='feature-icon'>{feature['icon']}</div>
            <div class='feature-title'>{feature['title']}</div>
            <div class='feature-desc'>{feature['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

# Your Access Section
st.markdown("---")
st.markdown("### 🔐 Your Access Level")

st.markdown(f"""
<div class='position-info'>
    <div class='position-title'>You are logged in as: {position_display}</div>
    <p style='color: #94a3b8; margin-bottom: 1rem;'>
        {POSITIONS.get(position, {}).get('description', 'Access to selected dashboard pages')}
    </p>
    <p style='color: #e2e8f0; font-weight: 600; margin-bottom: 0.5rem;'>Pages you can access:</p>
    <ul class='access-list'>
""", unsafe_allow_html=True)

# List accessible pages
page_display_names = {
    "1_Home.py": "🏠 Home Dashboard",
    "2_KPI_Dashboard.py": "📊 KPI Dashboard",
    "3_Cluster_Analysis.py": "🏢 Cluster Analysis",
    "4_Engineer_Performance.py": "👷 Engineer Performance",
    "5_Regional_Analysis.py": "🌍 Regional Analysis",
    "6_Service_Analysis.py": "🔧 Service Analysis",
    "7_Trends.py": "📈 Trends & Patterns",
    "8_SLA_Analysis.py": "🎯 SLA Analysis",
    "9_Challenges.py": "⚠️ Challenges",
    "10_Recurring_Issues.py": "🔄 Recurring Issues",
    "11_Admin.py": "⚙️ Admin Dashboard",
    "12_NOC Entries.py": "📝 NOC Entries",
    "13_CEO_Dashboard.py": "👔 CEO Dashboard",
    "14_Reports.py": "📋 Reports",
    "15_Predictions.py": "🔮 Predictions",
    "16_Ticket_Search.py": "🔍 Ticket Search",
    "18_Comparison.py": "📊 Comparison",
    "19_Advanced_Predictions.py": "🤖 Advanced Predictions"
}

access_html = ""
for page in allowed_pages:
    page_name = page_display_names.get(page, page.replace('_', ' ').replace('.py', ''))
    access_html += f"<li><span class='access-check'>✓</span>{page_name}</li>"

st.markdown(access_html + "</ul></div>", unsafe_allow_html=True)

# Getting Started Section
st.markdown("---")
st.markdown("### 🏁 Getting Started")

steps = [
    {"num": "1", "title": "Explore the Home Dashboard", "desc": "Start with the Home page for an overview of current system status and quick metrics"},
    {"num": "2", "title": "Check Your Performance", "desc": "Visit Engineer Performance to see individual and team metrics (if you're an engineer)"},
    {"num": "3", "title": "Analyze Trends", "desc": "Use the Trends page to identify patterns and forecast future ticket volumes"},
    {"num": "4", "title": "Generate Reports", "desc": "Create and download reports for meetings and stakeholder updates"}
]

for step in steps:
    st.markdown(f"""
    <div class='step-container'>
        <span class='step-number'>{step['num']}</span>
        <span class='step-title'>{step['title']}</span>
        <p class='step-desc'>{step['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

# CTA Section
st.markdown("""
<div class='cta-container'>
    <p class='cta-title'>Ready to explore?</p>
    <p class='cta-desc'>Click the button below to start using FIRESIDE!</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Go to Dashboard", use_container_width=True, type="primary"):
        # Mark introduction as seen
        st.session_state['intro_seen'] = True
        try:
            st.switch_page("pages/1_Home.py")
        except:
            st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 2rem 0; color: #6b7280;'>
    <p>Need help? Contact the administrator for support.</p>
    <p>Developed with ❤️ by <span class='signature'>Joseph Nderitu</span></p>
</div>
""", unsafe_allow_html=True)
