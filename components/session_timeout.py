"""
Session Timeout - Simple Inactivity Detection
- After 3 minutes of inactivity: Show warning
- After 5 minutes of inactivity: Auto logout
"""
import streamlit as st
from datetime import datetime

# Settings
INACTIVITY_WARNING_SECONDS = 180  # 3 minutes
INACTIVITY_LOGOUT_SECONDS = 300   # 5 minutes


def init_activity_tracking():
    """Start tracking activity - call after successful login"""
    st.session_state.last_activity = datetime.now()
    st.session_state.show_timeout_warning = False


def update_activity():
    """Update last activity time"""
    st.session_state.last_activity = datetime.now()
    st.session_state.show_timeout_warning = False


def check_session_timeout():
    """Check if session timed out. Returns True if should logout."""
    if 'last_activity' not in st.session_state:
        return False
    
    inactivity = (datetime.now() - st.session_state.last_activity).total_seconds()
    
    if inactivity >= INACTIVITY_LOGOUT_SECONDS:
        return True
    
    if inactivity >= INACTIVITY_WARNING_SECONDS:
        st.session_state.show_timeout_warning = True
    
    return False


def render_timeout_warning():
    """Show warning if inactive"""
    if not st.session_state.get('show_timeout_warning', False):
        return
    
    if 'last_activity' not in st.session_state:
        return
        
    inactivity = (datetime.now() - st.session_state.last_activity).total_seconds()
    remaining = max(0, int(INACTIVITY_LOGOUT_SECONDS - inactivity))
    
    if remaining > 0:
        st.warning(f"⏰ Inactive - session expires in {remaining}s. Click anywhere to stay logged in.")


def render_stay_active_button():
    """Button to reset activity"""
    if st.session_state.get('show_timeout_warning', False):
        if st.button("🔄 I'm Still Here", use_container_width=True):
            update_activity()
            st.rerun()
