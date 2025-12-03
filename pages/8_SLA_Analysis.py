"""
SLA Analysis Page - Deep Dive into SLA Performance
Shows detailed SLA metrics, breach analysis, and compliance tracking
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, SLA_THRESHOLDS
from utils import get_sla_grade, get_grade_color, format_duration
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("8_SLA_Analysis.py")
log_page_visit("8_SLA_Analysis.py")


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
    <h1 style='margin: 0;'>SLA Analysis</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Service Level Agreement Compliance & Breach Analysis</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Check for SLA columns
if 'EXTERNAL_BREACHED' not in df.columns:
    st.warning("No SLA breach column available in the data.")
    st.stop()

# Calculate SLA metrics with loading indicator
with st.spinner("Analyzing SLA compliance... This may take a moment for large datasets."):
    total_tickets = len(df)
    sla_compliant = len(df[df['EXTERNAL_BREACHED'] == 'No'])
    sla_breached = len(df[df['EXTERNAL_BREACHED'] == 'Yes'])
    sla_rate = (sla_compliant / total_tickets * 100) if total_tickets > 0 else 0
    sla_grade = get_sla_grade(sla_rate)

# Summary metrics
st.markdown("### SLA Performance Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "SLA Compliance",
        f"{sla_rate:.1f}%",
        delta=f"{sla_rate - 95:.1f}% from target"
    )

with col2:
    grade_color = get_grade_color(sla_grade)
    st.markdown(f"""
    <div style='text-align: center; padding: 0.5rem;'>
        <p style='margin: 0; color: #6b7280; font-size: 0.85rem;'>Grade</p>
        <span style='display: inline-block; background: {grade_color}; color: white; 
                     padding: 0.5rem 1.5rem; border-radius: 15px; font-weight: bold; font-size: 1.5rem;'>{sla_grade}</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.metric("SLA Compliant", f"{sla_compliant:,}", help="Tickets resolved within SLA")

with col4:
    st.metric("SLA Breached", f"{sla_breached:,}", help="Tickets exceeding SLA", delta_color="inverse")

with col5:
    if 'EXTERNAL_BREACHED_HOURS' in df.columns:
        avg_breach_hours = df[df['EXTERNAL_BREACHED'] == 'Yes']['EXTERNAL_BREACHED_HOURS'].mean()
        avg_breach_hours = avg_breach_hours if pd.notna(avg_breach_hours) else 0
        st.metric("Avg Breach Time", f"{avg_breach_hours:.1f}h")

# SLA Gauge
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sla_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "SLA Compliance Rate", 'font': {'size': 20}},
        delta={'reference': 95, 'position': "bottom", 'suffix': '%'},
        number={'suffix': '%', 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': get_grade_color(sla_grade)},
            'bgcolor': "white",
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

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Breach Analysis", "SLA Trends", "By Dimension", "Deep Dive"])

with tab1:
    st.markdown("#### Breach Analysis")
    
    breached_df = df[df['EXTERNAL_BREACHED'] == 'Yes']
    
    if len(breached_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Breach by cause
            if 'CAUSE' in breached_df.columns:
                cause_breach = breached_df['CAUSE'].value_counts().head(10)
                fig = px.bar(
                    x=cause_breach.values,
                    y=cause_breach.index,
                    orientation='h',
                    title="Top 10 Breach Causes",
                    labels={'x': 'Breached Tickets', 'y': 'Cause'},
                    color=cause_breach.values,
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Breach by cluster
            if 'CLUSTER' in breached_df.columns:
                cluster_breach = breached_df['CLUSTER'].value_counts().head(10)
                fig = px.pie(
                    values=cluster_breach.values,
                    names=cluster_breach.index,
                    title="Breach Distribution by Cluster (Top 10)",
                    color_discrete_sequence=px.colors.sequential.Reds_r
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Breach by service
            if 'SERVICE' in breached_df.columns:
                service_breach = breached_df['SERVICE'].value_counts().head(8)
                fig = px.bar(
                    x=service_breach.index,
                    y=service_breach.values,
                    title="Breaches by Service",
                    color=service_breach.values,
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Breach hours distribution
            if 'EXTERNAL_BREACHED_HOURS' in breached_df.columns:
                breach_hours = breached_df['EXTERNAL_BREACHED_HOURS'].dropna()
                if len(breach_hours) > 0:
                    fig = px.histogram(
                        breach_hours.clip(upper=100),
                        nbins=40,
                        title="Breach Duration Distribution",
                        labels={'value': 'Hours Over SLA', 'count': 'Frequency'},
                        color_discrete_sequence=['#ef4444']
                    )
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No SLA breaches in this period! Excellent performance!")

with tab2:
    st.markdown("#### SLA Trends Over Time")
    
    df_temp = df.copy()
    df_temp['Date'] = pd.to_datetime(df_temp['ESCALATED_TIME']).dt.date
    
    # Daily SLA trend
    daily_sla = df_temp.groupby('Date').agg({
        'EXTERNAL_BREACHED': [
            lambda x: (x == 'No').sum(),
            lambda x: (x == 'Yes').sum(),
            'count'
        ]
    }).reset_index()
    daily_sla.columns = ['Date', 'Compliant', 'Breached', 'Total']
    daily_sla['SLA_Rate'] = daily_sla['Compliant'] / daily_sla['Total'] * 100
    daily_sla['Date'] = pd.to_datetime(daily_sla['Date'])
    daily_sla['SLA_MA_7'] = daily_sla['SLA_Rate'].rolling(window=7, min_periods=1).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_sla['Date'],
        y=daily_sla['SLA_Rate'],
        mode='lines+markers',
        name='Daily SLA %',
        line=dict(color='#667eea', width=1),
        marker=dict(size=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_sla['Date'],
        y=daily_sla['SLA_MA_7'],
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color='#22c55e', width=2)
    ))
    
    fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target (95%)")
    fig.add_hline(y=90, line_dash="dot", line_color="orange", annotation_text="Warning (90%)")
    
    fig.update_layout(
        title="Daily SLA Compliance Trend",
        xaxis_title="Date",
        yaxis_title="SLA Compliance %",
        height=400,
        yaxis=dict(range=[max(0, daily_sla['SLA_Rate'].min() - 5), 100])
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Stacked area chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_sla['Date'],
        y=daily_sla['Compliant'],
        mode='lines',
        name='Compliant',
        fill='tonexty',
        line=dict(color='#22c55e')
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_sla['Date'],
        y=daily_sla['Total'],
        mode='lines',
        name='Breached',
        fill='tonexty',
        line=dict(color='#ef4444')
    ))
    
    fig.update_layout(
        title="Daily Compliant vs Breached Tickets",
        xaxis_title="Date",
        yaxis_title="Tickets",
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### SLA by Dimension")
    
    dimension = st.selectbox(
        "Select Dimension",
        options=['CLUSTER', 'REGION', 'SERVICE', 'CAUSE'],
        index=0
    )
    
    if dimension in df.columns:
        dim_sla = df.groupby(dimension).agg({
            'EXTERNAL_BREACHED': [
                lambda x: (x == 'No').sum(),
                lambda x: (x == 'Yes').sum(),
                'count'
            ]
        }).reset_index()
        dim_sla.columns = [dimension, 'Compliant', 'Breached', 'Total']
        dim_sla['SLA_Rate'] = dim_sla['Compliant'] / dim_sla['Total'] * 100
        dim_sla['Grade'] = dim_sla['SLA_Rate'].apply(get_sla_grade)
        dim_sla = dim_sla.sort_values('SLA_Rate', ascending=False)
        
        # Top performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Best Performers")
            top_perf = dim_sla.head(10)
            fig = px.bar(
                top_perf,
                x=dimension,
                y='SLA_Rate',
                color='Grade',
                color_discrete_map={
                    'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                    'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
                },
                title=f"Top 10 {dimension}s by SLA"
            )
            fig.add_hline(y=95, line_dash="dash", line_color="green")
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### Needs Improvement")
            bottom_perf = dim_sla.tail(10).iloc[::-1]
            fig = px.bar(
                bottom_perf,
                x=dimension,
                y='SLA_Rate',
                color='Grade',
                color_discrete_map={
                    'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                    'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
                },
                title=f"Bottom 10 {dimension}s by SLA"
            )
            fig.add_hline(y=95, line_dash="dash", line_color="green")
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full table
        st.markdown(f"##### Complete {dimension} SLA Table")
        display_df = dim_sla.copy()
        display_df['SLA_Rate'] = display_df['SLA_Rate'].apply(lambda x: f"{x:.1f}%")
        display_df['Total'] = display_df['Total'].apply(lambda x: f"{x:,}")
        display_df['Compliant'] = display_df['Compliant'].apply(lambda x: f"{x:,}")
        display_df['Breached'] = display_df['Breached'].apply(lambda x: f"{x:,}")
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

with tab4:
    st.markdown("#### Deep Dive Analysis")
    
    # Breach patterns
    if len(df[df['EXTERNAL_BREACHED'] == 'Yes']) > 0:
        breached_df = df[df['EXTERNAL_BREACHED'] == 'Yes'].copy()
        breached_df['Hour'] = pd.to_datetime(breached_df['ESCALATED_TIME']).dt.hour
        breached_df['DayOfWeek'] = pd.to_datetime(breached_df['ESCALATED_TIME']).dt.day_name()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Breach by hour
            hour_breach = breached_df.groupby('Hour').size().reset_index(name='Breaches')
            fig = px.bar(
                hour_breach,
                x='Hour',
                y='Breaches',
                title="Breaches by Hour of Day",
                color='Breaches',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Breach by day of week
            day_breach = breached_df.groupby('DayOfWeek').size().reindex(
                ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            ).reset_index(name='Breaches')
            day_breach.columns = ['Day', 'Breaches']
            
            fig = px.bar(
                day_breach,
                x='Day',
                y='Breaches',
                title="Breaches by Day of Week",
                color='Breaches',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Breach heatmap
        st.markdown("##### Breach Heatmap (Hour x Day)")
        heatmap_data = breached_df.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])
        
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Hour", y="Day", color="Breaches"),
            color_continuous_scale='Reds',
            aspect="auto"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# SLA grading reference
st.markdown("### SLA Grading Reference")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    | Grade | SLA Compliance | Status |
    |-------|---------------|--------|
    | A+ | ≥ 99.5% | Exceptional |
    | A | ≥ 98% | Excellent |
    | B | ≥ 95% | Good (Target) |
    | C | ≥ 90% | Satisfactory |
    | D | ≥ 85% | Needs Improvement |
    | F | < 85% | Critical |
    """)

with col2:
    st.info(f"""
    **Current Status:**
    - SLA Target: **95%**
    - Current Rate: **{sla_rate:.1f}%**
    - Grade: **{sla_grade}**
    - SLA Window: **24 hours**
    """)

# Footer
st.markdown("---")
st.caption("**Tip:** Focus on the breach patterns to identify systemic issues and optimize resource allocation.")
