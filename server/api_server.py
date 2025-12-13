"""
Fiber Maintenance Analytics System - API Server
This server handles all database operations and serves data to desktop clients.
Deploy this on your server - clients will connect to fetch data.
"""
import os
import sys
from pathlib import Path

# Set server directory as base
SERVER_DIR = Path(__file__).parent

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import json
import logging
import hashlib
import secrets

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from server's own .env file
env_file = SERVER_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
    logger.info(f"Loaded environment from: {env_file}")
else:
    # Fallback to parent directory
    load_dotenv(SERVER_DIR.parent / '.env')
    logger.info("Loaded environment from parent directory")

# ============================================================
# FASTAPI APP SETUP
# ============================================================
app = FastAPI(
    title="Fiber Maintenance Analytics API",
    description="REST API server for Fiber Maintenance Analytics desktop clients",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow desktop clients to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBasic()


# ============================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================
class DataRequest(BaseModel):
    """Request model for data queries"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD HH:MM:SS)")
    db_config: int = Field(default=1, description="Database config (1 or 2)")


class LoginRequest(BaseModel):
    """Request model for user login"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login"""
    success: bool
    token: str = None
    user_id: int = None
    username: str = None
    full_name: str = None
    email: str = None
    position: str = None
    is_admin: bool = False
    message: str = None


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    username: str
    email: str
    password: str
    full_name: str
    position: str = "NOC"


class DataResponse(BaseModel):
    """Response model for data queries"""
    success: bool
    row_count: int = 0
    columns: List[str] = []
    data: List[Dict[str, Any]] = []
    message: str = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    database: str
    timestamp: str


# ============================================================
# DATABASE CONNECTION
# ============================================================
def get_database_credentials(db_config: int):
    """Get database credentials from environment variables"""
    db_name = os.environ.get(f'DB_NAME_{db_config}')
    host = os.environ.get(f'DB_HOST_{db_config}')
    user = os.environ.get(f'DB_USER_{db_config}')
    password = os.environ.get(f'DB_PASSWORD_{db_config}')
    return db_name, host, user, password


def get_db_engine(db_config: int = 1):
    """Create database engine for queries"""
    db_name, host, user, password = get_database_credentials(db_config)
    
    if not all([db_name, host, user, password]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database credentials not configured"
        )
    
    try:
        connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}"
        engine = create_engine(
            connection_string,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=1800,
            echo=False
        )
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )


# In-memory token store (use Redis in production for scalability)
active_tokens: Dict[str, Dict[str, Any]] = {}


def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a token and return user info if valid"""
    if token in active_tokens:
        token_data = active_tokens[token]
        # Check if token has expired (24 hours)
        if datetime.now() - token_data['created_at'] < timedelta(hours=24):
            return token_data
        else:
            # Token expired, remove it
            del active_tokens[token]
    return None


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", tags=["General"])
async def root():
    """API root endpoint"""
    return {
        "message": "Fiber Maintenance Analytics API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Check API and database health"""
    try:
        engine = get_db_engine(1)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=datetime.now().isoformat()
    )


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Authenticate user and return access token.
    Token is required for all data endpoints.
    """
    try:
        engine = get_db_engine(1)
        
        with engine.connect() as conn:
            # Get user from database
            query = text("""
                SELECT id, username, email, password_hash, full_name, position, is_admin, is_active
                FROM app_users
                WHERE username = :username
            """)
            result = conn.execute(query, {"username": request.username})
            user = result.fetchone()
            
            if not user:
                return LoginResponse(success=False, message="Invalid username or password")
            
            user_dict = dict(user._mapping)
            
            # Check if user is active
            if not user_dict.get('is_active', True):
                return LoginResponse(success=False, message="Account is deactivated")
            
            # Verify password
            stored_hash = user_dict['password_hash']
            password_valid = False
            
            # Try bcrypt first (hashes start with $2)
            if stored_hash.startswith('$2'):
                try:
                    import bcrypt
                    password_valid = bcrypt.checkpw(
                        request.password.encode('utf-8'),
                        stored_hash.encode('utf-8')
                    )
                except ImportError:
                    pass
            
            # SHA-256 with salt format: salt$hash
            elif '$' in stored_hash:
                parts = stored_hash.split('$', 1)
                if len(parts) == 2:
                    salt, hash_value = parts
                    computed_hash = hashlib.sha256((request.password + salt).encode()).hexdigest()
                    password_valid = (computed_hash == hash_value)
            
            # Plain SHA-256 (no salt) - legacy format
            else:
                computed_hash = hashlib.sha256(request.password.encode()).hexdigest()
                password_valid = (computed_hash == stored_hash)
            
            if not password_valid:
                return LoginResponse(success=False, message="Invalid username or password")
            
            # Generate token
            token = generate_token()
            active_tokens[token] = {
                'user_id': user_dict['id'],
                'username': user_dict['username'],
                'email': user_dict['email'],
                'full_name': user_dict.get('full_name', ''),
                'position': user_dict.get('position', 'NOC'),
                'is_admin': user_dict.get('is_admin', False),
                'created_at': datetime.now()
            }
            
            # Update last login
            update_query = text("""
                UPDATE app_users SET last_login = NOW() WHERE id = :user_id
            """)
            conn.execute(update_query, {"user_id": user_dict['id']})
            conn.commit()
            
            logger.info(f"User {request.username} logged in successfully")
            
            return LoginResponse(
                success=True,
                token=token,
                user_id=user_dict['id'],
                username=user_dict['username'],
                full_name=user_dict.get('full_name', ''),
                email=user_dict.get('email', ''),
                position=user_dict.get('position', 'NOC'),
                is_admin=user_dict.get('is_admin', False),
                message="Login successful"
            )
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return LoginResponse(success=False, message=f"Login failed: {str(e)}")


@app.post("/auth/register", response_model=LoginResponse, tags=["Authentication"])
async def register(request: RegisterRequest):
    """Register a new user account"""
    try:
        engine = get_db_engine(1)
        
        # Hash password
        try:
            import bcrypt
            salt = bcrypt.gensalt(12)
            password_hash = bcrypt.hashpw(request.password.encode('utf-8'), salt).decode('utf-8')
        except ImportError:
            # Fallback to SHA-256
            import os
            salt = os.urandom(16).hex()
            hash_value = hashlib.sha256((request.password + salt).encode()).hexdigest()
            password_hash = f"{salt}${hash_value}"
        
        with engine.connect() as conn:
            # Check if username or email exists
            check_query = text("""
                SELECT id FROM app_users WHERE username = :username OR email = :email
            """)
            existing = conn.execute(check_query, {
                "username": request.username,
                "email": request.email
            }).fetchone()
            
            if existing:
                return LoginResponse(success=False, message="Username or email already exists")
            
            # Insert new user
            insert_query = text("""
                INSERT INTO app_users (username, email, password_hash, full_name, position, is_active, is_admin)
                VALUES (:username, :email, :password_hash, :full_name, :position, TRUE, FALSE)
            """)
            result = conn.execute(insert_query, {
                "username": request.username,
                "email": request.email,
                "password_hash": password_hash,
                "full_name": request.full_name,
                "position": request.position
            })
            conn.commit()
            
            user_id = result.lastrowid
            
            # Generate token
            token = generate_token()
            active_tokens[token] = {
                'user_id': user_id,
                'username': request.username,
                'email': request.email,
                'full_name': request.full_name,
                'position': request.position,
                'is_admin': False,
                'created_at': datetime.now()
            }
            
            logger.info(f"New user registered: {request.username}")
            
            return LoginResponse(
                success=True,
                token=token,
                user_id=user_id,
                username=request.username,
                full_name=request.full_name,
                email=request.email,
                position=request.position,
                is_admin=False,
                message="Registration successful"
            )
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return LoginResponse(success=False, message=f"Registration failed: {str(e)}")


@app.post("/auth/logout", tags=["Authentication"])
async def logout(token: str = Query(..., description="Access token")):
    """Logout and invalidate token"""
    if token in active_tokens:
        del active_tokens[token]
        return {"success": True, "message": "Logged out successfully"}
    return {"success": False, "message": "Invalid token"}


@app.get("/auth/verify", tags=["Authentication"])
async def verify_token_endpoint(token: str = Query(..., description="Access token")):
    """Verify if a token is valid"""
    user_data = verify_token(token)
    if user_data:
        return {"valid": True, "username": user_data['username']}
    return {"valid": False}


# ============================================================
# DATA ENDPOINTS
# ============================================================

@app.post("/data/tickets", response_model=DataResponse, tags=["Data"])
async def get_tickets(request: DataRequest, token: str = Query(..., description="Access token")):
    """
    Get ticket data for the specified date range.
    Requires valid authentication token.
    """
    # Verify token
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    try:
        engine = get_db_engine(request.db_config)
        
        start_date = pd.to_datetime(request.start_date)
        end_date = pd.to_datetime(request.end_date)
        
        query = text("""
            SELECT *
            FROM engineered_tickets
            WHERE ESCALATED_TIME BETWEEN :start_date AND :end_date
        """)
        
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={
                "start_date": start_date,
                "end_date": end_date
            })
        
        # Convert datetime columns to strings for JSON serialization
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].astype(str)
            elif df[col].dtype == 'timedelta64[ns]':
                df[col] = df[col].astype(str)
        
        # Convert to dict for JSON response
        data = df.to_dict(orient='records')
        
        logger.info(f"User {user_data['username']} fetched {len(df)} tickets")
        
        return DataResponse(
            success=True,
            row_count=len(df),
            columns=list(df.columns),
            data=data,
            message=f"Loaded {len(df)} records"
        )
        
    except Exception as e:
        logger.error(f"Data fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data: {str(e)}"
        )


@app.get("/data/columns", tags=["Data"])
async def get_columns(
    db_config: int = Query(default=1, description="Database config"),
    token: str = Query(..., description="Access token")
):
    """Get available columns in the tickets table"""
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    try:
        engine = get_db_engine(db_config)
        
        query = text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'engineered_tickets'
            ORDER BY ORDINAL_POSITION
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            columns = [row[0] for row in result]
        
        return {"columns": columns}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/summary", tags=["Data"])
async def get_data_summary(
    start_date: str = Query(..., description="Start date"),
    end_date: str = Query(..., description="End date"),
    db_config: int = Query(default=1),
    token: str = Query(..., description="Access token")
):
    """Get summary statistics for the date range"""
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    try:
        engine = get_db_engine(db_config)
        
        query = text("""
            SELECT 
                COUNT(*) as total_tickets,
                COUNT(DISTINCT ENGINEER1) as unique_engineers,
                COUNT(DISTINCT CLUSTER) as unique_clusters,
                AVG(TIMESTAMPDIFF(HOUR, ESCALATED_TIME, UPTIME)) as avg_resolution_hours,
                MIN(ESCALATED_TIME) as earliest_ticket,
                MAX(ESCALATED_TIME) as latest_ticket
            FROM engineered_tickets
            WHERE ESCALATED_TIME BETWEEN :start_date AND :end_date
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                "start_date": start_date,
                "end_date": end_date
            })
            row = result.fetchone()
            
            if row:
                return {
                    "total_tickets": row[0],
                    "unique_engineers": row[1],
                    "unique_clusters": row[2],
                    "avg_resolution_hours": float(row[3]) if row[3] else None,
                    "earliest_ticket": str(row[4]) if row[4] else None,
                    "latest_ticket": str(row[5]) if row[5] else None
                }
            
            return {"total_tickets": 0}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@app.get("/admin/users", tags=["Admin"])
async def get_users(token: str = Query(..., description="Access token")):
    """Get list of all users (admin only)"""
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    if not user_data.get('is_admin', False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        engine = get_db_engine(1)
        
        query = text("""
            SELECT id, username, email, full_name, position, is_active, is_admin, 
                   created_at, last_login
            FROM app_users
            ORDER BY created_at DESC
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            users = []
            for row in result:
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "full_name": row[3],
                    "position": row[4],
                    "is_active": row[5],
                    "is_admin": row[6],
                    "created_at": str(row[7]) if row[7] else None,
                    "last_login": str(row[8]) if row[8] else None
                })
        
        return {"users": users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/activity-logs", tags=["Admin"])
async def get_activity_logs(
    limit: int = Query(default=100, description="Max records to return"),
    token: str = Query(..., description="Access token")
):
    """Get activity logs (admin only)"""
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    if not user_data.get('is_admin', False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        engine = get_db_engine(1)
        
        query = text("""
            SELECT id, username, action, page, details, timestamp
            FROM activity_logs
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"limit": limit})
            logs = []
            for row in result:
                logs.append({
                    "id": row[0],
                    "username": row[1],
                    "action": row[2],
                    "page": row[3],
                    "details": row[4],
                    "timestamp": str(row[5]) if row[5] else None
                })
        
        return {"logs": logs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("API_PORT", 8000))
    host = os.environ.get("API_HOST", "0.0.0.0")
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║     FIBER MAINTENANCE ANALYTICS API SERVER                   ║
    ║                                                              ║
    ║     Running on: http://{host}:{port}                           ║
    ║     API Docs:   http://{host}:{port}/docs                      ║
    ║                                                              ║
    ║     Desktop clients connect to this server for data          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host=host, port=port, log_level="info")
