"""
CEO Executive Dashboard - Fiber Maintenance Analytics System
Comprehensive executive-level insights and strategic metrics
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_and_prepare_data, calculate_comprehensive_kpis,
    filter_non_alarm_data, calculate_cluster_performance,
    calculate_engineer_performance, calculate_regional_performance,
    calculate_service_performance, calculate_cause_analysis,
    format_duration, get_sla_grade, get_grade_color
)
from auth import require_page_access, get_current_user, log_page_visit


# Check page access
require_page_access("13_CEO_Dashboard.py")

# Log page visit
log_page_visit("CEO Dashboard")


def create_executive_header():
    """Create STUNNING executive dashboard header with premium branding"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0f172a 0%, #1a0d2e 50%, #0f172a 100%);
                padding: 3rem; border-radius: 24px; margin-bottom: 2rem;
                box-shadow: 
                    0 25px 60px rgba(0,0,0,0.5),
                    0 0 100px rgba(249, 115, 22, 0.1),
                    inset 0 1px 0 rgba(255,255,255,0.05);
                border: 1px solid rgba(168, 85, 247, 0.3);
                position: relative;
                overflow: hidden;'>
        <div style='position: absolute; top: 0; left: 0; right: 0; height: 5px;
                    background: linear-gradient(90deg, #f97316, #a855f7, #667eea, #a855f7, #f97316);
                    background-size: 200% 100%;
                    animation: borderFlow 3s linear infinite;'></div>
        <style>
            @keyframes borderFlow {{
                0% {{ background-position: 0% 50%; }}
                100% {{ background-position: 200% 50%; }}
            }}
            @keyframes float {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
        </style>
        <div style='display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 1;'>
            <div>
                <h1 style='background: linear-gradient(135deg, #f97316 0%, #a855f7 50%, #667eea 100%);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;
                           background-clip: text;
                           margin: 0; font-size: 3rem; font-weight: 900; 
                           text-transform: uppercase; letter-spacing: 4px;
                           text-shadow: 0 0 60px rgba(249, 115, 22, 0.3);'>
                    CEO Executive Dashboard
                </h1>
                <p style='color: #a78bfa; margin: 0.75rem 0 0 0; font-size: 1.2rem; font-weight: 500;
                          letter-spacing: 2px;'>
                    🔥 Fiber Maintenance Department | Strategic Overview & Business Intelligence
                </p>
            </div>
            <div style='text-align: right; background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
                        padding: 1.25rem 1.75rem; border-radius: 16px; border: 1px solid rgba(168, 85, 247, 0.3);'>
                <p style='color: #a855f7; margin: 0; font-size: 0.9rem; font-weight: 700; text-transform: uppercase;
                          letter-spacing: 1px;'>REPORT DATE</p>
                <p style='background: linear-gradient(135deg, #f97316, #a855f7);
                          -webkit-background-clip: text;
                          -webkit-text-fill-color: transparent;
                          background-clip: text;
                          margin: 0.25rem 0 0 0; font-size: 1.5rem; font-weight: 800;'>{date}</p>
            </div>
        </div>
    </div>
    """.format(date=datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)


def create_kpi_executive_card(title, value, subtitle, trend=None, trend_value=None, color="#f97316"):
    """Create STUNNING executive-style KPI card with glassmorphism"""
    trend_html = ""
    if trend and trend_value:
        trend_icon = "▲" if trend == "up" else "▼" if trend == "down" else "◆"
        trend_color = "#10b981" if trend == "up" else "#ef4444" if trend == "down" else "#f59e0b"
        trend_html = f"""
        <div style='display: flex; align-items: center; gap: 0.4rem; margin-top: 0.75rem;
                    background: linear-gradient(135deg, {trend_color}15 0%, {trend_color}08 100%);
                    padding: 0.5rem 1rem; border-radius: 20px; width: fit-content;
                    border: 1px solid {trend_color}40;'>
            <span style='color: {trend_color}; font-size: 1rem; filter: drop-shadow(0 0 5px {trend_color});'>{trend_icon}</span>
            <span style='color: {trend_color}; font-size: 0.9rem; font-weight: 700;'>{trend_value}</span>
        </div>
        """
    
    return f"""
    <div style='background: linear-gradient(145deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                padding: 1.75rem; border-radius: 20px; height: 100%;
                border: 1px solid rgba(168, 85, 247, 0.2);
                box-shadow: 
                    0 15px 40px rgba(0,0,0,0.4),
                    inset 0 1px 0 rgba(255,255,255,0.05);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;'>
        <div style='position: absolute; top: 0; left: 0; right: 0; height: 4px;
                    background: linear-gradient(90deg, {color}, #a855f7);'></div>
        <p style='color: #a78bfa; margin: 0; font-size: 0.9rem; text-transform: uppercase; 
                  letter-spacing: 1.5px; font-weight: 700;'>{title}</p>
        <h2 style='background: linear-gradient(135deg, {color} 0%, #a855f7 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   background-clip: text;
                   margin: 0.75rem 0; font-size: 2.25rem; font-weight: 900;'>{value}</h2>
        <p style='color: #64748b; margin: 0; font-size: 0.95rem; font-weight: 500;'>{subtitle}</p>
        {trend_html}
    </div>
    """


def create_health_score_gauge(score, title="Overall Health"):
    """Create a STUNNING comprehensive health score gauge"""
    # Determine color based on score
    if score >= 90:
        color = "#10b981"
        grade = "Excellent"
        glow = "rgba(16, 185, 129, 0.5)"
    elif score >= 80:
        color = "#22c55e"
        grade = "Good"
        glow = "rgba(34, 197, 94, 0.4)"
    elif score >= 70:
        color = "#f59e0b"
        grade = "Fair"
        glow = "rgba(245, 158, 11, 0.4)"
    elif score >= 60:
        color = "#f97316"
        grade = "Needs Attention"
        glow = "rgba(249, 115, 22, 0.4)"
    else:
        color = "#ef4444"
        grade = "Critical"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b><br><span style='font-size:0.8em;color:{color}'>{grade}</span>",
               'font': {'size': 20, 'color': '#e2e8f0'}},
        number={'font': {'size': 50, 'color': 'white'}, 'suffix': '%'},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [60, 70], 'color': 'rgba(249, 115, 22, 0.2)'},
                {'range': [70, 80], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [80, 90], 'color': 'rgba(34, 197, 94, 0.2)'},
                {'range': [90, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#e94560", 'width': 4},
                'thickness': 0.8,
                'value': 95
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=80, b=30),
        font={'color': '#e2e8f0'}
    )
    
    return fig


def create_trend_sparkline(dates, values, title, color="#667eea", height=120):
    """Create mini trend chart for executive view"""
    fig = go.Figure()
    
    # Add area fill
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
        line=dict(color=color, width=2),
        mode='lines',
        hovertemplate='%{y:.1f}<extra></extra>'
    ))
    
    # Add end point marker
    if len(values) > 0:
        fig.add_trace(go.Scatter(
            x=[dates[-1]],
            y=[values[-1]],
            mode='markers',
            marker=dict(size=8, color=color, symbol='circle'),
            hovertemplate='Current: %{y:.1f}<extra></extra>'
        ))
    
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=25, b=0),
        title=dict(text=title, x=0.5, font=dict(size=12, color='#94a3b8')),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_executive_summary_table(data, title):
    """Create styled executive summary table"""
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 1.5rem; border-radius: 16px; margin: 1rem 0;
                border: 1px solid #334155;'>
        <h4 style='color: #e94560; margin: 0 0 1rem 0; font-size: 1.1rem; 
                   text-transform: uppercase; letter-spacing: 1px;'>{title}</h4>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(data, use_container_width=True, hide_index=True)


def calculate_department_health_score(kpis, cluster_perf, engineer_perf):
    """Calculate overall department health score (0-100)"""
    scores = []
    weights = []
    
    # SLA Compliance (40% weight)
    sla_score = min(kpis.get('sla_compliance', 0), 100)
    scores.append(sla_score)
    weights.append(0.40)
    
    # MTTR Performance (25% weight) - lower is better, normalize to 0-100
    avg_mttr = kpis.get('avg_duration', 24)
    mttr_score = max(0, min(100, 100 - (avg_mttr / 24 * 100)))  # 24h = 0 score
    scores.append(mttr_score)
    weights.append(0.25)
    
    # Team Efficiency (20% weight)
    if engineer_perf is not None and len(engineer_perf) > 0:
        avg_eng_sla = engineer_perf['SLA_Compliance'].mean() if 'SLA_Compliance' in engineer_perf.columns else 95
        team_score = min(avg_eng_sla, 100)
    else:
        team_score = 80
    scores.append(team_score)
    weights.append(0.20)
    
    # Cluster Coverage (15% weight)
    if cluster_perf is not None and len(cluster_perf) > 0:
        avg_cluster_sla = cluster_perf['SLA_Compliance'].mean() if 'SLA_Compliance' in cluster_perf.columns else 90
        cluster_score = min(avg_cluster_sla, 100)
    else:
        cluster_score = 80
    scores.append(cluster_score)
    weights.append(0.15)
    
    # Weighted average
    health_score = sum(s * w for s, w in zip(scores, weights))
    
    return round(health_score, 1)


def create_strategic_insights(kpis, df, cluster_perf, engineer_perf):
    """Generate strategic insights for CEO"""
    insights = []
    
    # SLA Analysis
    sla = kpis.get('sla_compliance', 0)
    if sla >= 95:
        insights.append({
            "category": "SLA Performance",
            "status": "success",
            "icon": "✅",
            "title": "Excellent SLA Compliance",
            "detail": f"Department is meeting SLA targets at {sla:.1f}%. Continue current practices."
        })
    elif sla >= 85:
        insights.append({
            "category": "SLA Performance",
            "status": "warning",
            "icon": "⚠️",
            "title": "SLA Needs Improvement",
            "detail": f"Current SLA at {sla:.1f}% is below 95% target. Review breach causes."
        })
    else:
        insights.append({
            "category": "SLA Performance",
            "status": "danger",
            "icon": "🚨",
            "title": "Critical SLA Alert",
            "detail": f"SLA compliance at {sla:.1f}% requires immediate attention. Executive action needed."
        })
    
    # MTTR Analysis
    mttr = kpis.get('avg_duration', 0)
    if mttr <= 4:
        insights.append({
            "category": "Resolution Time",
            "status": "success",
            "icon": "⚡",
            "title": "Fast Resolution Times",
            "detail": f"Average MTTR of {mttr:.1f} hours indicates efficient operations."
        })
    elif mttr <= 8:
        insights.append({
            "category": "Resolution Time",
            "status": "warning",
            "icon": "⏱️",
            "title": "Moderate Resolution Time",
            "detail": f"MTTR of {mttr:.1f} hours. Consider process optimization."
        })
    else:
        insights.append({
            "category": "Resolution Time",
            "status": "danger",
            "icon": "🐌",
            "title": "High Resolution Time",
            "detail": f"MTTR of {mttr:.1f} hours is above target. Investigate bottlenecks."
        })
    
    # Volume Trend
    total = kpis.get('total_tickets', 0)
    per_day = kpis.get('avg_tickets_per_day', 0)
    if per_day > 0:
        insights.append({
            "category": "Ticket Volume",
            "status": "info",
            "icon": "📊",
            "title": f"Daily Volume: {per_day:.0f} tickets",
            "detail": f"Total {total:,} tickets processed. Monitor for capacity planning."
        })
    
    # Top Cluster Issue
    if cluster_perf is not None and len(cluster_perf) > 0:
        worst_cluster = cluster_perf.nsmallest(1, 'SLA_Compliance')
        if len(worst_cluster) > 0:
            cluster_name = worst_cluster.iloc[0]['CLUSTER']
            cluster_sla = worst_cluster.iloc[0]['SLA_Compliance']
            if cluster_sla < 90:
                insights.append({
                    "category": "Cluster Alert",
                    "status": "warning",
                    "icon": "📍",
                    "title": f"Cluster {cluster_name} Underperforming",
                    "detail": f"SLA at {cluster_sla:.1f}%. Recommend resource reallocation."
                })
    
    # Team Performance
    if engineer_perf is not None and len(engineer_perf) > 0:
        top_performer = engineer_perf.nlargest(1, 'Efficiency_Score')
        if len(top_performer) > 0:
            eng_name = top_performer.iloc[0]['Engineer']
            eng_score = top_performer.iloc[0]['Efficiency_Score']
            insights.append({
                "category": "Top Performer",
                "status": "success",
                "icon": "🏆",
                "title": f"Star Performer: {eng_name}",
                "detail": f"Efficiency score of {eng_score:.1f}. Recognize and replicate best practices."
            })
    
    return insights


def render_insight_card(insight):
    """Render a strategic insight card"""
    colors = {
        "success": ("#10b981", "rgba(16, 185, 129, 0.1)"),
        "warning": ("#f59e0b", "rgba(245, 158, 11, 0.1)"),
        "danger": ("#ef4444", "rgba(239, 68, 68, 0.1)"),
        "info": ("#3b82f6", "rgba(59, 130, 246, 0.1)")
    }
    border_color, bg_color = colors.get(insight["status"], ("#667eea", "rgba(102, 126, 234, 0.1)"))
    
    st.markdown(f"""
    <div style='background: {bg_color}; border-left: 4px solid {border_color};
                padding: 1rem 1.5rem; border-radius: 0 12px 12px 0; margin: 0.75rem 0;'>
        <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
            <span style='font-size: 1.5rem;'>{insight["icon"]}</span>
            <span style='color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; 
                         letter-spacing: 1px;'>{insight["category"]}</span>
        </div>
        <h4 style='color: white; margin: 0 0 0.5rem 0; font-size: 1.1rem;'>{insight["title"]}</h4>
        <p style='color: #cbd5e1; margin: 0; font-size: 0.95rem; line-height: 1.5;'>{insight["detail"]}</p>
    </div>
    """, unsafe_allow_html=True)


def create_financial_impact_card(breached_tickets, avg_breach_hours, estimated_cost_per_hour=500):
    """Create financial impact visualization"""
    total_breach_hours = breached_tickets * avg_breach_hours if avg_breach_hours else breached_tickets * 2
    estimated_cost = total_breach_hours * estimated_cost_per_hour
    
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #7f1d1d 0%, #450a0a 100%);
                padding: 1.5rem; border-radius: 16px; border: 1px solid #ef4444;'>
        <h4 style='color: #fca5a5; margin: 0 0 1rem 0; font-size: 0.9rem; 
                   text-transform: uppercase; letter-spacing: 1px;'>SLA Breach Impact</h4>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;'>
            <div style='text-align: center;'>
                <p style='color: #f87171; margin: 0; font-size: 1.8rem; font-weight: 800;'>{breached_tickets:,}</p>
                <p style='color: #fca5a5; margin: 0; font-size: 0.8rem;'>Breached Tickets</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #f87171; margin: 0; font-size: 1.8rem; font-weight: 800;'>{total_breach_hours:,.0f}h</p>
                <p style='color: #fca5a5; margin: 0; font-size: 0.8rem;'>Total Breach Hours</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #f87171; margin: 0; font-size: 1.8rem; font-weight: 800;'>KES {estimated_cost:,.0f}</p>
                <p style='color: #fca5a5; margin: 0; font-size: 0.8rem;'>Estimated Impact*</p>
            </div>
        </div>
        <p style='color: #a8a29e; margin: 1rem 0 0 0; font-size: 0.75rem; text-align: center;'>
            *Estimated at KES {estimated_cost_per_hour:,}/hour downtime cost
        </p>
    </div>
    """, unsafe_allow_html=True)


# ==================== MAIN PAGE ====================

# Create executive header
create_executive_header()

# Get current user
current_user = get_current_user()
if current_user:
    st.markdown(f"""
    <p style='color: #94a3b8; text-align: center; margin-bottom: 2rem;'>
        Prepared for: <strong style='color: #e94560;'>{current_user.get('full_name', current_user.get('username', 'Executive'))}</strong>
    </p>
    """, unsafe_allow_html=True)

# Check for data
if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.markdown("""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 3rem; border-radius: 20px; text-align: center; margin: 2rem 0;
                border: 2px dashed #475569;'>
        <h2 style='color: #e94560; margin-bottom: 1rem;'>📊 No Data Available</h2>
        <p style='color: #94a3b8; font-size: 1.1rem;'>
            Please use the sidebar to select a date range and load data.
        </p>
        <p style='color: #64748b; margin-top: 1rem;'>
            The CEO Dashboard requires data to generate executive insights and KPIs.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Get data
df = st.session_state['df']
df_non_alarm = filter_non_alarm_data(df)

# Date range info
date_range = st.session_state.get('date_range', 'Custom Range')
badge_text = f"Period: {st.session_state.get('loaded_start_date', 'N/A')} to {st.session_state.get('loaded_end_date', 'N/A')[:10]}"

st.markdown(f"""
<p style='color: #64748b; text-align: center; margin-bottom: 2rem;'>
    Analysis Period: <strong style='color: #a78bfa;'>{badge_text}</strong>
</p>
""", unsafe_allow_html=True)

# Calculate all metrics
kpis = calculate_comprehensive_kpis(df)
kpis_non_alarm = calculate_comprehensive_kpis(df_non_alarm)
cluster_perf = calculate_cluster_performance(df)
engineer_perf = calculate_engineer_performance(df)
regional_perf = calculate_regional_performance(df)
service_perf = calculate_service_performance(df)

# Calculate health score
health_score = calculate_department_health_score(kpis, cluster_perf, engineer_perf)

# ==================== EXECUTIVE SUMMARY ROW ====================

st.markdown("### Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_kpi_executive_card(
        "Total Incidents",
        f"{kpis['total_tickets']:,}",
        f"{kpis['avg_tickets_per_day']:.0f} per day avg",
        color="#3b82f6"
    ), unsafe_allow_html=True)

with col2:
    sla_color = "#10b981" if kpis['sla_compliance'] >= 95 else "#f59e0b" if kpis['sla_compliance'] >= 85 else "#ef4444"
    st.markdown(create_kpi_executive_card(
        "SLA Compliance",
        f"{kpis['sla_compliance']:.1f}%",
        f"Grade: {kpis['sla_grade']}",
        color=sla_color
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_kpi_executive_card(
        "Avg Resolution",
        format_duration(kpis['avg_duration']),
        f"Median: {format_duration(kpis['median_duration'])}",
        color="#8b5cf6"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_kpi_executive_card(
        "Active Engineers",
        f"{kpis['active_engineers']:,}",
        f"Across {kpis['active_clusters']} clusters",
        color="#06b6d4"
    ), unsafe_allow_html=True)

with col5:
    st.markdown(create_kpi_executive_card(
        "Total Downtime",
        f"{kpis['total_downtime']:,.0f}h",
        f"{kpis['breached_tickets']:,} SLA breaches",
        color="#f43f5e"
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================== HEALTH SCORE & INSIGHTS ====================

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Department Health")
    fig = create_health_score_gauge(health_score, "Overall Health Score")
    st.plotly_chart(fig, use_container_width=True)
    
    # Financial Impact
    avg_breach_hours = kpis.get('total_breach_hours', 0) / max(kpis['breached_tickets'], 1) if kpis['breached_tickets'] > 0 else 2
    create_financial_impact_card(kpis['breached_tickets'], avg_breach_hours)

with col2:
    st.markdown("### Strategic Insights & Recommendations")
    insights = create_strategic_insights(kpis, df, cluster_perf, engineer_perf)
    
    for insight in insights:
        render_insight_card(insight)

# ==================== PERFORMANCE TRENDS ====================

st.markdown("---")
st.markdown("### Performance Trends")

# Daily trends
if 'DATE' in df.columns:
    daily_data = df.groupby('DATE').agg({
        'INC': 'count',
        'DURATION': 'mean'
    }).reset_index()
    daily_data.columns = ['Date', 'Tickets', 'MTTR']
    
    # SLA by day
    if 'EXTERNAL_BREACHED' in df.columns:
        def calc_sla(x):
            breached = x.astype(str).str.strip().str.upper().isin(['YES', 'TRUE', '1', 'Y']).sum()
            return ((len(x) - breached) / len(x)) * 100 if len(x) > 0 else 0
        
        daily_sla = df.groupby('DATE').agg({'EXTERNAL_BREACHED': calc_sla}).reset_index()
        daily_sla.columns = ['Date', 'SLA']
        daily_data = daily_data.merge(daily_sla, on='Date', how='left')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = create_trend_sparkline(
            daily_data['Date'].tolist(),
            daily_data['Tickets'].tolist(),
            "Daily Ticket Volume",
            "#3b82f6"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_trend_sparkline(
            daily_data['Date'].tolist(),
            daily_data['MTTR'].tolist(),
            "Daily Avg MTTR (hours)",
            "#8b5cf6"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        if 'SLA' in daily_data.columns:
            fig = create_trend_sparkline(
                daily_data['Date'].tolist(),
                daily_data['SLA'].tolist(),
                "Daily SLA Compliance %",
                "#10b981"
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================== DETAILED BREAKDOWN ====================

st.markdown("---")
st.markdown("### Operational Breakdown")

tab1, tab2, tab3, tab4 = st.tabs(["📍 Regional", "🏢 Clusters", "👷 Team", "🔧 Services"])

with tab1:
    if regional_perf is not None and len(regional_perf) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                regional_perf.head(10),
                x='Total_Tickets',
                y='REGION',
                orientation='h',
                title="Ticket Distribution by Region",
                color='SLA_Compliance',
                color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
                range_color=[70, 100]
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                coloraxis_colorbar=dict(title="SLA %")
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            display_df = regional_perf[['REGION', 'Total_Tickets', 'SLA_Compliance', 'Avg_MTTR_Hours']].head(10).copy()
            display_df.columns = ['Region', 'Tickets', 'SLA %', 'MTTR (h)']
            display_df['SLA %'] = display_df['SLA %'].round(1)
            display_df['MTTR (h)'] = display_df['MTTR (h)'].round(2)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No regional data available")

with tab2:
    if cluster_perf is not None and len(cluster_perf) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_clusters = cluster_perf.head(15)
            fig = px.treemap(
                top_clusters,
                path=['CLUSTER'],
                values='Total_Tickets',
                color='SLA_Compliance',
                color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
                range_color=[70, 100],
                title="Cluster Performance (Size = Tickets, Color = SLA)"
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top 5 and Bottom 5
            st.markdown("**🏆 Top Performers**")
            top5 = cluster_perf.nlargest(5, 'SLA_Compliance')[['CLUSTER', 'SLA_Compliance', 'Grade']].copy()
            top5.columns = ['Cluster', 'SLA %', 'Grade']
            top5['SLA %'] = top5['SLA %'].round(1)
            st.dataframe(top5, use_container_width=True, hide_index=True)
            
            st.markdown("**⚠️ Needs Attention**")
            bottom5 = cluster_perf.nsmallest(5, 'SLA_Compliance')[['CLUSTER', 'SLA_Compliance', 'Grade']].copy()
            bottom5.columns = ['Cluster', 'SLA %', 'Grade']
            bottom5['SLA %'] = bottom5['SLA %'].round(1)
            st.dataframe(bottom5, use_container_width=True, hide_index=True)
    else:
        st.info("No cluster data available")

with tab3:
    if engineer_perf is not None and len(engineer_perf) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_engineers = engineer_perf.head(15)
            fig = px.scatter(
                top_engineers,
                x='Total_Tickets',
                y='SLA_Compliance',
                size='Efficiency_Score',
                color='Grade',
                color_discrete_map={'A+': '#10b981', 'A': '#22c55e', 'B': '#f59e0b', 
                                   'C': '#f97316', 'D': '#ef4444', 'F': '#dc2626'},
                hover_name='Engineer',
                title="Engineer Performance Matrix",
                labels={'Total_Tickets': 'Tickets Handled', 'SLA_Compliance': 'SLA Compliance %'}
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            fig.add_hline(y=95, line_dash="dash", line_color="#22c55e", annotation_text="SLA Target")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🏆 Top 10 Engineers**")
            top10 = engineer_perf.nlargest(10, 'Efficiency_Score')[['Engineer', 'Total_Tickets', 'SLA_Compliance', 'Grade']].copy()
            top10.columns = ['Engineer', 'Tickets', 'SLA %', 'Grade']
            top10['SLA %'] = top10['SLA %'].round(1)
            st.dataframe(top10, use_container_width=True, hide_index=True)
    else:
        st.info("No engineer data available")

with tab4:
    if service_perf is not None and len(service_perf) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                service_perf.head(10),
                values='Total_Tickets',
                names='SERVICE',
                title="Service Distribution",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                service_perf.head(10),
                x='SERVICE',
                y='Avg_MTTR_Hours',
                title="MTTR by Service Type",
                color='SLA_Compliance',
                color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
                range_color=[70, 100]
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No service data available")

# ==================== COMPARISON: WITH VS WITHOUT ALARMS ====================

st.markdown("---")
st.markdown("### True Performance Analysis (Alarm Impact)")

col1, col2, col3 = st.columns(3)

with col1:
    # Comparison metrics
    st.markdown("""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 1.5rem; border-radius: 16px; border: 1px solid #334155;'>
        <h4 style='color: #a78bfa; margin: 0 0 1rem 0; text-align: center;'>Including Alarms</h4>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
            <div style='text-align: center;'>
                <p style='color: #94a3b8; margin: 0; font-size: 0.8rem;'>Tickets</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:,}</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #94a3b8; margin: 0; font-size: 0.8rem;'>SLA %</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:.1f}%</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #94a3b8; margin: 0; font-size: 0.8rem;'>Avg MTTR</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{}</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #94a3b8; margin: 0; font-size: 0.8rem;'>Grade</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{}</p>
            </div>
        </div>
    </div>
    """.format(
        kpis['total_tickets'],
        kpis['sla_compliance'],
        format_duration(kpis['avg_duration']),
        kpis['sla_grade']
    ), unsafe_allow_html=True)

with col2:
    # Non-alarm metrics
    st.markdown("""
    <div style='background: linear-gradient(145deg, #064e3b 0%, #022c22 100%);
                padding: 1.5rem; border-radius: 16px; border: 1px solid #10b981;'>
        <h4 style='color: #34d399; margin: 0 0 1rem 0; text-align: center;'>Excluding Alarms (True Perf)</h4>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
            <div style='text-align: center;'>
                <p style='color: #6ee7b7; margin: 0; font-size: 0.8rem;'>Tickets</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:,}</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #6ee7b7; margin: 0; font-size: 0.8rem;'>SLA %</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:.1f}%</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #6ee7b7; margin: 0; font-size: 0.8rem;'>Avg MTTR</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{}</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #6ee7b7; margin: 0; font-size: 0.8rem;'>Grade</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{}</p>
            </div>
        </div>
    </div>
    """.format(
        kpis_non_alarm['total_tickets'],
        kpis_non_alarm['sla_compliance'],
        format_duration(kpis_non_alarm['avg_duration']),
        kpis_non_alarm['sla_grade']
    ), unsafe_allow_html=True)

with col3:
    # Impact of alarms
    alarm_count = kpis['total_tickets'] - kpis_non_alarm['total_tickets']
    alarm_pct = (alarm_count / kpis['total_tickets'] * 100) if kpis['total_tickets'] > 0 else 0
    sla_diff = kpis_non_alarm['sla_compliance'] - kpis['sla_compliance']
    mttr_diff = kpis_non_alarm['avg_duration'] - kpis['avg_duration']
    
    st.markdown("""
    <div style='background: linear-gradient(145deg, #1e3a5f 0%, #0c1929 100%);
                padding: 1.5rem; border-radius: 16px; border: 1px solid #3b82f6;'>
        <h4 style='color: #60a5fa; margin: 0 0 1rem 0; text-align: center;'>Alarm Impact Analysis</h4>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
            <div style='text-align: center;'>
                <p style='color: #93c5fd; margin: 0; font-size: 0.8rem;'>Alarm Tickets</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:,}</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #93c5fd; margin: 0; font-size: 0.8rem;'>% of Total</p>
                <p style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:.1f}%</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #93c5fd; margin: 0; font-size: 0.8rem;'>SLA Impact</p>
                <p style='color: {}; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:+.1f}%</p>
            </div>
            <div style='text-align: center;'>
                <p style='color: #93c5fd; margin: 0; font-size: 0.8rem;'>MTTR Impact</p>
                <p style='color: {}; margin: 0; font-size: 1.5rem; font-weight: 700;'>{:+.1f}h</p>
            </div>
        </div>
    </div>
    """.format(
        alarm_count,
        alarm_pct,
        '#10b981' if sla_diff >= 0 else '#ef4444',
        sla_diff,
        '#10b981' if mttr_diff <= 0 else '#ef4444',
        mttr_diff
    ), unsafe_allow_html=True)

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #64748b;'>
    <p style='margin: 0;'>CEO Executive Dashboard | Fiber Maintenance Department</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
        Generated on {} | Data refreshed from operational database
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #475569;'>
        Confidential - For Executive Use Only
    </p>
</div>
""".format(datetime.now().strftime("%B %d, %Y at %H:%M")), unsafe_allow_html=True)
