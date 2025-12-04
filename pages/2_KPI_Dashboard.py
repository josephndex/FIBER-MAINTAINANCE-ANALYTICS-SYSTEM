"""
KPI Dashboard Page - Comprehensive KPI Analysis
Shows detailed KPIs with grading and performance metrics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, SLA_THRESHOLDS, PERFORMANCE_GRADES
from utils import (
    calculate_comprehensive_kpis, calculate_cluster_performance,
    calculate_engineer_performance, get_sla_grade, get_performance_grade,
    get_grade_color, format_duration
)
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("2_KPI_Dashboard.py")
log_page_visit("2_KPI_Dashboard.py")


def create_kpi_card(title, value, subtitle, grade=None, icon=""):
    """Create a STUNNING styled KPI card - FIXED grade visibility"""
    # Determine grade color
    grade_color = get_grade_color(grade) if grade else "#667eea"
    
    # Build the HTML - grade badge is properly integrated
    if grade:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            padding: 1.75rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            border-top: 4px solid #f97316;
            text-align: center;
            margin-bottom: 1rem;
        '>
            <p style='margin: 0; color: #a78bfa; font-size: 0.9rem; text-transform: uppercase; 
                       letter-spacing: 1px; font-weight: 600;'>{icon} {title}</p>
            <p style='margin: 0.75rem 0 0.5rem 0; color: #f97316; font-size: 2.25rem; font-weight: 800;'>{value}</p>
            <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>{subtitle}</p>
            <div style='margin-top: 0.75rem;'>
                <span style='
                    display: inline-block;
                    background: {grade_color};
                    color: white;
                    padding: 0.4rem 1.2rem;
                    border-radius: 25px;
                    font-weight: 800;
                    font-size: 1rem;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    text-transform: uppercase;
                    letter-spacing: 1px;
                '>Grade: {grade}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            padding: 1.75rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            border-top: 4px solid #f97316;
            text-align: center;
            margin-bottom: 1rem;
        '>
            <p style='margin: 0; color: #a78bfa; font-size: 0.9rem; text-transform: uppercase; 
                       letter-spacing: 1px; font-weight: 600;'>{icon} {title}</p>
            <p style='margin: 0.75rem 0 0.5rem 0; color: #f97316; font-size: 2.25rem; font-weight: 800;'>{value}</p>
            <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)


def create_performance_table(df, title, value_col, grade_col):
    """Create a STUNNING styled performance table with grades"""
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='rgba(249, 115, 22, 0.9)',
            font=dict(color='white', size=12, family='Arial Black'),
            align='left',
            height=45,
            line=dict(color='rgba(168, 85, 247, 0.5)', width=1)
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color=[['rgba(30, 41, 59, 0.9)', 'rgba(15, 23, 42, 0.9)'] * (len(df) // 2 + 1)][:len(df)],
            font=dict(color='#e2e8f0', size=11),
            align='left',
            height=40,
            line=dict(color='rgba(71, 85, 105, 0.3)', width=1)
        )
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#374151')),
        height=400,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig


# Page header
st.markdown("""
<div style='
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
'>
    <h1 style='margin: 0;'>KPI Dashboard</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Comprehensive Performance Metrics & Grading</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Show loading indicator while calculating KPIs
with st.spinner("Calculating comprehensive KPIs..."):
    kpis = calculate_comprehensive_kpis(df)

# Overall Performance Summary
st.markdown("### Overall Performance Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    sla_grade = kpis['sla_grade']
    compliant = kpis['total_tickets'] - kpis['breached_tickets']
    create_kpi_card(
        "SLA Compliance",
        f"{kpis['sla_compliance']:.1f}%",
        f"{compliant:,} of {kpis['total_tickets']:,} tickets",
        grade=sla_grade,
        icon=""
    )

with col2:
    perf_grade = kpis['performance_grade']
    create_kpi_card(
        "Average MTTR",
        format_duration(kpis['avg_duration']),
        f"Median: {format_duration(kpis['median_duration'])}",
        grade=perf_grade,
        icon=""
    )

with col3:
    # Calculate overall efficiency
    efficiency = (kpis['sla_compliance'] / 100) * (1 - min(1, kpis['avg_duration'] / 24)) * 100
    eff_grade = get_sla_grade(efficiency)
    create_kpi_card(
        "Efficiency Score",
        f"{efficiency:.1f}%",
        "Combined SLA + MTTR",
        grade=eff_grade,
        icon=""
    )

with col4:
    # Non-alarm rate as quality indicator
    non_alarm_rate = 100 - kpis['alarm_percentage']
    res_grade = get_sla_grade(non_alarm_rate)
    create_kpi_card(
        "Manual Tickets",
        f"{non_alarm_rate:.1f}%",
        f"{kpis['non_alarm_tickets']:,} tickets",
        grade=res_grade,
        icon=""
    )

# Detailed KPI Breakdown
st.markdown("### Detailed KPI Breakdown")

tab1, tab2, tab3, tab4 = st.tabs(["Volume Metrics", "Time Metrics", "SLA Metrics", "Resource Metrics"])

with tab1:
    # Volume metrics
    col1, col2 = st.columns(2)
    
    with col1:
        volume_data = {
            "Metric": ["Total Tickets", "Non-Alarm Tickets", "Alarm Tickets", "Active Clusters", "Service Types"],
            "Value": [
                f"{kpis['total_tickets']:,}",
                f"{kpis['non_alarm_tickets']:,}",
                f"{kpis['alarm_tickets']:,}",
                f"{kpis['active_clusters']:,}",
                f"{kpis['service_types']:,}"
            ],
            "Percentage": [
                "100%",
                f"{100 - kpis['alarm_percentage']:.1f}%",
                f"{kpis['alarm_percentage']:.1f}%",
                "-",
                "-"
            ]
        }
        st.dataframe(pd.DataFrame(volume_data), use_container_width=True, hide_index=True)
    
    with col2:
        # Volume distribution chart
        if 'SERVICE' in df.columns:
            service_dist = df['SERVICE'].value_counts().head(8)
            fig = px.pie(
                values=service_dist.values,
                names=service_dist.index,
                title="Ticket Distribution by Service",
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Time metrics
    col1, col2 = st.columns(2)
    
    with col1:
        time_data = {
            "Metric": ["Average MTTR", "Median MTTR", "Min MTTR", "Max MTTR", "Std Dev MTTR"],
            "Value": [
                format_duration(kpis['avg_duration']),
                format_duration(kpis['median_duration']),
                format_duration(kpis['min_duration']),
                format_duration(kpis['max_duration']),
                format_duration(kpis['std_duration'])
            ],
            "Hours": [
                f"{kpis['avg_duration']:.2f}h",
                f"{kpis['median_duration']:.2f}h",
                f"{kpis['min_duration']:.2f}h",
                f"{kpis['max_duration']:.2f}h",
                f"{kpis['std_duration']:.2f}h"
            ]
        }
        st.dataframe(pd.DataFrame(time_data), use_container_width=True, hide_index=True)
    
    with col2:
        # MTTR distribution histogram
        if 'DURATION' in df.columns:
            duration_hours = df['DURATION'].dropna()
            if len(duration_hours) > 0:
                # Cap at 48 hours for visualization
                duration_capped = duration_hours.clip(upper=48)
                fig = px.histogram(
                    duration_capped,
                    nbins=50,
                    title="MTTR Distribution (capped at 48h)",
                    labels={'value': 'Duration (hours)', 'count': 'Frequency'},
                    color_discrete_sequence=['#667eea']
                )
                fig.add_vline(x=24, line_dash="dash", line_color="red", 
                            annotation_text="SLA (24h)")
                fig.add_vline(x=kpis['avg_duration'], line_dash="dash", line_color="green",
                            annotation_text=f"Avg ({kpis['avg_duration']:.1f}h)")
                st.plotly_chart(fig, use_container_width=True)

with tab3:
    # SLA metrics
    col1, col2 = st.columns(2)
    
    sla_compliant = kpis['total_tickets'] - kpis['breached_tickets']
    sla_breached = kpis['breached_tickets']
    
    with col1:
        sla_data = {
            "Metric": ["SLA Compliance", "SLA Compliant", "SLA Breached", "Breach Rate", "Avg Breach Hours"],
            "Value": [
                f"{kpis['sla_compliance']:.2f}%",
                f"{sla_compliant:,}",
                f"{sla_breached:,}",
                f"{100 - kpis['sla_compliance']:.2f}%",
                f"{kpis.get('avg_breach_hours', 0):.2f}h"
            ],
            "Grade": [
                get_sla_grade(kpis['sla_compliance']),
                "-",
                "-",
                get_sla_grade(100 - (100 - kpis['sla_compliance'])),  # Inverse grade
                "-"
            ]
        }
        st.dataframe(pd.DataFrame(sla_data), use_container_width=True, hide_index=True)
    
    with col2:
        # SLA compliance gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=kpis['sla_compliance'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "SLA Compliance Rate"},
            delta={'reference': 95, 'position': "bottom"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': get_grade_color(get_sla_grade(kpis['sla_compliance']))},
                'steps': [
                    {'range': [0, 85], 'color': '#fee2e2'},
                    {'range': [85, 90], 'color': '#fef3c7'},
                    {'range': [90, 95], 'color': '#fef9c3'},
                    {'range': [95, 100], 'color': '#dcfce7'}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    # Resource metrics
    col1, col2 = st.columns(2)
    
    with col1:
        resource_data = {
            "Metric": ["Active Engineers", "Active Clusters", "Active Regions", "Service Types"],
            "Value": [
                f"{kpis['active_engineers']:,}",
                f"{kpis['active_clusters']:,}",
                f"{kpis['active_regions']:,}",
                f"{kpis['service_types']:,}"
            ]
        }
        st.dataframe(pd.DataFrame(resource_data), use_container_width=True, hide_index=True)
    
    with col2:
        # Tickets per engineer
        avg_tickets_per_engineer = kpis['total_tickets'] / kpis['active_engineers'] if kpis['active_engineers'] > 0 else 0
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=avg_tickets_per_engineer,
            title={'text': "Avg Tickets per Engineer"},
            delta={'reference': 50}
        ))
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)

# Performance Grading Guide
st.markdown("### Performance Grading Guide")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### SLA Compliance Grades")
    sla_grades = {
        "Grade": ["A+", "A", "B", "C", "D", "F"],
        "SLA %": ["≥ 99.5%", "≥ 98%", "≥ 95%", "≥ 90%", "≥ 85%", "< 85%"],
        "Rating": ["Excellent", "Very Good", "Good", "Satisfactory", "Needs Improvement", "Critical"]
    }
    sla_df = pd.DataFrame(sla_grades)
    st.dataframe(sla_df, use_container_width=True, hide_index=True)

with col2:
    st.markdown("#### MTTR Performance Grades")
    perf_grades = {
        "Grade": ["A+", "A", "B", "C", "D", "F"],
        "MTTR": ["≤ 2 hours", "≤ 4 hours", "≤ 6 hours", "≤ 8 hours", "≤ 10 hours", "> 10 hours"],
        "Rating": ["Exceptional", "Excellent", "Good", "Average", "Below Average", "Poor"]
    }
    perf_df = pd.DataFrame(perf_grades)
    st.dataframe(perf_df, use_container_width=True, hide_index=True)

# Summary Statistics
st.markdown("### Summary Statistics")

# Create a comprehensive summary table
if 'CLUSTER' in df.columns:
    with st.spinner("Analyzing cluster performance..."):
        cluster_perf = calculate_cluster_performance(df)
    if not cluster_perf.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 5 Performing Clusters")
            top_clusters = cluster_perf.head(5)[['CLUSTER', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Grade']]
            top_clusters['SLA_Compliance'] = top_clusters['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
            top_clusters['Avg_MTTR_Hours'] = top_clusters['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
            st.dataframe(top_clusters, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Bottom 5 Performing Clusters")
            bottom_clusters = cluster_perf.tail(5)[['CLUSTER', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Grade']]
            bottom_clusters['SLA_Compliance'] = bottom_clusters['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
            bottom_clusters['Avg_MTTR_Hours'] = bottom_clusters['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
            st.dataframe(bottom_clusters, use_container_width=True, hide_index=True)

# Grade distribution
if 'CLUSTER' in df.columns:
    with st.spinner("Generating grade distribution..."):
        cluster_perf = calculate_cluster_performance(df)
    if not cluster_perf.empty and 'Grade' in cluster_perf.columns:
        st.markdown("#### Grade Distribution")
        grade_dist = cluster_perf['Grade'].value_counts()
        
        # Create grade distribution bar chart
        grade_order = ['A+', 'A', 'B', 'C', 'D', 'F']
        grade_colors = ['#10b981', '#22c55e', '#f59e0b', '#f97316', '#ef4444', '#dc2626']
        
        fig = go.Figure(data=[
            go.Bar(
                x=[g for g in grade_order if g in grade_dist.index],
                y=[grade_dist.get(g, 0) for g in grade_order if g in grade_dist.index],
                marker_color=[grade_colors[grade_order.index(g)] for g in grade_order if g in grade_dist.index],
                text=[grade_dist.get(g, 0) for g in grade_order if g in grade_dist.index],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Cluster Grade Distribution",
            xaxis_title="Grade",
            yaxis_title="Number of Clusters",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("**Tip:** Use the navigation menu to dive deeper into specific metrics like Cluster Analysis, Engineer Performance, and more.")
