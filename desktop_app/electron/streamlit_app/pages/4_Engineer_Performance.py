"""
Engineer Performance Page - Detailed Engineer Analysis
Shows engineer performance with SLA compliance, efficiency, and grading
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, EXCLUDED_ENGINEERS
from utils import (
    calculate_engineer_performance, get_sla_grade, get_performance_grade,
    get_grade_color, format_duration
)
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("4_Engineer_Performance.py")
log_page_visit("4_Engineer_Performance.py")


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
    <h1 style='margin: 0;'>Engineer Performance</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Individual Engineer Metrics, SLA Compliance & Efficiency</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# ============================================
# ENGINEER EXCLUSION MANAGEMENT
# ============================================
st.markdown("""
<div style='
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border: 2px solid rgba(249, 115, 22, 0.4);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
'>
    <h3 style='margin: 0 0 0.5rem 0; color: #f97316;'>🔧 Engineer Exclusion Settings</h3>
    <p style='margin: 0; color: #e2e8f0; font-size: 0.9rem;'>
        Manage which engineers appear in performance analytics. Excluded engineers won't appear in rankings.
    </p>
</div>
""", unsafe_allow_html=True)

with st.expander("📋 Manage Excluded Engineers", expanded=False):
    # Initialize session state for custom exclusions
    if 'custom_excluded_engineers' not in st.session_state:
        st.session_state.custom_excluded_engineers = list(EXCLUDED_ENGINEERS)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🚫 Currently Excluded")
        if st.session_state.custom_excluded_engineers:
            for eng in st.session_state.custom_excluded_engineers:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"<span style='color: #f87171;'>⛔ {eng}</span>", unsafe_allow_html=True)
                with c2:
                    if st.button("❌", key=f"remove_{eng}", help=f"Remove {eng} from exclusion list"):
                        st.session_state.custom_excluded_engineers.remove(eng)
                        st.rerun()
        else:
            st.info("No engineers excluded")
    
    with col2:
        st.markdown("##### ➕ Add New Exclusion")
        
        # Get unique engineers from data - from ALL engineer columns
        all_engineers = set()
        for col in ['ENGINEER1', 'ENGINEER2', 'ENGINEER3']:
            if col in df.columns:
                all_engineers.update(df[col].dropna().unique())
        
        all_engineers = sorted([e for e in all_engineers if e and str(e).strip().upper() != 'NONE'])
        available_engineers = [e for e in all_engineers if e not in st.session_state.custom_excluded_engineers]
        
        # Dropdown to select engineer to exclude
        new_exclusion = st.selectbox(
            "Select Engineer to Exclude",
            options=["-- Select an engineer --"] + available_engineers,
            key="new_exclusion_select",
            help="Choose an engineer from the dropdown to exclude from analysis"
        )
        
        if st.button("➕ Add to Exclusion List", use_container_width=True, type="primary"):
            if new_exclusion and new_exclusion != "-- Select an engineer --" and new_exclusion not in st.session_state.custom_excluded_engineers:
                    st.session_state.custom_excluded_engineers.append(new_exclusion)
                    st.success(f"Added {new_exclusion} to exclusion list")
                    st.rerun()
        
        # Manual entry
        manual_exclusion = st.text_input("Or enter name manually:", key="manual_exclusion")
        if st.button("➕ Add Manual Entry", use_container_width=True):
            if manual_exclusion and manual_exclusion.strip() not in st.session_state.custom_excluded_engineers:
                st.session_state.custom_excluded_engineers.append(manual_exclusion.strip().upper())
                st.success(f"Added {manual_exclusion} to exclusion list")
                st.rerun()
    
    # Reset to defaults button
    if st.button("🔄 Reset to Default Exclusions", use_container_width=True):
        st.session_state.custom_excluded_engineers = list(EXCLUDED_ENGINEERS)
        st.success("Reset to default exclusion list")
        st.rerun()

# Use custom exclusion list
active_exclusions = st.session_state.get('custom_excluded_engineers', EXCLUDED_ENGINEERS)

# Calculate engineer performance with loading indicator
with st.spinner("Analyzing engineer performance... This may take a moment for large datasets."):
    engineer_perf = calculate_engineer_performance(df, excluded_engineers=active_exclusions)

if engineer_perf.empty:
    st.warning("No engineer data available for analysis.")
    st.stop()

# Summary metrics
st.markdown("### Engineer Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Engineers",
        f"{len(engineer_perf):,}",
        help="Unique engineers in the dataset"
    )

with col2:
    avg_sla = engineer_perf['SLA_Compliance'].mean()
    st.metric(
        "Avg SLA Compliance",
        f"{avg_sla:.1f}%",
        delta=f"{avg_sla - 95:.1f}% from target"
    )

with col3:
    avg_efficiency = engineer_perf['Efficiency_Score'].mean() if 'Efficiency_Score' in engineer_perf.columns else 0
    st.metric(
        "Avg Efficiency",
        f"{avg_efficiency:.1f}%",
        help="Combined SLA and MTTR efficiency"
    )

with col4:
    total_tickets = engineer_perf['Total_Tickets'].sum()
    avg_tickets = total_tickets / len(engineer_perf) if len(engineer_perf) > 0 else 0
    st.metric(
        "Avg Tickets/Engineer",
        f"{avg_tickets:.1f}",
        help="Average workload per engineer"
    )

# Filters
st.markdown("### Filters")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    # Region filter
    region_options = ['All Regions']
    if 'REGION' in df.columns:
        regions = df['REGION'].dropna().unique().tolist()
        region_options.extend(sorted(regions))
    elif 'CLUSTER' in df.columns:
        # Try to infer region from cluster names
        clusters = df['CLUSTER'].dropna().unique().tolist()
        if any('NAIROBI' in str(c).upper() for c in clusters):
            region_options.append('Nairobi')
        if any('MOMBASA' in str(c).upper() or 'COAST' in str(c).upper() for c in clusters):
            region_options.append('Mombasa')
    
    region_filter = st.selectbox(
        "Filter by Region",
        options=region_options,
        index=0,
        help="Filter engineers by region"
    )

with col2:
    grade_filter = st.multiselect(
        "Filter by SLA Grade",
        options=['A+', 'A', 'B', 'C', 'D', 'F'],
        default=None
    )

with col3:
    min_tickets = st.number_input(
        "Minimum Tickets",
        min_value=0,
        max_value=int(engineer_perf['Total_Tickets'].max()) if len(engineer_perf) > 0 else 100,
        value=0,
        help="Filter engineers with at least this many tickets"
    )

with col4:
    sort_by = st.selectbox(
        "Sort By",
        options=['Efficiency_Score', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Total_Tickets'],
        index=0
    )

with col5:
    sort_order = st.radio(
        "Order",
        options=['Best First', 'Worst First'],
        horizontal=True
    )

# Apply filters
filtered_engineers = engineer_perf.copy()

# Apply region filter - get engineers from melted engineer columns
if region_filter != 'All Regions':
    # First get the clusters for the selected region
    if region_filter == 'Nairobi':
        region_clusters = [c for c in df['CLUSTER'].dropna().unique() if 'NAIROBI' in str(c).upper()]
    elif region_filter == 'Mombasa':
        region_clusters = [c for c in df['CLUSTER'].dropna().unique() if 'MOMBASA' in str(c).upper() or 'COAST' in str(c).upper()]
    else:
        region_clusters = []
    
    if region_clusters:
        # Filter df to region clusters first
        region_df = df[df['CLUSTER'].isin(region_clusters)]
        
        # Get engineers from ALL engineer columns (ENGINEER1, ENGINEER2, ENGINEER3)
        region_engineers = set()
        for col in ['ENGINEER1', 'ENGINEER2', 'ENGINEER3']:
            if col in region_df.columns:
                region_engineers.update(region_df[col].dropna().unique())
        
        # Filter the performance dataframe
        filtered_engineers = filtered_engineers[filtered_engineers['Engineer'].isin(region_engineers)]

if grade_filter:
    filtered_engineers = filtered_engineers[filtered_engineers['SLA_Grade'].isin(grade_filter)]

if min_tickets > 0:
    filtered_engineers = filtered_engineers[filtered_engineers['Total_Tickets'] >= min_tickets]

# Sort
ascending = (sort_order == 'Worst First') if sort_by != 'Avg_MTTR_Hours' else (sort_order == 'Best First')
filtered_engineers = filtered_engineers.sort_values(sort_by, ascending=ascending)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Performance Table", "Visualizations", "Leaderboard", "Analysis"])

with tab1:
    st.markdown("#### Engineer Performance Rankings")
    
    # Display dataframe
    display_df = filtered_engineers.copy()
    
    # Format columns
    display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
    display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
    display_df['Efficiency_Score'] = display_df['Efficiency_Score'].apply(lambda x: f"{x:.1f}%")
    display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
    display_df['SLA_Compliant'] = display_df['SLA_Compliant'].apply(lambda x: f"{x:,}")
    display_df['SLA_Breached'] = display_df['SLA_Breached'].apply(lambda x: f"{x:,}")
    
    # Select columns
    display_cols = ['Engineer', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 
                    'Efficiency_Score', 'SLA_Compliant', 'SLA_Breached', 'SLA_Grade']
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
        "engineer_performance.csv",
        "text/csv",
        use_container_width=True
    )

with tab2:
    st.markdown("#### Performance Visualizations")
    
    # Top and Bottom Efficiency
    st.markdown("##### Efficiency Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top engineers by efficiency
        top_n = min(15, len(filtered_engineers))
        top_eff = filtered_engineers.sort_values('Efficiency_Score', ascending=False).head(top_n)
        
        fig = px.bar(
            top_eff,
            x='Engineer',
            y='Efficiency_Score',
            color='SLA_Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title=f"🏆 Top {top_n} Engineers by Efficiency"
        )
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bottom engineers by efficiency
        bottom_eff = filtered_engineers.sort_values('Efficiency_Score', ascending=True).head(top_n)
        
        fig = px.bar(
            bottom_eff,
            x='Engineer',
            y='Efficiency_Score',
            color='SLA_Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title=f"⚠️ Bottom {top_n} Engineers by Efficiency"
        )
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top and Bottom Ticket Volume
    st.markdown("##### Ticket Volume Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top by ticket volume
        top_vol = filtered_engineers.sort_values('Total_Tickets', ascending=False).head(top_n)
        
        fig = px.bar(
            top_vol,
            x='Engineer',
            y='Total_Tickets',
            color='SLA_Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title=f"📊 Top {top_n} Engineers - Highest Ticket Volume"
        )
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bottom by ticket volume
        bottom_vol = filtered_engineers.sort_values('Total_Tickets', ascending=True).head(top_n)
        
        fig = px.bar(
            bottom_vol,
            x='Engineer',
            y='Total_Tickets',
            color='SLA_Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title=f"📉 Bottom {top_n} Engineers - Lowest Ticket Volume"
        )
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # SLA Compliance Visualizations
    st.markdown("##### SLA Compliance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top SLA Compliance
        top_sla = filtered_engineers.sort_values('SLA_Compliance', ascending=False).head(top_n)
        
        fig = px.bar(
            top_sla,
            x='Engineer',
            y='SLA_Compliance',
            color='SLA_Compliance',
            color_continuous_scale='RdYlGn',
            title=f"✅ Top {top_n} Engineers - Best SLA Compliance"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bottom SLA Compliance
        bottom_sla = filtered_engineers.sort_values('SLA_Compliance', ascending=True).head(top_n)
        
        fig = px.bar(
            bottom_sla,
            x='Engineer',
            y='SLA_Compliance',
            color='SLA_Compliance',
            color_continuous_scale='RdYlGn',
            title=f"❌ Bottom {top_n} Engineers - Lowest SLA Compliance"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # SLA Breaches Analysis
    st.markdown("##### SLA Breaches by Engineer")
    col1, col2 = st.columns(2)
    
    with col1:
        # Most SLA breaches
        if 'SLA_Breached' in filtered_engineers.columns:
            most_breaches = filtered_engineers.sort_values('SLA_Breached', ascending=False).head(top_n)
            
            fig = px.bar(
                most_breaches,
                x='Engineer',
                y='SLA_Breached',
                color='SLA_Breached',
                color_continuous_scale='Reds',
                title=f"🚨 Engineers with Most SLA Breaches"
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Least SLA breaches (best performers)
        if 'SLA_Breached' in filtered_engineers.columns:
            least_breaches = filtered_engineers[filtered_engineers['Total_Tickets'] >= 5].sort_values('SLA_Breached', ascending=True).head(top_n)
            
            fig = px.bar(
                least_breaches,
                x='Engineer',
                y='SLA_Breached',
                color='SLA_Breached',
                color_continuous_scale='Greens_r',
                title=f"🌟 Engineers with Fewest SLA Breaches (min 5 tickets)"
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Distribution Charts
    st.markdown("##### Distribution Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Grade distribution
        grade_dist = engineer_perf['SLA_Grade'].value_counts()
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
        fig.update_layout(title="SLA Grade Distribution", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Efficiency vs MTTR scatter
        fig = px.scatter(
            engineer_perf[engineer_perf['Total_Tickets'] >= min_tickets],
            x='Avg_MTTR_Hours',
            y='SLA_Compliance',
            size='Total_Tickets',
            color='SLA_Grade',
            color_discrete_map=grade_colors,
            hover_name='Engineer',
            title="SLA vs MTTR (bubble = ticket volume)"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Engineer Leaderboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Top 10 Performers")
        top_10 = engineer_perf.head(10)
        
        for idx, (_, row) in enumerate(top_10.iterrows(), 1):
            medal = "1st" if idx == 1 else "2nd" if idx == 2 else "3rd" if idx == 3 else f"{idx}."
            grade_color = get_grade_color(row['SLA_Grade'])
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; 
                        border-left: 4px solid {grade_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
                <span style='font-size: 1.5rem;'>{medal}</span>
                <strong style='font-size: 1.1rem; color: #f1f5f9;'>{row['Engineer']}</strong>
                <span style='float: right; background: {grade_color}; color: white; padding: 0.2rem 0.6rem; 
                             border-radius: 15px; font-weight: bold;'>{row['SLA_Grade']}</span>
                <br>
                <span style='color: #94a3b8; font-size: 0.85rem;'>
                    Efficiency: {row['Efficiency_Score']:.1f}% | 
                    SLA: {row['SLA_Compliance']:.1f}% | 
                    MTTR: {row['Avg_MTTR_Hours']:.1f}h | 
                    Tickets: {row['Total_Tickets']:,}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### Needs Improvement (Bottom 10)")
        bottom_10 = engineer_perf.tail(10).iloc[::-1]
        
        for idx, (_, row) in enumerate(bottom_10.iterrows(), 1):
            grade_color = get_grade_color(row['SLA_Grade'])
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #2d1f1f 0%, #3d2929 100%); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; 
                        border-left: 4px solid {grade_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.3);'>
                <span style='font-size: 1rem; color: #ef4444;'>!</span>
                <strong style='font-size: 1rem; color: #f1f5f9;'>{row['Engineer']}</strong>
                <span style='float: right; background: {grade_color}; color: white; padding: 0.2rem 0.6rem; 
                             border-radius: 15px; font-weight: bold;'>{row['SLA_Grade']}</span>
                <br>
                <span style='color: #94a3b8; font-size: 0.85rem;'>
                    Efficiency: {row['Efficiency_Score']:.1f}% | 
                    SLA: {row['SLA_Compliance']:.1f}% | 
                    MTTR: {row['Avg_MTTR_Hours']:.1f}h | 
                    Tickets: {row['Total_Tickets']:,}
                </span>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("#### Performance Analysis")
    
    # Workload analysis
    st.markdown("##### Workload Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            engineer_perf,
            x='Total_Tickets',
            nbins=30,
            title="Ticket Distribution per Engineer",
            color_discrete_sequence=['#667eea']
        )
        fig.add_vline(x=engineer_perf['Total_Tickets'].mean(), line_dash="dash", 
                     line_color="red", annotation_text=f"Avg: {engineer_perf['Total_Tickets'].mean():.0f}")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Efficiency distribution
        fig = px.histogram(
            engineer_perf,
            x='Efficiency_Score',
            nbins=30,
            title="Efficiency Score Distribution",
            color_discrete_sequence=['#667eea']
        )
        fig.add_vline(x=engineer_perf['Efficiency_Score'].mean(), line_dash="dash",
                     line_color="red", annotation_text=f"Avg: {engineer_perf['Efficiency_Score'].mean():.1f}%")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance vs Workload
    st.markdown("##### Performance vs Workload Analysis")
    
    fig = px.scatter(
        engineer_perf,
        x='Total_Tickets',
        y='Efficiency_Score',
        color='SLA_Grade',
        color_discrete_map={
            'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
            'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
        },
        size='SLA_Compliance',
        hover_name='Engineer',
        title="Does Higher Workload Affect Performance?",
        trendline="ols"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.markdown("##### Correlation Matrix")
    
    corr_cols = ['Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Efficiency_Score']
    corr_matrix = engineer_perf[corr_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=corr_cols,
        y=corr_cols,
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    fig.update_traces(texttemplate="%{z:.2f}")
    fig.update_layout(title="Metric Correlations", height=400)
    st.plotly_chart(fig, use_container_width=True)

# Performance grading explanation
st.markdown("### Grading Methodology")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### SLA-Based Grading
    | Grade | SLA Compliance |
    |-------|---------------|
    | A+ | ≥ 99.5% |
    | A | ≥ 98% |
    | B | ≥ 95% |
    | C | ≥ 90% |
    | D | ≥ 85% |
    | F | < 85% |
    """)

with col2:
    st.markdown("""
    #### Efficiency Calculation
    
    **Formula:**
    ```
    Efficiency = (SLA_Compliance / 100) × 
                 (1 - min(1, Avg_MTTR / 24)) × 100
    ```
    
    - Combines SLA compliance with MTTR performance
    - Higher efficiency = better overall performance
    - Penalizes both SLA breaches and slow resolution
    """)

# Excluded engineers note
if active_exclusions:
    with st.expander(f"ℹ️ **{len(active_exclusions)} Engineers Excluded from Analysis**", expanded=False):
        cols = st.columns(3)
        for i, eng in enumerate(sorted(active_exclusions)):
            with cols[i % 3]:
                st.markdown(f"<span style='color: #f87171;'>🚫 {eng}</span>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("**Tip:** Use the 'Manage Excluded Engineers' section at the top to add/remove engineers from analysis.")
