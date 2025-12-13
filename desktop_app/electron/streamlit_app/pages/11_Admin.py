"""
Admin Dashboard - Activity Logs and User Management
Only accessible to admin users
Super Admin (NDERITU) has full control over user management
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import APP_TITLE, DEVELOPER_NAME
from auth import (
    check_authentication, get_current_user, get_auth_manager, 
    log_page_visit, require_admin, is_super_admin, is_admin,
    SUPER_ADMIN_USERNAME, USER_POSITIONS, POSITION_PAGE_ACCESS
)

# Custom CSS - STUNNING Admin Dashboard
st.markdown("""
<style>
    /* Animated background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1a0d2e, #0f172a, #1e1033);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* STUNNING Admin Header */
    .admin-header {
        background: linear-gradient(135deg, #dc2626 0%, #f97316 50%, #a855f7 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 50px rgba(220, 38, 38, 0.3),
            0 10px 30px rgba(249, 115, 22, 0.2),
            inset 0 1px 0 rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .admin-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: headerShine 4s ease-in-out infinite;
    }
    
    @keyframes headerShine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    /* STUNNING Super Admin Header */
    .super-admin-header {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #f97316 100%);
        padding: 2.5rem;
        border-radius: 24px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 25px 60px rgba(124, 58, 237, 0.35),
            0 15px 40px rgba(168, 85, 247, 0.25),
            inset 0 1px 0 rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .super-admin-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #fde047, #f97316, #a855f7, #f97316, #fde047);
        background-size: 200% 100%;
        animation: goldBorder 3s linear infinite;
    }
    
    @keyframes goldBorder {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    .admin-header h1, .admin-header p,
    .super-admin-header h1, .super-admin-header p {
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    /* STUNNING Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 1.75rem;
        border-radius: 20px;
        border: 1px solid rgba(168, 85, 247, 0.2);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(180deg, #f97316, #a855f7);
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 20px 50px rgba(249, 115, 22, 0.2),
            0 10px 30px rgba(168, 85, 247, 0.15);
        border-color: #f97316;
    }
    
    .stat-card h3 {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        font-size: 2.25rem;
        font-weight: 900;
    }
    
    .stat-card p {
        color: #94a3b8 !important;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1033 0%, #0f172a 50%, #1a0d2e 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    .stDataFrame {
        background: rgba(30, 41, 59, 0.9) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }
    
    .super-admin-badge {
        background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .admin-badge {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .position-badge-management {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .position-badge-engineer {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .position-badge-noc {
        background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Require admin access
require_admin()

# Get current user and log page visit
current_user = get_current_user()
auth_manager = get_auth_manager()
log_page_visit("11_Admin.py")

# Check if current user is super admin
user_is_super_admin = is_super_admin(current_user)

# Header based on role
if user_is_super_admin:
    st.markdown("""
    <div class='super-admin-header'>
        <h1>Super Admin Dashboard</h1>
        <p>Full Control - Activity Logs & User Management</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class='admin-header'>
        <h1>Admin Dashboard</h1>
        <p>Activity Logs & User Monitoring (View Only)</p>
    </div>
    """, unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Activity Logs", "User Management", "Position Management", "Statistics", "Audit Trail"])

with tab1:
    st.markdown("### Recent Activity Logs")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_limit = st.selectbox(
            "Number of logs",
            options=[50, 100, 200, 500],
            index=1
        )
    
    with col2:
        # Get all users for filtering
        all_users = auth_manager.get_all_users()
        user_options = ["All Users"] + [u['username'] for u in all_users]
        selected_user = st.selectbox(
            "Filter by user",
            options=user_options
        )
    
    with col3:
        action_filter = st.selectbox(
            "Filter by action",
            options=["All Actions", "USER_LOGIN", "USER_LOGOUT", "PAGE_VISIT", "DATA_LOAD", 
                    "USER_REGISTERED", "LOGIN_FAILED", "ADMIN_GRANTED", "ADMIN_REVOKED",
                    "USER_ACTIVATED", "USER_DEACTIVATED"]
        )
    
    # Get activity logs
    if selected_user != "All Users":
        user_id = next((u['id'] for u in all_users if u['username'] == selected_user), None)
        logs = auth_manager.get_user_activity(user_id=user_id, limit=log_limit)
    else:
        logs = auth_manager.get_user_activity(limit=log_limit)
    
    # Filter by action if needed
    if action_filter != "All Actions":
        logs = [log for log in logs if log['action'] == action_filter]
    
    if logs:
        # Convert to DataFrame for display
        logs_df = pd.DataFrame(logs)
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        logs_df = logs_df.sort_values('timestamp', ascending=False)
        
        # Format for display
        display_df = logs_df[['timestamp', 'username', 'action', 'page', 'details']].copy()
        display_df.columns = ['Timestamp', 'User', 'Action', 'Page', 'Details']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm:ss"),
                "Action": st.column_config.TextColumn(width="medium"),
                "Details": st.column_config.TextColumn(width="large")
            }
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download Logs as CSV",
            data=csv,
            file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No activity logs found for the selected criteria.")

with tab2:
    st.markdown("### Registered Users")
    
    users = auth_manager.get_all_users()
    
    if users:
        # Show info about permissions
        if user_is_super_admin:
            st.success("You are the **Super Admin**. You can manage user positions, activate/deactivate, and delete accounts.")
        else:
            st.info("You have **view-only** access to user management. Only the Super Admin can modify user settings.")
        
        st.markdown("---")
        
        # Display users in a more interactive way
        for user in users:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 1.5, 2, 1.5, 1.5])
                
                with col1:
                    # Username with badges
                    badges = ""
                    if user.get('is_super_admin') or user['username'].upper() == SUPER_ADMIN_USERNAME:
                        badges = "<span class='super-admin-badge'>SUPER ADMIN</span>"
                    
                    # Position badge
                    position = user.get('position', 'NOC')
                    position_badge_class = {
                        'MANAGEMENT': 'position-badge-management',
                        'ENGINEER': 'position-badge-engineer',
                        'NOC': 'position-badge-noc'
                    }.get(position, 'position-badge-noc')
                    position_badge = f" <span class='{position_badge_class}'>{position}</span>"
                    
                    st.markdown(f"""
                    <div style='padding: 0.5rem 0;'>
                        <strong style='color: #e2e8f0;'>{user['username']}</strong><br>
                        {badges}{position_badge}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 0.5rem 0; color: #94a3b8;'>
                        Email: {user['email']}<br>
                        Name: {user['full_name'] or 'N/A'}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    status_color = "#10b981" if user['is_active'] else "#ef4444"
                    status_text = "Active" if user['is_active'] else "Inactive"
                    st.markdown(f"<span style='color: {status_color};'>{status_text}</span>", unsafe_allow_html=True)
                
                with col4:
                    # Only super admin can change positions
                    if user_is_super_admin and user['username'].upper() != SUPER_ADMIN_USERNAME:
                        current_position = user.get('position', 'NOC')
                        new_position = st.selectbox(
                            "Position",
                            options=USER_POSITIONS,
                            index=USER_POSITIONS.index(current_position) if current_position in USER_POSITIONS else 0,
                            key=f"pos_{user['id']}",
                            label_visibility="collapsed"
                        )
                        if new_position != current_position:
                            if st.button("Update", key=f"upd_pos_{user['id']}", type="primary"):
                                success, msg = auth_manager.set_user_position(
                                    user['id'],
                                    new_position,
                                    current_user.get('username', 'Unknown')
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        if user['username'].upper() == SUPER_ADMIN_USERNAME:
                            st.markdown("*Full Access*")
                        else:
                            st.markdown(f"*{user.get('position', 'NOC')}*")
                
                with col5:
                    # Only super admin can activate/deactivate users
                    if user_is_super_admin and user['username'].upper() != SUPER_ADMIN_USERNAME:
                        if user['is_active']:
                            if st.button("Deactivate", key=f"deact_{user['id']}", type="secondary"):
                                success, msg = auth_manager.set_user_active_status(
                                    user['id'],
                                    False,
                                    current_user.get('username', 'Unknown')
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            if st.button("Activate", key=f"act_{user['id']}", type="primary"):
                                success, msg = auth_manager.set_user_active_status(
                                    user['id'],
                                    True,
                                    current_user.get('username', 'Unknown')
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                
                with col6:
                    # Only super admin can delete users (not super admin themselves)
                    if user_is_super_admin and user['username'].upper() != SUPER_ADMIN_USERNAME:
                        # Use a confirmation pattern with session state
                        confirm_key = f"confirm_delete_{user['id']}"
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False
                        
                        if not st.session_state[confirm_key]:
                            if st.button("🗑️ Delete", key=f"del_{user['id']}", type="secondary"):
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            st.markdown("<span style='color: #ef4444; font-size: 0.85rem;'>Confirm?</span>", unsafe_allow_html=True)
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("Yes", key=f"yes_del_{user['id']}", type="primary"):
                                    success, msg = auth_manager.delete_user(
                                        user['id'],
                                        current_user.get('username', 'Unknown')
                                    )
                                    st.session_state[confirm_key] = False
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            with col_no:
                                if st.button("No", key=f"no_del_{user['id']}", type="secondary"):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                    else:
                        if user['username'].upper() == SUPER_ADMIN_USERNAME:
                            st.markdown("<span style='color: #6b7280; font-size: 0.75rem;'>Protected</span>", unsafe_allow_html=True)
                
                st.markdown("<hr style='border-color: #334155; margin: 0.5rem 0;'>", unsafe_allow_html=True)
        
        # Summary stats
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            active_users = sum(1 for u in users if u['is_active'])
            st.metric("Active", active_users)
        with col3:
            management_count = sum(1 for u in users if u.get('position') == 'MANAGEMENT')
            st.metric("Management", management_count)
        with col4:
            engineer_count = sum(1 for u in users if u.get('position') == 'ENGINEER')
            st.metric("Engineers", engineer_count)
        with col5:
            noc_count = sum(1 for u in users if u.get('position') == 'NOC')
            st.metric("NOC", noc_count)
    else:
        st.info("No users found.")

with tab3:
    st.markdown("### Position Management")
    st.markdown("""
    Positions control which pages users can access:
    - **MANAGEMENT**: Access to all dashboards except Admin
    - **ENGINEER**: Full analytics access (except Admin)
    - **NOC**: Full analytics access (except Admin)
    
    *Note: All positions now have access to all dashboard pages. Only Admin access is restricted.*
    """)
    
    # Only super admin can modify positions
    if user_is_super_admin:
        st.success("As **Super Admin**, you have full control over user positions.")
    else:
        st.info("Only the **Super Admin** can modify user positions.")
    
    st.markdown("---")
    
    # Get all users
    position_users = auth_manager.get_all_users()
    
    if position_users:
        # Position summary
        col1, col2, col3 = st.columns(3)
        management_count = sum(1 for u in position_users if u.get('position') == 'MANAGEMENT')
        engineer_count = sum(1 for u in position_users if u.get('position') == 'ENGINEER')
        noc_count = sum(1 for u in position_users if u.get('position') == 'NOC')
        
        with col1:
            st.metric("MANAGEMENT", management_count, help="Full access including Admin")
        with col2:
            st.metric("ENGINEER", engineer_count, help="Full analytics access")
        with col3:
            st.metric("NOC", noc_count, help="Full analytics access")
        
        st.markdown("---")
        
        # User position table
        for user in position_users:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                
                with col1:
                    username = user['username']
                    if username.upper() == SUPER_ADMIN_USERNAME:
                        st.markdown(f"**{username}** 👑")
                    else:
                        st.markdown(f"**{username}**")
                
                with col2:
                    current_position = user.get('position', 'N/A')
                    position_colors = {
                        'MANAGEMENT': '#f97316',  # Orange
                        'ENGINEER': '#3b82f6',    # Blue
                        'NOC': '#a855f7'          # Purple
                    }
                    color = position_colors.get(current_position, '#6b7280')
                    st.markdown(f"<span style='color: {color}; font-weight: bold;'>{current_position}</span>", unsafe_allow_html=True)
                
                with col3:
                    status = "Active" if user['is_active'] else "Inactive"
                    status_color = "#10b981" if user['is_active'] else "#ef4444"
                    st.markdown(f"<span style='color: {status_color};'>{status}</span>", unsafe_allow_html=True)
                
                with col4:
                    # Only super admin can change positions, and cannot change their own position
                    if user_is_super_admin and username.upper() != SUPER_ADMIN_USERNAME:
                        new_position = st.selectbox(
                            "Position",
                            options=USER_POSITIONS,
                            index=USER_POSITIONS.index(current_position) if current_position in USER_POSITIONS else 0,
                            key=f"position_{user['id']}",
                            label_visibility="collapsed"
                        )
                        
                        if new_position != current_position:
                            if st.button(f"Update", key=f"update_pos_{user['id']}", type="primary"):
                                success, msg = auth_manager.set_user_position(
                                    user['id'],
                                    new_position,
                                    current_user.get('username', 'Unknown')
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        if username.upper() == SUPER_ADMIN_USERNAME:
                            st.markdown("*Full Access - Protected*")
                        else:
                            st.markdown(f"*{current_position}*")
                
                st.markdown("<hr style='border-color: #334155; margin: 0.5rem 0;'>", unsafe_allow_html=True)
        
        # Position access reference
        st.markdown("---")
        st.markdown("### Position Access Reference")
        
        access_data = []
        for position, pages in POSITION_PAGE_ACCESS.items():
            access_data.append({
                'Position': position,
                'Accessible Pages': ', '.join(pages) if pages else 'None'
            })
        
        access_df = pd.DataFrame(access_data)
        st.dataframe(access_df, use_container_width=True, hide_index=True)
    else:
        st.info("No users found.")

with tab4:
    st.markdown("### Usage Statistics")
    
    # Filter options for statistics
    st.markdown("#### Filter Options")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Date range filter
        from datetime import timedelta
        date_options = {
            "Last 7 Days": 7,
            "Last 14 Days": 14,
            "Last 30 Days": 30,
            "Last 60 Days": 60,
            "Last 90 Days": 90,
            "All Time": 0
        }
        selected_range = st.selectbox(
            "Date Range",
            options=list(date_options.keys()),
            index=2,  # Default to Last 30 Days
            key="stats_date_range"
        )
    
    with filter_col2:
        # User filter
        all_users_list = auth_manager.get_all_users()
        stats_user_options = ["All Users"] + [u['username'] for u in all_users_list]
        stats_selected_user = st.selectbox(
            "Filter by User",
            options=stats_user_options,
            key="stats_user_filter"
        )
    
    with filter_col3:
        # Action type filter
        stats_action_filter = st.selectbox(
            "Filter by Action Type",
            options=["All Actions", "USER_LOGIN", "USER_LOGOUT", "PAGE_VISIT", "DATA_LOAD"],
            key="stats_action_filter"
        )
    
    st.markdown("---")
    
    # Get filtered data
    users = auth_manager.get_all_users()
    
    # Get logs based on user filter
    if stats_selected_user != "All Users":
        stats_user_id = next((u['id'] for u in all_users_list if u['username'] == stats_selected_user), None)
        all_logs = auth_manager.get_user_activity(user_id=stats_user_id, limit=5000)
    else:
        all_logs = auth_manager.get_user_activity(limit=5000)
    
    # Filter by date range
    if date_options[selected_range] > 0:
        cutoff_date = datetime.now() - timedelta(days=date_options[selected_range])
        all_logs = [log for log in all_logs if log['timestamp'] >= cutoff_date]
    
    # Filter by action type
    if stats_action_filter != "All Actions":
        all_logs = [log for log in all_logs if log['action'] == stats_action_filter]
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate stats from filtered logs
    total_activities = len(all_logs)
    logins_count = len([log for log in all_logs if log['action'] == 'USER_LOGIN'])
    page_visits = len([log for log in all_logs if log['action'] == 'PAGE_VISIT'])
    data_loads = len([log for log in all_logs if log['action'] == 'DATA_LOAD'])
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{len(users)}</h3>
            <p>Total Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{logins_count}</h3>
            <p>Logins ({selected_range})</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{page_visits}</h3>
            <p>Page Visits</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>{data_loads}</h3>
            <p>Data Loads</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show filter summary
    filter_summary = f"Showing data for: **{selected_range}**"
    if stats_selected_user != "All Users":
        filter_summary += f" | User: **{stats_selected_user}**"
    if stats_action_filter != "All Actions":
        filter_summary += f" | Action: **{stats_action_filter}**"
    filter_summary += f" | Total Activities: **{total_activities}**"
    st.info(filter_summary)
    
    st.markdown("---")
    
    # Activity over time chart
    if all_logs:
        import plotly.express as px
        
        logs_df = pd.DataFrame(all_logs)
        logs_df['date'] = pd.to_datetime(logs_df['timestamp']).dt.date
        
        daily_activity = logs_df.groupby('date').size().reset_index(name='activities')
        
        fig = px.line(
            daily_activity,
            x='date',
            y='activities',
            title='Daily Activity Trend',
            markers=True
        )
        fig.update_traces(line_color='#667eea', fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis_title="Date",
            yaxis_title="Number of Activities"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Most active users
        st.markdown("### Most Active Users")
        user_activity = logs_df['username'].value_counts().head(10)
        
        fig2 = px.bar(
            x=user_activity.values,
            y=user_activity.index,
            orientation='h',
            title='Top 10 Most Active Users',
            labels={'x': 'Number of Activities', 'y': 'Username'},
            color=user_activity.values,
            color_continuous_scale='Purples'
        )
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Most visited pages
        st.markdown("### Most Visited Pages")
        page_visits_df = logs_df[logs_df['action'] == 'PAGE_VISIT']
        if not page_visits_df.empty:
            page_counts = page_visits_df['page'].value_counts().head(10)
            
            fig3 = px.pie(
                values=page_counts.values,
                names=page_counts.index,
                title='Page Visit Distribution',
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig3, use_container_width=True)

with tab5:
    st.markdown("### Audit Trail")
    st.markdown("*Track all user actions for compliance and security monitoring*")
    
    # Audit trail filters
    st.markdown("#### Filter Options")
    audit_col1, audit_col2, audit_col3, audit_col4 = st.columns(4)
    
    with audit_col1:
        audit_date_options = {
            "Last 24 Hours": 1,
            "Last 7 Days": 7,
            "Last 14 Days": 14,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "All Time": 0
        }
        audit_date_range = st.selectbox(
            "Date Range",
            options=list(audit_date_options.keys()),
            index=2,
            key="audit_date_range"
        )
    
    with audit_col2:
        audit_action_types = st.multiselect(
            "Action Types",
            options=[
                "USER_LOGIN", "USER_LOGOUT", "LOGIN_FAILED", "USER_REGISTERED",
                "USER_DELETED", "USER_ACTIVATED", "USER_DEACTIVATED", 
                "POSITION_CHANGED", "ADMIN_GRANTED", "ADMIN_REVOKED",
                "PAGE_VISIT", "DATA_LOAD"
            ],
            default=[],
            key="audit_action_types",
            help="Leave empty for all actions"
        )
    
    with audit_col3:
        audit_all_users = auth_manager.get_all_users()
        audit_user_options = ["All Users"] + [u['username'] for u in audit_all_users]
        audit_selected_user = st.selectbox(
            "Filter by User",
            options=audit_user_options,
            key="audit_user_filter"
        )
    
    with audit_col4:
        audit_limit = st.selectbox(
            "Max Records",
            options=[100, 250, 500, 1000, 2500],
            index=2,
            key="audit_limit"
        )
    
    st.markdown("---")
    
    # Calculate date filters
    if audit_date_options[audit_date_range] > 0:
        audit_start_date = datetime.now() - timedelta(days=audit_date_options[audit_date_range])
    else:
        audit_start_date = None
    
    # Get audit trail
    audit_logs = auth_manager.get_audit_trail(
        limit=audit_limit,
        action_types=audit_action_types if audit_action_types else None,
        start_date=audit_start_date
    )
    
    # Filter by user if needed
    if audit_selected_user != "All Users":
        audit_logs = [log for log in audit_logs if log['username'] == audit_selected_user]
    
    if audit_logs:
        # Summary metrics
        audit_summary_col1, audit_summary_col2, audit_summary_col3, audit_summary_col4 = st.columns(4)
        
        login_attempts = len([l for l in audit_logs if l['action'] == 'USER_LOGIN'])
        failed_logins = len([l for l in audit_logs if l['action'] == 'LOGIN_FAILED'])
        admin_actions = len([l for l in audit_logs if l['action'] in ['USER_DELETED', 'USER_ACTIVATED', 'USER_DEACTIVATED', 'POSITION_CHANGED', 'ADMIN_GRANTED', 'ADMIN_REVOKED']])
        registrations = len([l for l in audit_logs if l['action'] == 'USER_REGISTERED'])
        
        with audit_summary_col1:
            st.markdown(f"""
            <div class='stat-card' style='border-left-color: #10b981;'>
                <h3 style='color: #10b981 !important;'>{login_attempts}</h3>
                <p>Successful Logins</p>
            </div>
            """, unsafe_allow_html=True)
        
        with audit_summary_col2:
            st.markdown(f"""
            <div class='stat-card' style='border-left-color: #ef4444;'>
                <h3 style='color: #ef4444 !important;'>{failed_logins}</h3>
                <p>Failed Login Attempts</p>
            </div>
            """, unsafe_allow_html=True)
        
        with audit_summary_col3:
            st.markdown(f"""
            <div class='stat-card' style='border-left-color: #f97316;'>
                <h3 style='color: #f97316 !important;'>{admin_actions}</h3>
                <p>Admin Actions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with audit_summary_col4:
            st.markdown(f"""
            <div class='stat-card' style='border-left-color: #a855f7;'>
                <h3 style='color: #a855f7 !important;'>{registrations}</h3>
                <p>New Registrations</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Convert to DataFrame
        audit_df = pd.DataFrame(audit_logs)
        audit_df['timestamp'] = pd.to_datetime(audit_df['timestamp'])
        audit_df = audit_df.sort_values('timestamp', ascending=False)
        
        # Color-code actions
        def get_action_color(action):
            colors = {
                'USER_LOGIN': '#10b981',
                'USER_LOGOUT': '#6b7280',
                'LOGIN_FAILED': '#ef4444',
                'USER_REGISTERED': '#3b82f6',
                'USER_DELETED': '#dc2626',
                'USER_ACTIVATED': '#10b981',
                'USER_DEACTIVATED': '#f97316',
                'POSITION_CHANGED': '#a855f7',
                'ADMIN_GRANTED': '#7c3aed',
                'ADMIN_REVOKED': '#dc2626',
                'PAGE_VISIT': '#64748b',
                'DATA_LOAD': '#64748b'
            }
            return colors.get(action, '#6b7280')
        
        # Display audit log table
        st.markdown("#### Audit Log Details")
        
        display_audit_df = audit_df[['timestamp', 'username', 'action', 'page', 'details', 'email', 'full_name']].copy()
        display_audit_df.columns = ['Timestamp', 'Username', 'Action', 'Page', 'Details', 'Email', 'Full Name']
        
        st.dataframe(
            display_audit_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm:ss"),
                "Action": st.column_config.TextColumn(width="medium"),
                "Details": st.column_config.TextColumn(width="large")
            }
        )
        
        # Download audit trail
        st.markdown("---")
        st.markdown("#### Export Audit Trail")
        
        export_col1, export_col2, export_col3 = st.columns([2, 2, 4])
        
        with export_col1:
            audit_csv = display_audit_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=audit_csv,
                file_name=f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with export_col2:
            # Generate audit report summary
            report_text = f"""AUDIT TRAIL REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date Range: {audit_date_range}
Total Records: {len(audit_logs)}

SUMMARY:
- Successful Logins: {login_attempts}
- Failed Login Attempts: {failed_logins}
- Admin Actions: {admin_actions}
- New Registrations: {registrations}

ACTIONS BREAKDOWN:
"""
            action_counts = audit_df['action'].value_counts()
            for action, count in action_counts.items():
                report_text += f"- {action}: {count}\n"
            
            st.download_button(
                label="Download Report",
                data=report_text,
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with export_col3:
            st.markdown("""
            <div style='color: #94a3b8; font-size: 0.85rem; padding: 0.5rem;'>
                <strong>Compliance Note:</strong> This audit trail is for internal compliance tracking. 
                Store exported data securely and in accordance with your organization's data retention policies.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No audit logs found for the selected criteria.")

# Sidebar
with st.sidebar:
    if current_user:
        role_badge = "Super Admin" if user_is_super_admin else "Admin"
        badge_color = "#7c3aed" if user_is_super_admin else "#dc2626"
        
        st.markdown(f"""
        <div style='text-align: center; padding: 0.5rem; background: linear-gradient(135deg, {badge_color}20 0%, {badge_color}40 100%); 
                    border-radius: 10px; margin-bottom: 1rem; border: 1px solid {badge_color}60;'>
            <p style='margin: 0; font-size: 0.85rem; color: {badge_color};'>{role_badge}</p>
            <p style='margin: 0; font-weight: 600; color: #e2e8f0;'>{current_user.get('username', 'Admin')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Home.py")
    
    st.markdown("---")
    st.caption(f"© 2025 {DEVELOPER_NAME}")

# Footer
footer_color = "#7c3aed" if user_is_super_admin else "#dc2626"
st.markdown(f"""
<div style='text-align: center; padding: 2rem; color: #6b7280; border-top: 2px solid {footer_color}; margin-top: 3rem;'>
    <p>{'Super Admin' if user_is_super_admin else 'Admin'} Dashboard | Activity Monitoring & User Management</p>
</div>
""", unsafe_allow_html=True)
