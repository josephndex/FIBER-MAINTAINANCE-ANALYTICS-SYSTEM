"""
Dispatcher Performance Page - Detailed Dispatcher Analysis
Shows dispatcher performance with ticket handling, SLA compliance, and efficiency metrics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, DISPATCHER_MAPPING
from utils import get_sla_grade, get_grade_color, format_duration
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("20_Dispatcher_Performance.py")
log_page_visit("20_Dispatcher_Performance.py")


# Page header
st.markdown("""
<div style='
    background: linear-gradient(135deg, #f97316 0%, #a855f7 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
'>
    <h1 style='margin: 0;'>Dispatcher Performance</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Ticket Handling, SLA Compliance & Efficiency Metrics</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Check if DISPATCHER column exists
if 'DISPATCHER' not in df.columns:
    st.error("DISPATCHER column not found in the data. This page requires dispatcher information.")
    st.stop()

# Calculate dispatcher performance with loading indicator
with st.spinner("Analyzing dispatcher performance... This may take a moment for large datasets."):
    # Determine the correct column names based on what exists in the dataframe
    # Use 'INC' for ticket count if available, otherwise try common alternatives
    ticket_col = None
    for col in ['INC', 'TICKET_NO', 'TICKET', 'ID']:
        if col in df.columns:
            ticket_col = col
            break
    
    if ticket_col is None:
        # Just use the index if no ticket column found
        df['_ticket_count'] = 1
        ticket_col = '_ticket_count'
    
    # Use 'DURATION' for MTTR if available
    duration_col = 'DURATION' if 'DURATION' in df.columns else None
    
    # Group by dispatcher
    agg_dict = {ticket_col: 'count'}
    
    # Add EXTERNAL_BREACHED aggregations
    if 'EXTERNAL_BREACHED' in df.columns:
        # Create temporary numeric columns for aggregation
        df_temp = df.copy()
        df_temp['_breached_no'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.strip().str.lower().isin(['no', 'false', '0', 'n']).astype(int)
        df_temp['_breached_yes'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.strip().str.lower().isin(['yes', 'true', '1', 'y']).astype(int)
        
        dispatcher_perf = df_temp.groupby('DISPATCHER').agg({
            ticket_col: 'count',
            '_breached_no': 'sum',
            '_breached_yes': 'sum'
        }).reset_index()
        dispatcher_perf.columns = ['Dispatcher', 'Total_Tickets', 'SLA_Compliant', 'SLA_Breached']
    else:
        dispatcher_perf = df.groupby('DISPATCHER').agg({
            ticket_col: 'count'
        }).reset_index()
        dispatcher_perf.columns = ['Dispatcher', 'Total_Tickets']
        dispatcher_perf['SLA_Compliant'] = dispatcher_perf['Total_Tickets']
        dispatcher_perf['SLA_Breached'] = 0
    
    # Calculate SLA compliance rate
    dispatcher_perf['SLA_Compliance'] = (
        dispatcher_perf['SLA_Compliant'] / dispatcher_perf['Total_Tickets'] * 100
    )
    
    # Add average MTTR/Duration if available
    if duration_col and duration_col in df.columns:
        avg_mttr = df.groupby('DISPATCHER')[duration_col].mean().reset_index()
        avg_mttr.columns = ['Dispatcher', 'Avg_MTTR_Hours']
        dispatcher_perf = dispatcher_perf.merge(avg_mttr, on='Dispatcher', how='left')
        dispatcher_perf['Avg_MTTR_Hours'] = dispatcher_perf['Avg_MTTR_Hours'].fillna(0)
    else:
        dispatcher_perf['Avg_MTTR_Hours'] = 0
    
    # Calculate workload metrics
    avg_tickets = dispatcher_perf['Total_Tickets'].mean()
    max_tickets = dispatcher_perf['Total_Tickets'].max()
    
    # Workload factor: How much more work compared to average (capped at 2x credit)
    # High-volume dispatchers get bonus credit for handling stress
    dispatcher_perf['Workload_Factor'] = (dispatcher_perf['Total_Tickets'] / avg_tickets).clip(upper=2.0)
    
    # Workload category for display
    def get_workload_category(tickets, avg, max_t):
        if tickets >= max_t * 0.7:
            return 'Very High'
        elif tickets >= avg * 1.3:
            return 'High'
        elif tickets >= avg * 0.7:
            return 'Normal'
        else:
            return 'Low'
    
    dispatcher_perf['Workload_Level'] = dispatcher_perf['Total_Tickets'].apply(
        lambda x: get_workload_category(x, avg_tickets, max_tickets)
    )
    
    # MTTR Score: Lower MTTR = better (normalize to 0-100 scale)
    # Assume 24 hours is poor, 0 is perfect
    avg_mttr_overall = dispatcher_perf['Avg_MTTR_Hours'].mean() if dispatcher_perf['Avg_MTTR_Hours'].mean() > 0 else 12
    dispatcher_perf['MTTR_Score'] = (1 - (dispatcher_perf['Avg_MTTR_Hours'] / 48).clip(upper=1)) * 100
    
    # Workload-Adjusted Performance Score
    # Formula: Base performance + Workload bonus
    # Base = 60% SLA Compliance + 40% MTTR Score
    # Workload Bonus = up to 15% extra for handling high volume with good SLA
    
    dispatcher_perf['Base_Score'] = (
        (dispatcher_perf['SLA_Compliance'] * 0.6) + 
        (dispatcher_perf['MTTR_Score'] * 0.4)
    )
    
    # Workload bonus: Only applies if SLA >= 90% (handling stress well)
    # More tickets + good SLA = bonus points
    dispatcher_perf['Workload_Bonus'] = dispatcher_perf.apply(
        lambda row: min(15, (row['Workload_Factor'] - 1) * 15) if row['SLA_Compliance'] >= 90 else 0,
        axis=1
    )
    
    # Final Performance Score (capped at 100)
    dispatcher_perf['Performance_Score'] = (dispatcher_perf['Base_Score'] + dispatcher_perf['Workload_Bonus']).clip(upper=100)
    
    # Assign grade based on Performance Score (workload-adjusted)
    def get_performance_grade(score):
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    dispatcher_perf['Grade'] = dispatcher_perf['Performance_Score'].apply(get_performance_grade)
    
    # Keep Efficiency_Score as alias for backwards compatibility
    dispatcher_perf['Efficiency_Score'] = dispatcher_perf['Performance_Score']
    
    # Sort by efficiency score
    dispatcher_perf = dispatcher_perf.sort_values('Efficiency_Score', ascending=False)
    
    # Remove null/empty dispatchers
    dispatcher_perf = dispatcher_perf[
        dispatcher_perf['Dispatcher'].notna() & 
        (dispatcher_perf['Dispatcher'] != '') &
        (dispatcher_perf['Dispatcher'].astype(str) != 'nan') &
        (dispatcher_perf['Dispatcher'].astype(str).str.upper() != 'NONE')
    ]

if dispatcher_perf.empty:
    st.warning("No dispatcher data available for analysis.")
    st.stop()

# Summary metrics
st.markdown("### Dispatcher Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Dispatchers",
        f"{len(dispatcher_perf):,}",
        help="Unique dispatchers in the dataset"
    )

with col2:
    avg_sla = dispatcher_perf['SLA_Compliance'].mean()
    st.metric(
        "Avg SLA Compliance",
        f"{avg_sla:.1f}%",
        delta=f"{avg_sla - 95:.1f}% from target"
    )

with col3:
    avg_performance = dispatcher_perf['Performance_Score'].mean()
    st.metric(
        "Avg Performance",
        f"{avg_performance:.1f}%",
        help="Workload-adjusted performance (SLA + MTTR + Volume bonus)"
    )

with col4:
    high_workload = len(dispatcher_perf[dispatcher_perf['Workload_Level'].isin(['High', 'Very High'])])
    st.metric(
        "High Workload Dispatchers",
        f"{high_workload}",
        delta=f"{high_workload/len(dispatcher_perf)*100:.0f}% of team" if len(dispatcher_perf) > 0 else "0%",
        help="Dispatchers handling above-average ticket volumes"
    )

# Filters
st.markdown("### Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    grade_filter = st.multiselect(
        "Filter by Grade",
        options=['A+', 'A', 'B', 'C', 'D', 'F'],
        default=None
    )

with col2:
    min_tickets = st.number_input(
        "Minimum Tickets",
        min_value=0,
        max_value=int(dispatcher_perf['Total_Tickets'].max()) if len(dispatcher_perf) > 0 else 100,
        value=10,
        help="Filter dispatchers with at least this many tickets"
    )

with col3:
    sort_by = st.selectbox(
        "Sort By",
        options=['Performance_Score', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Total_Tickets', 'Workload_Bonus'],
        format_func=lambda x: {'Performance_Score': 'Performance (Adjusted)', 'SLA_Compliance': 'SLA Compliance', 
                               'Avg_MTTR_Hours': 'MTTR', 'Total_Tickets': 'Ticket Volume', 
                               'Workload_Bonus': 'Workload Bonus'}.get(x, x),
        index=0
    )

with col4:
    sort_order = st.radio(
        "Order",
        options=['Best First', 'Worst First'],
        horizontal=True
    )

# Apply filters
filtered_dispatchers = dispatcher_perf.copy()

if grade_filter:
    filtered_dispatchers = filtered_dispatchers[filtered_dispatchers['Grade'].isin(grade_filter)]

if min_tickets > 0:
    filtered_dispatchers = filtered_dispatchers[filtered_dispatchers['Total_Tickets'] >= min_tickets]

# Sort
ascending = (sort_order == 'Worst First') if sort_by != 'Avg_MTTR_Hours' else (sort_order == 'Best First')
filtered_dispatchers = filtered_dispatchers.sort_values(sort_by, ascending=ascending)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Performance Table", "Visualizations", "Leaderboard", "Detailed Analysis"])

with tab1:
    st.markdown("#### Dispatcher Performance Rankings")
    
    # Display dataframe
    display_df = filtered_dispatchers.copy()
    
    # Format columns
    display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
    display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
    display_df['Performance_Score'] = display_df['Performance_Score'].apply(lambda x: f"{x:.1f}%")
    display_df['Workload_Bonus'] = display_df['Workload_Bonus'].apply(lambda x: f"+{x:.1f}%" if x > 0 else "-")
    display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
    display_df['SLA_Compliant'] = display_df['SLA_Compliant'].apply(lambda x: f"{x:,}")
    display_df['SLA_Breached'] = display_df['SLA_Breached'].apply(lambda x: f"{x:,}")
    
    # Select columns - show workload level and bonus
    display_cols = ['Dispatcher', 'Total_Tickets', 'Workload_Level', 'SLA_Compliance', 'Avg_MTTR_Hours', 
                    'Workload_Bonus', 'Performance_Score', 'Grade']
    available_cols = [col for col in display_cols if col in display_df.columns]
    display_df = display_df[available_cols]
    
    # Add rank
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)
    
    # Download
    csv = display_df.to_csv(index=False)
    st.download_button(
        "Download as CSV",
        csv,
        "dispatcher_performance.csv",
        "text/csv",
        use_container_width=True
    )

with tab2:
    st.markdown("#### Performance Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top dispatchers by performance
        top_n = min(15, len(filtered_dispatchers))
        top_perf = filtered_dispatchers.sort_values('Performance_Score', ascending=False).head(top_n)
        
        # Stacked bar showing base score + workload bonus
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Base Score (SLA + MTTR)',
            x=top_perf['Dispatcher'],
            y=top_perf['Base_Score'],
            marker_color='#f97316'
        ))
        fig.add_trace(go.Bar(
            name='Workload Bonus',
            x=top_perf['Dispatcher'],
            y=top_perf['Workload_Bonus'],
            marker_color='#10b981'
        ))
        fig.update_layout(
            barmode='stack',
            title=f"Top {top_n} Dispatchers - Performance Breakdown",
            xaxis_tickangle=-45, 
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Workload vs Performance scatter
        fig = px.scatter(
            filtered_dispatchers,
            x='Total_Tickets',
            y='SLA_Compliance',
            color='Workload_Level',
            color_discrete_map={
                'Very High': '#dc2626', 'High': '#f97316', 
                'Normal': '#f59e0b', 'Low': '#10b981'
            },
            size='Performance_Score',
            hover_name='Dispatcher',
            title="Workload vs SLA (size = performance)"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="SLA Target")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Grade distribution
        grade_dist = dispatcher_perf['Grade'].value_counts()
        grade_colors = {
            'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
            'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
        }
        grade_order = ['A+', 'A', 'B', 'C', 'D', 'F']
        
        fig = go.Figure(data=[go.Pie(
            labels=[g for g in grade_order if g in grade_dist.index],
            values=[grade_dist.get(g, 0) for g in grade_order if g in grade_dist.index],
            marker_colors=[grade_colors[g] for g in grade_order if g in grade_dist.index],
            hole=0.4,
            textinfo='label+percent+value'
        )])
        fig.update_layout(title="Grade Distribution", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Workload Level distribution
        workload_dist = dispatcher_perf['Workload_Level'].value_counts()
        workload_colors = {
            'Very High': '#dc2626', 'High': '#f97316', 
            'Normal': '#f59e0b', 'Low': '#10b981'
        }
        workload_order = ['Very High', 'High', 'Normal', 'Low']
        
        fig = go.Figure(data=[go.Pie(
            labels=[w for w in workload_order if w in workload_dist.index],
            values=[workload_dist.get(w, 0) for w in workload_order if w in workload_dist.index],
            marker_colors=[workload_colors[w] for w in workload_order if w in workload_dist.index],
            hole=0.4,
            textinfo='label+percent+value'
        )])
        fig.update_layout(title="Workload Distribution", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # SLA Compliance Bar Chart
    st.markdown("##### SLA Compliance by Dispatcher")
    fig = px.bar(
        dispatcher_perf.head(20),
        x='Dispatcher',
        y='SLA_Compliance',
        color='SLA_Compliance',
        color_continuous_scale='RdYlGn',
        title="SLA Compliance % - Top 20 Dispatchers"
    )
    fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Dispatcher Leaderboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Top 10 Performers")
        top_10 = dispatcher_perf.head(10)
        
        for idx, (_, row) in enumerate(top_10.iterrows(), 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            grade_color = get_grade_color(row['Grade'])
            
            workload_badge = '🔥' if row['Workload_Level'] in ['Very High', 'High'] else ''
            bonus_text = f" (+{row['Workload_Bonus']:.0f}% bonus)" if row['Workload_Bonus'] > 0 else ""
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; 
                        border-left: 4px solid {grade_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
                <span style='font-size: 1.5rem;'>{medal}</span>
                <strong style='font-size: 1.1rem; color: #f1f5f9;'>{row['Dispatcher']}</strong> {workload_badge}
                <span style='float: right; background: {grade_color}; color: white; padding: 0.2rem 0.6rem; 
                             border-radius: 15px; font-weight: bold;'>{row['Grade']}</span>
                <br>
                <span style='color: #94a3b8; font-size: 0.85rem;'>
                    Performance: {row['Performance_Score']:.1f}%{bonus_text} | 
                    SLA: {row['SLA_Compliance']:.1f}% | 
                    MTTR: {row['Avg_MTTR_Hours']:.1f}h | 
                    Tickets: {row['Total_Tickets']:,} ({row['Workload_Level']})
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### Needs Improvement (Bottom 10)")
        bottom_10 = dispatcher_perf.tail(10).iloc[::-1]
        
        for idx, (_, row) in enumerate(bottom_10.iterrows(), 1):
            grade_color = get_grade_color(row['Grade'])
            
            workload_badge = '🔥' if row['Workload_Level'] in ['Very High', 'High'] else ''
            stress_note = " (High workload - may need support)" if row['Workload_Level'] in ['Very High', 'High'] else ""
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #2d1f1f 0%, #3d2929 100%); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; 
                        border-left: 4px solid {grade_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
                <span style='font-size: 1rem; color: #ef4444;'>⚠</span>
                <strong style='font-size: 1rem; color: #f1f5f9;'>{row['Dispatcher']}</strong> {workload_badge}
                <span style='float: right; background: {grade_color}; color: white; padding: 0.2rem 0.6rem; 
                             border-radius: 15px; font-weight: bold;'>{row['Grade']}</span>
                <br>
                <span style='color: #94a3b8; font-size: 0.85rem;'>
                    Performance: {row['Performance_Score']:.1f}% | 
                    SLA: {row['SLA_Compliance']:.1f}% | 
                    MTTR: {row['Avg_MTTR_Hours']:.1f}h | 
                    Tickets: {row['Total_Tickets']:,} ({row['Workload_Level']}){stress_note}
                </span>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("#### Detailed Performance Analysis")
    
    # Workload analysis
    st.markdown("##### Workload Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            dispatcher_perf,
            x='Total_Tickets',
            nbins=30,
            title="Ticket Distribution per Dispatcher",
            color_discrete_sequence=['#f97316']
        )
        fig.add_vline(x=dispatcher_perf['Total_Tickets'].mean(), line_dash="dash", 
                     line_color="red", annotation_text=f"Avg: {dispatcher_perf['Total_Tickets'].mean():.0f}")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Efficiency distribution
        fig = px.histogram(
            dispatcher_perf,
            x='Efficiency_Score',
            nbins=30,
            title="Efficiency Score Distribution",
            color_discrete_sequence=['#a855f7']
        )
        fig.add_vline(x=dispatcher_perf['Efficiency_Score'].mean(), line_dash="dash",
                     line_color="red", annotation_text=f"Avg: {dispatcher_perf['Efficiency_Score'].mean():.1f}%")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance vs Workload
    st.markdown("##### Performance vs Workload Analysis")
    
    fig = px.scatter(
        dispatcher_perf,
        x='Total_Tickets',
        y='Efficiency_Score',
        color='Grade',
        color_discrete_map={
            'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
            'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
        },
        size='SLA_Compliance',
        hover_name='Dispatcher',
        title="Does Higher Workload Affect Dispatcher Performance?",
        trendline="ols"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # SLA Breaches by Dispatcher
    st.markdown("##### SLA Breaches Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top breaching dispatchers
        top_breach = dispatcher_perf.nlargest(10, 'SLA_Breached')
        fig = px.bar(
            top_breach,
            x='Dispatcher',
            y='SLA_Breached',
            color='SLA_Breached',
            color_continuous_scale='Reds',
            title="Top 10 Dispatchers by SLA Breaches"
        )
        fig.update_layout(xaxis_tickangle=-45, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Breach rate
        fig = px.bar(
            top_breach,
            x='Dispatcher',
            y='SLA_Compliance',
            color='Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title="SLA Compliance % (Same Dispatchers)"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target")
        fig.update_layout(xaxis_tickangle=-45, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.markdown("##### Correlation Matrix")
    
    corr_cols = ['Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Efficiency_Score']
    corr_matrix = dispatcher_perf[corr_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=corr_cols,
        y=corr_cols,
        color_continuous_scale='RdBu_r',
        aspect="auto",
        text_auto='.2f'
    )
    fig.update_layout(title="Metric Correlations", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tickets by time (if ESCALATED_TIME available)
    if 'ESCALATED_TIME' in df.columns:
        st.markdown("##### Ticket Volume Trends by Dispatcher")
        
        # Select top dispatchers
        top_dispatchers = dispatcher_perf.nlargest(5, 'Total_Tickets')['Dispatcher'].tolist()
        
        df_temp = df[df['DISPATCHER'].isin(top_dispatchers)].copy()
        df_temp['Date'] = pd.to_datetime(df_temp['ESCALATED_TIME']).dt.date
        
        daily_tickets = df_temp.groupby(['Date', 'DISPATCHER']).size().reset_index(name='Tickets')
        daily_tickets['Date'] = pd.to_datetime(daily_tickets['Date'])
        
        fig = px.line(
            daily_tickets,
            x='Date',
            y='Tickets',
            color='DISPATCHER',
            title="Daily Ticket Volume - Top 5 Dispatchers",
            markers=True
        )
        fig.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

# Performance grading explanation
st.markdown("### Grading Methodology")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### Performance Grades
    | Grade | Score |
    |-------|-------|
    | A+ | ≥ 95% |
    | A | ≥ 90% |
    | B | ≥ 80% |
    | C | ≥ 70% |
    | D | ≥ 60% |
    | F | < 60% |
    """)

with col2:
    st.markdown("""
    #### Workload Levels
    | Level | Definition |
    |-------|------------|
    | 🔥 Very High | Top 30% volume |
    | High | 130%+ of average |
    | Normal | 70-130% of avg |
    | Low | Below 70% avg |
    """)

with col3:
    st.markdown("""
    #### Performance Formula
    
    **Base Score (60% SLA + 40% MTTR)**
    ```
    Base = (SLA × 0.6) + (MTTR_Score × 0.4)
    ```
    
    **Workload Bonus (up to +15%)**
    - Requires SLA ≥ 90%
    - Higher volume = bigger bonus
    - Rewards handling stress well
    """)

# Key Insights
st.markdown("### Key Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    best_dispatcher = dispatcher_perf.sort_values('Performance_Score', ascending=False).iloc[0]
    bonus_info = f" (+{best_dispatcher['Workload_Bonus']:.0f}% bonus)" if best_dispatcher['Workload_Bonus'] > 0 else ""
    st.success(f"""
    **🏆 Best Performer**
    {best_dispatcher['Dispatcher']}
    - Score: {best_dispatcher['Performance_Score']:.1f}%{bonus_info}
    - SLA: {best_dispatcher['SLA_Compliance']:.1f}%
    - Tickets: {best_dispatcher['Total_Tickets']:,}
    """)

with col2:
    # Best high-volume performer (handles stress well)
    high_vol = dispatcher_perf[dispatcher_perf['Workload_Level'].isin(['Very High', 'High'])]
    if len(high_vol) > 0:
        best_high_vol = high_vol.sort_values('Performance_Score', ascending=False).iloc[0]
        st.info(f"""
        **🔥 Best Under Pressure**
        {best_high_vol['Dispatcher']}
        - Tickets: {best_high_vol['Total_Tickets']:,} ({best_high_vol['Workload_Level']})
        - SLA: {best_high_vol['SLA_Compliance']:.1f}%
        - Bonus: +{best_high_vol['Workload_Bonus']:.0f}%
        """)
    else:
        most_tickets = dispatcher_perf.nlargest(1, 'Total_Tickets').iloc[0]
        st.info(f"""
        **📊 Highest Volume**
        {most_tickets['Dispatcher']}
        - Tickets: {most_tickets['Total_Tickets']:,}
        - SLA: {most_tickets['SLA_Compliance']:.1f}%
        """)

with col3:
    # Overwhelmed: High workload + low SLA
    overwhelmed = dispatcher_perf[
        (dispatcher_perf['Workload_Level'].isin(['Very High', 'High'])) & 
        (dispatcher_perf['SLA_Compliance'] < 90)
    ]
    if len(overwhelmed) > 0:
        st.error(f"""
        **⚠️ Potentially Overwhelmed**
        {len(overwhelmed)} dispatcher(s)
        - High workload + Low SLA
        - May need workload redistribution
        - Consider additional support
        """)
    else:
        st.success(f"""
        **✅ Team Balance**
        No overwhelmed dispatchers
        - High-volume staff maintaining SLA
        - Good workload distribution
        """)

with col4:
    # Low effort: Low workload + low SLA (no excuse)
    low_effort = dispatcher_perf[
        (dispatcher_perf['Workload_Level'].isin(['Normal', 'Low'])) & 
        (dispatcher_perf['SLA_Compliance'] < 90)
    ]
    if len(low_effort) > 0:
        st.warning(f"""
        **📉 Needs Improvement**
        {len(low_effort)} dispatcher(s)
        - Low/Normal workload
        - But SLA < 90%
        - Training may be needed
        """)
    else:
        st.success(f"""
        **✅ All Performing Well**
        Normal/Low workload staff
        - All meeting SLA targets
        """)

# Footer
st.markdown("---")
st.caption("""
**Understanding the Metrics:**
- 🔥 High workload dispatchers get bonus points for maintaining SLA under pressure
- Dispatchers with low/normal workload but poor SLA may need training (no stress excuse)
- High workload + poor SLA = potentially overwhelmed, consider redistributing tickets
""")
