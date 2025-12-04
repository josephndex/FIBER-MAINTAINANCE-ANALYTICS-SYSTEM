import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import os
from dotenv import load_dotenv
from tqdm.auto import tqdm
import time
from typing import Union, Tuple, Optional
from datetime import datetime
import logging
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_database_credentials(db_config: int) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Get database credentials from environment variables, Streamlit secrets (cloud), or .env file (local).
    Priority: Environment Variables > Streamlit Secrets > .env file
    
    Args:
        db_config: Database configuration number (1-6)
        
    Returns:
        Tuple of (db_name, host, user, password)
    """
    db_name = None
    host = None
    user = None
    password = None
    
    # Try environment variables first (for Docker deployment)
    db_name = os.environ.get(f'DB_NAME_{db_config}')
    host = os.environ.get(f'DB_HOST_{db_config}')
    user = os.environ.get(f'DB_USER_{db_config}')
    password = os.environ.get(f'DB_PASSWORD_{db_config}')
    
    if db_name and host and user and password:
        logger.info(f"Using environment variables for database config {db_config}")
        return db_name, host, user, password
    
    # Try Streamlit secrets second (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and f'database_{db_config}' in st.secrets:
            secrets = st.secrets[f'database_{db_config}']
            db_name = secrets.get('DB_NAME', '')
            host = secrets.get('DB_HOST', '')
            user = secrets.get('DB_USER', '')
            password = secrets.get('DB_PASSWORD', '')
            
            # Check if credentials are actually set (not empty)
            if db_name and host and user and password:
                logger.info(f"Using Streamlit secrets for database config {db_config}")
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
        logger.info(f"Using .env file for database config {db_config}")
    
    return db_name, host, user, password


def get_db_engine(db_config: int = 1):
    """
    Get a database engine for direct queries.
    Used by NOC Entries and other pages that need direct DB access.
    
    Args:
        db_config: Database configuration number (1 or 2)
        
    Returns:
        SQLAlchemy engine or None if connection fails
    """
    try:
        db_name, host, user, password = get_database_credentials(db_config)
        
        if not all([db_name, host, user, password]):
            logger.error("Missing database credentials")
            return None
        
        connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}"
        engine = create_engine(connection_string, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        return None


class DataLoader:
    """
    Robust data loader with progress tracking and comprehensive error handling.
    Supports database configurations 1 and 2 only.
    """
    
    def __init__(self):
        self.engine = None
        self.current_db_config = None
        
    def _get_env_path(self) -> str:
        """Get the .env file path - uses local .env in the same directory."""
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '.env')
    
    def _get_table_name(self, db_config: int) -> str:
        """Get the appropriate table name based on database configuration."""
        # Only configs 1 and 2 are supported - both use engineered_tickets
        if db_config in [1, 2]:
            return "engineered_tickets"
        else:
            raise ValueError(f"Unsupported database configuration: {db_config}. Only 1 and 2 are supported.")
    
    def _create_engine(self, db_config: int) -> bool:
        """Create database engine with error handling."""
        # Validate db_config
        if db_config not in [1, 2]:
            logger.error(f"Invalid database configuration: {db_config}. Only 1 and 2 are supported.")
            return False
            
        try:
            # Get credentials from Streamlit secrets or .env file
            db_name, host, user, password = get_database_credentials(db_config)
            
            # Validate all required credentials
            missing_vars = []
            for var_name, var_value in [
                (f'DB_NAME_{db_config}', db_name),
                (f'DB_HOST_{db_config}', host),
                (f'DB_USER_{db_config}', user),
                (f'DB_PASSWORD_{db_config}', password)
            ]:
                if not var_value:
                    missing_vars.append(var_name)
            
            if missing_vars:
                logger.error(f"Missing database credentials: {', '.join(missing_vars)}")
                return False
            
            # Create engine with connection pooling
            engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}"
            self.engine = create_engine(
                engine_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            self.current_db_config = db_config
            logger.info(f"Database engine created for config {db_config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            return False
    
    def _test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def load_data_with_progress(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        db_config: int,
        chunk_size: Optional[int] = 1000,
        show_progress: bool = True,
        progress_container=None
    ) -> pd.DataFrame:
        """
        Load ticket data with progress tracking and comprehensive error handling.
        Shows progress in Streamlit UI when progress_container is provided.
        
        Args:
            start_date: Start date (datetime or string)
            end_date: End date (datetime or string)
            db_config: Database configuration (1 or 2 only)
                       1 = Remote server (NDERITU Laptop)
                       2 = Local server (localhost)
            chunk_size: Number of rows to fetch per chunk (default 1000)
            show_progress: Whether to show progress bar
            progress_container: Streamlit container for progress display
            
        Returns:
            pandas.DataFrame with ticket data
        """
        start_time = time.time()
        
        # Create Streamlit progress elements if container provided
        if progress_container is not None:
            status_text = progress_container.empty()
            progress_bar = progress_container.progress(0)
            details_text = progress_container.empty()
        else:
            status_text = None
            progress_bar = None
            details_text = None
        
        def update_ui(status: str, progress: float, details: str = ""):
            """Update Streamlit UI progress elements."""
            if status_text is not None:
                status_text.markdown(f"**{status}**")
            if progress_bar is not None:
                progress_bar.progress(min(progress, 1.0))
            if details_text is not None and details:
                details_text.caption(details)
            # Also print to terminal for debugging
            logger.info(f"{status} - {progress*100:.0f}% - {details}")
        
        update_ui("Initializing data load...", 0.05, 
                  f"Date range: {start_date} to {end_date}")
        
        # Step 1: Create database engine
        update_ui("Connecting to database...", 0.10, 
                  f"Database config: {db_config}")
        
        if not self._create_engine(db_config):
            if status_text:
                status_text.error("Failed to create database connection")
            return pd.DataFrame()
        
        # Step 2: Test connection
        update_ui("Testing connection...", 0.15, "Verifying database accessibility")
        
        if not self._test_connection():
            if status_text:
                status_text.error("Database connection test failed")
            return pd.DataFrame()
        
        # Step 3: Prepare parameters
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            table_name = self._get_table_name(db_config)
            if table_name == "engineered_tickets":
                 column = "ESCALATED_TIME"
            else:
                 column = "CREATED"
            
            update_ui("Connection established!", 0.20, 
                      f"Table: {table_name} | Column: {column}")
            
        except Exception as e:
            logger.error(f"Failed to prepare query parameters: {e}")
            if status_text:
                status_text.error(f"Failed to prepare query: {e}")
            return pd.DataFrame()
        
        # Step 4: Execute query
        try:
            query = text(f"""
                SELECT *
                FROM {table_name}
                WHERE {column} BETWEEN :start_date AND :end_date
            """)
            
            params = {"start_date": start_date, "end_date": end_date}
            
            update_ui("Counting records...", 0.25, "Preparing to fetch data")
            
            # First, get total count for progress tracking
            count_query = text(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE {column} BETWEEN :start_date AND :end_date
            """)
            
            with self.engine.connect() as conn:
                total_rows = conn.execute(count_query, params).scalar()
            
            update_ui(f"Found {total_rows:,} records", 0.30, 
                      f"Starting data fetch from {table_name}")
            
            if total_rows == 0:
                update_ui("No data found", 1.0, "No records in the specified date range")
                return pd.DataFrame()
            
            # Fetch data with progress tracking using chunks
            update_ui(f"Fetching {total_rows:,} rows...", 0.35, 
                      f"Loading in chunks of {chunk_size:,}")
            
            if chunk_size and total_rows > chunk_size:
                # Read in chunks for progress tracking
                df_chunks = pd.read_sql(
                    query, 
                    self.engine, 
                    params=params,
                    chunksize=chunk_size
                )
                
                chunks = []
                rows_loaded = 0
                
                for chunk in df_chunks:
                    chunks.append(chunk)
                    rows_loaded += len(chunk)
                    
                    # Calculate progress (35% to 90% is data loading)
                    load_progress = 0.35 + (rows_loaded / total_rows) * 0.55
                    speed = rows_loaded / (time.time() - start_time) if time.time() > start_time else 0
                    
                    update_ui(
                        f"Loading data: {rows_loaded:,} / {total_rows:,} rows",
                        load_progress,
                        f"Speed: {speed:,.0f} rows/sec | Progress: {(rows_loaded/total_rows)*100:.1f}%"
                    )
                
                df = pd.concat(chunks, ignore_index=True)
            else:
                # Fetch all at once for smaller datasets
                df = pd.read_sql(query, self.engine, params=params)
                update_ui(f"Loaded {len(df):,} rows", 0.90, "Data fetch complete")
            
            processing_time = time.time() - start_time
            
            # Step 5: Finalize and display summary
            update_ui("Processing complete!", 0.95, "Preparing data summary")
            
            if not df.empty:
                created_min = df[column].min()
                created_max = df[column].max()
                memory_mb = df.memory_usage(deep=True).sum() / 1024**2
                
                summary = (f"Loaded {len(df):,} rows, {len(df.columns)} columns | "
                          f"Time: {processing_time:.1f}s | Memory: {memory_mb:.1f} MB")
                
                update_ui("Data loaded successfully!", 1.0, summary)
                
                # Clear progress elements after a brief pause
                time.sleep(0.5)
                if status_text:
                    status_text.empty()
                if progress_bar:
                    progress_bar.empty()
                if details_text:
                    details_text.empty()
            
            return df
            
        except OperationalError as e:
            logger.error(f"Database operational error: {e}")
            if status_text:
                status_text.error(f"Database error: Check if server is running")
            return pd.DataFrame()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            if status_text:
                status_text.error(f"Database error: {e}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Unexpected error during data loading: {e}")
            if status_text:
                status_text.error(f"Error: {e}")
            return pd.DataFrame()
        
        finally:
            # Clean up
            if self.engine:
                self.engine.dispose()

# Convenience function for quick usage
def load_data(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    db_config: int = 2,
    chunk_size: Optional[int] = 1000,
    show_progress: bool = True,
    progress_container=None
) -> pd.DataFrame:
    """
    Convenience function to load data with progress tracking.
    
    Args:
        start_date: Start date (datetime or string)
        end_date: End date (datetime or string)
        db_config: Database configuration (1 or 2 only)
                   1 = Remote server (NDERITU Laptop)
                   2 = Local server (localhost) - DEFAULT
        chunk_size: Number of rows to fetch per chunk (default 1000)
        show_progress: Whether to show progress bar
        progress_container: Streamlit container for UI progress display
        
    Returns:
        pandas.DataFrame with ticket data
    """
    if db_config not in [1, 2]:
        raise ValueError(f"Invalid db_config: {db_config}. Only 1 (remote) and 2 (local) are supported.")
    
    loader = DataLoader()
    return loader.load_data_with_progress(
        start_date, end_date, db_config, chunk_size, show_progress, progress_container
    )
