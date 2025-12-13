"""
Regional Analysis Page - Performance by Region
Shows regional performance metrics and comparisons
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS
from utils import (
    calculate_regional_performance, get_sla_grade, get_grade_color, format_duration
)
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("5_Regional_Analysis.py")
log_page_visit("5_Regional_Analysis.py")


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
    <h1 style='margin: 0;'>Regional Analysis</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Geographic Performance Distribution & Regional Metrics</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Check if REGION column exists
if 'REGION' not in df.columns:
    st.warning("No REGION column available in the data.")
    st.stop()

# Calculate regional performance with loading indicator
with st.spinner("Analyzing regional performance... This may take a moment for large datasets."):
    regional_perf = calculate_regional_performance(df)

if regional_perf.empty:
    st.warning("No regional data available for analysis.")
    st.stop()

# Summary metrics
st.markdown("### Regional Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Regions",
        f"{len(regional_perf):,}",
        help="Number of unique regions"
    )

with col2:
    avg_sla = regional_perf['SLA_Compliance'].mean()
    st.metric(
        "Avg SLA Compliance",
        f"{avg_sla:.1f}%",
        delta=f"{avg_sla - 95:.1f}% from target"
    )

with col3:
    avg_mttr = regional_perf['Avg_MTTR_Hours'].mean()
    st.metric(
        "Avg MTTR",
        f"{avg_mttr:.2f}h",
        help="Average across all regions"
    )

with col4:
    total_tickets = regional_perf['Total_Tickets'].sum()
    st.metric(
        "Total Tickets",
        f"{total_tickets:,}",
        help="Total tickets across all regions"
    )

# Tabs
tab1, tab2, tab3 = st.tabs(["Performance Table", "Visualizations", "Comparisons"])

with tab1:
    st.markdown("#### Regional Performance Rankings")
    
    display_df = regional_perf.copy()
    display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
    display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
    display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
    display_df['SLA_Compliant'] = display_df['SLA_Compliant'].apply(lambda x: f"{x:,}")
    display_df['SLA_Breached'] = display_df['SLA_Breached'].apply(lambda x: f"{x:,}")
    
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    csv = display_df.to_csv(index=False)
    st.download_button(
        "Download as CSV",
        csv,
        "regional_performance.csv",
        "text/csv",
        use_container_width=True
    )

with tab2:
    st.markdown("#### Regional Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ticket distribution by region
        fig = px.pie(
            regional_perf,
            values='Total_Tickets',
            names='REGION',
            title="Ticket Distribution by Region",
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # SLA by region bar chart
        fig = px.bar(
            regional_perf.sort_values('SLA_Compliance', ascending=True),
            x='SLA_Compliance',
            y='REGION',
            orientation='h',
            title="SLA Compliance by Region",
            color='SLA_Compliance',
            color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
        )
        fig.add_vline(x=95, line_dash="dash", line_color="green", annotation_text="Target (95%)")
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # MTTR by region
        fig = px.bar(
            regional_perf.sort_values('Avg_MTTR_Hours'),
            x='REGION',
            y='Avg_MTTR_Hours',
            title="Average MTTR by Region",
            color='Avg_MTTR_Hours',
            color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
        )
        fig.add_hline(y=24, line_dash="dash", line_color="red", annotation_text="SLA Limit (24h)")
        fig.update_layout(height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Volume vs SLA scatter
        fig = px.scatter(
            regional_perf,
            x='Total_Tickets',
            y='SLA_Compliance',
            size='Total_Tickets',
            color='REGION',
            title="Ticket Volume vs SLA Compliance"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    st.markdown("#### Performance Heatmap")
    
    heatmap_df = regional_perf[['REGION', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Total_Tickets']].copy()
    
    # Normalize for heatmap
    for col in ['SLA_Compliance', 'Total_Tickets']:
        max_val = heatmap_df[col].max()
        if max_val > 0:
            heatmap_df[f'{col}_norm'] = heatmap_df[col] / max_val * 100
    
    # Invert MTTR
    max_mttr = heatmap_df['Avg_MTTR_Hours'].max()
    if max_mttr > 0:
        heatmap_df['MTTR_norm'] = 100 - (heatmap_df['Avg_MTTR_Hours'] / max_mttr * 100)
    
    fig = go.Figure(data=go.Heatmap(
        z=[heatmap_df['SLA_Compliance_norm'].values, 
           heatmap_df['MTTR_norm'].values,
           heatmap_df['Total_Tickets_norm'].values],
        x=heatmap_df['REGION'].values,
        y=['SLA Compliance', 'MTTR Score', 'Volume'],
        colorscale='RdYlGn',
        text=[[f"{v:.1f}%" for v in heatmap_df['SLA_Compliance'].values],
              [f"{v:.1f}h" for v in heatmap_df['Avg_MTTR_Hours'].values],
              [f"{v:,}" for v in heatmap_df['Total_Tickets'].values]],
        texttemplate="%{text}",
        textfont={"size": 11}
    ))
    fig.update_layout(title="Regional Performance Heatmap", height=250, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Regional Comparisons")
    
    # Select regions to compare
    selected_regions = st.multiselect(
        "Select Regions to Compare",
        options=regional_perf['REGION'].tolist(),
        default=regional_perf['REGION'].head(5).tolist() if len(regional_perf) >= 5 else regional_perf['REGION'].tolist()
    )
    
    if selected_regions:
        comparison_df = regional_perf[regional_perf['REGION'].isin(selected_regions)]
        
        # Radar chart
        fig = go.Figure()
        
        for _, row in comparison_df.iterrows():
            max_tickets = regional_perf['Total_Tickets'].max()
            values = [
                row['SLA_Compliance'],
                100 - min(100, row['Avg_MTTR_Hours'] / 24 * 100),  # Invert MTTR
                row['Total_Tickets'] / max_tickets * 100 if max_tickets > 0 else 0
            ]
            values.append(values[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=['SLA %', 'MTTR Score', 'Volume', 'SLA %'],
                fill='toself',
                name=row['REGION']
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Regional Comparison Radar",
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        st.markdown("#### Side-by-Side Comparison")
        comp_display = comparison_df[['REGION', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours']].copy()
        comp_display['SLA_Compliance'] = comp_display['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
        comp_display['Avg_MTTR_Hours'] = comp_display['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
        comp_display['Total_Tickets'] = comp_display['Total_Tickets'].apply(lambda x: f"{x:,}")
        st.dataframe(comp_display, use_container_width=True, hide_index=True)

# Regional insights
st.markdown("### Regional Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Best Performing Region")
    best_region = regional_perf.iloc[0]
    st.success(f"""
    **{best_region['REGION']}**
    - SLA Compliance: {best_region['SLA_Compliance']:.1f}%
    - Avg MTTR: {best_region['Avg_MTTR_Hours']:.2f}h
    - Total Tickets: {best_region['Total_Tickets']:,}
    """)

with col2:
    st.markdown("#### Needs Improvement")
    worst_region = regional_perf.iloc[-1]
    st.warning(f"""
    **{worst_region['REGION']}**
    - SLA Compliance: {worst_region['SLA_Compliance']:.1f}%
    - Avg MTTR: {worst_region['Avg_MTTR_Hours']:.2f}h
    - Total Tickets: {worst_region['Total_Tickets']:,}
    """)

# Footer
st.markdown("---")
st.caption("**Tip:** Click on regions in charts to drill down into specific regional data.")
