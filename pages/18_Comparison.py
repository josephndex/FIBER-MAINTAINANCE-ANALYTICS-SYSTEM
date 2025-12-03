"""
Period Comparison Analysis - Fiber Maintenance Analytics System
Compare performance metrics across different time periods
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    calculate_comprehensive_kpis, filter_non_alarm_data,
    calculate_cluster_performance, calculate_engineer_performance,
    format_duration
)
from auth import require_page_access, get_current_user, log_page_visit

# Check page access
require_page_access("18_Comparison.py")
log_page_visit("Period Comparison")


def create_header():
    """Create page header"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3);'>
        <h1 style='color: white; margin: 0; text-align: center;'>📊 Period Comparison</h1>
        <p style='color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;'>
            Compare performance metrics across different time periods (Week-over-Week, Month-over-Month)
        </p>
    </div>
    """, unsafe_allow_html=True)


def create_comparison_metric(label, current, previous, format_type="number", inverse=False):
    """Create a comparison metric card"""
    if previous and previous != 0:
        change = ((current - previous) / abs(previous)) * 100
    else:
        change = 0
    
    # Determine if change is good or bad
    if inverse:  # For metrics where lower is better (e.g., MTTR, breaches)
        is_good = change <= 0
    else:  # For metrics where higher is better (e.g., SLA compliance)
        is_good = change >= 0
    
    color = "#22c55e" if is_good else "#ef4444"
    arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
    
    if format_type == "percent":
        current_str = f"{current:.1f}%"
        previous_str = f"{previous:.1f}%"
    elif format_type == "duration":
        current_str = format_duration(current)
        previous_str = format_duration(previous)
    else:
        current_str = f"{current:,.0f}"
        previous_str = f"{previous:,.0f}"
    
    return f"""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 1.5rem; border-radius: 12px; text-align: center;
                border: 1px solid #334155;'>
        <p style='color: #94a3b8; margin: 0; font-size: 0.85rem; text-transform: uppercase;'>{label}</p>
        <h2 style='color: #e2e8f0; margin: 0.5rem 0; font-size: 1.8rem;'>{current_str}</h2>
        <p style='color: #64748b; margin: 0; font-size: 0.8rem;'>Previous: {previous_str}</p>
        <p style='color: {color}; margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 600;'>
            {arrow} {abs(change):.1f}%
        </p>
    </div>
    """


def split_data_by_period(df, period_type="week"):
    """Split data into current and previous period"""
    if 'ESCALATED_TIME' not in df.columns:
        return None, None
    
    df = df.copy()
    df['ESCALATED_TIME'] = pd.to_datetime(df['ESCALATED_TIME'])
    
    max_date = df['ESCALATED_TIME'].max()
    
    if period_type == "week":
        current_start = max_date - timedelta(days=7)
        previous_start = current_start - timedelta(days=7)
        previous_end = current_start
    elif period_type == "month":
        current_start = max_date - timedelta(days=30)
        previous_start = current_start - timedelta(days=30)
        previous_end = current_start
    elif period_type == "quarter":
        current_start = max_date - timedelta(days=90)
        previous_start = current_start - timedelta(days=90)
        previous_end = current_start
    else:  # custom half
        total_days = (max_date - df['ESCALATED_TIME'].min()).days
        half = total_days // 2
        current_start = max_date - timedelta(days=half)
        previous_start = df['ESCALATED_TIME'].min()
        previous_end = current_start
    
    current_df = df[df['ESCALATED_TIME'] >= current_start]
    previous_df = df[(df['ESCALATED_TIME'] >= previous_start) & (df['ESCALATED_TIME'] < previous_end)]
    
    return current_df, previous_df


def create_comparison_chart(current_kpis, previous_kpis, metrics):
    """Create side-by-side comparison chart"""
    categories = []
    current_values = []
    previous_values = []
    
    for metric, label in metrics:
        categories.append(label)
        current_values.append(current_kpis.get(metric, 0))
        previous_values.append(previous_kpis.get(metric, 0))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current Period',
        x=categories,
        y=current_values,
        marker_color='#667eea'
    ))
    
    fig.add_trace(go.Bar(
        name='Previous Period',
        x=categories,
        y=previous_values,
        marker_color='#94a3b8'
    ))
    
    fig.update_layout(
        barmode='group',
        title='Period Comparison',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    
    return fig


def create_trend_comparison(current_df, previous_df):
    """Create daily trend comparison"""
    # Current period daily
    current_daily = current_df.groupby(current_df['ESCALATED_TIME'].dt.date).agg({
        'INC': 'count'
    }).reset_index()
    current_daily.columns = ['Date', 'Tickets']
    current_daily['Period'] = 'Current'
    current_daily['Day'] = range(1, len(current_daily) + 1)
    
    # Previous period daily
    previous_daily = previous_df.groupby(previous_df['ESCALATED_TIME'].dt.date).agg({
        'INC': 'count'
    }).reset_index()
    previous_daily.columns = ['Date', 'Tickets']
    previous_daily['Period'] = 'Previous'
    previous_daily['Day'] = range(1, len(previous_daily) + 1)
    
    # Combine
    combined = pd.concat([current_daily, previous_daily])
    
    fig = px.line(
        combined,
        x='Day',
        y='Tickets',
        color='Period',
        title='Daily Ticket Volume Comparison',
        markers=True,
        color_discrete_map={'Current': '#667eea', 'Previous': '#94a3b8'}
    )
    
    fig.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis_title='Day of Period',
        yaxis_title='Number of Tickets'
    )
    
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    
    return fig


def create_cluster_comparison(current_cluster, previous_cluster):
    """Create cluster performance comparison"""
    if current_cluster is None or previous_cluster is None:
        return None
    
    if len(current_cluster) == 0 or len(previous_cluster) == 0:
        return None
    
    # Merge on cluster
    comparison = current_cluster[['CLUSTER', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours']].copy()
    comparison.columns = ['Cluster', 'Current_Tickets', 'Current_SLA', 'Current_MTTR']
    
    previous_renamed = previous_cluster[['CLUSTER', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours']].copy()
    previous_renamed.columns = ['Cluster', 'Previous_Tickets', 'Previous_SLA', 'Previous_MTTR']
    
    comparison = comparison.merge(previous_renamed, on='Cluster', how='outer').fillna(0)
    
    # Calculate changes
    comparison['Ticket_Change'] = comparison['Current_Tickets'] - comparison['Previous_Tickets']
    comparison['SLA_Change'] = comparison['Current_SLA'] - comparison['Previous_SLA']
    comparison['MTTR_Change'] = comparison['Current_MTTR'] - comparison['Previous_MTTR']
    
    return comparison


# ==================== MAIN PAGE ====================

create_header()

# Check for data
if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.warning("⚠️ No data loaded. Please load data from the sidebar first.")
    st.stop()

df = st.session_state['df']

# Configuration
st.markdown("### Comparison Settings")

col1, col2, col3 = st.columns(3)

with col1:
    period_type = st.selectbox(
        "Comparison Period",
        ["week", "month", "quarter", "half"],
        format_func=lambda x: {
            "week": "Week-over-Week",
            "month": "Month-over-Month",
            "quarter": "Quarter-over-Quarter",
            "half": "First Half vs Second Half"
        }[x]
    )

with col2:
    exclude_alarms = st.checkbox("Exclude Alarm Tickets", value=True)

with col3:
    show_details = st.checkbox("Show Detailed Analysis", value=True)

# Split data
with st.spinner("Analyzing periods..."):
    work_df = filter_non_alarm_data(df) if exclude_alarms else df
    current_df, previous_df = split_data_by_period(work_df, period_type)

if current_df is None or previous_df is None:
    st.error("Unable to split data into periods. Check date range.")
    st.stop()

if len(current_df) == 0 or len(previous_df) == 0:
    st.warning("Insufficient data for comparison. One or both periods have no data.")
    st.stop()

# Calculate KPIs for both periods
current_kpis = calculate_comprehensive_kpis(current_df)
previous_kpis = calculate_comprehensive_kpis(previous_df)

# Period info
current_start = current_df['ESCALATED_TIME'].min().strftime('%b %d')
current_end = current_df['ESCALATED_TIME'].max().strftime('%b %d, %Y')
previous_start = previous_df['ESCALATED_TIME'].min().strftime('%b %d')
previous_end = previous_df['ESCALATED_TIME'].max().strftime('%b %d, %Y')

st.markdown(f"""
<div style='display: flex; justify-content: space-around; margin: 1rem 0;'>
    <div style='background: #667eea20; padding: 1rem 2rem; border-radius: 10px; border: 1px solid #667eea;'>
        <p style='color: #667eea; margin: 0; font-weight: 600;'>📅 Current Period</p>
        <p style='color: #e2e8f0; margin: 0;'>{current_start} - {current_end}</p>
        <p style='color: #94a3b8; margin: 0;'>{len(current_df):,} tickets</p>
    </div>
    <div style='background: #94a3b820; padding: 1rem 2rem; border-radius: 10px; border: 1px solid #94a3b8;'>
        <p style='color: #94a3b8; margin: 0; font-weight: 600;'>📅 Previous Period</p>
        <p style='color: #e2e8f0; margin: 0;'>{previous_start} - {previous_end}</p>
        <p style='color: #94a3b8; margin: 0;'>{len(previous_df):,} tickets</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Key metrics comparison
st.markdown("---")
st.markdown("### 📈 Key Metrics Comparison")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_comparison_metric(
        "Total Tickets",
        current_kpis['total_tickets'],
        previous_kpis['total_tickets'],
        "number",
        inverse=True  # Lower tickets might be better
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_comparison_metric(
        "SLA Compliance",
        current_kpis['sla_compliance'],
        previous_kpis['sla_compliance'],
        "percent",
        inverse=False  # Higher SLA is better
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_comparison_metric(
        "Avg MTTR",
        current_kpis['avg_duration'],
        previous_kpis['avg_duration'],
        "duration",
        inverse=True  # Lower MTTR is better
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_comparison_metric(
        "Breached",
        current_kpis['breached_tickets'],
        previous_kpis['breached_tickets'],
        "number",
        inverse=True  # Lower breaches is better
    ), unsafe_allow_html=True)

with col5:
    st.markdown(create_comparison_metric(
        "Active Engineers",
        current_kpis['active_engineers'],
        previous_kpis['active_engineers'],
        "number",
        inverse=False
    ), unsafe_allow_html=True)

# Visual comparisons
st.markdown("---")
st.markdown("### 📊 Visual Comparison")

col1, col2 = st.columns(2)

with col1:
    # Bar chart comparison
    metrics = [
        ('total_tickets', 'Tickets'),
        ('breached_tickets', 'Breached'),
        ('active_engineers', 'Engineers'),
        ('active_clusters', 'Clusters')
    ]
    fig = create_comparison_chart(current_kpis, previous_kpis, metrics)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Trend comparison
    fig = create_trend_comparison(current_df, previous_df)
    st.plotly_chart(fig, use_container_width=True)

# Performance indicators
st.markdown("---")
st.markdown("### 🎯 Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    # SLA gauge comparison
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
                       subplot_titles=['Current Period', 'Previous Period'])
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=current_kpis['sla_compliance'],
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': '#667eea'},
               'steps': [
                   {'range': [0, 85], 'color': '#fee2e2'},
                   {'range': [85, 95], 'color': '#fef3c7'},
                   {'range': [95, 100], 'color': '#dcfce7'}
               ],
               'threshold': {'line': {'color': '#22c55e', 'width': 4}, 'thickness': 0.75, 'value': 95}},
        number={'suffix': '%'}
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=previous_kpis['sla_compliance'],
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': '#94a3b8'},
               'steps': [
                   {'range': [0, 85], 'color': '#fee2e2'},
                   {'range': [85, 95], 'color': '#fef3c7'},
                   {'range': [95, 100], 'color': '#dcfce7'}
               ],
               'threshold': {'line': {'color': '#22c55e', 'width': 4}, 'thickness': 0.75, 'value': 95}},
        number={'suffix': '%'}
    ), row=1, col=2)
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0')
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Grade comparison
    current_grade = current_kpis['sla_grade']
    previous_grade = previous_kpis['sla_grade']
    
    grade_colors = {
        'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
        'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
    }
    
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 2rem; border-radius: 12px; text-align: center;'>
        <h4 style='color: #94a3b8; margin: 0 0 1rem 0;'>Performance Grade</h4>
        <div style='display: flex; justify-content: space-around; align-items: center;'>
            <div>
                <p style='color: #667eea; margin: 0; font-size: 0.9rem;'>Current</p>
                <span style='font-size: 3rem; font-weight: 800; color: {grade_colors.get(current_grade, "#666")};'>
                    {current_grade}
                </span>
            </div>
            <span style='font-size: 2rem; color: #475569;'>→</span>
            <div>
                <p style='color: #94a3b8; margin: 0; font-size: 0.9rem;'>Previous</p>
                <span style='font-size: 3rem; font-weight: 800; color: {grade_colors.get(previous_grade, "#666")};'>
                    {previous_grade}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Improvement summary
    improvements = []
    declines = []
    
    if current_kpis['sla_compliance'] > previous_kpis['sla_compliance']:
        improvements.append(f"SLA improved by {current_kpis['sla_compliance'] - previous_kpis['sla_compliance']:.1f}%")
    elif current_kpis['sla_compliance'] < previous_kpis['sla_compliance']:
        declines.append(f"SLA decreased by {previous_kpis['sla_compliance'] - current_kpis['sla_compliance']:.1f}%")
    
    if current_kpis['avg_duration'] < previous_kpis['avg_duration']:
        improvements.append(f"MTTR reduced by {previous_kpis['avg_duration'] - current_kpis['avg_duration']:.1f}h")
    elif current_kpis['avg_duration'] > previous_kpis['avg_duration']:
        declines.append(f"MTTR increased by {current_kpis['avg_duration'] - previous_kpis['avg_duration']:.1f}h")
    
    if current_kpis['breached_tickets'] < previous_kpis['breached_tickets']:
        improvements.append(f"Breaches reduced by {previous_kpis['breached_tickets'] - current_kpis['breached_tickets']}")
    elif current_kpis['breached_tickets'] > previous_kpis['breached_tickets']:
        declines.append(f"Breaches increased by {current_kpis['breached_tickets'] - previous_kpis['breached_tickets']}")
    
    st.markdown("""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 1.5rem; border-radius: 12px;'>
        <h4 style='color: #94a3b8; margin: 0 0 1rem 0;'>📋 Summary</h4>
    """, unsafe_allow_html=True)
    
    if improvements:
        st.markdown("**✅ Improvements:**")
        for imp in improvements:
            st.markdown(f"<p style='color: #22c55e; margin: 0.3rem 0;'>• {imp}</p>", unsafe_allow_html=True)
    
    if declines:
        st.markdown("**⚠️ Declines:**")
        for dec in declines:
            st.markdown(f"<p style='color: #ef4444; margin: 0.3rem 0;'>• {dec}</p>", unsafe_allow_html=True)
    
    if not improvements and not declines:
        st.info("No significant changes detected")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Detailed analysis
if show_details:
    st.markdown("---")
    st.markdown("### 🔍 Detailed Analysis")
    
    tab1, tab2 = st.tabs(["Cluster Comparison", "Day-of-Week Analysis"])
    
    with tab1:
        current_cluster = calculate_cluster_performance(current_df)
        previous_cluster = calculate_cluster_performance(previous_df)
        
        comparison = create_cluster_comparison(current_cluster, previous_cluster)
        
        if comparison is not None and len(comparison) > 0:
            # Show clusters with biggest changes
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📈 Most Improved Clusters (SLA)**")
                improved = comparison.nlargest(5, 'SLA_Change')[['Cluster', 'Current_SLA', 'Previous_SLA', 'SLA_Change']]
                improved.columns = ['Cluster', 'Current SLA %', 'Previous SLA %', 'Change']
                st.dataframe(improved, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**📉 Declining Clusters (SLA)**")
                declined = comparison.nsmallest(5, 'SLA_Change')[['Cluster', 'Current_SLA', 'Previous_SLA', 'SLA_Change']]
                declined.columns = ['Cluster', 'Current SLA %', 'Previous SLA %', 'Change']
                st.dataframe(declined, use_container_width=True, hide_index=True)
    
    with tab2:
        # Day of week comparison
        current_df['DayOfWeek'] = pd.to_datetime(current_df['ESCALATED_TIME']).dt.day_name()
        previous_df['DayOfWeek'] = pd.to_datetime(previous_df['ESCALATED_TIME']).dt.day_name()
        
        current_dow = current_df.groupby('DayOfWeek').size().reset_index(name='Current')
        previous_dow = previous_df.groupby('DayOfWeek').size().reset_index(name='Previous')
        
        dow_comparison = current_dow.merge(previous_dow, on='DayOfWeek', how='outer').fillna(0)
        
        # Order days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_comparison['DayOfWeek'] = pd.Categorical(dow_comparison['DayOfWeek'], categories=day_order, ordered=True)
        dow_comparison = dow_comparison.sort_values('DayOfWeek')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Current Period',
            x=dow_comparison['DayOfWeek'],
            y=dow_comparison['Current'],
            marker_color='#667eea'
        ))
        
        fig.add_trace(go.Bar(
            name='Previous Period',
            x=dow_comparison['DayOfWeek'],
            y=dow_comparison['Previous'],
            marker_color='#94a3b8'
        ))
        
        fig.update_layout(
            barmode='group',
            title='Ticket Volume by Day of Week',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Export
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Create comparison summary for export
    summary_data = {
        'Metric': ['Total Tickets', 'SLA Compliance (%)', 'Avg MTTR (hours)', 'Breached Tickets', 
                   'Active Engineers', 'Active Clusters', 'Alarm Tickets'],
        'Current Period': [
            current_kpis['total_tickets'],
            f"{current_kpis['sla_compliance']:.1f}",
            f"{current_kpis['avg_duration']:.2f}",
            current_kpis['breached_tickets'],
            current_kpis['active_engineers'],
            current_kpis['active_clusters'],
            current_kpis['alarm_tickets']
        ],
        'Previous Period': [
            previous_kpis['total_tickets'],
            f"{previous_kpis['sla_compliance']:.1f}",
            f"{previous_kpis['avg_duration']:.2f}",
            previous_kpis['breached_tickets'],
            previous_kpis['active_engineers'],
            previous_kpis['active_clusters'],
            previous_kpis['alarm_tickets']
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    csv = summary_df.to_csv(index=False)
    
    st.download_button(
        label="📥 Export Comparison Report",
        data=csv,
        file_name=f"period_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
