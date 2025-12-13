"""
Login Page - User Authentication
Provides login and registration functionality
"""
import streamlit as st
import sys
import re
import time
from datetime import datetime
sys.path.insert(0, '..')

from config import APP_TITLE, DEVELOPER_NAME
from auth import get_auth_manager, check_authentication, logout, log_page_visit, POSITIONS, get_position_display_name, SUPER_ADMIN_USERNAME

# Custom CSS for STUNNING login page
st.markdown("""
<style>
    /* Animated background with gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1a0d2e, #0f172a, #1e1033);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(249, 115, 22, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(102, 126, 234, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Hide sidebar on login page */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Login container with glassmorphism */
    .login-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 
            0 25px 60px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(168, 85, 247, 0.2);
        max-width: 480px;
        margin: 0 auto;
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #f97316, #a855f7, #667eea, #a855f7, #f97316);
        background-size: 200% 100%;
        animation: borderGlow 3s linear infinite;
    }
    
    @keyframes borderGlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* Header styling - STUNNING */
    .login-header {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 50%, #667eea 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 50px rgba(249, 115, 22, 0.3),
            0 10px 30px rgba(168, 85, 247, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .login-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
        );
        animation: headerShine 4s ease-in-out infinite;
    }
    
    @keyframes headerShine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .login-header::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
        opacity: 0.5;
    }
    
    .login-header h1, .login-header p {
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    .fireside-logo {
        font-size: 3.5rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 
            2px 2px 4px rgba(0,0,0,0.3),
            0 0 40px rgba(255,255,255,0.2);
        margin-bottom: 0.5rem;
        animation: logoPulse 2s ease-in-out infinite;
    }
    
    @keyframes logoPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .fireside-tagline {
        font-size: 1.1rem;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 2px;
    }
    
    /* Form styling */
    .stTextInput > label, .stSelectbox > label {
        color: #a78bfa !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem !important;
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 2px solid rgba(168, 85, 247, 0.2) !important;
        color: #f1f5f9 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #f97316 !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2), 0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Button styling - STUNNING */
    .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.85rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 10px 30px rgba(249, 115, 22, 0.3),
            0 5px 15px rgba(168, 85, 247, 0.2) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 
            0 20px 50px rgba(249, 115, 22, 0.4),
            0 10px 30px rgba(168, 85, 247, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Tab styling - STUNNING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 16px;
        padding: 0.5rem;
        border: 1px solid rgba(168, 85, 247, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #a78bfa !important;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        color: #f97316 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f97316 0%, #a855f7 100%) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
    }
    
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    /* Success/Error messages - STUNNING */
    .success-msg {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 1.25rem;
        color: #10b981;
        text-align: center;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.15);
        animation: successPop 0.5s ease-out;
    }
    
    @keyframes successPop {
        0% { transform: scale(0.9); opacity: 0; }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .error-msg {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 1rem;
        color: #ef4444;
        text-align: center;
    }
    
    /* Welcome animation */
    .welcome-container {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #dc2626 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 40px rgba(249, 115, 22, 0.4);
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 15px 40px rgba(249, 115, 22, 0.4); }
        50% { box-shadow: 0 20px 50px rgba(249, 115, 22, 0.6); }
    }
    
    .welcome-title {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .welcome-subtitle {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .welcome-user {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 600;
        animation: fadeInUp 1s ease-out;
    }
    
    .crafted-by {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.2);
        animation: fadeInUp 1.2s ease-out;
    }
    
    .crafted-by p {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .crafted-by .joseph {
        color: white !important;
        font-size: 1.1rem;
        font-weight: 600;
        background: linear-gradient(90deg, #fbbf24, #f59e0b, #fbbf24);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Footer */
    .login-footer {
        text-align: center;
        color: #6b7280;
        margin-top: 2rem;
        font-size: 0.85rem;
    }
    
    .login-footer .signature {
        background: linear-gradient(90deg, #f97316, #ea580c, #f97316);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_staff_email(email: str) -> tuple[bool, str]:
    """Validate that email belongs to staff (must end with .africa or .org)."""
    email = email.strip().lower()
    
    # Check basic format first
    if not validate_email(email):
        return False, "Please enter a valid email address"
    
    # Check if email ends with allowed domains
    allowed_endings = ['.africa', '.org']
    
    for ending in allowed_endings:
        if email.endswith(ending):
            return True, ""
    
    return False, "This system is only available to staff. Please use your official staff email ending with .africa or .org"


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


def render_login_form():
    """Render the login form."""
    st.markdown("### Sign In to Your Account")
    
    with st.form("login_form", clear_on_submit=False):
        username_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if not username_email or not password:
                st.error("Please fill in all fields")
                return
            
            auth = get_auth_manager()
            success, user_data, message = auth.authenticate_user(username_email, password)
            
            if success and user_data:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user_data
                st.session_state['show_welcome'] = True
                st.session_state['last_activity'] = datetime.now()  # Start activity tracking
                
                # Get position display name
                position = user_data.get('position', 'NOC')
                position_display = get_position_display_name(position)
                
                # Show welcome message with position
                user_name = user_data.get('full_name', user_data.get('username', 'User'))
                st.markdown(f"""
                <div class='welcome-container'>
                    <p class='welcome-title'>Welcome to FIRESIDE</p>
                    <p class='welcome-subtitle'>Fiber Maintenance Analytics</p>
                    <p class='welcome-user'>{user_name}</p>
                    <p style='color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem;'>
                        Logged in as <strong style='color: #fbbf24;'>{position_display}</strong>
                    </p>
                    <div class='crafted-by'>
                        <p>Crafted with passion by</p>
                        <p class='joseph'>Joseph Nderitu</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Check if this is a new user (first login - no last_page recorded)
                last_page = user_data.get('last_page')
                is_first_login = last_page is None or last_page == ''
                
                time.sleep(2.5)
                try:
                    if is_first_login:
                        # New user - show introduction page
                        st.session_state['is_new_user'] = True
                        st.switch_page("pages/00_Introduction.py")
                    elif last_page and last_page not in ['login', 'registration', '0_Login.py', '00_Introduction.py']:
                        try:
                            st.switch_page(f"pages/{last_page}")
                        except:
                            st.switch_page("pages/1_Home.py")
                    else:
                        st.switch_page("pages/1_Home.py")
                except Exception as e:
                    # Fallback - just rerun and let user navigate
                    st.rerun()
            else:
                st.error(f"{message}")


def render_registration_form():
    """Render the registration form."""
    st.markdown("### Create New Account")
    
    with st.form("registration_form", clear_on_submit=True):
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="reg_fullname"
        )
        
        username = st.text_input(
            "Username",
            placeholder="Choose a unique username",
            key="reg_username"
        )
        
        email = st.text_input(
            "Email (Staff Only)",
            placeholder="Enter your staff email ending with .africa or .org",
            key="reg_email",
            help="This system is only available to staff. Your email must end with .africa or .org"
        )
        
        # Show email requirement notice
        st.markdown("""
        <div style='background: #1e293b; padding: 0.75rem 1rem; border-radius: 8px; border-left: 3px solid #f97316; margin-bottom: 1rem;'>
            <p style='margin: 0; color: #f97316; font-size: 0.85rem;'>
                <strong>Staff Email Required:</strong> Only emails ending with <code>.africa</code> or <code>.org</code> are accepted.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if this will be the super admin
        is_super_admin_registration = username.strip().upper() == SUPER_ADMIN_USERNAME if username else False
        
        # Position selection - Super admin gets MANAGEMENT automatically
        if is_super_admin_registration:
            st.markdown("**Position**")
            st.success(f"Username '{SUPER_ADMIN_USERNAME}' is the **Super Admin**. You will automatically be assigned **MANAGEMENT** position with full admin access.")
            position = "MANAGEMENT"
        else:
            st.markdown("**Select Your Position**")
            position_options = {
                "NOC": "NOC (Network Operations Center) - Full Analytics Access",
                "ENGINEER": "Engineer - Full Analytics Access",
                "MANAGEMENT": "Management - Full Access including Admin"
            }
            position = st.selectbox(
                "Position",
                options=list(position_options.keys()),
                format_func=lambda x: position_options[x],
                key="reg_position",
                help="Select your role in the organization. All positions have full analytics access."
            )
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password",
                key="reg_password"
            )
        with col2:
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm password",
                key="reg_confirm"
            )
        
        # Show position access info
        if position and not is_super_admin_registration:
            position_info = POSITIONS.get(position, {})
            allowed_pages = position_info.get("allowed_pages", [])
            st.info(f"**{position_info.get('description', '')}**\n\nYou will have access to: {', '.join([p.replace('_', ' ').replace('.py', '') for p in allowed_pages])}")
        elif is_super_admin_registration:
            st.warning("**Super Admin** has full access to ALL pages including Admin Dashboard.")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            # Validate inputs
            if not all([full_name, username, email, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            # Validate staff email (must end with .africa or .org)
            valid_email, email_error = validate_staff_email(email)
            if not valid_email:
                st.error(email_error)
                return
            
            valid_password, password_error = validate_password(password)
            if not valid_password:
                st.error(password_error)
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(username) < 3:
                st.error("Username must be at least 3 characters long")
                return
            
            # Register user with position
            auth = get_auth_manager()
            success, message = auth.register_user(username, email, password, full_name, position)
            
            if success:
                st.session_state['is_new_user'] = True  # Flag for showing introduction
                st.success(f"{message}")
                st.info("Switch to the Login tab to sign in")
            else:
                st.error(f"{message}")


# Main page content
if check_authentication():
    # User is already logged in
    user = st.session_state.get('user', {})
    user_name = user.get('full_name', user.get('username', 'User'))
    position = user.get('position', 'NOC')
    position_display = get_position_display_name(position)
    
    st.markdown(f"""
    <div class='welcome-container'>
        <p class='welcome-title'>Welcome to FIRESIDE</p>
        <p class='welcome-subtitle'>Fiber Maintenance Analytics</p>
        <p class='welcome-user'>{user_name}</p>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem;'>
            Logged in as <strong style='color: #fbbf24;'>{position_display}</strong>
        </p>
        <div class='crafted-by'>
            <p>Crafted with passion by</p>
            <p class='joseph'>Joseph Nderitu</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1.5rem; border-radius: 15px; border: 1px solid #475569;'>
            <p style='color: #e2e8f0; margin-bottom: 1rem;'>
                <strong>Username:</strong> {user.get('username', 'N/A')}<br>
                <strong>Email:</strong> {user.get('email', 'N/A')}<br>
                <strong>Name:</strong> {user.get('full_name', 'N/A')}<br>
                <strong>Position:</strong> <span style='color: #fbbf24;'>{position_display}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Go to Dashboard", use_container_width=True):
                try:
                    st.switch_page("pages/1_Home.py")
                except:
                    st.rerun()
        
        with col_b:
            if st.button("Logout", use_container_width=True, type="secondary"):
                logout()
                st.rerun()

else:
    # Show login/registration forms
    st.markdown("""
    <div class='login-header'>
        <p class='fireside-logo'>FIRESIDE</p>
        <p class='fireside-tagline'>Fiber Maintenance Analytics Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Sign In", "Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_registration_form()
    
    # Help section
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 1rem;'>
        <p><strong>Need help?</strong></p>
        <p>Contact the administrator if you're having trouble logging in.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class='login-footer'>
    <p>© 2025 <span class='signature'>Joseph Nderitu</span> | All rights reserved</p>
    <p>Your data is protected with secure authentication</p>
</div>
""", unsafe_allow_html=True)
