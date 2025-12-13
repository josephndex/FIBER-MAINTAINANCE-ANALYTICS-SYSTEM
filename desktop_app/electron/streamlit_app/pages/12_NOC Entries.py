"""
NOC Entries Page - Ticket Entry System for NOC Team
Allows NOC and Management to add new fiber maintenance tickets
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import APP_TITLE, DEVELOPER_NAME
from auth import (
    require_authentication, log_page_visit, get_current_user,
    require_page_access, get_auth_manager
)
from data_loader import get_db_engine

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    .noc-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(5, 150, 105, 0.3);
    }
    
    .noc-header h1, .noc-header p {
        color: white !important;
    }
    
    .form-section {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 4px solid #059669;
    }
    
    .form-section h3 {
        color: #10b981 !important;
        margin-bottom: 1rem;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    .success-card {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .recent-entries {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Require authentication and page access
require_authentication()
require_page_access("12_NOC Entries.py")
log_page_visit("12_NOC Entries.py")

current_user = get_current_user()


def get_noc_db_connection():
    """Get database connection for NOC entries."""
    try:
        engine = get_db_engine()
        return engine
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def save_noc_entry(entry_data: dict) -> tuple:
    """Save a new NOC entry to the database."""
    engine = get_noc_db_connection()
    if not engine:
        return False, "Database connection failed"
    
    try:
        from sqlalchemy import text
        
        insert_query = text("""
            INSERT INTO noc_entries (
                INC, LINK_DESCRIPTION, SERVICE, ENGINEER1, ENGINEER2, ENGINEER3,
                ESCALATED_TIME, STATUS, ROOT_CAUSE, LATITUDE, LONGITUDE,
                CHALLENGE, MATERIAL_USED, CLEARS, UPTIME, SLA,
                ACCESS_SITE, ACCESS_PROVIDER, REGION,
                ACCESS_REQUEST_TIME, ACCESS_GRANTED_TIME, ACCESS_DURATION,
                SECURITY_REQUEST_TIME, SECURITY_ARRIVAL_TIME, SECURITY_TIME_TAKEN,
                DISPATCHER, created_by
            ) VALUES (
                :INC, :LINK_DESCRIPTION, :SERVICE, :ENGINEER1, :ENGINEER2, :ENGINEER3,
                :ESCALATED_TIME, :STATUS, :ROOT_CAUSE, :LATITUDE, :LONGITUDE,
                :CHALLENGE, :MATERIAL_USED, :CLEARS, :UPTIME, :SLA,
                :ACCESS_SITE, :ACCESS_PROVIDER, :REGION,
                :ACCESS_REQUEST_TIME, :ACCESS_GRANTED_TIME, :ACCESS_DURATION,
                :SECURITY_REQUEST_TIME, :SECURITY_ARRIVAL_TIME, :SECURITY_TIME_TAKEN,
                :DISPATCHER, :created_by
            )
        """)
        
        with engine.connect() as conn:
            conn.execute(insert_query, entry_data)
            conn.commit()
        
        return True, f"Ticket {entry_data['INC']} saved successfully!"
    
    except Exception as e:
        error_msg = str(e)
        if "Duplicate entry" in error_msg:
            return False, f"Ticket {entry_data['INC']} already exists!"
        return False, f"Error saving entry: {error_msg}"


def get_recent_entries(limit: int = 10) -> pd.DataFrame:
    """Get recent NOC entries."""
    engine = get_noc_db_connection()
    if not engine:
        return pd.DataFrame()
    
    try:
        query = f"""
            SELECT INC, LINK_DESCRIPTION, SERVICE, ENGINEER1, STATUS, 
                   ESCALATED_TIME, REGION, created_by, created_at
            FROM noc_entries 
            ORDER BY created_at DESC 
            LIMIT {limit}
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching entries: {e}")
        return pd.DataFrame()


def get_dropdown_options():
    """Get dropdown options from existing data."""
    engine = get_noc_db_connection()
    options = {
        'services': ['SDC/FTTS', 'NPS', 'FTTB', 'FTTH', 'FTTM', 'SDH', 'FTTC', 'Other'],
        'regions': ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Other'],
        'statuses': ['Open', 'In Progress', 'Pending', 'Resolved', 'Closed'],
        'sla_options': ['4 Hours', '8 Hours', '24 Hours', '48 Hours', '72 Hours'],
        'engineers': []
    }
    
    if engine:
        try:
            # Get unique engineers from engineered_tickets
            query = """
                SELECT DISTINCT ASSIGNED_ENGINEER FROM engineered_tickets 
                WHERE ASSIGNED_ENGINEER IS NOT NULL AND ASSIGNED_ENGINEER != ''
                ORDER BY ASSIGNED_ENGINEER
                LIMIT 100
            """
            df = pd.read_sql(query, engine)
            if not df.empty:
                options['engineers'] = [''] + df['ASSIGNED_ENGINEER'].tolist()
        except:
            pass
    
    return options


# Header
st.markdown("""
<div class='noc-header'>
    <h1>NOC Ticket Entry System</h1>
    <p>Add New Fiber Maintenance Tickets</p>
</div>
""", unsafe_allow_html=True)

# Get dropdown options
options = get_dropdown_options()

# Create tabs
tab1, tab2 = st.tabs(["New Entry", "Recent Entries"])

with tab1:
    st.markdown("### Add New Ticket")
    
    with st.form("noc_entry_form", clear_on_submit=True):
        # Section 1: Basic Info
        st.markdown("#### Ticket Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            inc = st.text_input("INC (Ticket Number)*", placeholder="e.g., INC12345678")
        with col2:
            service = st.selectbox("Service*", options=options['services'])
        with col3:
            region = st.selectbox("Region*", options=options['regions'])
        
        link_description = st.text_area("Link Description", placeholder="Describe the affected link...", height=80)
        
        # Section 2: Assignment
        st.markdown("---")
        st.markdown("#### Assignment")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            dispatcher = st.text_input("Dispatcher", placeholder="Dispatcher name")
        with col2:
            engineer1 = st.selectbox("Engineer 1", options=options['engineers'] if options['engineers'] else [''])
        with col3:
            engineer2 = st.selectbox("Engineer 2", options=options['engineers'] if options['engineers'] else [''])
        with col4:
            engineer3 = st.selectbox("Engineer 3", options=options['engineers'] if options['engineers'] else [''])
        
        # Section 3: Time & Status
        st.markdown("---")
        st.markdown("#### Time & Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            escalated_date = st.date_input("Escalated Date", value=datetime.now().date())
            escalated_time = st.time_input("Escalated Time", value=datetime.now().time())
        with col2:
            status = st.selectbox("Status", options=options['statuses'])
        with col3:
            sla = st.selectbox("SLA Target", options=options['sla_options'])
        
        # Section 4: Location
        st.markdown("---")
        st.markdown("#### Location (Optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.text_input("Latitude", placeholder="e.g., -1.2921")
        with col2:
            longitude = st.text_input("Longitude", placeholder="e.g., 36.8219")
        
        # Section 5: Access & Security
        st.markdown("---")
        st.markdown("#### Access & Security (Optional)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            access_site = st.text_input("Access Site", placeholder="Site name")
            access_provider = st.text_input("Access Provider", placeholder="Provider name")
        with col2:
            access_request_date = st.date_input("Access Request Date", value=None, key="access_req_date")
            access_request_time = st.time_input("Access Request Time", value=None, key="access_req_time")
            access_granted_date = st.date_input("Access Granted Date", value=None, key="access_grant_date")
            access_granted_time = st.time_input("Access Granted Time", value=None, key="access_grant_time")
        with col3:
            security_request_date = st.date_input("Security Request Date", value=None, key="sec_req_date")
            security_request_time = st.time_input("Security Request Time", value=None, key="sec_req_time")
            security_arrival_date = st.date_input("Security Arrival Date", value=None, key="sec_arr_date")
            security_arrival_time = st.time_input("Security Arrival Time", value=None, key="sec_arr_time")
        
        # Section 6: Resolution Details
        st.markdown("---")
        st.markdown("#### Resolution Details (Optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            root_cause = st.text_area("Root Cause", placeholder="Describe the root cause...", height=80)
            challenge = st.text_area("Challenge", placeholder="Any challenges faced...", height=80)
        with col2:
            material_used = st.text_area("Material Used", placeholder="List materials used...", height=80)
            col_a, col_b = st.columns(2)
            with col_a:
                clears = st.number_input("Clears", min_value=0, value=0)
            with col_b:
                uptime = st.number_input("Uptime %", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        
        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button("Save Ticket", use_container_width=True, type="primary")
        
        if submitted:
            # Validate required fields
            if not inc:
                st.error("INC (Ticket Number) is required!")
            elif not service:
                st.error("Service is required!")
            elif not region:
                st.error("Region is required!")
            else:
                # Combine date and time
                escalated_datetime = datetime.combine(escalated_date, escalated_time)
                
                # Handle optional datetime fields
                access_request_datetime = None
                if access_request_date and access_request_time:
                    access_request_datetime = datetime.combine(access_request_date, access_request_time)
                
                access_granted_datetime = None
                if access_granted_date and access_granted_time:
                    access_granted_datetime = datetime.combine(access_granted_date, access_granted_time)
                
                security_request_datetime = None
                if security_request_date and security_request_time:
                    security_request_datetime = datetime.combine(security_request_date, security_request_time)
                
                security_arrival_datetime = None
                if security_arrival_date and security_arrival_time:
                    security_arrival_datetime = datetime.combine(security_arrival_date, security_arrival_time)
                
                # Calculate durations
                access_duration = None
                if access_request_datetime and access_granted_datetime:
                    delta = access_granted_datetime - access_request_datetime
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes = remainder // 60
                    access_duration = f"{hours}h {minutes}m"
                
                security_time_taken = None
                if security_request_datetime and security_arrival_datetime:
                    delta = security_arrival_datetime - security_request_datetime
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes = remainder // 60
                    security_time_taken = f"{hours}h {minutes}m"
                
                # Prepare entry data
                entry_data = {
                    'INC': inc.strip().upper(),
                    'LINK_DESCRIPTION': link_description if link_description else None,
                    'SERVICE': service,
                    'ENGINEER1': engineer1 if engineer1 else None,
                    'ENGINEER2': engineer2 if engineer2 else None,
                    'ENGINEER3': engineer3 if engineer3 else None,
                    'ESCALATED_TIME': escalated_datetime,
                    'STATUS': status,
                    'ROOT_CAUSE': root_cause if root_cause else None,
                    'LATITUDE': float(latitude) if latitude else None,
                    'LONGITUDE': float(longitude) if longitude else None,
                    'CHALLENGE': challenge if challenge else None,
                    'MATERIAL_USED': material_used if material_used else None,
                    'CLEARS': clears,
                    'UPTIME': uptime if uptime > 0 else None,
                    'SLA': sla,
                    'ACCESS_SITE': access_site if access_site else None,
                    'ACCESS_PROVIDER': access_provider if access_provider else None,
                    'REGION': region,
                    'ACCESS_REQUEST_TIME': access_request_datetime,
                    'ACCESS_GRANTED_TIME': access_granted_datetime,
                    'ACCESS_DURATION': access_duration,
                    'SECURITY_REQUEST_TIME': security_request_datetime,
                    'SECURITY_ARRIVAL_TIME': security_arrival_datetime,
                    'SECURITY_TIME_TAKEN': security_time_taken,
                    'DISPATCHER': dispatcher if dispatcher else None,
                    'created_by': current_user.get('username', 'Unknown')
                }
                
                # Save to database
                success, message = save_noc_entry(entry_data)
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

with tab2:
    st.markdown("### Recent Entries")
    
    # Refresh button
    if st.button("Refresh", type="secondary"):
        st.rerun()
    
    # Get recent entries
    recent_df = get_recent_entries(20)
    
    if not recent_df.empty:
        # Format datetime columns
        if 'ESCALATED_TIME' in recent_df.columns:
            recent_df['ESCALATED_TIME'] = pd.to_datetime(recent_df['ESCALATED_TIME']).dt.strftime('%Y-%m-%d %H:%M')
        if 'created_at' in recent_df.columns:
            recent_df['created_at'] = pd.to_datetime(recent_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename columns for display
        display_df = recent_df.rename(columns={
            'INC': 'Ticket',
            'LINK_DESCRIPTION': 'Description',
            'SERVICE': 'Service',
            'ENGINEER1': 'Engineer',
            'STATUS': 'Status',
            'ESCALATED_TIME': 'Escalated',
            'REGION': 'Region',
            'created_by': 'Created By',
            'created_at': 'Created At'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ticket": st.column_config.TextColumn(width="small"),
                "Description": st.column_config.TextColumn(width="large"),
                "Status": st.column_config.TextColumn(width="small"),
            }
        )
        
        # Download option
        csv = recent_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"noc_entries_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No entries found. Add your first ticket using the 'New Entry' tab!")

# Sidebar
with st.sidebar:
    if current_user:
        position = current_user.get('position', 'NOC')
        st.markdown(f"""
        <div style='text-align: center; padding: 0.5rem; background: linear-gradient(135deg, #05966920 0%, #04785740 100%); 
                    border-radius: 10px; margin-bottom: 1rem; border: 1px solid #05966960;'>
            <p style='margin: 0; font-size: 0.85rem; color: #10b981;'>{position}</p>
            <p style='margin: 0; font-weight: 600; color: #e2e8f0;'>{current_user.get('username', 'User')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    
    # Get stats
    engine = get_noc_db_connection()
    if engine:
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN STATUS = 'Open' THEN 1 ELSE 0 END) as open_count,
                    SUM(CASE WHEN STATUS = 'Resolved' OR STATUS = 'Closed' THEN 1 ELSE 0 END) as resolved_count
                FROM noc_entries
            """
            stats_df = pd.read_sql(stats_query, engine)
            
            if not stats_df.empty:
                st.metric("Total Entries", int(stats_df['total'].iloc[0]))
                st.metric("Open Tickets", int(stats_df['open_count'].iloc[0]))
                st.metric("Resolved", int(stats_df['resolved_count'].iloc[0]))
        except:
            pass
    
    st.markdown("---")
    
    if st.button("Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Home.py")
    
    st.markdown("---")
    st.caption(f"© 2025 {DEVELOPER_NAME}")

# Footer
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #6b7280; border-top: 2px solid #059669; margin-top: 3rem;'>
    <p>NOC Ticket Entry System | Fiber Maintenance Analytics</p>
</div>
""", unsafe_allow_html=True)
