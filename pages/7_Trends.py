"""
Trends Page - Temporal Analysis and Patterns
Shows time-based trends and patterns
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS
from utils import (
    get_hourly_distribution, get_daily_distribution, get_weekly_trend,
    get_daily_trend, get_monthly_trend, format_duration
)
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("7_Trends.py")
log_page_visit("7_Trends.py")


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
    <h1 style='margin: 0;'>Trends & Patterns</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Temporal Analysis, Trends, and Pattern Detection</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Ensure datetime columns exist
if 'ESCALATED_TIME' not in df.columns:
    st.warning("No timestamp column available for trend analysis.")
    st.stop()

# Create temporal columns if not exist
# Show loading indicator during processing
with st.spinner("Processing temporal data... This may take a moment for large datasets."):
    df_temp = df.copy()
    df_temp['ESCALATED_TIME'] = pd.to_datetime(df_temp['ESCALATED_TIME'])
    df_temp['Date'] = df_temp['ESCALATED_TIME'].dt.date
    df_temp['Hour'] = df_temp['ESCALATED_TIME'].dt.hour
    df_temp['DayOfWeek'] = df_temp['ESCALATED_TIME'].dt.dayofweek
    df_temp['DayName'] = df_temp['ESCALATED_TIME'].dt.day_name()
    df_temp['Week'] = df_temp['ESCALATED_TIME'].dt.isocalendar().week
    df_temp['Month'] = df_temp['ESCALATED_TIME'].dt.to_period('M').astype(str)

# Summary metrics
st.markdown("### Temporal Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    date_range = (df_temp['ESCALATED_TIME'].max() - df_temp['ESCALATED_TIME'].min()).days
    st.metric("Analysis Period", f"{date_range} days")

with col2:
    avg_daily = len(df_temp) / max(1, date_range)
    st.metric("Avg Daily Tickets", f"{avg_daily:.1f}")

with col3:
    peak_hour = df_temp['Hour'].mode().iloc[0] if len(df_temp) > 0 else 0
    st.metric("Peak Hour", f"{peak_hour}:00")

with col4:
    peak_day = df_temp['DayName'].mode().iloc[0] if len(df_temp) > 0 else "N/A"
    st.metric("Peak Day", peak_day)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Daily Trends", "Hourly Patterns", "Weekly Analysis", "Monthly Overview"])

with tab1:
    st.markdown("#### Daily Ticket Trends")
    
    # Daily trend
    daily_trend = df_temp.groupby('Date').size().reset_index(name='Tickets')
    daily_trend['Date'] = pd.to_datetime(daily_trend['Date'])
    
    # Calculate moving averages
    daily_trend['MA_7'] = daily_trend['Tickets'].rolling(window=7, min_periods=1).mean()
    daily_trend['MA_14'] = daily_trend['Tickets'].rolling(window=14, min_periods=1).mean()
    
    fig = go.Figure()
    
    # Daily tickets
    fig.add_trace(go.Scatter(
        x=daily_trend['Date'],
        y=daily_trend['Tickets'],
        mode='lines+markers',
        name='Daily Tickets',
        line=dict(color='#667eea', width=1),
        marker=dict(size=4)
    ))
    
    # 7-day MA
    fig.add_trace(go.Scatter(
        x=daily_trend['Date'],
        y=daily_trend['MA_7'],
        mode='lines',
        name='7-Day MA',
        line=dict(color='#22c55e', width=2, dash='dash')
    ))
    
    # 14-day MA
    fig.add_trace(go.Scatter(
        x=daily_trend['Date'],
        y=daily_trend['MA_14'],
        mode='lines',
        name='14-Day MA',
        line=dict(color='#f59e0b', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title="Daily Ticket Volume with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Tickets",
        height=450,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Daily SLA trend
    if 'EXTERNAL_BREACHED' in df_temp.columns:
        daily_sla = df_temp.groupby('Date').agg({
            'EXTERNAL_BREACHED': lambda x: (x == 'No').sum() / len(x) * 100 if len(x) > 0 else 0
        }).reset_index()
        daily_sla.columns = ['Date', 'SLA_Compliance']
        daily_sla['Date'] = pd.to_datetime(daily_sla['Date'])
        daily_sla['SLA_MA_7'] = daily_sla['SLA_Compliance'].rolling(window=7, min_periods=1).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_sla['Date'],
            y=daily_sla['SLA_Compliance'],
            mode='lines+markers',
            name='Daily SLA %',
            line=dict(color='#667eea', width=1),
            marker=dict(size=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_sla['Date'],
            y=daily_sla['SLA_MA_7'],
            mode='lines',
            name='7-Day MA',
            line=dict(color='#22c55e', width=2)
        ))
        
        fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Target (95%)")
        
        fig.update_layout(
            title="Daily SLA Compliance Trend",
            xaxis_title="Date",
            yaxis_title="SLA %",
            height=350,
            yaxis=dict(range=[max(0, daily_sla['SLA_Compliance'].min() - 5), 100])
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("#### Hourly Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly bar chart
        hourly_dist = df_temp.groupby('Hour').size().reset_index(name='Tickets')
        
        fig = px.bar(
            hourly_dist,
            x='Hour',
            y='Tickets',
            title="Ticket Volume by Hour of Day",
            color='Tickets',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            height=400,
            xaxis=dict(tickmode='linear', dtick=2)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Polar/Radial hour chart
        fig = go.Figure()
        
        theta = [f"{h}:00" for h in range(24)]
        r = hourly_dist['Tickets'].tolist()
        
        fig.add_trace(go.Barpolar(
            r=r,
            theta=theta,
            marker_color=r,
            marker_colorscale='Purples'
        ))
        
        fig.update_layout(
            title="24-Hour Clock Distribution",
            height=400,
            polar=dict(
                radialaxis=dict(visible=True),
                angularaxis=dict(direction="clockwise")
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Hourly heatmap by day of week
    st.markdown("#### Hourly Heatmap by Day of Week")
    
    heatmap_data = df_temp.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
    
    # Ensure all hours are present (0-23)
    for hour in range(24):
        if hour not in heatmap_data.columns:
            heatmap_data[hour] = 0
    heatmap_data = heatmap_data.reindex(columns=range(24), fill_value=0)
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Only use days that exist in the data
    existing_days = [day_names[i] for i in heatmap_data.index if i < len(day_names)]
    heatmap_data.index = existing_days
    
    if not heatmap_data.empty:
        fig = px.imshow(
            heatmap_data.values,
            labels=dict(x="Hour of Day", y="Day of Week", color="Tickets"),
            x=[f"{h}:00" for h in range(24)],
            y=heatmap_data.index.tolist(),
            color_continuous_scale='Purples',
            aspect="auto"
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for hourly heatmap")

with tab3:
    st.markdown("#### Weekly Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week distribution
        dow_dist = df_temp.groupby('DayName').size().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ).reset_index(name='Tickets')
        dow_dist.columns = ['Day', 'Tickets']
        
        fig = px.bar(
            dow_dist,
            x='Day',
            y='Tickets',
            title="Tickets by Day of Week",
            color='Tickets',
            color_continuous_scale='Purples'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Weekly SLA by day
        if 'EXTERNAL_BREACHED' in df_temp.columns:
            dow_sla = df_temp.groupby('DayName').agg({
                'EXTERNAL_BREACHED': lambda x: (x == 'No').sum() / len(x) * 100 if len(x) > 0 else 0
            }).reset_index()
            dow_sla.columns = ['Day', 'SLA_Compliance']
            dow_sla = dow_sla.set_index('Day').reindex(
                ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            ).reset_index()
            
            fig = px.bar(
                dow_sla,
                x='Day',
                y='SLA_Compliance',
                title="SLA Compliance by Day of Week",
                color='SLA_Compliance',
                color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
            )
            fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    # Weekly trend
    weekly_trend = df_temp.groupby('Week').size().reset_index(name='Tickets')
    
    fig = px.line(
        weekly_trend,
        x='Week',
        y='Tickets',
        title="Weekly Ticket Trend",
        markers=True
    )
    fig.update_traces(line_color='#667eea', fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)')
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("#### Monthly Overview")
    
    # Monthly trend
    monthly_data = df_temp.groupby('Month').agg({
        'ESCALATED_TIME': 'count'
    }).reset_index()
    monthly_data.columns = ['Month', 'Tickets']
    
    fig = px.bar(
        monthly_data,
        x='Month',
        y='Tickets',
        title="Monthly Ticket Volume",
        color='Tickets',
        color_continuous_scale='Purples'
    )
    fig.update_layout(height=350, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly SLA trend
    if 'EXTERNAL_BREACHED' in df_temp.columns:
        monthly_sla = df_temp.groupby('Month').agg({
            'EXTERNAL_BREACHED': lambda x: (x == 'No').sum() / len(x) * 100 if len(x) > 0 else 0
        }).reset_index()
        monthly_sla.columns = ['Month', 'SLA_Compliance']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                monthly_sla,
                x='Month',
                y='SLA_Compliance',
                title="Monthly SLA Trend",
                markers=True
            )
            fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target")
            fig.update_traces(line_color='#667eea')
            fig.update_layout(height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Monthly MTTR
            if 'DURATION' in df_temp.columns:
                monthly_mttr = df_temp.groupby('Month').agg({
                    'DURATION': 'mean'
                }).reset_index()
                monthly_mttr.columns = ['Month', 'Avg_MTTR']
                
                fig = px.bar(
                    monthly_mttr,
                    x='Month',
                    y='Avg_MTTR',
                    title="Monthly Average MTTR",
                    color='Avg_MTTR',
                    color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
                )
                fig.add_hline(y=24, line_dash="dash", line_color="red", annotation_text="SLA Limit")
                fig.update_layout(height=300, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

# Pattern insights
st.markdown("### Pattern Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Key Findings")
    
    # Peak analysis
    peak_hour_data = df_temp.groupby('Hour').size()
    peak_hour = peak_hour_data.idxmax()
    peak_hour_count = peak_hour_data.max()
    
    peak_day_data = df_temp.groupby('DayName').size()
    peak_day = peak_day_data.idxmax()
    peak_day_count = peak_day_data.max()
    
    low_hour = peak_hour_data.idxmin()
    low_day = peak_day_data.idxmin()
    
    st.info(f"""
    **Peak Activity:**
    - Peak Hour: **{peak_hour}:00** ({peak_hour_count:,} tickets)
    - Peak Day: **{peak_day}** ({peak_day_count:,} tickets)
    
    **Low Activity:**
    - Lowest Hour: **{low_hour}:00**
    - Lowest Day: **{low_day}**
    """)

with col2:
    st.markdown("#### Trend Summary")
    
    # Calculate week-over-week change
    weekly_data = df_temp.groupby('Week').size()
    if len(weekly_data) >= 2:
        last_week = weekly_data.iloc[-1]
        prev_week = weekly_data.iloc[-2]
        wow_change = ((last_week - prev_week) / prev_week * 100) if prev_week > 0 else 0
        
        st.metric(
            "Week-over-Week Change",
            f"{last_week:,} tickets",
            delta=f"{wow_change:+.1f}%",
            delta_color="inverse"  # Fewer tickets is good for maintenance
        )
    
    # Average daily by day type
    weekday_avg = df_temp[df_temp['DayOfWeek'] < 5].groupby('Date').size().mean()
    weekend_avg = df_temp[df_temp['DayOfWeek'] >= 5].groupby('Date').size().mean()
    
    st.info(f"""
    **Daily Averages:**
    - Weekday Avg: **{weekday_avg:.1f}** tickets/day
    - Weekend Avg: **{weekend_avg:.1f}** tickets/day
    """)

# Footer
st.markdown("---")
st.caption("**Tip:** Use these patterns to optimize resource allocation and predict future ticket volumes.")
