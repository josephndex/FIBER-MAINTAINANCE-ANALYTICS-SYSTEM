"""
Help & Documentation Page
Provides user guidance and system documentation
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, DEVELOPER_NAME

from auth import check_authentication, get_current_user, log_page_visit

# Authentication check
check_authentication()
current_user = get_current_user()

# Log page visit
log_page_visit("17_Help.py")

# Custom CSS
st.markdown("""
<style>
    .help-header {
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .help-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .help-card h3 {
        color: #a78bfa;
        margin-bottom: 1rem;
    }
    
    .help-card p, .help-card li {
        color: #e2e8f0;
    }
    
    .faq-question {
        color: #fbbf24;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    .faq-answer {
        color: #cbd5e1;
        padding-left: 1rem;
        border-left: 3px solid #7c3aed;
        margin-left: 0.5rem;
    }
    
    .shortcut-key {
        background: linear-gradient(135deg, #374151, #1f2937);
        color: #fbbf24;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-family: monospace;
        border: 1px solid #4b5563;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='help-header'>📚 Help & Documentation</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Everything you need to know about FIRESIDE</p>", unsafe_allow_html=True)

# Quick navigation tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Getting Started",
    "📊 Features Guide",
    "❓ FAQ",
    "⌨️ Shortcuts",
    "📞 Support"
])

with tab1:
    st.markdown("### 🚀 Getting Started with FIRESIDE")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='help-card'>
            <h3>📥 Loading Your Data</h3>
            <p>Follow these steps to load fiber maintenance data:</p>
            <ol>
                <li>Go to the <strong>Home</strong> page</li>
                <li>Select your <strong>Date Range</strong> in the sidebar</li>
                <li>Choose your <strong>Database Server</strong></li>
                <li>Click <strong>Load Data</strong></li>
            </ol>
            <p style="margin-top: 1rem; color: #a78bfa;">
                💡 Tip: Use the 🔄 Refresh button to reload data with the same settings.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='help-card'>
            <h3>🔐 Understanding Access Levels</h3>
            <p>Different positions have different access:</p>
            <ul>
                <li><strong style="color: #ef4444;">MANAGEMENT:</strong> Full access to all features including Admin</li>
                <li><strong style="color: #22c55e;">ENGINEER:</strong> Access to operational dashboards</li>
                <li><strong style="color: #3b82f6;">NOC:</strong> Basic viewing access</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='help-card'>
            <h3>📱 Navigation</h3>
            <p>Navigate using the sidebar menu:</p>
            <ul>
                <li><strong>🏠 Home:</strong> Overview and data loading</li>
                <li><strong>📊 KPI Dashboard:</strong> Key Performance Indicators</li>
                <li><strong>🏢 Cluster Analysis:</strong> Cluster-level metrics</li>
                <li><strong>👷 Engineer Performance:</strong> Individual engineer stats</li>
                <li><strong>🌍 Regional Analysis:</strong> Geographic breakdown</li>
                <li><strong>📈 Trends:</strong> Time-based analysis</li>
                <li><strong>🎯 SLA Analysis:</strong> Service Level Agreement tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='help-card'>
            <h3>⏱️ Session Information</h3>
            <p>Your session will automatically timeout after 30 minutes of inactivity.</p>
            <p>To stay logged in, simply interact with any page element.</p>
            <p style="margin-top: 1rem; color: #fbbf24;">
                ⚠️ Always logout when finished to secure your account.
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📊 Feature Guide")
    
    features = [
        {
            "icon": "📊",
            "name": "KPI Dashboard",
            "desc": "Track key performance indicators including MTTR, ticket resolution rates, and overall performance scores. View grades (A to F) based on performance thresholds."
        },
        {
            "icon": "🏢",
            "name": "Cluster Analysis",
            "desc": "Analyze performance by cluster. Compare ticket volumes, resolution times, and identify high-performing and underperforming clusters."
        },
        {
            "icon": "👷",
            "name": "Engineer Performance",
            "desc": "Individual engineer metrics including tickets handled, average resolution time, and performance rankings."
        },
        {
            "icon": "🌍",
            "name": "Regional Analysis",
            "desc": "Geographic breakdown of tickets and performance. Interactive maps show regional distribution and performance metrics."
        },
        {
            "icon": "🔧",
            "name": "Service Analysis",
            "desc": "Analyze performance by service type. Identify which services have the highest ticket volumes and longest resolution times."
        },
        {
            "icon": "📈",
            "name": "Trends",
            "desc": "Time-series analysis showing ticket trends over time. Identify patterns, peak periods, and improvement trends."
        },
        {
            "icon": "🎯",
            "name": "SLA Analysis",
            "desc": "Service Level Agreement tracking. Monitor SLA compliance rates and identify tickets that breached SLA targets."
        },
        {
            "icon": "⚠️",
            "name": "Challenges",
            "desc": "Identify and track challenges reported during ticket resolution. Analyze common issues and improvement areas."
        },
        {
            "icon": "🔄",
            "name": "Recurring Issues",
            "desc": "Track recurring problems and repeat tickets. Identify systemic issues that need permanent fixes."
        },
        {
            "icon": "📋",
            "name": "Reports",
            "desc": "Generate and download detailed reports. Export data to Excel for offline analysis."
        },
        {
            "icon": "🔮",
            "name": "Predictions",
            "desc": "Machine learning-powered predictions for ticket volumes and resolution times."
        }
    ]
    
    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='help-card' style='min-height: 180px;'>
                <h3>{feature['icon']} {feature['name']}</h3>
                <p>{feature['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("### ❓ Frequently Asked Questions")
    
    faqs = [
        {
            "q": "Why can't I see certain pages?",
            "a": "Page access is based on your position. MANAGEMENT has full access, while ENGINEER and NOC positions have limited access. Contact your administrator to request additional access."
        },
        {
            "q": "How often is the data updated?",
            "a": "Data is loaded on-demand when you click 'Load Data'. For real-time updates, use the 🔄 Refresh button in the sidebar."
        },
        {
            "q": "What does MTTR mean?",
            "a": "MTTR stands for Mean Time To Repair. It measures the average time taken to resolve a ticket from the time it was created."
        },
        {
            "q": "How are performance grades calculated?",
            "a": "Grades are based on predefined thresholds: A (Excellent) ≥90%, B (Good) ≥80%, C (Average) ≥70%, D (Below Average) ≥60%, F (Needs Improvement) <60%."
        },
        {
            "q": "Can I export data to Excel?",
            "a": "Yes! Most dashboards have an export option. Go to the Reports page for comprehensive data export features."
        },
        {
            "q": "Why did my session expire?",
            "a": "For security, sessions expire after 30 minutes of inactivity. Simply log in again to continue."
        },
        {
            "q": "How do I reset my password?",
            "a": "Currently, password reset must be done by an administrator through the Admin panel. Contact your system administrator for assistance."
        },
        {
            "q": "What if I encounter an error?",
            "a": "Try refreshing the page first. If the error persists, note the error message and contact support with details of what you were doing when the error occurred."
        }
    ]
    
    for faq in faqs:
        st.markdown(f"<p class='faq-question'>Q: {faq['q']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='faq-answer'>{faq['a']}</p>", unsafe_allow_html=True)

with tab4:
    st.markdown("### ⌨️ Keyboard Shortcuts & Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='help-card'>
            <h3>🖱️ General Navigation</h3>
            <ul>
                <li><span class='shortcut-key'>Ctrl/Cmd + K</span> - Quick search</li>
                <li><span class='shortcut-key'>Ctrl/Cmd + /</span> - Toggle sidebar</li>
                <li><span class='shortcut-key'>R</span> - Rerun current page (when focused)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='help-card'>
            <h3>📊 Chart Interactions</h3>
            <ul>
                <li><strong>Hover:</strong> View detailed data points</li>
                <li><strong>Click + Drag:</strong> Zoom into a region</li>
                <li><strong>Double-click:</strong> Reset zoom</li>
                <li><strong>Legend click:</strong> Toggle series visibility</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='help-card'>
            <h3>📱 Mobile Tips</h3>
            <ul>
                <li>Swipe right to open sidebar</li>
                <li>Pinch to zoom on charts</li>
                <li>Use landscape mode for better chart viewing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='help-card'>
            <h3>💡 Pro Tips</h3>
            <ul>
                <li>Use date filters to focus on specific periods</li>
                <li>Compare different time ranges for trend analysis</li>
                <li>Export data to Excel for custom analysis</li>
                <li>Check the CEO Dashboard for executive summaries</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with tab5:
    st.markdown("### 📞 Contact & Support")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='help-card'>
            <h3>👨‍💻 Developer</h3>
            <p><strong>Name:</strong> {DEVELOPER_NAME}</p>
            <p><strong>Role:</strong> System Developer & Administrator</p>
            <p style="margin-top: 1rem;">
                For technical issues, feature requests, or bug reports, 
                please contact the developer directly.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='help-card'>
            <h3>🐛 Reporting Issues</h3>
            <p>When reporting an issue, please include:</p>
            <ol>
                <li>Screenshot of the error (if applicable)</li>
                <li>Steps to reproduce the issue</li>
                <li>Date range and filters you were using</li>
                <li>Your browser and device type</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='help-card'>
            <h3>📝 System Information</h3>
            <p><strong>Application:</strong> FIRESIDE - Fiber Maintenance Analytics</p>
            <p><strong>Version:</strong> 2.0.0</p>
            <p><strong>Framework:</strong> Streamlit</p>
            <p><strong>Database:</strong> MySQL</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='help-card'>
            <h3>🔒 Security</h3>
            <p>This system implements:</p>
            <ul>
                <li>Secure password hashing (bcrypt)</li>
                <li>Session timeout protection</li>
                <li>Role-based access control</li>
                <li>Activity audit logging</li>
            </ul>
            <p style="margin-top: 1rem; color: #fbbf24;">
                Always log out when finished and never share your credentials.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280; padding: 1rem;'>
    <p>FIRESIDE v2.0.0 | © 2025 {DEVELOPER_NAME}</p>
    <p style='font-size: 0.8rem;'>Crafted with ❤️ for Fiber Maintenance Excellence</p>
</div>
""", unsafe_allow_html=True)
