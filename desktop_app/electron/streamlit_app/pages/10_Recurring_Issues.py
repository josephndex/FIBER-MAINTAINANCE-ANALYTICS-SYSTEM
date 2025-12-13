"""
Recurring Issues Page - Repeat Issue Detection
Shows analysis of recurring/repeat issues on fiber links
Uses SUMMARY column and LINK_DESCRIPTION column in two-column layout
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS
from utils import analyze_recurring_issues, format_duration
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("10_Recurring_Issues.py")
log_page_visit("10_Recurring_Issues.py")


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
    <h1 style='margin: 0;'>Recurring Issues</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Repeat Issue Detection & Pattern Analysis</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Check for required columns
has_summary = 'SUMMARY' in df.columns
has_link_desc = 'LINK_DESCRIPTION' in df.columns

if not has_summary and not has_link_desc:
    st.warning("No SUMMARY or LINK_DESCRIPTION columns available for recurring issue analysis.")
    st.stop()

# Settings
st.markdown("### Analysis Settings")
col1, col2 = st.columns(2)

with col1:
    min_occurrences = st.slider(
        "Minimum Occurrences",
        min_value=2,
        max_value=20,
        value=2,
        help="Filter to only show issues that occurred at least this many times"
    )

with col2:
    show_top = st.number_input(
        "Show Top N Issues",
        min_value=10,
        max_value=100,
        value=25
    )

# Analyze recurring issues - returns two dataframes
# Show loading indicator during analysis
with st.spinner("Analyzing recurring issues... This may take a moment for large datasets."):
    summary_recurring, link_recurring = analyze_recurring_issues(df, min_occurrences)

# Summary metrics
st.markdown("### Recurring Issues Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    summary_count = len(summary_recurring) if not summary_recurring.empty else 0
    st.metric(
        "Summary Patterns",
        f"{summary_count:,}",
        help="Unique SUMMARY entries with 2+ occurrences"
    )

with col2:
    link_count = len(link_recurring) if not link_recurring.empty else 0
    st.metric(
        "Link Description Patterns",
        f"{link_count:,}",
        help="Unique LINK_DESCRIPTION entries with 2+ occurrences"
    )

with col3:
    summary_tickets = summary_recurring['Occurrences'].sum() if not summary_recurring.empty else 0
    st.metric(
        "Summary Recurring Tickets",
        f"{summary_tickets:,}"
    )

with col4:
    link_tickets = link_recurring['Occurrences'].sum() if not link_recurring.empty else 0
    st.metric(
        "Link Recurring Tickets",
        f"{link_tickets:,}"
    )

st.markdown("---")

# Two column layout for SUMMARY and LINK_DESCRIPTION
st.markdown("### Recurring Issues Analysis")

col1, col2 = st.columns(2)

# Column 1: SUMMARY Analysis
with col1:
    st.markdown("#### By SUMMARY")
    
    if summary_recurring.empty:
        st.info("No recurring issues found based on SUMMARY.")
    else:
        # Top recurring summaries
        display_summary = summary_recurring.head(show_top).copy()
        
        # Format columns
        if 'Avg_MTTR_Hours' in display_summary.columns:
            display_summary['Avg_MTTR'] = display_summary['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h" if pd.notna(x) else "N/A")
        if 'Total_MTTR_Hours' in display_summary.columns:
            display_summary['Total_MTTR'] = display_summary['Total_MTTR_Hours'].apply(lambda x: f"{x:.1f}h" if pd.notna(x) else "N/A")
        if 'First_Occurrence' in display_summary.columns:
            display_summary['First'] = pd.to_datetime(display_summary['First_Occurrence']).dt.strftime('%Y-%m-%d')
        if 'Last_Occurrence' in display_summary.columns:
            display_summary['Last'] = pd.to_datetime(display_summary['Last_Occurrence']).dt.strftime('%Y-%m-%d')
        
        # Select columns to display
        display_cols = ['SUMMARY', 'Occurrences', 'Avg_MTTR', 'Total_MTTR']
        if 'CLUSTER' in display_summary.columns:
            display_cols.insert(1, 'CLUSTER')
        if 'First' in display_summary.columns:
            display_cols.extend(['First', 'Last'])
        
        available_cols = [c for c in display_cols if c in display_summary.columns]
        
        st.dataframe(
            display_summary[available_cols],
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download button
        csv_summary = summary_recurring.to_csv(index=False)
        st.download_button(
            "Download SUMMARY Data",
            csv_summary,
            "recurring_summary.csv",
            "text/csv",
            key="download_summary"
        )

# Column 2: LINK_DESCRIPTION Analysis  
with col2:
    st.markdown("#### By LINK_DESCRIPTION")
    
    if link_recurring.empty:
        st.info("No recurring issues found based on LINK_DESCRIPTION.")
    else:
        # Top recurring link descriptions
        display_link = link_recurring.head(show_top).copy()
        
        # Format columns
        if 'Avg_MTTR_Hours' in display_link.columns:
            display_link['Avg_MTTR'] = display_link['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h" if pd.notna(x) else "N/A")
        if 'Total_MTTR_Hours' in display_link.columns:
            display_link['Total_MTTR'] = display_link['Total_MTTR_Hours'].apply(lambda x: f"{x:.1f}h" if pd.notna(x) else "N/A")
        if 'First_Occurrence' in display_link.columns:
            display_link['First'] = pd.to_datetime(display_link['First_Occurrence']).dt.strftime('%Y-%m-%d')
        if 'Last_Occurrence' in display_link.columns:
            display_link['Last'] = pd.to_datetime(display_link['Last_Occurrence']).dt.strftime('%Y-%m-%d')
        
        # Select columns to display
        display_cols = ['LINK_DESCRIPTION', 'Occurrences', 'Avg_MTTR', 'Total_MTTR']
        if 'CLUSTER' in display_link.columns:
            display_cols.insert(1, 'CLUSTER')
        if 'First' in display_link.columns:
            display_cols.extend(['First', 'Last'])
        
        available_cols = [c for c in display_cols if c in display_link.columns]
        
        st.dataframe(
            display_link[available_cols],
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download button
        csv_link = link_recurring.to_csv(index=False)
        st.download_button(
            "Download LINK_DESCRIPTION Data",
            csv_link,
            "recurring_link_description.csv",
            "text/csv",
            key="download_link"
        )

# Visualizations
st.markdown("---")
st.markdown("### Visualizations")

tab1, tab2 = st.tabs(["Charts", "Deep Dive"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        if not summary_recurring.empty:
            top_summary = summary_recurring.head(10)
            fig = px.bar(
                top_summary,
                x='Occurrences',
                y='SUMMARY',
                orientation='h',
                title="Top 10 Recurring by SUMMARY",
                color='Occurrences',
                color_continuous_scale='Purples'
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No SUMMARY data for visualization")
    
    with col2:
        if not link_recurring.empty:
            top_link = link_recurring.head(10)
            fig = px.bar(
                top_link,
                x='Occurrences',
                y='LINK_DESCRIPTION',
                orientation='h',
                title="Top 10 Recurring by LINK_DESCRIPTION",
                color='Occurrences',
                color_continuous_scale='Oranges'
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No LINK_DESCRIPTION data for visualization")
    
    # MTTR Impact comparison
    col1, col2 = st.columns(2)
    
    with col1:
        if not summary_recurring.empty and 'Total_MTTR_Hours' in summary_recurring.columns:
            top_mttr_summary = summary_recurring.sort_values('Total_MTTR_Hours', ascending=False).head(10)
            fig = px.bar(
                top_mttr_summary,
                x='Total_MTTR_Hours',
                y='SUMMARY',
                orientation='h',
                title="Top 10 SUMMARY by Total MTTR Impact",
                color='Total_MTTR_Hours',
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not link_recurring.empty and 'Total_MTTR_Hours' in link_recurring.columns:
            top_mttr_link = link_recurring.sort_values('Total_MTTR_Hours', ascending=False).head(10)
            fig = px.bar(
                top_mttr_link,
                x='Total_MTTR_Hours',
                y='LINK_DESCRIPTION',
                orientation='h',
                title="Top 10 LINK_DESCRIPTION by Total MTTR Impact",
                color='Total_MTTR_Hours',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("#### Deep Dive Analysis")
    
    # Choose which to analyze
    analysis_type = st.radio(
        "Select Analysis Type",
        options=["SUMMARY", "LINK_DESCRIPTION"],
        horizontal=True
    )
    
    if analysis_type == "SUMMARY" and not summary_recurring.empty:
        selected_item = st.selectbox(
            "Select a SUMMARY to Analyze",
            options=summary_recurring.head(50)['SUMMARY'].tolist()
        )
        
        if selected_item:
            item_data = df[df['SUMMARY'] == selected_item]
            item_stats = summary_recurring[summary_recurring['SUMMARY'] == selected_item].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Occurrences", f"{item_stats['Occurrences']:,}")
            with col2:
                st.metric("Avg MTTR", f"{item_stats['Avg_MTTR_Hours']:.2f}h")
            with col3:
                st.metric("Total MTTR", f"{item_stats['Total_MTTR_Hours']:.1f}h")
            with col4:
                if 'CLUSTER' in item_stats:
                    st.metric("Cluster", item_stats['CLUSTER'])
            
            # Timeline
            if 'ESCALATED_TIME' in item_data.columns:
                timeline = item_data.sort_values('ESCALATED_TIME')[['ESCALATED_TIME', 'DURATION']].copy()
                timeline['ESCALATED_TIME'] = pd.to_datetime(timeline['ESCALATED_TIME'])
                
                fig = px.scatter(
                    timeline,
                    x='ESCALATED_TIME',
                    y='DURATION',
                    title=f"Occurrence Timeline",
                    labels={'ESCALATED_TIME': 'Date', 'DURATION': 'MTTR (hours)'}
                )
                fig.update_traces(marker=dict(size=12, color='#667eea'))
                fig.add_hline(y=24, line_dash="dash", line_color="red", annotation_text="SLA (24h)")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed tickets
            st.markdown("##### Individual Tickets")
            display_cols = ['INC', 'ESCALATED_TIME', 'DURATION', 'CAUSE', 'CLUSTER', 'EXTERNAL_BREACHED']
            available_cols = [c for c in display_cols if c in item_data.columns]
            st.dataframe(item_data[available_cols], use_container_width=True, hide_index=True)
    
    elif analysis_type == "LINK_DESCRIPTION" and not link_recurring.empty:
        selected_item = st.selectbox(
            "Select a LINK_DESCRIPTION to Analyze",
            options=link_recurring.head(50)['LINK_DESCRIPTION'].tolist()
        )
        
        if selected_item:
            item_data = df[df['LINK_DESCRIPTION'] == selected_item]
            item_stats = link_recurring[link_recurring['LINK_DESCRIPTION'] == selected_item].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Occurrences", f"{item_stats['Occurrences']:,}")
            with col2:
                st.metric("Avg MTTR", f"{item_stats['Avg_MTTR_Hours']:.2f}h")
            with col3:
                st.metric("Total MTTR", f"{item_stats['Total_MTTR_Hours']:.1f}h")
            with col4:
                if 'CLUSTER' in item_stats:
                    st.metric("Cluster", item_stats['CLUSTER'])
            
            # Timeline
            if 'ESCALATED_TIME' in item_data.columns:
                timeline = item_data.sort_values('ESCALATED_TIME')[['ESCALATED_TIME', 'DURATION']].copy()
                timeline['ESCALATED_TIME'] = pd.to_datetime(timeline['ESCALATED_TIME'])
                
                fig = px.scatter(
                    timeline,
                    x='ESCALATED_TIME',
                    y='DURATION',
                    title=f"Occurrence Timeline",
                    labels={'ESCALATED_TIME': 'Date', 'DURATION': 'MTTR (hours)'}
                )
                fig.update_traces(marker=dict(size=12, color='#f59e0b'))
                fig.add_hline(y=24, line_dash="dash", line_color="red", annotation_text="SLA (24h)")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed tickets
            st.markdown("##### Individual Tickets")
            display_cols = ['INC', 'ESCALATED_TIME', 'DURATION', 'CAUSE', 'CLUSTER', 'EXTERNAL_BREACHED']
            available_cols = [c for c in display_cols if c in item_data.columns]
            st.dataframe(item_data[available_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No data available for deep dive analysis.")

# Impact Summary
st.markdown("---")
st.markdown("### Impact Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### SUMMARY Statistics")
    if not summary_recurring.empty:
        total_mttr = summary_recurring['Total_MTTR_Hours'].sum() if 'Total_MTTR_Hours' in summary_recurring.columns else 0
        avg_occurrences = summary_recurring['Occurrences'].mean()
        
        st.info(f"""
        - Recurring Patterns: **{len(summary_recurring):,}**
        - Total Recurring Tickets: **{summary_recurring['Occurrences'].sum():,}**
        - Total MTTR Impact: **{total_mttr:,.1f} hours**
        - Avg Occurrences: **{avg_occurrences:.1f}**
        """)
    else:
        st.info("No recurring SUMMARY patterns found.")

with col2:
    st.markdown("#### LINK_DESCRIPTION Statistics")
    if not link_recurring.empty:
        total_mttr = link_recurring['Total_MTTR_Hours'].sum() if 'Total_MTTR_Hours' in link_recurring.columns else 0
        avg_occurrences = link_recurring['Occurrences'].mean()
        
        st.info(f"""
        - Recurring Patterns: **{len(link_recurring):,}**
        - Total Recurring Tickets: **{link_recurring['Occurrences'].sum():,}**
        - Total MTTR Impact: **{total_mttr:,.1f} hours**
        - Avg Occurrences: **{avg_occurrences:.1f}**
        """)
    else:
        st.info("No recurring LINK_DESCRIPTION patterns found.")

# Recommendations
st.markdown("### Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Technical Actions
    1. **Investigate root causes** for top recurring patterns
    2. **Implement permanent fixes** for high-frequency issues
    3. **Review infrastructure** at recurring locations
    4. **Update maintenance schedules** for problem areas
    """)

with col2:
    st.markdown("""
    #### Process Actions
    1. **Create knowledge base** for recurring issues
    2. **Assign dedicated teams** to chronic problems
    3. **Set up proactive monitoring** for known issues
    4. **Track fix effectiveness** over time
    """)

# Footer
st.markdown("---")
st.caption("**Tip:** Focus on high-frequency, high-MTTR patterns for maximum impact reduction. These represent the best ROI for permanent fixes.")
