"""
Cluster Analysis Page - Detailed Cluster Performance Analysis
Shows cluster performance with grading and comparative metrics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, CLUSTER_MAPPING
from utils import (
    calculate_cluster_performance, get_sla_grade, get_performance_grade,
    get_grade_color, format_duration
)
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("3_Cluster_Analysis.py")
log_page_visit("3_Cluster_Analysis.py")


def get_grade_badge_html(grade):
    """Generate HTML for grade badge"""
    color = get_grade_color(grade)
    return f"""
    <span style='
        display: inline-block;
        background: {color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: 700;
        font-size: 0.85rem;
    '>{grade}</span>
    """


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
    <h1 style='margin: 0;'>Cluster Analysis</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Performance Metrics by Cluster with Comparative Grading</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Calculate cluster performance with loading indicator
with st.spinner("Analyzing cluster performance... This may take a moment for large datasets."):
    cluster_perf = calculate_cluster_performance(df)

if cluster_perf.empty:
    st.warning("No cluster data available for analysis.")
    st.stop()

# Summary metrics
st.markdown("### Cluster Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Clusters",
        f"{len(cluster_perf):,}",
        help="Number of unique clusters in the dataset"
    )

with col2:
    avg_sla = cluster_perf['SLA_Compliance'].mean()
    st.metric(
        "Avg SLA Compliance",
        f"{avg_sla:.1f}%",
        delta=f"{avg_sla - 95:.1f}% from target",
        delta_color="normal" if avg_sla >= 95 else "inverse"
    )

with col3:
    avg_mttr = cluster_perf['Avg_MTTR_Hours'].mean()
    st.metric(
        "Avg MTTR (All Clusters)",
        f"{avg_mttr:.2f}h",
        help="Average Mean Time To Resolve across all clusters"
    )

with col4:
    # Count clusters by grade
    grade_counts = cluster_perf['Grade'].value_counts()
    passing_grades = grade_counts.get('A+', 0) + grade_counts.get('A', 0) + grade_counts.get('B', 0)
    passing_rate = (passing_grades / len(cluster_perf) * 100) if len(cluster_perf) > 0 else 0
    st.metric(
        "Clusters Passing (B+)",
        f"{passing_grades} ({passing_rate:.0f}%)",
        help="Clusters with grade B or higher"
    )

# Filters
st.markdown("### Filters")

col1, col2, col3 = st.columns(3)

with col1:
    grade_filter = st.multiselect(
        "Filter by Grade",
        options=['A+', 'A', 'B', 'C', 'D', 'F'],
        default=None,
        help="Select grades to filter"
    )

with col2:
    min_tickets = st.number_input(
        "Minimum Tickets",
        min_value=0,
        max_value=int(cluster_perf['Total_Tickets'].max()),
        value=0,
        help="Filter clusters with at least this many tickets"
    )

with col3:
    sort_by = st.selectbox(
        "Sort By",
        options=['Performance_Score', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Total_Tickets'],
        index=0,
        help="Sort clusters by selected metric"
    )

# Apply filters
filtered_clusters = cluster_perf.copy()

if grade_filter:
    filtered_clusters = filtered_clusters[filtered_clusters['Grade'].isin(grade_filter)]

if min_tickets > 0:
    filtered_clusters = filtered_clusters[filtered_clusters['Total_Tickets'] >= min_tickets]

# Sort
ascending = sort_by in ['Avg_MTTR_Hours']  # Lower is better for MTTR
filtered_clusters = filtered_clusters.sort_values(sort_by, ascending=ascending)

# Display tabs
tab1, tab2, tab3, tab4 = st.tabs(["Performance Table", "Visualizations", "Heatmap", "Comparisons"])

with tab1:
    st.markdown("#### Cluster Performance Rankings")
    
    # Create display dataframe
    display_df = filtered_clusters.copy()
    
    # Format columns for display
    display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
    display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
    display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
    display_df['SLA_Compliant'] = display_df['SLA_Compliant'].apply(lambda x: f"{x:,}")
    display_df['SLA_Breached'] = display_df['SLA_Breached'].apply(lambda x: f"{x:,}")
    display_df['Performance_Score'] = display_df['Performance_Score'].apply(lambda x: f"{x:.2f}")
    
    # Select and reorder columns
    display_cols = ['CLUSTER', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 
                    'SLA_Compliant', 'SLA_Breached', 'Performance_Score', 'Grade']
    
    available_cols = [col for col in display_cols if col in display_df.columns]
    display_df = display_df[available_cols]
    
    # Add rank column
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500
    )
    
    # Download option
    csv = display_df.to_csv(index=False)
    st.download_button(
        "Download as CSV",
        csv,
        "cluster_performance.csv",
        "text/csv",
        use_container_width=True
    )

with tab2:
    st.markdown("#### Performance Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SLA Compliance bar chart
        top_n = min(15, len(filtered_clusters))
        fig = px.bar(
            filtered_clusters.head(top_n),
            x='CLUSTER',
            y='SLA_Compliance',
            color='Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title=f"Top {top_n} Clusters by SLA Compliance"
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target (95%)")
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # MTTR bar chart
        mttr_sorted = filtered_clusters.sort_values('Avg_MTTR_Hours').head(top_n)
        fig = px.bar(
            mttr_sorted,
            x='CLUSTER',
            y='Avg_MTTR_Hours',
            color='Grade',
            color_discrete_map={
                'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
                'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
            },
            title=f"Top {top_n} Clusters by MTTR (Lowest First)"
        )
        fig.add_hline(y=24, line_dash="dash", line_color="red", annotation_text="SLA Limit (24h)")
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Grade distribution
    col1, col2 = st.columns(2)
    
    with col1:
        grade_dist = cluster_perf['Grade'].value_counts()
        grade_order = ['A+', 'A', 'B', 'C', 'D', 'F']
        grade_colors = {
            'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
            'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
        }
        
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
        # Ticket volume distribution
        fig = px.box(
            cluster_perf,
            y='Total_Tickets',
            color='Grade',
            color_discrete_map=grade_colors,
            title="Ticket Volume by Grade"
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Performance Heatmap")
    
    # Create heatmap data
    if len(cluster_perf) > 0:
        heatmap_data = cluster_perf[['CLUSTER', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Total_Tickets']].head(20)
        
        # Normalize values for heatmap
        normalized_df = heatmap_data.copy()
        for col in ['SLA_Compliance', 'Total_Tickets']:
            if normalized_df[col].max() > 0:
                normalized_df[col] = (normalized_df[col] - normalized_df[col].min()) / (normalized_df[col].max() - normalized_df[col].min()) * 100
        
        # Invert MTTR (lower is better)
        if normalized_df['Avg_MTTR_Hours'].max() > 0:
            normalized_df['Avg_MTTR_Hours'] = 100 - ((normalized_df['Avg_MTTR_Hours'] - normalized_df['Avg_MTTR_Hours'].min()) / 
                                                      (normalized_df['Avg_MTTR_Hours'].max() - normalized_df['Avg_MTTR_Hours'].min()) * 100)
        
        fig = go.Figure(data=go.Heatmap(
            z=[normalized_df['SLA_Compliance'].values, 
               normalized_df['Avg_MTTR_Hours'].values,
               normalized_df['Total_Tickets'].values],
            x=normalized_df['CLUSTER'].values,
            y=['SLA Compliance', 'MTTR Score', 'Volume'],
            colorscale='RdYlGn',
            showscale=True,
            text=[heatmap_data['SLA_Compliance'].apply(lambda x: f"{x:.1f}%").values,
                  heatmap_data['Avg_MTTR_Hours'].apply(lambda x: f"{x:.1f}h").values,
                  heatmap_data['Total_Tickets'].apply(lambda x: f"{x:,}").values],
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Cluster Performance Heatmap (Top 20)",
            xaxis_tickangle=-45,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # SLA vs MTTR scatter
    st.markdown("#### SLA vs MTTR Scatter")
    
    fig = px.scatter(
        cluster_perf,
        x='Avg_MTTR_Hours',
        y='SLA_Compliance',
        size='Total_Tickets',
        color='Grade',
        color_discrete_map={
            'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b',
            'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'
        },
        hover_name='CLUSTER',
        title="SLA Compliance vs MTTR (bubble size = ticket volume)"
    )
    
    # Add quadrant lines
    fig.add_hline(y=95, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=24, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant annotations
    fig.add_annotation(x=12, y=97.5, text="High Performers", showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=36, y=97.5, text="Slow but Compliant", showarrow=False, font=dict(color="orange"))
    fig.add_annotation(x=12, y=87, text="Fast but Breaching", showarrow=False, font=dict(color="blue"))
    fig.add_annotation(x=36, y=87, text="Needs Improvement", showarrow=False, font=dict(color="red"))
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("#### Cluster Comparisons")
    
    # Select clusters to compare
    selected_clusters = st.multiselect(
        "Select Clusters to Compare",
        options=cluster_perf['CLUSTER'].tolist(),
        default=cluster_perf['CLUSTER'].head(5).tolist() if len(cluster_perf) >= 5 else cluster_perf['CLUSTER'].tolist(),
        max_selections=10
    )
    
    if selected_clusters:
        comparison_df = cluster_perf[cluster_perf['CLUSTER'].isin(selected_clusters)]
        
        # Radar chart comparison
        categories = ['SLA_Compliance', 'Performance_Score', 'Total_Tickets']
        
        fig = go.Figure()
        
        for _, row in comparison_df.iterrows():
            values = [
                row['SLA_Compliance'],
                row['Performance_Score'] * 10,  # Scale for visibility
                min(100, row['Total_Tickets'] / comparison_df['Total_Tickets'].max() * 100)  # Normalize
            ]
            values.append(values[0])  # Close the loop
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=['SLA %', 'Performance', 'Volume', 'SLA %'],
                fill='toself',
                name=row['CLUSTER']
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Cluster Comparison Radar",
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        st.markdown("#### Comparison Table")
        comp_display = comparison_df[['CLUSTER', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours', 'Grade']].copy()
        comp_display['SLA_Compliance'] = comp_display['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
        comp_display['Avg_MTTR_Hours'] = comp_display['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
        comp_display['Total_Tickets'] = comp_display['Total_Tickets'].apply(lambda x: f"{x:,}")
        st.dataframe(comp_display, use_container_width=True, hide_index=True)
    else:
        st.info("Select clusters above to compare their performance.")

# Insights section
st.markdown("### Key Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top Performers")
    top_performers = cluster_perf.head(5)
    for _, row in top_performers.iterrows():
        grade_color = get_grade_color(row['Grade'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 0.75rem; border-radius: 10px; margin-bottom: 0.5rem; 
                    border-left: 4px solid {grade_color};'>
            <strong style='color: #f1f5f9;'>{row['CLUSTER']}</strong> 
            <span style='float: right; background: {grade_color}; color: white; padding: 0.1rem 0.5rem; border-radius: 10px;'>{row['Grade']}</span>
            <br><small style='color: #94a3b8;'>SLA: {row['SLA_Compliance']:.1f}% | MTTR: {row['Avg_MTTR_Hours']:.1f}h | Tickets: {row['Total_Tickets']:,}</small>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("#### Needs Attention")
    bottom_performers = cluster_perf.tail(5)
    for _, row in bottom_performers.iloc[::-1].iterrows():
        grade_color = get_grade_color(row['Grade'])
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 0.75rem; border-radius: 10px; margin-bottom: 0.5rem; 
                    border-left: 4px solid {grade_color};'>
            <strong style='color: #f1f5f9;'>{row['CLUSTER']}</strong> 
            <span style='float: right; background: {grade_color}; color: white; padding: 0.1rem 0.5rem; border-radius: 10px;'>{row['Grade']}</span>
            <br><small style='color: #94a3b8;'>SLA: {row['SLA_Compliance']:.1f}% | MTTR: {row['Avg_MTTR_Hours']:.1f}h | Tickets: {row['Total_Tickets']:,}</small>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("**Performance Formula:** Performance_Score = Ticket_Score + MTTR_Score (Lower is better in maintenance context)")
