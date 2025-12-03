"""
Ticket Search & Lookup - Fiber Maintenance Analytics System
Quick search for specific incidents and detailed ticket information
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import format_duration
from auth import require_page_access, get_current_user, log_page_visit

# Check page access
require_page_access("16_Ticket_Search.py")
log_page_visit("Ticket Search")


def create_header():
    """Create page header"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(6, 182, 212, 0.3);'>
        <h1 style='color: white; margin: 0; text-align: center;'>🔍 Ticket Search & Lookup</h1>
        <p style='color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;'>
            Search for specific incidents, view details, and analyze ticket history
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_ticket_details(ticket):
    """Display detailed ticket information"""
    # Main ticket info
    st.markdown(f"""
    <div style='background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
                padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1rem;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
            <h2 style='color: #06b6d4; margin: 0;'>🎫 {ticket.get('INC', 'N/A')}</h2>
            <span style='background: {"#ef4444" if str(ticket.get("EXTERNAL_BREACHED", "")).upper() in ["YES", "TRUE", "1", "Y"] else "#22c55e"};
                         padding: 0.5rem 1rem; border-radius: 20px; color: white; font-weight: 600;'>
                {"SLA BREACHED" if str(ticket.get("EXTERNAL_BREACHED", "")).upper() in ["YES", "TRUE", "1", "Y"] else "SLA MET"}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📋 Basic Information")
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1rem; border-radius: 8px;'>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Service:</strong> {ticket.get('SERVICE', 'N/A')}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Cluster:</strong> {ticket.get('CLUSTER', 'N/A')}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Region:</strong> {ticket.get('REGION', 'N/A')}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Dispatcher:</strong> {ticket.get('DISPATCHER', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⏱️ Timeline")
        escalated = ticket.get('ESCALATED_TIME', 'N/A')
        uptime = ticket.get('UPTIME', 'N/A')
        duration = ticket.get('DURATION', 0)
        
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1rem; border-radius: 8px;'>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Escalated:</strong> {escalated}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Resolved:</strong> {uptime}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Duration:</strong> {format_duration(duration) if pd.notna(duration) else 'N/A'}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Hours:</strong> {f"{duration:.2f}h" if pd.notna(duration) else 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 👷 Team")
        engineers = []
        for col in ['ENGINEER1', 'ENGINEER2', 'ENGINEER3']:
            if col in ticket and pd.notna(ticket.get(col)):
                engineers.append(str(ticket.get(col)))
        
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1rem; border-radius: 8px;'>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Engineer 1:</strong> {ticket.get('ENGINEER1', 'N/A')}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Engineer 2:</strong> {ticket.get('ENGINEER2', '-')}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Engineer 3:</strong> {ticket.get('ENGINEER3', '-')}</p>
            <p style='color: #94a3b8; margin: 0.3rem 0;'><strong style='color: #e2e8f0;'>Total Assigned:</strong> {len([e for e in engineers if e and e != 'nan'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cause and Summary
    st.markdown("#### 📝 Issue Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1rem; border-radius: 8px; height: 150px; overflow-y: auto;'>
            <p style='color: #a78bfa; font-weight: 600; margin: 0 0 0.5rem 0;'>Cause:</p>
            <p style='color: #e2e8f0; margin: 0;'>{ticket.get('CAUSE', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1rem; border-radius: 8px; height: 150px; overflow-y: auto;'>
            <p style='color: #a78bfa; font-weight: 600; margin: 0 0 0.5rem 0;'>Root Cause:</p>
            <p style='color: #e2e8f0; margin: 0;'>{ticket.get('ROOT_CAUSE', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary and Link Description
    st.markdown(f"""
    <div style='background: #1e293b; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
        <p style='color: #a78bfa; font-weight: 600; margin: 0 0 0.5rem 0;'>Summary:</p>
        <p style='color: #e2e8f0; margin: 0;'>{ticket.get('SUMMARY', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: #1e293b; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
        <p style='color: #a78bfa; font-weight: 600; margin: 0 0 0.5rem 0;'>Link Description:</p>
        <p style='color: #e2e8f0; margin: 0;'>{ticket.get('LINK_DESCRIPTION', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Challenge if exists
    if 'CHALLENGE' in ticket and pd.notna(ticket.get('CHALLENGE')):
        st.markdown(f"""
        <div style='background: linear-gradient(145deg, #7f1d1d 0%, #450a0a 100%); 
                    padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #ef4444;'>
            <p style='color: #fca5a5; font-weight: 600; margin: 0 0 0.5rem 0;'>⚠️ Challenge Encountered:</p>
            <p style='color: #fecaca; margin: 0;'>{ticket.get('CHALLENGE')}</p>
        </div>
        """, unsafe_allow_html=True)


def find_related_tickets(df, ticket, limit=10):
    """Find tickets related to the current one"""
    related = []
    
    # Same link description
    if 'LINK_DESCRIPTION' in ticket and pd.notna(ticket.get('LINK_DESCRIPTION')):
        link_desc = ticket.get('LINK_DESCRIPTION')
        same_link = df[
            (df['LINK_DESCRIPTION'] == link_desc) & 
            (df['INC'] != ticket.get('INC'))
        ]
        if len(same_link) > 0:
            related.append(('Same Link/Location', same_link))
    
    # Same cluster and cause
    if 'CLUSTER' in ticket and 'CAUSE' in ticket:
        same_cluster_cause = df[
            (df['CLUSTER'] == ticket.get('CLUSTER')) & 
            (df['CAUSE'] == ticket.get('CAUSE')) &
            (df['INC'] != ticket.get('INC'))
        ]
        if len(same_cluster_cause) > 0:
            related.append(('Same Cluster & Cause', same_cluster_cause))
    
    return related


# ==================== MAIN PAGE ====================

create_header()

# Check for data
if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.warning("⚠️ No data loaded. Please load data from the sidebar first.")
    st.stop()

df = st.session_state['df']

# Search section
st.markdown("### 🔎 Search Tickets")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input(
        "Search by INC Number, Link Description, or Summary",
        placeholder="Enter INC number (e.g., INC123456) or keywords...",
        help="Search across incident numbers, link descriptions, and summaries"
    )

with col2:
    search_field = st.selectbox(
        "Search In",
        ["All Fields", "INC Number", "Link Description", "Summary", "Cause", "Engineer"]
    )

with col3:
    search_btn = st.button("🔍 Search", use_container_width=True, type="primary")

# Perform search
if search_query or search_btn:
    with st.spinner("Searching..."):
        query = search_query.strip().upper() if search_query else ""
        
        if query:
            if search_field == "All Fields":
                # Search across multiple fields
                mask = (
                    df['INC'].astype(str).str.upper().str.contains(query, na=False) |
                    df['LINK_DESCRIPTION'].astype(str).str.upper().str.contains(query, na=False) |
                    df['SUMMARY'].astype(str).str.upper().str.contains(query, na=False) |
                    df['CAUSE'].astype(str).str.upper().str.contains(query, na=False)
                )
            elif search_field == "INC Number":
                mask = df['INC'].astype(str).str.upper().str.contains(query, na=False)
            elif search_field == "Link Description":
                mask = df['LINK_DESCRIPTION'].astype(str).str.upper().str.contains(query, na=False)
            elif search_field == "Summary":
                mask = df['SUMMARY'].astype(str).str.upper().str.contains(query, na=False)
            elif search_field == "Cause":
                mask = df['CAUSE'].astype(str).str.upper().str.contains(query, na=False)
            elif search_field == "Engineer":
                mask = (
                    df['ENGINEER1'].astype(str).str.upper().str.contains(query, na=False) |
                    df['ENGINEER2'].astype(str).str.upper().str.contains(query, na=False) |
                    df['ENGINEER3'].astype(str).str.upper().str.contains(query, na=False)
                )
            else:
                mask = df['INC'].astype(str).str.upper().str.contains(query, na=False)
            
            results = df[mask]
            
            if len(results) > 0:
                st.success(f"✅ Found {len(results)} matching ticket(s)")
                
                # Results table
                display_cols = ['INC', 'SERVICE', 'CLUSTER', 'ESCALATED_TIME', 'DURATION', 'EXTERNAL_BREACHED']
                display_cols = [c for c in display_cols if c in results.columns]
                
                st.dataframe(
                    results[display_cols].head(50),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Select ticket for details
                st.markdown("---")
                selected_inc = st.selectbox(
                    "Select a ticket to view details:",
                    options=results['INC'].tolist()[:50],
                    key="selected_ticket"
                )
                
                if selected_inc:
                    ticket = results[results['INC'] == selected_inc].iloc[0].to_dict()
                    st.markdown("---")
                    display_ticket_details(ticket)
                    
                    # Related tickets
                    st.markdown("---")
                    st.markdown("### 🔗 Related Tickets")
                    
                    related = find_related_tickets(df, ticket)
                    
                    if related:
                        for category, rel_df in related:
                            with st.expander(f"{category} ({len(rel_df)} tickets)"):
                                display_cols = ['INC', 'ESCALATED_TIME', 'SERVICE', 'CAUSE', 'DURATION']
                                display_cols = [c for c in display_cols if c in rel_df.columns]
                                st.dataframe(rel_df[display_cols].head(20), use_container_width=True, hide_index=True)
                    else:
                        st.info("No related tickets found")
            else:
                st.warning(f"❌ No tickets found matching '{search_query}'")
        else:
            st.info("Enter a search term to find tickets")

# Quick filters section
st.markdown("---")
st.markdown("### 🎛️ Quick Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔴 SLA Breached", use_container_width=True):
        breached = df[df['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y'])]
        st.session_state['quick_filter_results'] = breached
        st.session_state['quick_filter_name'] = 'SLA Breached Tickets'

with col2:
    if st.button("⏰ Long Duration (>12h)", use_container_width=True):
        long_duration = df[df['DURATION'] > 12]
        st.session_state['quick_filter_results'] = long_duration
        st.session_state['quick_filter_name'] = 'Long Duration Tickets (>12 hours)'

with col3:
    if st.button("📅 Today's Tickets", use_container_width=True):
        today = datetime.now().date()
        if 'ESCALATED_TIME' in df.columns:
            today_tickets = df[pd.to_datetime(df['ESCALATED_TIME']).dt.date == today]
            st.session_state['quick_filter_results'] = today_tickets
            st.session_state['quick_filter_name'] = f"Today's Tickets ({today})"

with col4:
    if st.button("⚠️ With Challenges", use_container_width=True):
        with_challenges = df[df['CHALLENGE'].notna() & (df['CHALLENGE'] != '')]
        st.session_state['quick_filter_results'] = with_challenges
        st.session_state['quick_filter_name'] = 'Tickets with Challenges'

# Display quick filter results
if 'quick_filter_results' in st.session_state and st.session_state['quick_filter_results'] is not None:
    results = st.session_state['quick_filter_results']
    filter_name = st.session_state.get('quick_filter_name', 'Filtered Results')
    
    st.markdown(f"#### {filter_name}")
    st.info(f"Found {len(results)} tickets")
    
    if len(results) > 0:
        display_cols = ['INC', 'SERVICE', 'CLUSTER', 'ESCALATED_TIME', 'DURATION', 'CAUSE']
        display_cols = [c for c in display_cols if c in results.columns]
        
        st.dataframe(results[display_cols].head(100), use_container_width=True, hide_index=True)
        
        # Clear button
        if st.button("Clear Filter"):
            del st.session_state['quick_filter_results']
            del st.session_state['quick_filter_name']
            st.rerun()

# Statistics section
st.markdown("---")
st.markdown("### 📊 Data Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", f"{len(df):,}")

with col2:
    breached_count = len(df[df['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y'])])
    st.metric("Breached", f"{breached_count:,}")

with col3:
    unique_links = df['LINK_DESCRIPTION'].nunique() if 'LINK_DESCRIPTION' in df.columns else 0
    st.metric("Unique Links", f"{unique_links:,}")

with col4:
    if 'ESCALATED_TIME' in df.columns:
        date_range = f"{pd.to_datetime(df['ESCALATED_TIME']).min().strftime('%b %d')} - {pd.to_datetime(df['ESCALATED_TIME']).max().strftime('%b %d')}"
        st.metric("Date Range", date_range)
