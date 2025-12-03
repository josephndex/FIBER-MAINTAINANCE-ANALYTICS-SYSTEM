"""
Service Analysis Page - Performance by Service Type
Shows service-level metrics and analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS
from utils import (
    calculate_service_performance, get_sla_grade, get_grade_color, format_duration
)
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("6_Service_Analysis.py")
log_page_visit("6_Service_Analysis.py")


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
    <h1 style='margin: 0;'>Service Analysis</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Performance Breakdown by Service Type</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Check if SERVICE column exists
if 'SERVICE' not in df.columns:
    st.warning("No SERVICE column available in the data.")
    st.stop()

# Calculate service performance with loading indicator
with st.spinner("Analyzing service performance... This may take a moment for large datasets."):
    service_perf = calculate_service_performance(df)

if service_perf.empty:
    st.warning("No service data available for analysis.")
    st.stop()

# Summary metrics
st.markdown("### Service Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Services",
        f"{len(service_perf):,}",
        help="Number of unique service types"
    )

with col2:
    avg_sla = service_perf['SLA_Compliance'].mean()
    st.metric(
        "Avg SLA Compliance",
        f"{avg_sla:.1f}%",
        delta=f"{avg_sla - 95:.1f}% from target"
    )

with col3:
    avg_mttr = service_perf['Avg_MTTR_Hours'].mean()
    st.metric(
        "Avg MTTR",
        f"{avg_mttr:.2f}h"
    )

with col4:
    total_tickets = service_perf['Total_Tickets'].sum()
    st.metric(
        "Total Tickets",
        f"{total_tickets:,}"
    )

# Tabs
tab1, tab2, tab3 = st.tabs(["Performance Table", "Visualizations", "Deep Dive"])

with tab1:
    st.markdown("#### Service Performance Rankings")
    
    display_df = service_perf.copy()
    display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
    display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
    display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
    display_df['SLA_Compliant'] = display_df['SLA_Compliant'].apply(lambda x: f"{x:,}")
    display_df['SLA_Breached'] = display_df['SLA_Breached'].apply(lambda x: f"{x:,}")
    display_df['Percentage'] = display_df['Percentage'].apply(lambda x: f"{x:.1f}%")
    
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("#### Service Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Service distribution pie chart
        fig = px.pie(
            service_perf.head(10),
            values='Total_Tickets',
            names='SERVICE',
            title="Top 10 Services by Ticket Volume",
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # SLA by service bar chart
        top_services = service_perf.head(15)
        fig = px.bar(
            top_services.sort_values('SLA_Compliance'),
            x='SLA_Compliance',
            y='SERVICE',
            orientation='h',
            title="SLA Compliance by Service",
            color='SLA_Compliance',
            color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
        )
        fig.add_vline(x=95, line_dash="dash", line_color="green", annotation_text="Target")
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # MTTR by service
        fig = px.bar(
            service_perf.sort_values('Avg_MTTR_Hours').head(15),
            x='SERVICE',
            y='Avg_MTTR_Hours',
            title="MTTR by Service (Best Performers)",
            color='Avg_MTTR_Hours',
            color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
        )
        fig.add_hline(y=24, line_dash="dash", line_color="red", annotation_text="SLA Limit")
        fig.update_layout(height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Treemap of services
        fig = px.treemap(
            service_perf.head(20),
            path=['SERVICE'],
            values='Total_Tickets',
            color='SLA_Compliance',
            color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
            title="Service Volume Treemap (color = SLA)"
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Service Deep Dive")
    
    selected_service = st.selectbox(
        "Select a Service to Analyze",
        options=service_perf['SERVICE'].tolist()
    )
    
    if selected_service:
        service_data = df[df['SERVICE'] == selected_service]
        service_stats = service_perf[service_perf['SERVICE'] == selected_service].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Tickets", f"{service_stats['Total_Tickets']:,}")
        with col2:
            st.metric("SLA Compliance", f"{service_stats['SLA_Compliance']:.1f}%")
        with col3:
            st.metric("Avg MTTR", f"{service_stats['Avg_MTTR_Hours']:.2f}h")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Clusters for this service
            if 'CLUSTER' in service_data.columns:
                cluster_dist = service_data['CLUSTER'].value_counts().head(10)
                fig = px.bar(
                    x=cluster_dist.values,
                    y=cluster_dist.index,
                    orientation='h',
                    title=f"Top Clusters for {selected_service}",
                    labels={'x': 'Tickets', 'y': 'Cluster'},
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(height=350, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Causes for this service
            if 'CAUSE' in service_data.columns:
                cause_dist = service_data['CAUSE'].value_counts().head(8)
                fig = px.pie(
                    values=cause_dist.values,
                    names=cause_dist.index,
                    title=f"Causes for {selected_service}",
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        
        # Daily trend for this service
        if 'ESCALATED_TIME' in service_data.columns:
            service_data['Date'] = pd.to_datetime(service_data['ESCALATED_TIME']).dt.date
            daily_trend = service_data.groupby('Date').size().reset_index(name='Tickets')
            
            fig = px.line(
                daily_trend,
                x='Date',
                y='Tickets',
                title=f"Daily Ticket Trend for {selected_service}",
                markers=True
            )
            fig.update_traces(line_color='#667eea', fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

# Service insights
st.markdown("### Service Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Best Performing Services")
    best_services = service_perf[service_perf['Total_Tickets'] >= 10].head(5)
    for _, row in best_services.iterrows():
        sla_color = "#10b981" if row['SLA_Compliance'] >= 95 else "#f59e0b" if row['SLA_Compliance'] >= 90 else "#ef4444"
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 0.75rem; border-radius: 10px; margin-bottom: 0.5rem; 
                    border-left: 4px solid {sla_color};'>
            <strong style='color: #f1f5f9;'>{row['SERVICE']}</strong><br>
            <small style='color: #94a3b8;'>SLA: {row['SLA_Compliance']:.1f}% | MTTR: {row['Avg_MTTR_Hours']:.1f}h | Tickets: {row['Total_Tickets']:,}</small>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("#### Services Needing Attention")
    worst_services = service_perf[service_perf['Total_Tickets'] >= 10].tail(5).iloc[::-1]
    for _, row in worst_services.iterrows():
        sla_color = "#10b981" if row['SLA_Compliance'] >= 95 else "#f59e0b" if row['SLA_Compliance'] >= 90 else "#ef4444"
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #2d1f1f 0%, #3d2929 100%); padding: 0.75rem; border-radius: 10px; margin-bottom: 0.5rem; 
                    border-left: 4px solid {sla_color};'>
            <strong style='color: #f1f5f9;'>{row['SERVICE']}</strong><br>
            <small style='color: #94a3b8;'>SLA: {row['SLA_Compliance']:.1f}% | MTTR: {row['Avg_MTTR_Hours']:.1f}h | Tickets: {row['Total_Tickets']:,}</small>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("**Tip:** Use the Deep Dive tab to analyze specific services in detail.")
