"""
Authentication Module for Fiber Maintenance Analytics System
Handles user authentication, registration, and activity logging
Supports multiple concurrent users with isolated sessions
"""
import streamlit as st
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

# Try to import bcrypt for secure password hashing
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("bcrypt not available, falling back to SHA-256 hashing")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base = declarative_base()

# Super Admin - The first user (NDERITU) is the super admin
# Only super admin can promote/demote admins and deactivate users
SUPER_ADMIN_USERNAME = "NDERITU"

# Position definitions and their page access
# NOTE: All users now have access to ALL pages except Admin (11_Admin.py)
# Admin page is restricted to admins only
POSITIONS = {
    "MANAGEMENT": {
        "display_name": "Management",
        "description": "Full access to all analytics pages including Admin",
        "allowed_pages": [
            "00_Introduction.py", "1_Home.py", "2_KPI_Dashboard.py", "3_Cluster_Analysis.py",
            "4_Engineer_Performance.py", "5_Regional_Analysis.py", "6_Service_Analysis.py",
            "7_Trends.py", "8_SLA_Analysis.py", "9_Challenges.py", "10_Recurring_Issues.py",
            "12_NOC Entries.py", "13_CEO_Dashboard.py", "14_Reports.py", "15_Predictions.py",
            "16_Ticket_Search.py", "18_Comparison.py", "19_Advanced_Predictions.py",
            "20_Dispatcher_Performance.py", "21_Suggestions.py"
        ]
    },
    "ENGINEER": {
        "display_name": "Engineer",
        "description": "Full access to all analytics pages (except Admin)",
        "allowed_pages": [
            "00_Introduction.py", "1_Home.py", "2_KPI_Dashboard.py", "3_Cluster_Analysis.py",
            "4_Engineer_Performance.py", "5_Regional_Analysis.py", "6_Service_Analysis.py",
            "7_Trends.py", "8_SLA_Analysis.py", "9_Challenges.py", "10_Recurring_Issues.py",
            "12_NOC Entries.py", "13_CEO_Dashboard.py", "14_Reports.py", "15_Predictions.py",
            "16_Ticket_Search.py", "18_Comparison.py", "19_Advanced_Predictions.py",
            "20_Dispatcher_Performance.py", "21_Suggestions.py"
        ]
    },
    "NOC": {
        "display_name": "NOC (Network Operations Center)",
        "description": "Full access to all analytics pages (except Admin)",
        "allowed_pages": [
            "00_Introduction.py", "1_Home.py", "2_KPI_Dashboard.py", "3_Cluster_Analysis.py",
            "4_Engineer_Performance.py", "5_Regional_Analysis.py", "6_Service_Analysis.py",
            "7_Trends.py", "8_SLA_Analysis.py", "9_Challenges.py", "10_Recurring_Issues.py",
            "12_NOC Entries.py", "13_CEO_Dashboard.py", "14_Reports.py", "15_Predictions.py",
            "16_Ticket_Search.py", "18_Comparison.py", "19_Advanced_Predictions.py",
            "20_Dispatcher_Performance.py", "21_Suggestions.py"
        ]
    }
}

# Pages that require specific positions
ALL_DASHBOARD_PAGES = [
    "00_Introduction.py", "1_Home.py", "2_KPI_Dashboard.py", "3_Cluster_Analysis.py",
    "4_Engineer_Performance.py", "5_Regional_Analysis.py", "6_Service_Analysis.py",
    "7_Trends.py", "8_SLA_Analysis.py", "9_Challenges.py", "10_Recurring_Issues.py",
    "11_Admin.py", "12_NOC Entries.py", "13_CEO_Dashboard.py", "14_Reports.py",
    "15_Predictions.py", "16_Ticket_Search.py", "18_Comparison.py", "19_Advanced_Predictions.py",
    "20_Dispatcher_Performance.py", "21_Suggestions.py"
]

# Convenience list of position names
USER_POSITIONS = list(POSITIONS.keys())  # ["MANAGEMENT", "ENGINEER", "NOC"]

# Position page access mapping for display in admin
POSITION_PAGE_ACCESS = {pos: data["allowed_pages"] for pos, data in POSITIONS.items()}


def get_auth_credentials() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Get database credentials for authentication from Streamlit secrets or .env file.
    Uses database config 1 for authentication.
    
    Returns:
        Tuple of (db_name, host, user, password)
    """
    db_config = 1
    db_name = None
    host = None
    user = None
    password = None
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and f'database_{db_config}' in st.secrets:
            secrets = st.secrets[f'database_{db_config}']
            db_name = secrets.get('DB_NAME', '')
            host = secrets.get('DB_HOST', '')
            user = secrets.get('DB_USER', '')
            password = secrets.get('DB_PASSWORD', '')
            
            if db_name and host and user and password:
                logger.info("Using Streamlit secrets for authentication")
                return db_name, host, user, password
    except Exception as e:
        logger.debug(f"Streamlit secrets not available: {e}")
    
    # Fall back to .env file (for local development)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        db_name = os.getenv(f'DB_NAME_{db_config}')
        host = os.getenv(f'DB_HOST_{db_config}')
        user = os.getenv(f'DB_USER_{db_config}')
        password = os.getenv(f'DB_PASSWORD_{db_config}')
        logger.info("Using .env file for authentication")
    
    return db_name, host, user, password


class AuthManager:
    """
    Authentication manager for user login, registration, and activity logging.
    Uses database config 1 to store user credentials and activity logs.
    """
    
    def __init__(self):
        self.engine = None
        self._create_engine()
        self._create_tables()
    
    def _get_env_path(self) -> str:
        """Get the .env file path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '.env')
    
    def _create_engine(self) -> bool:
        """Create database engine using config 1."""
        try:
            # Get credentials from Streamlit secrets or .env file
            db_name, host, user, password = get_auth_credentials()
            
            # Validate all required credentials
            missing_vars = []
            for var_name, var_value in [
                ('DB_NAME_1', db_name),
                ('DB_HOST_1', host),
                ('DB_USER_1', user),
                ('DB_PASSWORD_1', password)
            ]:
                if not var_value:
                    missing_vars.append(var_name)
            
            if missing_vars:
                logger.error(f"Missing database credentials: {', '.join(missing_vars)}")
                return False
            
            # Create engine
            engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}"
            self.engine = create_engine(
                engine_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            logger.info("Auth database engine created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create auth database engine: {e}")
            return False
    
    def _create_tables(self):
        """Create user and activity log tables if they don't exist."""
        if not self.engine:
            logger.error("Cannot create tables: No database engine")
            return
        
        try:
            # Create users table with position column
            create_users_table = text("""
                CREATE TABLE IF NOT EXISTS app_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    position VARCHAR(50) DEFAULT 'NOC',
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    last_page VARCHAR(255),
                    session_data TEXT
                )
            """)
            
            # Create activity log table
            create_logs_table = text("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    username VARCHAR(100),
                    action VARCHAR(100) NOT NULL,
                    page VARCHAR(255),
                    details TEXT,
                    ip_address VARCHAR(50),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL
                )
            """)
            
            with self.engine.connect() as conn:
                conn.execute(create_users_table)
                conn.execute(create_logs_table)
                conn.commit()
            
            # Add position column if it doesn't exist (for existing databases)
            try:
                # Check if position column exists
                check_column = text("""
                    SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'app_users' 
                    AND column_name = 'position'
                """)
                with self.engine.connect() as conn:
                    result = conn.execute(check_column)
                    column_exists = result.scalar() > 0
                
                if not column_exists:
                    add_position_column = text("""
                        ALTER TABLE app_users 
                        ADD COLUMN position VARCHAR(50) DEFAULT 'NOC'
                    """)
                    with self.engine.connect() as conn:
                        conn.execute(add_position_column)
                        conn.commit()
                    logger.info("Added position column to app_users table")
            except Exception as e:
                logger.warning(f"Could not add position column: {e}")
            
            logger.info("Auth tables created/verified")
            
        except Exception as e:
            logger.error(f"Failed to create auth tables: {e}")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt (preferred) or SHA-256 (fallback).
        bcrypt is more secure and includes salt automatically.
        """
        if BCRYPT_AVAILABLE:
            # Use bcrypt for secure hashing with automatic salt
            # Note: Some bcrypt libraries use gensalt(rounds=12), others use gensalt(12)
            try:
                salt = bcrypt.gensalt(12)  # Try without keyword argument first
            except TypeError:
                try:
                    salt = bcrypt.gensalt(rounds=12)  # Try with keyword argument
                except TypeError:
                    salt = bcrypt.gensalt()  # Fall back to default
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            # Fallback to SHA-256 with a simple salt
            salt = os.urandom(16).hex()
            hash_value = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"{salt}${hash_value}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        Verify a password against a stored hash.
        Handles both bcrypt and legacy SHA-256 hashes.
        """
        if BCRYPT_AVAILABLE and stored_hash.startswith('$2'):
            # bcrypt hash
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except Exception:
                return False
        elif '$' in stored_hash and not stored_hash.startswith('$2'):
            # Legacy SHA-256 with salt format: salt$hash
            try:
                salt, hash_value = stored_hash.split('$', 1)
                computed = hashlib.sha256((password + salt).encode()).hexdigest()
                return computed == hash_value
            except Exception:
                return False
        else:
            # Very old format: plain SHA-256 (for backward compatibility)
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "", position: str = "NOC") -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: User's chosen username
            email: User's email address
            password: User's password
            full_name: User's full name
            position: User's position (MANAGEMENT, ENGINEER, NOC)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.engine:
            return False, "Database connection not available"
        
        # Validate position
        if position.upper() not in POSITIONS:
            position = "NOC"  # Default to NOC if invalid
        else:
            position = position.upper()
        
        # Check if this is the super admin (NDERITU)
        is_super_admin_user = username.strip().upper() == SUPER_ADMIN_USERNAME
        
        # Super admin automatically gets MANAGEMENT position and admin rights
        if is_super_admin_user:
            position = "MANAGEMENT"
            is_admin = True
        else:
            is_admin = False
        
        try:
            password_hash = self.hash_password(password)
            
            insert_query = text("""
                INSERT INTO app_users (username, email, password_hash, full_name, position, is_admin, created_at)
                VALUES (:username, :email, :password_hash, :full_name, :position, :is_admin, :created_at)
            """)
            
            with self.engine.connect() as conn:
                conn.execute(insert_query, {
                    "username": username.strip(),
                    "email": email.strip().lower(),
                    "password_hash": password_hash,
                    "full_name": full_name.strip(),
                    "position": position,
                    "is_admin": is_admin,
                    "created_at": datetime.now()
                })
                conn.commit()
            
            # Log the registration
            position_display = POSITIONS[position]["display_name"]
            self.log_activity(None, username, "USER_REGISTERED", "registration", 
                            f"New user registered: {email} as {position_display}")
            
            logger.info(f"User registered: {username} with position {position}")
            
            # Special message for super admin
            if is_super_admin_user:
                return True, f"Super Admin account created successfully! You have full access to all pages including Admin. Please log in."
            
            return True, f"Registration successful as {position_display}! You can now log in."
            
        except SQLAlchemyError as e:
            error_msg = str(e)
            if "Duplicate entry" in error_msg:
                if "username" in error_msg:
                    return False, "Username already exists. Please choose a different username."
                elif "email" in error_msg:
                    return False, "Email already registered. Please use a different email or log in."
            logger.error(f"Registration failed: {e}")
            return False, f"Registration failed: {error_msg}"
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"An error occurred: {str(e)}"
    
    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Authenticate a user with proper password verification.
        Supports multiple concurrent users with isolated sessions.
        
        Returns:
            Tuple of (success: bool, user_data: Optional[Dict], message: str)
        """
        if not self.engine:
            return False, None, "Database connection not available"
        
        try:
            # First, get the user's stored hash
            query = text("""
                SELECT id, username, email, full_name, position, is_active, is_admin, 
                       last_page, session_data, password_hash
                FROM app_users
                WHERE (username = :identifier OR email = :identifier)
                AND is_active = TRUE
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "identifier": username_or_email.strip()
                })
                user = result.fetchone()
            
            if not user:
                return False, None, "Invalid username/email or password"
            
            # Verify password using the proper method
            stored_hash = user[9]  # password_hash is at index 9
            if not self.verify_password(password, stored_hash):
                # Log failed attempt
                self.log_activity(None, username_or_email, "LOGIN_FAILED", "login", 
                                "Invalid password attempt")
                return False, None, "Invalid username/email or password"
            
            # Password verified, create user data dict
            user_data = {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "full_name": user[3],
                "position": user[4] or "NOC",
                "is_active": user[5],
                "is_admin": user[6],
                "last_page": user[7],
                "session_data": user[8],
                # Generate unique session ID for this user's session
                "session_id": str(uuid.uuid4()),
                "login_time": datetime.now().isoformat()
            }
            
            # Auto-upgrade super admin to admin if not already
            if user_data["username"].upper() == SUPER_ADMIN_USERNAME and not user_data["is_admin"]:
                upgrade_query = text("""
                    UPDATE app_users
                    SET is_admin = TRUE, position = 'MANAGEMENT'
                    WHERE id = :user_id
                """)
                with self.engine.connect() as conn:
                    conn.execute(upgrade_query, {"user_id": user_data["id"]})
                    conn.commit()
                user_data["is_admin"] = True
                user_data["position"] = "MANAGEMENT"
                logger.info(f"Auto-upgraded super admin {user_data['username']} to admin")
            
            # Update last login
            update_query = text("""
                UPDATE app_users
                SET last_login = :last_login
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(update_query, {
                    "last_login": datetime.now(),
                    "user_id": user_data["id"]
                })
                conn.commit()
            
            # Log the login
            position_display = POSITIONS.get(user_data["position"], {}).get("display_name", user_data["position"])
            self.log_activity(user_data["id"], user_data["username"], "USER_LOGIN", "login", 
                            f"User logged in as {position_display}")
            
            logger.info(f"User authenticated: {user_data['username']} as {position_display}")
            return True, user_data, f"Login successful! You are logged in as {position_display}"
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, f"An error occurred: {str(e)}"
    
    def log_activity(self, user_id: Optional[int], username: str, action: str, page: str = "", details: str = ""):
        """Log user activity to the database."""
        if not self.engine:
            return
        
        try:
            insert_query = text("""
                INSERT INTO activity_logs (user_id, username, action, page, details, timestamp)
                VALUES (:user_id, :username, :action, :page, :details, :timestamp)
            """)
            
            with self.engine.connect() as conn:
                conn.execute(insert_query, {
                    "user_id": user_id,
                    "username": username,
                    "action": action,
                    "page": page,
                    "details": details,
                    "timestamp": datetime.now()
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def save_user_session(self, user_id: int, page: str, session_data: str = ""):
        """Save user's current page and session data."""
        if not self.engine:
            return
        
        try:
            update_query = text("""
                UPDATE app_users
                SET last_page = :page, session_data = :session_data
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(update_query, {
                    "page": page,
                    "session_data": session_data,
                    "user_id": user_id
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def get_user_activity(self, user_id: Optional[int] = None, limit: int = 100) -> list:
        """Get activity logs, optionally filtered by user."""
        if not self.engine:
            return []
        
        try:
            if user_id:
                query = text("""
                    SELECT id, username, action, page, details, timestamp
                    FROM activity_logs
                    WHERE user_id = :user_id
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """)
                params = {"user_id": user_id, "limit": limit}
            else:
                query = text("""
                    SELECT id, username, action, page, details, timestamp
                    FROM activity_logs
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """)
                params = {"limit": limit}
            
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                logs = result.fetchall()
            
            return [
                {
                    "id": log[0],
                    "username": log[1],
                    "action": log[2],
                    "page": log[3],
                    "details": log[4],
                    "timestamp": log[5]
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Failed to get activity logs: {e}")
            return []
    
    def get_all_users(self) -> list:
        """Get all users (admin function)."""
        if not self.engine:
            return []
        
        try:
            query = text("""
                SELECT id, username, email, full_name, position, is_active, is_admin, created_at, last_login
                FROM app_users
                ORDER BY created_at DESC
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query)
                users = result.fetchall()
            
            return [
                {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "full_name": user[3],
                    "position": user[4] or "NOC",
                    "is_active": user[5],
                    "is_admin": user[6],
                    "created_at": user[7],
                    "last_login": user[8],
                    "is_super_admin": user[1].upper() == SUPER_ADMIN_USERNAME
                }
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
    def set_user_admin_status(self, user_id: int, is_admin: bool, by_user: str) -> Tuple[bool, str]:
        """Set a user's admin status. Only super admin can do this."""
        if not self.engine:
            return False, "Database connection not available"
        
        try:
            # Check if target user is super admin (cannot change super admin status)
            check_query = text("SELECT username FROM app_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if user and user[0].upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot modify super admin's status"
            
            update_query = text("""
                UPDATE app_users
                SET is_admin = :is_admin
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(update_query, {
                    "is_admin": is_admin,
                    "user_id": user_id
                })
                conn.commit()
            
            action = "ADMIN_GRANTED" if is_admin else "ADMIN_REVOKED"
            self.log_activity(None, by_user, action, "admin", f"User ID {user_id} admin status set to {is_admin}")
            
            return True, f"User admin status {'granted' if is_admin else 'revoked'} successfully"
            
        except Exception as e:
            logger.error(f"Failed to update admin status: {e}")
            return False, f"Error: {str(e)}"
    
    def set_user_active_status(self, user_id: int, is_active: bool, by_user: str) -> Tuple[bool, str]:
        """Activate or deactivate a user. Only super admin can do this."""
        if not self.engine:
            return False, "Database connection not available"
        
        try:
            # Check if target user is super admin (cannot deactivate super admin)
            check_query = text("SELECT username FROM app_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if user and user[0].upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot deactivate super admin"
            
            update_query = text("""
                UPDATE app_users
                SET is_active = :is_active
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(update_query, {
                    "is_active": is_active,
                    "user_id": user_id
                })
                conn.commit()
            
            action = "USER_ACTIVATED" if is_active else "USER_DEACTIVATED"
            self.log_activity(None, by_user, action, "admin", f"User ID {user_id} active status set to {is_active}")
            
            return True, f"User {'activated' if is_active else 'deactivated'} successfully"
            
        except Exception as e:
            logger.error(f"Failed to update user status: {e}")
            return False, f"Error: {str(e)}"
    
    def set_user_position(self, user_id: int, new_position: str, by_user: str) -> Tuple[bool, str]:
        """
        Change a user's position. Only super admin can do this.
        
        Args:
            user_id: ID of the user to modify
            new_position: New position (MANAGEMENT, ENGINEER, NOC)
            by_user: Username of the admin making the change
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.engine:
            return False, "Database connection not available"
        
        # Validate new position
        new_position = new_position.upper()
        if new_position not in POSITIONS:
            return False, f"Invalid position. Must be one of: {', '.join(POSITIONS.keys())}"
        
        try:
            # Check if target user is super admin (cannot change super admin position)
            check_query = text("SELECT username, position FROM app_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if not user:
                return False, "User not found"
            
            if user[0].upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot modify super admin's position"
            
            old_position = user[1] or "NOC"
            
            update_query = text("""
                UPDATE app_users
                SET position = :position
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(update_query, {
                    "position": new_position,
                    "user_id": user_id
                })
                conn.commit()
            
            old_display = POSITIONS.get(old_position, {}).get("display_name", old_position)
            new_display = POSITIONS[new_position]["display_name"]
            
            self.log_activity(None, by_user, "POSITION_CHANGED", "admin", 
                            f"User {user[0]} position changed from {old_display} to {new_display}")
            
            logger.info(f"User {user[0]} position changed from {old_position} to {new_position} by {by_user}")
            return True, f"Position changed from {old_display} to {new_display} successfully"
            
        except Exception as e:
            logger.error(f"Failed to update user position: {e}")
            return False, f"Error: {str(e)}"
    
    def get_position_stats(self) -> Dict[str, int]:
        """Get count of users by position."""
        if not self.engine:
            return {}
        
        try:
            query = text("""
                SELECT position, COUNT(*) as count
                FROM app_users
                WHERE is_active = TRUE
                GROUP BY position
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query)
                stats = result.fetchall()
            
            return {row[0] or "NOC": row[1] for row in stats}
            
        except Exception as e:
            logger.error(f"Failed to get position stats: {e}")
            return {}
    
    def delete_user(self, user_id: int, by_user: str) -> Tuple[bool, str]:
        """
        Permanently delete a user account. Only super admin can do this.
        
        Args:
            user_id: ID of the user to delete
            by_user: Username of the admin performing the deletion
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.engine:
            return False, "Database connection not available"
        
        try:
            # Get user info before deletion
            check_query = text("SELECT username, email FROM app_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if not user:
                return False, "User not found"
            
            username = user[0]
            email = user[1]
            
            # Cannot delete super admin
            if username.upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot delete the Super Admin account"
            
            # Delete user's activity logs first (foreign key constraint)
            delete_logs_query = text("""
                DELETE FROM activity_logs
                WHERE user_id = :user_id
            """)
            
            # Delete the user
            delete_user_query = text("""
                DELETE FROM app_users
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(delete_logs_query, {"user_id": user_id})
                conn.execute(delete_user_query, {"user_id": user_id})
                conn.commit()
            
            # Log the deletion (without user_id since user is deleted)
            self.log_activity(None, by_user, "USER_DELETED", "admin", 
                            f"Deleted user: {username} ({email})")
            
            logger.info(f"User {username} deleted by {by_user}")
            return True, f"User '{username}' has been permanently deleted"
            
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False, f"Error: {str(e)}"
    
    def get_audit_trail(self, limit: int = 500, action_types: List[str] = None, 
                        start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Get comprehensive audit trail for compliance tracking.
        
        Args:
            limit: Maximum number of records to return
            action_types: Filter by specific action types (e.g., ['USER_LOGIN', 'USER_DELETED'])
            start_date: Filter logs after this date
            end_date: Filter logs before this date
            
        Returns:
            List of audit log dictionaries
        """
        if not self.engine:
            return []
        
        try:
            query_parts = ["""
                SELECT al.id, al.username, al.action, al.page, al.details, 
                       al.timestamp, al.ip_address, au.email, au.full_name
                FROM activity_logs al
                LEFT JOIN app_users au ON al.user_id = au.id
                WHERE 1=1
            """]
            params = {"limit": limit}
            
            if action_types:
                query_parts.append("AND al.action IN :action_types")
                params["action_types"] = tuple(action_types)
            
            if start_date:
                query_parts.append("AND al.timestamp >= :start_date")
                params["start_date"] = start_date
            
            if end_date:
                query_parts.append("AND al.timestamp <= :end_date")
                params["end_date"] = end_date
            
            query_parts.append("ORDER BY al.timestamp DESC LIMIT :limit")
            
            query = text(" ".join(query_parts))
            
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                logs = result.fetchall()
            
            return [
                {
                    "id": log[0],
                    "username": log[1],
                    "action": log[2],
                    "page": log[3],
                    "details": log[4],
                    "timestamp": log[5],
                    "ip_address": log[6],
                    "email": log[7],
                    "full_name": log[8]
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []


# Singleton instance
_auth_manager = None


def get_auth_manager() -> AuthManager:
    """Get the singleton AuthManager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# Session timeout in minutes (default 30)
def get_session_timeout() -> int:
    """Get session timeout from secrets or use default."""
    try:
        if hasattr(st, 'secrets') and 'app' in st.secrets:
            return st.secrets['app'].get('session_timeout_minutes', 30)
    except:
        pass
    return 30


def check_session_timeout() -> bool:
    """
    Check if the current session has timed out.
    Returns True if session is still valid, False if timed out.
    """
    if 'last_activity' not in st.session_state:
        return True  # No activity recorded, session is valid
    
    last_activity = st.session_state.get('last_activity')
    if last_activity:
        try:
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity)
            
            timeout_minutes = get_session_timeout()
            if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
                return False  # Session timed out
        except:
            pass
    
    return True  # Session still valid


def update_activity():
    """Update the last activity timestamp."""
    st.session_state['last_activity'] = datetime.now()


def check_authentication() -> bool:
    """
    Check if user is authenticated and session is still valid.
    Handles session timeout for security.
    Returns True if logged in and session is valid.
    """
    if not st.session_state.get('authenticated', False):
        return False
    
    # Check session timeout
    if not check_session_timeout():
        # Session timed out - log out user
        user = st.session_state.get('user')
        if user:
            auth = get_auth_manager()
            auth.log_activity(
                user.get('id'), 
                user.get('username', 'Unknown'), 
                "SESSION_TIMEOUT", 
                "security", 
                "Session timed out due to inactivity"
            )
        
        # Clear session
        for key in ['authenticated', 'user', 'last_activity']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.warning(f"⏰ Your session has timed out due to inactivity. Please log in again.")
        return False
    
    # Update activity timestamp
    update_activity()
    return True


def get_current_user() -> Optional[Dict]:
    """Get the current logged-in user data."""
    if check_authentication():
        return st.session_state.get('user', None)
    return None


def require_authentication():
    """
    Decorator/function to require authentication.
    Redirects to login page if not authenticated.
    """
    if not check_authentication():
        st.warning("Please log in to access this page.")
        # Use experimental_set_query_params to signal login needed
        try:
            st.switch_page("pages/0_Login.py")
        except:
            st.rerun()
        st.stop()


def logout():
    """Log out the current user and clear all session data."""
    auth = get_auth_manager()
    user = get_current_user()
    
    if user:
        auth.log_activity(user.get('id'), user.get('username', 'Unknown'), "USER_LOGOUT", "logout", "User logged out")
    
    # Clear all user-specific session state for clean logout
    keys_to_clear = [
        'authenticated', 'user', 'df', 'data_loaded',
        'session_id', 'login_time', 'last_activity',
        'is_new_user', 'show_welcome', 'welcome_shown'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state['authenticated'] = False


def log_page_visit(page_name: str):
    """Log when a user visits a page."""
    auth = get_auth_manager()
    user = get_current_user()
    
    if user:
        user_id = user.get('id')
        username = user.get('username', 'Unknown')
        auth.log_activity(
            user_id,
            username,
            "PAGE_VISIT",
            page_name,
            f"Visited {page_name}"
        )
        # Save the last visited page
        if user_id:
            auth.save_user_session(user_id, page_name)


def is_super_admin(user: Optional[Dict] = None) -> bool:
    """Check if the current user or provided user is the super admin."""
    if user is None:
        user = get_current_user()
    if user:
        return user.get('username', '').upper() == SUPER_ADMIN_USERNAME
    return False


def is_admin(user: Optional[Dict] = None) -> bool:
    """Check if the current user or provided user is an admin."""
    if user is None:
        user = get_current_user()
    if user:
        return user.get('is_admin', False) or is_super_admin(user)
    return False


def require_admin():
    """Require admin access. Redirects non-admins."""
    require_authentication()
    user = get_current_user()
    if not is_admin(user):
        st.error("Access Denied. Admin privileges required.")
        st.stop()


def get_user_position(user: Optional[Dict] = None) -> str:
    """Get the position of the current user or provided user."""
    if user is None:
        user = get_current_user()
    if user:
        return user.get('position', 'NOC').upper()
    return 'NOC'


def get_position_display_name(position: str) -> str:
    """Get the display name for a position."""
    return POSITIONS.get(position.upper(), {}).get("display_name", position)


def get_allowed_pages(user: Optional[Dict] = None) -> List[str]:
    """
    Get the list of pages a user is allowed to access.
    
    Args:
        user: User dict (optional, defaults to current user)
        
    Returns:
        List of page filenames the user can access
    """
    if user is None:
        user = get_current_user()
    
    if not user:
        return []
    
    # Super admin can access everything
    if is_super_admin(user):
        return ALL_DASHBOARD_PAGES
    
    position = get_user_position(user)
    
    # Get allowed pages for position
    allowed = POSITIONS.get(position, {}).get("allowed_pages", [])
    
    # Admins can also access admin page
    if is_admin(user):
        if "11_Admin.py" not in allowed:
            allowed = allowed + ["11_Admin.py"]
    
    return allowed


def can_access_page(page_name: str, user: Optional[Dict] = None) -> bool:
    """
    Check if a user can access a specific page.
    
    Args:
        page_name: Name of the page file (e.g., "1_Home.py")
        user: User dict (optional, defaults to current user)
        
    Returns:
        True if user can access the page
    """
    if user is None:
        user = get_current_user()
    
    if not user:
        return False
    
    # Super admin can access everything
    if is_super_admin(user):
        return True
    
    allowed_pages = get_allowed_pages(user)
    return page_name in allowed_pages


def require_page_access(page_name: str):
    """
    Require access to a specific page.
    Shows access denied message and stops execution if user cannot access.
    
    Args:
        page_name: Name of the page file (e.g., "1_Home.py")
    """
    require_authentication()
    user = get_current_user()
    
    if not can_access_page(page_name, user):
        position = get_user_position(user)
        position_display = get_position_display_name(position)
        
        st.error(f"Access Denied")
        st.warning(f"""
        Your current position ({position_display}) does not have access to this page.
        
        **Allowed pages for {position_display}:**
        """)
        
        allowed = get_allowed_pages(user)
        for page in allowed:
            page_display = page.replace("_", " ").replace(".py", "")
            st.markdown(f"- {page_display}")
        
        st.info("Contact the administrator if you need access to additional pages.")
        st.stop()
