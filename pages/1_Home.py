"""
Home Page - Executive Dashboard Overview
Provides high-level KPIs and summary statistics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, SLA_THRESHOLDS, ALARM_ROOT_CAUSES
from utils import (
    load_data_from_db, prepare_dataframe, calculate_comprehensive_kpis,
    get_sla_grade, get_performance_grade, get_grade_color, format_duration
)
from auth import require_authentication, log_page_visit, get_current_user, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("1_Home.py")

# Log page visit
log_page_visit("1_Home.py")
current_user = get_current_user()


def render_metric_card(title, value, subtitle=None, icon=None, color="primary"):
    """Render a STUNNING styled metric card - FIXED to display properly"""
    colors = {
        "primary": ("#f97316", "#a855f7"),
        "success": ("#10b981", "#059669"),
        "warning": ("#f59e0b", "#d97706"),
        "danger": ("#ef4444", "#dc2626"),
        "info": ("#3b82f6", "#2563eb")
    }
    color_pair = colors.get(color, colors["primary"])
    
    # Direct inline styling - no CSS classes that might not render
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
                padding: 1.5rem;
                border-radius: 16px;
                border-top: 4px solid {color_pair[0]};
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
                margin-bottom: 1rem;
                text-align: center;'>
        <p style='margin: 0; color: #a78bfa; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>
            {icon or ''} {title}
        </p>
        <p style='margin: 0.5rem 0; color: {color_pair[0]}; font-size: 2rem; font-weight: 800;'>
            {value}
        </p>
        <p style='margin: 0; color: #94a3b8; font-size: 0.85rem;'>
            {subtitle or ''}
        </p>
    </div>
    """, unsafe_allow_html=True)


def create_gauge_chart(value, title, max_val=100, suffix="%"):
    """Create a STUNNING gauge chart for KPIs with gradient colors"""
    if value >= 98:
        color = "#10b981"
        glow = "rgba(16, 185, 129, 0.5)"
    elif value >= 95:
        color = "#22c55e"
        glow = "rgba(34, 197, 94, 0.5)"
    elif value >= 90:
        color = "#f59e0b"
        glow = "rgba(245, 158, 11, 0.5)"
    elif value >= 85:
        color = "#f97316"
        glow = "rgba(249, 115, 22, 0.5)"
    else:
        color = "#ef4444"
        glow = "rgba(239, 68, 68, 0.5)"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#e2e8f0'}},
        number={'suffix': suffix, 'font': {'size': 28, 'color': color}},
        gauge={
            'axis': {'range': [0, max_val], 'tickcolor': "#475569", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 85], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [85, 90], 'color': 'rgba(249, 115, 22, 0.2)'},
                {'range': [90, 95], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [95, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#a855f7", 'width': 4},
                'thickness': 0.75,
                'value': 95
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e2e8f0'}
    )
    
    return fig


def create_trend_sparkline(data, title, color="#667eea"):
    """Create a mini trend line chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines+markers',
        line=dict(color=color, width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}'
    ))
    
    fig.update_layout(
        height=100,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


# Main page content - STUNNING header with visible text
st.markdown("""
<div style='background: linear-gradient(135deg, #f97316 0%, #a855f7 50%, #667eea 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 20px 50px rgba(249, 115, 22, 0.3), 0 10px 30px rgba(168, 85, 247, 0.2);
            position: relative;
            overflow: hidden;'>
    <h1 style='color: white !important; font-size: 2.5rem; font-weight: 800; margin: 0;
               text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>Fiber Maintenance Analytics</h1>
    <p style='color: rgba(255,255,255,0.95) !important; font-size: 1.2rem; margin: 0.5rem 0 0 0;
              font-weight: 500;'>Executive Dashboard - Real-time Performance Insights</p>
</div>
""", unsafe_allow_html=True)

# Check if data is loaded
if 'df' not in st.session_state or st.session_state.get('df') is None or (hasattr(st.session_state.get('df'), 'empty') and st.session_state['df'].empty):
    # Load data with sidebar parameters
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        # Create a prominent loading container
        loading_container = st.container()
        with loading_container:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                        border-radius: 15px; border: 1px solid #667eea; margin: 1rem 0;'>
                <h2 style='color: #667eea; margin-bottom: 1rem;'>Loading Data</h2>
                <p style='color: #e2e8f0;'>Please wait while we fetch your data from the database...</p>
            </div>
            """, unsafe_allow_html=True)
            
        try:
            df = load_data_from_db(
                st.session_state.get('loaded_start_date', (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")),
                st.session_state.get('loaded_end_date', datetime.now().strftime("%Y-%m-%d 23:59:59")),
                st.session_state.get('loaded_db_config', 2)
            )
            
            if df is not None and not df.empty:
                df = prepare_dataframe(df)
                st.session_state['df'] = df
                st.session_state['date_range'] = f"{st.session_state.get('loaded_start_date')} to {st.session_state.get('loaded_end_date')}"
                st.success(f"Loaded {len(df):,} records successfully!")
                st.balloons()  # Celebration effect!
                import time
                time.sleep(1)
                st.rerun()  # Refresh to show the dashboard
            else:
                st.error("No data returned from database. Please check your date range and database configuration.")
                st.session_state['data_loaded'] = False  # Reset so user can try again
                st.stop()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("Tip: Make sure the data_loader module is available and database is accessible.")
            st.session_state['data_loaded'] = False  # Reset so user can try again
            st.stop()
    else:
        st.info("""
        **Welcome to the Fiber Maintenance Analytics Dashboard!**
        
        To get started:
        1. Select your date range in the sidebar
        2. Choose the database configuration
        3. Click "Load Data" to begin analysis
        """)
        
        # Show sample metrics for demo
        st.markdown("### Sample Dashboard Preview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Total Tickets", "1,234", "Last 90 days", "", "primary")
        with col2:
            render_metric_card("SLA Compliance", "94.5%", "Within target", "", "success")
        with col3:
            render_metric_card("Avg MTTR", "4.2 hrs", "Mean time to resolve", "", "warning")
        with col4:
            render_metric_card("Active Engineers", "25", "This period", "", "info")
        
        st.stop()

# Data is loaded - show dashboard
df = st.session_state['df']

# Separate alarms from non-alarms
from utils import filter_non_alarm_data, is_alarm_ticket

# Create alarm and non-alarm dataframes
df_non_alarm = filter_non_alarm_data(df)
df_alarm = df[df.apply(lambda row: is_alarm_ticket(row), axis=1)] if 'Is_Alarm' not in df.columns else df[df['Is_Alarm'] == True]

# Calculate KPIs for BOTH (but focus on non-alarm for true performance)
# Show loading indicator during calculation
kpi_status = st.empty()
kpi_status.info("Calculating performance metrics... Please wait.")

with st.spinner("Analyzing data..."):
    kpis_all = calculate_comprehensive_kpis(df)
    kpis_non_alarm = calculate_comprehensive_kpis(df_non_alarm)

kpi_status.empty()  # Clear the status message

# Toggle for viewing mode
view_mode = st.radio(
    "View Mode",
    ["Non-Alarm Only (True Performance)", "All Tickets", "Comparison"],
    horizontal=True,
    index=0
)

# Select which KPIs to show based on view mode
if view_mode == "Non-Alarm Only (True Performance)":
    kpis = kpis_non_alarm
    df_display = df_non_alarm.copy()
    badge_text = "Non-Alarm"
elif view_mode == "All Tickets":
    kpis = kpis_all
    df_display = df.copy()
    badge_text = "All"
else:
    kpis = kpis_non_alarm  # Default to non-alarm for main display
    df_display = df_non_alarm.copy()
    badge_text = "Comparison"

# Add Date column to df_display for charts
if 'ESCALATED_TIME' in df_display.columns:
    df_display['Date'] = pd.to_datetime(df_display['ESCALATED_TIME']).dt.date

# Display date range info
st.markdown(f"""
<div class='info-box'>
    <strong>Analysis Period:</strong> {st.session_state.get('date_range', 'Not specified')} | 
    <strong>Total Records:</strong> {len(df):,} (Alarms: {len(df) - len(df_non_alarm):,}, Non-Alarm: {len(df_non_alarm):,}) | 
    <strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>
""", unsafe_allow_html=True)

# Show comparison view if selected
if view_mode == "Comparison":
    st.markdown("### Alarm vs Non-Alarm Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### With Alarms (All Tickets)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Tickets", f"{kpis_all['total_tickets']:,}")
        with c2:
            st.metric("SLA Compliance", f"{kpis_all['sla_compliance']:.1f}%")
        with c3:
            st.metric("Avg MTTR", format_duration(kpis_all['avg_duration']))
    
    with col2:
        st.markdown("#### Without Alarms (True Performance)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Tickets", f"{kpis_non_alarm['total_tickets']:,}")
        with c2:
            st.metric("SLA Compliance", f"{kpis_non_alarm['sla_compliance']:.1f}%", 
                     delta=f"{kpis_non_alarm['sla_compliance'] - kpis_all['sla_compliance']:.1f}%")
        with c3:
            st.metric("Avg MTTR", format_duration(kpis_non_alarm['avg_duration']),
                     delta=f"{kpis_non_alarm['avg_duration'] - kpis_all['avg_duration']:.1f}h")
    
    st.markdown("---")
    st.info("**Note:** Alarms are auto-generated tickets that typically have faster resolution times. Excluding them gives a more accurate view of team performance on manual/complex issues.")

# Main KPI Cards Row
st.markdown(f"### Key Performance Indicators ({badge_text})")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    render_metric_card(
        "Total Tickets",
        f"{kpis['total_tickets']:,}",
        f"Non-Alarm: {kpis['non_alarm_tickets']:,}",
        "",
        "primary"
    )

with col2:
    sla_rate = kpis['sla_compliance']
    sla_grade = kpis['sla_grade']
    sla_color = "success" if sla_rate >= 95 else "warning" if sla_rate >= 90 else "danger"
    render_metric_card(
        "SLA Compliance",
        f"{sla_rate:.1f}%",
        f"Grade: {sla_grade}",
        "",
        sla_color
    )

with col3:
    avg_duration = kpis['avg_duration']
    mttr_color = "success" if avg_duration <= 4 else "warning" if avg_duration <= 8 else "danger"
    render_metric_card(
        "Avg MTTR",
        format_duration(avg_duration),
        f"Median: {format_duration(kpis['median_duration'])}",
        "",
        mttr_color
    )

with col4:
    render_metric_card(
        "SLA Breached",
        f"{kpis['breached_tickets']:,}",
        f"{100 - kpis['sla_compliance']:.1f}% of total",
        "",
        "danger"
    )

with col5:
    render_metric_card(
        "Active Engineers",
        f"{kpis['active_engineers']:,}",
        f"Active this period",
        "",
        "info"
    )

# Gauge Charts Row
st.markdown("### Performance Gauges")

col1, col2, col3, col4 = st.columns(4)

with col1:
    fig = create_gauge_chart(kpis['sla_compliance'], "SLA Compliance")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Convert MTTR to a percentage score (lower is better)
    mttr_score = max(0, min(100, 100 - (kpis['avg_duration'] / 24 * 100)))
    fig = create_gauge_chart(mttr_score, "MTTR Score", suffix="pts")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    # Non-alarm percentage as a quality indicator
    non_alarm_rate = 100 - kpis['alarm_percentage']
    fig = create_gauge_chart(non_alarm_rate, "Manual Tickets")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    # First-time fix rate (non-recurring)
    if 'recurring_tickets' in kpis:
        ftf_rate = 100 - kpis.get('recurring_rate', 0)
    else:
        ftf_rate = 100
    fig = create_gauge_chart(ftf_rate, "First-Time Fix")
    st.plotly_chart(fig, use_container_width=True)

# Distribution Charts
st.markdown(f"### Distribution Analysis ({badge_text})")

col1, col2 = st.columns(2)

with col1:
    # Ticket by Cluster
    if 'CLUSTER' in df_display.columns:
        cluster_data = df_display['CLUSTER'].value_counts().head(10)
        fig = px.bar(
            x=cluster_data.values,
            y=cluster_data.index,
            orientation='h',
            title=f"Top 10 Clusters by Ticket Volume ({badge_text})",
            labels={'x': 'Ticket Count', 'y': 'Cluster'},
            color=cluster_data.values,
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Ticket by Service
    if 'SERVICE' in df_display.columns:
        service_data = df_display['SERVICE'].value_counts().head(8)
        fig = px.pie(
            values=service_data.values,
            names=service_data.index,
            title=f"Ticket Distribution by Service ({badge_text})",
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)

# Time-based Analysis
st.markdown(f"### Temporal Analysis ({badge_text})")

col1, col2 = st.columns(2)

with col1:
    # Daily trend
    if 'Date' in df_display.columns:
        daily_trend = df_display.groupby('Date').size().reset_index(name='Tickets')
        
        fig = px.line(
            daily_trend,
            x='Date',
            y='Tickets',
            title=f"Daily Ticket Trend ({badge_text})",
            markers=True
        )
        fig.update_traces(
            line_color='#667eea',
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        )
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Hourly distribution
    if 'HOUR' in df_display.columns:
        hourly_data = df_display['HOUR'].value_counts().sort_index()
        fig = px.bar(
            x=hourly_data.index,
            y=hourly_data.values,
            title=f"Hourly Distribution ({badge_text})",
            labels={'x': 'Hour of Day', 'y': 'Ticket Count'},
            color=hourly_data.values,
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            xaxis=dict(tickmode='linear', dtick=2),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)

# SLA Analysis
st.markdown(f"### SLA Performance Summary ({badge_text})")

col1, col2, col3 = st.columns(3)

with col1:
    # SLA by Cluster
    if 'CLUSTER' in df_display.columns and 'EXTERNAL_BREACHED' in df_display.columns:
        # Use consistent SLA calculation - NOT breached = compliant
        def calc_sla_compliance(x):
            if len(x) == 0:
                return 0
            # Count tickets where EXTERNAL_BREACHED is NOT 'Yes'/'TRUE'/'1'/'Y'
            breached = x.astype(str).str.strip().str.upper().isin(['YES', 'TRUE', '1', 'Y']).sum()
            return ((len(x) - breached) / len(x)) * 100
        
        cluster_sla = df_display.groupby('CLUSTER').agg({
            'EXTERNAL_BREACHED': calc_sla_compliance
        }).reset_index()
        cluster_sla.columns = ['Cluster', 'SLA %']
        cluster_sla = cluster_sla.sort_values('SLA %', ascending=False).head(10)
        
        fig = px.bar(
            cluster_sla,
            x='SLA %',
            y='Cluster',
            orientation='h',
            title=f"Top 10 Clusters by SLA ({badge_text})",
            color='SLA %',
            color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
        )
        fig.update_layout(
            height=350, 
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Breach reasons (by CAUSE)
    if 'EXTERNAL_BREACHED' in df_display.columns and 'CAUSE' in df_display.columns:
        breached_df = df_display[df_display['EXTERNAL_BREACHED'] == 'Yes']
        if not breached_df.empty:
            cause_breach = breached_df['CAUSE'].value_counts().head(8)
            fig = px.pie(
                values=cause_breach.values,
                names=cause_breach.index,
                title=f"Breach Causes ({badge_text})",
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No breached tickets in this period!")

with col3:
    # SLA trend over time
    if 'Date' in df_display.columns and 'EXTERNAL_BREACHED' in df_display.columns:
        # Use consistent SLA calculation - NOT breached = compliant
        def calc_daily_sla(x):
            if len(x) == 0:
                return 0
            # Count tickets where EXTERNAL_BREACHED is NOT 'Yes'/'TRUE'/'1'/'Y'
            breached = x.astype(str).str.strip().str.upper().isin(['YES', 'TRUE', '1', 'Y']).sum()
            return ((len(x) - breached) / len(x)) * 100
        
        daily_sla = df_display.groupby('Date').agg({
            'EXTERNAL_BREACHED': calc_daily_sla
        }).reset_index()
        daily_sla.columns = ['Date', 'SLA %']
        
        fig = px.line(
            daily_sla,
            x='Date',
            y='SLA %',
            title=f"SLA Trend ({badge_text})",
            markers=True
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target (95%)")
        fig.update_traces(line_color='#667eea')
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)

# Quick Stats Table
st.markdown("### Quick Statistics")

col1, col2 = st.columns(2)

with col1:
    compliant_tickets = kpis['total_tickets'] - kpis['breached_tickets']
    stats_data = {
        "Metric": [
            "Total Tickets",
            "SLA Compliant",
            "SLA Breached",
            "Average MTTR",
            "Median MTTR",
            "Max MTTR",
            "Alarm Tickets",
            "Active Clusters",
            "Active Engineers"
        ],
        "Value": [
            f"{kpis['total_tickets']:,}",
            f"{compliant_tickets:,}",
            f"{kpis['breached_tickets']:,}",
            format_duration(kpis['avg_duration']),
            format_duration(kpis['median_duration']),
            format_duration(kpis['max_duration']),
            f"{kpis['alarm_tickets']:,}",
            f"{kpis['active_clusters']:,}",
            f"{kpis['active_engineers']:,}"
        ]
    }
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

with col2:
    if 'SERVICE' in df.columns:
        service_stats = df['SERVICE'].value_counts().head(10)
        service_df = pd.DataFrame({
            "Service": service_stats.index,
            "Tickets": service_stats.values,
            "Percentage": (service_stats.values / len(df) * 100).round(1)
        })
        service_df['Percentage'] = service_df['Percentage'].apply(lambda x: f"{x}%")
        st.dataframe(service_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("""
<div class='footer'>
    <p>Fiber Maintenance Analytics Dashboard | Built with Streamlit</p>
    <p style='font-size: 0.8rem;'>Data refreshes on demand | For support, contact the Analytics Team</p>
</div>
""", unsafe_allow_html=True)
