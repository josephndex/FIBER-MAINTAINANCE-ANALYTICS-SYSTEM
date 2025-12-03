"""
Challenges & Causes Page - Root Cause Analysis
Shows cause and challenge analysis for maintenance issues
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS, ALARM_ROOT_CAUSES
from utils import calculate_cause_analysis, calculate_challenge_analysis, format_duration
from auth import require_authentication, log_page_visit, require_page_access

# Require authentication and page access
require_authentication()
require_page_access("9_Challenges.py")
log_page_visit("9_Challenges.py")


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
    <h1 style='margin: 0;'>Challenges & Causes</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Root Cause Analysis & Challenge Impact Assessment</p>
</div>
""", unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state.get('df') is None:
    st.warning("No data loaded. Please load data from the sidebar on the Home page.")
    st.stop()

df = st.session_state['df']

# Tabs
tab1, tab2, tab3 = st.tabs(["Cause Analysis", "Challenge Analysis", "Combined View"])

with tab1:
    st.markdown("#### Root Cause Analysis")
    
    if 'CAUSE' not in df.columns:
        st.warning("No CAUSE column available in the data.")
    else:
        with st.spinner("Analyzing root causes... This may take a moment for large datasets."):
            cause_analysis = calculate_cause_analysis(df)
        
        if cause_analysis.empty:
            st.warning("No cause data available for analysis.")
        else:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Unique Causes", f"{len(cause_analysis):,}")
            with col2:
                top_cause = cause_analysis.iloc[0]
                st.metric("Top Cause", top_cause['CAUSE'][:20] + "..." if len(top_cause['CAUSE']) > 20 else top_cause['CAUSE'])
            with col3:
                st.metric("Top Cause Tickets", f"{top_cause['Total_Tickets']:,}")
            with col4:
                avg_sla = cause_analysis['SLA_Compliance'].mean()
                st.metric("Avg SLA by Cause", f"{avg_sla:.1f}%")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top causes by volume
                top_causes = cause_analysis.head(15)
                fig = px.bar(
                    top_causes,
                    x='Total_Tickets',
                    y='CAUSE',
                    orientation='h',
                    title="Top 15 Causes by Ticket Volume",
                    color='SLA_Compliance',
                    color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
                )
                fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Cause distribution pie
                fig = px.pie(
                    cause_analysis.head(10),
                    values='Total_Tickets',
                    names='CAUSE',
                    title="Top 10 Causes Distribution",
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # SLA by cause
                fig = px.bar(
                    cause_analysis.sort_values('SLA_Compliance').head(15),
                    x='SLA_Compliance',
                    y='CAUSE',
                    orientation='h',
                    title="Causes with Lowest SLA Compliance",
                    color='SLA_Compliance',
                    color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
                )
                fig.add_vline(x=95, line_dash="dash", line_color="green", annotation_text="Target")
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # MTTR by cause
                fig = px.bar(
                    cause_analysis.sort_values('Avg_MTTR_Hours', ascending=False).head(15),
                    x='Avg_MTTR_Hours',
                    y='CAUSE',
                    orientation='h',
                    title="Causes with Highest MTTR",
                    color='Avg_MTTR_Hours',
                    color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
                )
                fig.add_vline(x=24, line_dash="dash", line_color="red", annotation_text="SLA Limit")
                fig.update_layout(height=400, yaxis={'categoryorder': 'total descending'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Cause table
            st.markdown("##### Complete Cause Analysis Table")
            display_df = cause_analysis.copy()
            display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
            display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
            display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
            display_df['Percentage'] = display_df['Percentage'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

with tab2:
    st.markdown("#### Challenge Analysis")
    
    if 'CHALLENGE' not in df.columns:
        st.warning("No CHALLENGE column available in the data.")
    else:
        with st.spinner("Analyzing challenges... This may take a moment for large datasets."):
            challenge_analysis = calculate_challenge_analysis(df)
        
        if challenge_analysis.empty:
            st.warning("No challenge data available for analysis.")
        else:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Unique Challenges", f"{len(challenge_analysis):,}")
            with col2:
                top_challenge = challenge_analysis.iloc[0]
                st.metric("Top Challenge", top_challenge['CHALLENGE'][:15] + "..." if len(str(top_challenge['CHALLENGE'])) > 15 else top_challenge['CHALLENGE'])
            with col3:
                st.metric("Top Challenge Tickets", f"{top_challenge['Total_Tickets']:,}")
            with col4:
                avg_mttr = challenge_analysis['Avg_MTTR_Hours'].mean()
                st.metric("Avg MTTR by Challenge", f"{avg_mttr:.1f}h")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top challenges by volume
                top_challenges = challenge_analysis.head(15)
                fig = px.bar(
                    top_challenges,
                    x='Total_Tickets',
                    y='CHALLENGE',
                    orientation='h',
                    title="Top 15 Challenges by Ticket Volume",
                    color='SLA_Compliance',
                    color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
                )
                fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Challenge distribution
                fig = px.treemap(
                    challenge_analysis.head(15),
                    path=['CHALLENGE'],
                    values='Total_Tickets',
                    color='SLA_Compliance',
                    color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
                    title="Challenge Volume Treemap"
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # SLA by challenge
                fig = px.bar(
                    challenge_analysis.sort_values('SLA_Compliance').head(15),
                    x='SLA_Compliance',
                    y='CHALLENGE',
                    orientation='h',
                    title="Challenges with Lowest SLA",
                    color='SLA_Compliance',
                    color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e']
                )
                fig.add_vline(x=95, line_dash="dash", line_color="green", annotation_text="Target")
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # MTTR by challenge
                fig = px.bar(
                    challenge_analysis.sort_values('Avg_MTTR_Hours', ascending=False).head(15),
                    x='Avg_MTTR_Hours',
                    y='CHALLENGE',
                    orientation='h',
                    title="Challenges with Highest MTTR",
                    color='Avg_MTTR_Hours',
                    color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
                )
                fig.add_vline(x=24, line_dash="dash", line_color="red", annotation_text="SLA Limit")
                fig.update_layout(height=400, yaxis={'categoryorder': 'total descending'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Challenge table
            st.markdown("##### Complete Challenge Analysis Table")
            display_df = challenge_analysis.copy()
            display_df['SLA_Compliance'] = display_df['SLA_Compliance'].apply(lambda x: f"{x:.1f}%")
            display_df['Avg_MTTR_Hours'] = display_df['Avg_MTTR_Hours'].apply(lambda x: f"{x:.2f}h")
            display_df['Total_Tickets'] = display_df['Total_Tickets'].apply(lambda x: f"{x:,}")
            display_df['Percentage'] = display_df['Percentage'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

with tab3:
    st.markdown("#### Combined Cause-Challenge Analysis")
    
    if 'CAUSE' in df.columns and 'CHALLENGE' in df.columns:
        # Create combined analysis
        combined = df.groupby(['CAUSE', 'CHALLENGE']).size().reset_index(name='Tickets')
        combined = combined.sort_values('Tickets', ascending=False).head(30)
        
        # Sunburst chart
        fig = px.sunburst(
            combined,
            path=['CAUSE', 'CHALLENGE'],
            values='Tickets',
            title="Cause-Challenge Hierarchy",
            color='Tickets',
            color_continuous_scale='Purples'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Sankey diagram
        st.markdown("##### Cause to Challenge Flow")
        
        # Prepare data for Sankey
        cause_list = combined['CAUSE'].unique().tolist()
        challenge_list = combined['CHALLENGE'].unique().tolist()
        
        # Create indices
        source_indices = [cause_list.index(c) for c in combined['CAUSE']]
        target_indices = [len(cause_list) + challenge_list.index(c) for c in combined['CHALLENGE']]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=cause_list + challenge_list,
                color=["#667eea"] * len(cause_list) + ["#764ba2"] * len(challenge_list)
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=combined['Tickets'].tolist(),
                color='rgba(102, 126, 234, 0.4)'
            )
        )])
        
        fig.update_layout(title_text="Cause to Challenge Flow (Top Combinations)", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation matrix
        st.markdown("##### Cause-Challenge Heatmap")
        
        pivot = df.groupby(['CAUSE', 'CHALLENGE']).size().unstack(fill_value=0)
        top_causes = df['CAUSE'].value_counts().head(10).index.tolist()
        top_challenges = df['CHALLENGE'].value_counts().head(10).index.tolist()
        
        pivot_filtered = pivot.loc[[c for c in top_causes if c in pivot.index], 
                                   [c for c in top_challenges if c in pivot.columns]]
        
        if not pivot_filtered.empty:
            fig = px.imshow(
                pivot_filtered,
                labels=dict(x="Challenge", y="Cause", color="Tickets"),
                color_continuous_scale='Purples',
                aspect="auto"
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Both CAUSE and CHALLENGE columns are required for combined analysis.")

# Root cause categories
st.markdown("### Root Cause Categories")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Alarm-Based Issues")
    st.info(f"""
    **Alarm Root Causes:**
    {', '.join(ALARM_ROOT_CAUSES)}
    
    These are automatically detected issues from monitoring systems.
    """)

with col2:
    if 'Is_Alarm' in df.columns:
        alarm_count = df['Is_Alarm'].sum()
        manual_count = len(df) - alarm_count
        
        fig = go.Figure(data=[go.Pie(
            labels=['Alarm-Detected', 'Manual Report'],
            values=[alarm_count, manual_count],
            marker_colors=['#667eea', '#764ba2'],
            hole=0.4
        )])
        fig.update_layout(title="Alarm vs Manual Detection", height=300)
        st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("### Key Insights")

if 'CAUSE' in df.columns:
    cause_analysis = calculate_cause_analysis(df)
    if not cause_analysis.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Critical Causes (Low SLA)")
            critical_causes = cause_analysis[cause_analysis['SLA_Compliance'] < 90].head(5)
            for _, row in critical_causes.iterrows():
                st.warning(f"**{row['CAUSE']}**: SLA {row['SLA_Compliance']:.1f}% | {row['Total_Tickets']:,} tickets")
        
        with col2:
            st.markdown("#### Slowest Causes (High MTTR)")
            slow_causes = cause_analysis.sort_values('Avg_MTTR_Hours', ascending=False).head(5)
            for _, row in slow_causes.iterrows():
                st.info(f"**{row['CAUSE']}**: MTTR {row['Avg_MTTR_Hours']:.1f}h | {row['Total_Tickets']:,} tickets")

# Footer
st.markdown("---")
st.caption("**Tip:** Focus on high-volume, low-SLA causes for maximum impact on overall performance.")
