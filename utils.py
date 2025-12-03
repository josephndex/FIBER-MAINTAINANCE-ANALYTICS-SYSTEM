"""
Utility functions for Fiber Maintenance Analytics System
Contains all core calculations, data processing, and analysis functions
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from scipy import stats
import streamlit as st
import os

from config import (
    EXCLUDED_ENGINEERS, DISPATCHER_MAPPING, CLUSTER_MAPPING,
    ALARM_ROOT_CAUSES, ALARM_CAUSE_KEYWORD, SLA_THRESHOLDS,
    PERFORMANCE_GRADES, SLA_TARGET_HOURS
)

# Import local data_loader
from data_loader import load_data


# ==================== DATA LOADING ====================

def load_data_from_db(start_date: str, end_date: str, db_config: int = 2) -> pd.DataFrame:
    """
    Load data from database using the local data_loader module.
    Falls back to empty dataframe if database connection fails.
    Shows progress indicators during loading in the Streamlit UI.
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD HH:MM:SS)
        db_config: Database configuration (1 = Remote, 2 = Local)
    
    Returns:
        DataFrame with loaded data
    """
    # Validate db_config
    if db_config not in [1, 2]:
        st.error(f"Invalid database configuration: {db_config}. Only 1 (Remote) and 2 (Local) are supported.")
        return pd.DataFrame()
    
    # Create a progress container for loading feedback
    progress_container = st.container()
    
    with progress_container:
        try:
            db_name = "Remote Server" if db_config == 1 else "Local Server"
            
            # Use local data_loader with Streamlit progress container
            df = load_data(
                start_date=start_date,
                end_date=end_date,
                db_config=db_config,
                chunk_size=1000,  # Load in chunks for progress tracking
                show_progress=True,
                progress_container=progress_container
            )
            
            if df is not None and not df.empty:
                return df
            else:
                st.warning("No data returned from database")
                return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            import traceback
            st.code(traceback.format_exc())
            return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_and_prepare_data(start_date: str, end_date: str, db_config: int = 2) -> pd.DataFrame:
    """Load and prepare data with caching for performance."""
    with st.spinner("Loading and preparing data..."):
        df = load_data_from_db(start_date, end_date, db_config)
        if not df.empty:
            with st.spinner("Processing and transforming data..."):
                df = prepare_dataframe(df)
    return df


def prepare_dataframe(df: pd.DataFrame, show_progress: bool = True) -> pd.DataFrame:
    """
    Prepare and clean the dataframe for analysis.
    Applies all necessary transformations with optional progress display.
    """
    df = df.copy()
    
    # Create progress indicators if showing progress
    if show_progress:
        prep_status = st.empty()
        prep_progress = st.progress(0)
        prep_status.info("Processing data: Converting datetime columns...")
    
    # Ensure datetime columns
    if 'ESCALATED_TIME' in df.columns:
        df['ESCALATED_TIME'] = pd.to_datetime(df['ESCALATED_TIME'], errors='coerce')
    if 'UPTIME' in df.columns:
        df['UPTIME'] = pd.to_datetime(df['UPTIME'], errors='coerce')
    
    if show_progress:
        prep_progress.progress(20)
        prep_status.info("Processing data: Calculating durations...")
    
    # Calculate DURATION if not present or recalculate
    if 'ESCALATED_TIME' in df.columns and 'UPTIME' in df.columns:
        df['DURATION'] = (df['UPTIME'] - df['ESCALATED_TIME']).dt.total_seconds() / 3600
    
    # Ensure DURATION is numeric
    df['DURATION'] = pd.to_numeric(df.get('DURATION', pd.Series(dtype=float)), errors='coerce')
    
    if show_progress:
        prep_progress.progress(40)
        prep_status.info("Processing data: Adding temporal columns...")
    
    # Add temporal columns
    if 'ESCALATED_TIME' in df.columns:
        df['YEAR_MONTH'] = df['ESCALATED_TIME'].dt.to_period('M')
        df['MONTH_NAME'] = df['ESCALATED_TIME'].dt.strftime('%B')
        df['WEEK'] = df['ESCALATED_TIME'].dt.isocalendar().week
        df['DAY_OF_WEEK'] = df['ESCALATED_TIME'].dt.day_name()
        df['HOUR'] = df['ESCALATED_TIME'].dt.hour
        df['DATE'] = df['ESCALATED_TIME'].dt.date
    
    if show_progress:
        prep_progress.progress(60)
        prep_status.info("Processing data: Applying cluster and dispatcher mappings...")
    
    # Apply cluster mapping
    if 'CLUSTER' in df.columns:
        df['CLUSTER'] = df['CLUSTER'].replace(CLUSTER_MAPPING)
    
    # Standardize dispatcher names
    if 'DISPATCHER' in df.columns:
        df['DISPATCHER'] = df['DISPATCHER'].replace(DISPATCHER_MAPPING)
    
    if show_progress:
        prep_progress.progress(80)
        prep_status.info("Processing data: Cleaning engineer data and detecting alarms...")
    
    # Clean engineer columns - replace excluded names with NaN
    engineer_cols = ["ENGINEER1", "ENGINEER2", "ENGINEER3"]
    existing_cols = [c for c in engineer_cols if c in df.columns]
    if existing_cols:
        df[existing_cols] = df[existing_cols].replace(EXCLUDED_ENGINEERS, np.nan)
    
    # Add alarm detection flags
    df['IS_ALARM'] = False
    if 'CAUSE' in df.columns:
        df['IS_ALARM'] = df['CAUSE'].astype(str).str.upper().str.contains(ALARM_CAUSE_KEYWORD, na=False)
    if 'ROOT_CAUSE' in df.columns:
        df['IS_ALARM'] = df['IS_ALARM'] | df['ROOT_CAUSE'].isin(ALARM_ROOT_CAUSES)
    
    # Add alarm category for visualization
    df['ALARM_CATEGORY'] = df['IS_ALARM'].map({True: 'ALARM', False: 'NON-ALARM'})
    
    if show_progress:
        prep_progress.progress(100)
        prep_status.success(f"Data processing complete! {len(df):,} records ready.")
        import time
        time.sleep(0.3)  # Brief pause to show completion
        prep_status.empty()
        prep_progress.empty()
    
    return df


def is_alarm_ticket(row) -> bool:
    """Check if a single row/ticket is an alarm ticket."""
    if 'IS_ALARM' in row.index:
        return bool(row['IS_ALARM'])
    
    # Fallback check using CAUSE and ROOT_CAUSE
    is_alarm = False
    if 'CAUSE' in row.index and pd.notna(row['CAUSE']):
        is_alarm = ALARM_CAUSE_KEYWORD.upper() in str(row['CAUSE']).upper()
    if 'ROOT_CAUSE' in row.index and pd.notna(row['ROOT_CAUSE']):
        is_alarm = is_alarm or (row['ROOT_CAUSE'] in ALARM_ROOT_CAUSES)
    return is_alarm


def filter_non_alarm_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out alarm tickets from the dataset."""
    if 'IS_ALARM' in df.columns:
        return df[~df['IS_ALARM']].copy()
    else:
        # Fallback: filter based on CAUSE column
        mask = ~df['CAUSE'].astype(str).str.upper().str.contains(ALARM_CAUSE_KEYWORD, na=False)
        return df[mask].copy()


def filter_alarm_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only alarm tickets."""
    if 'IS_ALARM' in df.columns:
        return df[df['IS_ALARM']].copy()
    else:
        mask = df['CAUSE'].astype(str).str.upper().str.contains(ALARM_CAUSE_KEYWORD, na=False)
        return df[mask].copy()


# ==================== KPI CALCULATIONS ====================

def calculate_comprehensive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all KPI metrics from the dataframe.
    This is the master KPI calculation function.
    """
    df = df.copy()
    
    # Basic volume metrics
    total_tickets = len(df)
    alarm_tickets = df['IS_ALARM'].sum() if 'IS_ALARM' in df.columns else 0
    non_alarm_tickets = total_tickets - alarm_tickets
    alarm_percentage = (alarm_tickets / total_tickets * 100) if total_tickets > 0 else 0
    
    # Date range
    date_range = "N/A"
    days_in_period = 0
    if 'ESCALATED_TIME' in df.columns and not df['ESCALATED_TIME'].isna().all():
        start_date = df['ESCALATED_TIME'].min()
        end_date = df['ESCALATED_TIME'].max()
        date_range = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
        days_in_period = (end_date - start_date).days + 1
    
    avg_tickets_per_day = total_tickets / days_in_period if days_in_period > 0 else 0
    
    # Duration metrics
    avg_duration = df['DURATION'].mean() if 'DURATION' in df.columns else 0
    median_duration = df['DURATION'].median() if 'DURATION' in df.columns else 0
    min_duration = df['DURATION'].min() if 'DURATION' in df.columns else 0
    max_duration = df['DURATION'].max() if 'DURATION' in df.columns else 0
    std_duration = df['DURATION'].std() if 'DURATION' in df.columns else 0
    total_downtime = df['DURATION'].sum() if 'DURATION' in df.columns else 0
    
    # Alarm-specific MTTR
    alarm_avg_duration = 0
    non_alarm_avg_duration = 0
    if 'IS_ALARM' in df.columns and 'DURATION' in df.columns:
        alarm_df = df[df['IS_ALARM']]
        non_alarm_df = df[~df['IS_ALARM']]
        if len(alarm_df) > 0:
            alarm_avg_duration = alarm_df['DURATION'].mean()
        if len(non_alarm_df) > 0:
            non_alarm_avg_duration = non_alarm_df['DURATION'].mean()
    
    # SLA metrics
    breached_tickets = 0
    sla_compliance = 100.0
    total_breach_hours = 0.0
    
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['EXTERNAL_BREACHED'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.strip().str.upper()
        breached_tickets = len(df_temp[df_temp['EXTERNAL_BREACHED'].isin(['YES', 'TRUE', '1', 'Y'])])
        sla_compliance = ((total_tickets - breached_tickets) / total_tickets * 100) if total_tickets > 0 else 100.0
        
        if 'EXTERNAL_BREACHED_HOURS' in df.columns:
            breach_df = df_temp[df_temp['EXTERNAL_BREACHED'].isin(['YES', 'TRUE', '1', 'Y'])]
            total_breach_hours = pd.to_numeric(breach_df['EXTERNAL_BREACHED_HOURS'], errors='coerce').sum()
    
    # Calculate grades
    sla_grade = get_sla_grade(sla_compliance)
    performance_grade = get_performance_grade(avg_duration)
    
    # Coverage metrics
    active_clusters = df['CLUSTER'].nunique() if 'CLUSTER' in df.columns else 0
    active_regions = df['REGION'].nunique() if 'REGION' in df.columns else 0
    service_types = df['SERVICE'].nunique() if 'SERVICE' in df.columns else 0
    
    # Team metrics
    engineer_cols = [c for c in ['ENGINEER1', 'ENGINEER2', 'ENGINEER3'] if c in df.columns]
    active_engineers = 0
    if engineer_cols:
        all_engineers = pd.concat([df[col].dropna() for col in engineer_cols])
        active_engineers = all_engineers.nunique()
    
    active_dispatchers = df['DISPATCHER'].nunique() if 'DISPATCHER' in df.columns else 0
    
    # Trend analysis
    trend_direction, trend_slope, trend_r_squared = calculate_trend(df)
    
    return {
        # Volume metrics
        'total_tickets': total_tickets,
        'alarm_tickets': alarm_tickets,
        'non_alarm_tickets': non_alarm_tickets,
        'alarm_percentage': alarm_percentage,
        'avg_tickets_per_day': avg_tickets_per_day,
        'days_in_period': days_in_period,
        
        # Date range
        'date_range': date_range,
        
        # Duration metrics
        'avg_duration': avg_duration,
        'median_duration': median_duration,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'std_duration': std_duration,
        'total_downtime': total_downtime,
        'alarm_avg_duration': alarm_avg_duration,
        'non_alarm_avg_duration': non_alarm_avg_duration,
        
        # SLA metrics
        'sla_compliance': sla_compliance,
        'breached_tickets': breached_tickets,
        'total_breach_hours': total_breach_hours,
        'sla_grade': sla_grade,
        
        # Performance
        'performance_grade': performance_grade,
        
        # Coverage
        'active_clusters': active_clusters,
        'active_regions': active_regions,
        'service_types': service_types,
        
        # Team
        'active_engineers': active_engineers,
        'active_dispatchers': active_dispatchers,
        
        # Trend
        'trend_direction': trend_direction,
        'trend_slope': trend_slope,
        'trend_r_squared': trend_r_squared,
        
        # Metadata
        'generated_at': datetime.now().isoformat()
    }


def calculate_trend(df: pd.DataFrame) -> Tuple[str, float, float]:
    """Calculate trend direction from daily ticket counts."""
    trend_direction = "STABLE"
    trend_slope = 0.0
    trend_r_squared = 0.0
    
    if len(df) > 1 and 'ESCALATED_TIME' in df.columns:
        daily_counts = df.groupby(df['ESCALATED_TIME'].dt.date).size().reset_index(name='count')
        if len(daily_counts) > 1:
            x_numeric = np.arange(len(daily_counts))
            y_values = daily_counts['count'].values
            try:
                result = stats.linregress(x_numeric, y_values)
                # Access result tuple elements
                slope_val = result[0]
                r_val = result[2]
                trend_slope = slope_val if isinstance(slope_val, (int, float)) else 0.0
                r_value = r_val if isinstance(r_val, (int, float)) else 0.0
                trend_r_squared = r_value ** 2
                
                if trend_slope > 0.1:
                    trend_direction = "INCREASING"
                elif trend_slope < -0.1:
                    trend_direction = "DECREASING"
            except Exception:
                pass
    
    return trend_direction, trend_slope, trend_r_squared


# ==================== CLUSTER PERFORMANCE ====================

def calculate_cluster_performance(df: pd.DataFrame, exclude_alarms: bool = True) -> pd.DataFrame:
    """
    Calculate cluster performance metrics.
    Uses the formula: Lower MTTR + Fewer Tickets = Better Performance
    """
    if exclude_alarms:
        df = filter_non_alarm_data(df)
    
    df = df.dropna(subset=['CLUSTER'])
    df = df[df['CLUSTER'].astype(str).str.upper() != 'NONE']
    
    if len(df) == 0:
        return pd.DataFrame()
    
    cluster_perf = df.groupby('CLUSTER').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean'),
        Median_MTTR=('DURATION', 'median'),
        Total_Downtime=('DURATION', 'sum'),
        Min_Duration=('DURATION', 'min'),
        Max_Duration=('DURATION', 'max'),
        Std_Duration=('DURATION', 'std')
    ).reset_index()
    
    # Calculate SLA if available
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['BREACHED_NUMERIC'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = df_temp.groupby('CLUSTER').agg(
            SLA_Breached=('BREACHED_NUMERIC', 'sum')
        ).reset_index()
        cluster_perf = cluster_perf.merge(sla_df, on='CLUSTER', how='left')
        cluster_perf['SLA_Breached'] = cluster_perf['SLA_Breached'].fillna(0).astype(int)
        cluster_perf['SLA_Compliant'] = cluster_perf['Total_Tickets'] - cluster_perf['SLA_Breached']
        cluster_perf['SLA_Compliance'] = (cluster_perf['SLA_Compliant'] / cluster_perf['Total_Tickets'] * 100)
    else:
        cluster_perf['SLA_Breached'] = 0
        cluster_perf['SLA_Compliant'] = cluster_perf['Total_Tickets']
        cluster_perf['SLA_Compliance'] = 100.0
    
    # Calculate performance score
    # Lower tickets + Lower MTTR = Higher score
    max_tickets = cluster_perf['Total_Tickets'].max()
    max_mttr = cluster_perf['Avg_MTTR_Hours'].max()
    
    # Normalize and invert (so lower values become higher scores)
    cluster_perf['Ticket_Score'] = (max_tickets - cluster_perf['Total_Tickets'] + 1) / max_tickets * 50
    cluster_perf['MTTR_Score'] = (max_mttr - cluster_perf['Avg_MTTR_Hours'] + 1) / max_mttr * 50
    cluster_perf['Performance_Score'] = cluster_perf['Ticket_Score'] + cluster_perf['MTTR_Score']
    
    # Assign grades
    cluster_perf['Grade'] = cluster_perf['Performance_Score'].apply(get_cluster_grade)
    
    # Sort by performance score (highest first)
    cluster_perf = cluster_perf.sort_values('Performance_Score', ascending=False).reset_index(drop=True)
    cluster_perf['Rank'] = range(1, len(cluster_perf) + 1)
    
    return cluster_perf


def get_cluster_grade(score: float) -> str:
    """Assign a grade based on performance score."""
    if score >= 80:
        return "A+"
    elif score >= 70:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


# ==================== ENGINEER PERFORMANCE ====================

def calculate_engineer_performance(df: pd.DataFrame, exclude_alarms: bool = True) -> pd.DataFrame:
    """
    Calculate engineer performance metrics.
    Combines data from ENGINEER1, ENGINEER2, ENGINEER3 columns.
    """
    if exclude_alarms:
        df = filter_non_alarm_data(df)
    
    engineer_cols = ['ENGINEER1', 'ENGINEER2', 'ENGINEER3']
    existing_cols = [c for c in engineer_cols if c in df.columns]
    
    if not existing_cols:
        return pd.DataFrame()
    
    # Melt engineer columns into one
    engineer_data = []
    for col in existing_cols:
        temp_df = df[df[col].notna()].copy()
        temp_df['ENGINEER'] = temp_df[col]
        engineer_data.append(temp_df)
    
    if not engineer_data:
        return pd.DataFrame()
    
    engineer_df = pd.concat(engineer_data, ignore_index=True)
    engineer_df = engineer_df[engineer_df['ENGINEER'].str.strip().str.upper() != 'NONE']
    
    # Calculate metrics
    perf_df = engineer_df.groupby('ENGINEER').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean'),
        Median_MTTR=('DURATION', 'median'),
        Total_Hours=('DURATION', 'sum'),
        Min_Duration=('DURATION', 'min'),
        Max_Duration=('DURATION', 'max')
    ).reset_index()
    
    # Rename ENGINEER to Engineer for display
    perf_df = perf_df.rename(columns={'ENGINEER': 'Engineer'})
    
    # Calculate SLA metrics if available
    if 'EXTERNAL_BREACHED' in engineer_df.columns:
        engineer_df['BREACHED_NUMERIC'] = engineer_df['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = engineer_df.groupby('ENGINEER').agg(
            SLA_Breached=('BREACHED_NUMERIC', 'sum')
        ).reset_index()
        sla_df = sla_df.rename(columns={'ENGINEER': 'Engineer'})
        perf_df = perf_df.merge(sla_df, on='Engineer', how='left')
        perf_df['SLA_Breached'] = perf_df['SLA_Breached'].fillna(0).astype(int)
        perf_df['SLA_Compliant'] = perf_df['Total_Tickets'] - perf_df['SLA_Breached']
        perf_df['SLA_Compliance'] = (perf_df['SLA_Compliant'] / perf_df['Total_Tickets'] * 100)
    else:
        perf_df['SLA_Breached'] = 0
        perf_df['SLA_Compliant'] = perf_df['Total_Tickets']
        perf_df['SLA_Compliance'] = 100.0
    
    # Calculate efficiency score
    perf_df['Efficiency_Score'] = (perf_df['SLA_Compliance'] / (perf_df['Avg_MTTR_Hours'] + 1)) * 10
    
    # Assign grades
    perf_df['Grade'] = perf_df['SLA_Compliance'].apply(get_engineer_grade)
    
    # Sort by efficiency
    perf_df = perf_df.sort_values('Efficiency_Score', ascending=False).reset_index(drop=True)
    perf_df['Rank'] = range(1, len(perf_df) + 1)
    
    return perf_df


def get_engineer_grade(sla_compliance: float) -> str:
    """Assign a grade based on SLA compliance."""
    if sla_compliance >= 98:
        return "A+"
    elif sla_compliance >= 95:
        return "A"
    elif sla_compliance >= 90:
        return "B"
    elif sla_compliance >= 85:
        return "C"
    elif sla_compliance >= 80:
        return "D"
    else:
        return "F"


# ==================== REGIONAL ANALYSIS ====================

def calculate_regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics by region."""
    df = df.dropna(subset=['REGION'])
    
    if len(df) == 0:
        return pd.DataFrame()
    
    regional_perf = df.groupby('REGION').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean'),
        Median_MTTR=('DURATION', 'median'),
        Total_Downtime=('DURATION', 'sum'),
        Alarm_Count=('IS_ALARM', 'sum')
    ).reset_index()
    
    regional_perf['Non_Alarm_Count'] = regional_perf['Total_Tickets'] - regional_perf['Alarm_Count']
    regional_perf['Alarm_Percentage'] = (regional_perf['Alarm_Count'] / regional_perf['Total_Tickets'] * 100)
    
    # Calculate SLA if available
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['BREACHED_NUMERIC'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = df_temp.groupby('REGION').agg(
            SLA_Breached=('BREACHED_NUMERIC', 'sum')
        ).reset_index()
        regional_perf = regional_perf.merge(sla_df, on='REGION', how='left')
        regional_perf['SLA_Breached'] = regional_perf['SLA_Breached'].fillna(0).astype(int)
        regional_perf['SLA_Compliant'] = regional_perf['Total_Tickets'] - regional_perf['SLA_Breached']
        regional_perf['SLA_Compliance'] = (regional_perf['SLA_Compliant'] / regional_perf['Total_Tickets'] * 100)
    else:
        regional_perf['SLA_Breached'] = 0
        regional_perf['SLA_Compliant'] = regional_perf['Total_Tickets']
        regional_perf['SLA_Compliance'] = 100.0
    
    regional_perf = regional_perf.sort_values('Total_Tickets', ascending=False).reset_index(drop=True)
    
    return regional_perf


# ==================== SERVICE ANALYSIS ====================

def calculate_service_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics by service type."""
    df = df.dropna(subset=['SERVICE'])
    
    if len(df) == 0:
        return pd.DataFrame()
    
    service_perf = df.groupby('SERVICE').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean'),
        Median_MTTR=('DURATION', 'median'),
        Total_Downtime=('DURATION', 'sum'),
        Alarm_Count=('IS_ALARM', 'sum')
    ).reset_index()
    
    service_perf['Ticket_Percentage'] = (service_perf['Total_Tickets'] / service_perf['Total_Tickets'].sum() * 100)
    service_perf['Percentage'] = service_perf['Ticket_Percentage']  # Alias for display
    
    # Complexity score (higher duration = more complex)
    avg_all_duration = service_perf['Avg_MTTR_Hours'].mean()
    service_perf['Complexity_Score'] = (service_perf['Avg_MTTR_Hours'] / avg_all_duration * 100)
    
    # Calculate SLA if available
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['BREACHED_NUMERIC'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = df_temp.groupby('SERVICE').agg(
            SLA_Breached=('BREACHED_NUMERIC', 'sum')
        ).reset_index()
        service_perf = service_perf.merge(sla_df, on='SERVICE', how='left')
        service_perf['SLA_Breached'] = service_perf['SLA_Breached'].fillna(0).astype(int)
        service_perf['SLA_Compliant'] = service_perf['Total_Tickets'] - service_perf['SLA_Breached']
        service_perf['SLA_Compliance'] = (service_perf['SLA_Compliant'] / service_perf['Total_Tickets'] * 100)
    else:
        service_perf['SLA_Breached'] = 0
        service_perf['SLA_Compliant'] = service_perf['Total_Tickets']
        service_perf['SLA_Compliance'] = 100.0
    
    service_perf = service_perf.sort_values('Total_Tickets', ascending=False).reset_index(drop=True)
    
    return service_perf


# ==================== CAUSE/CHALLENGE ANALYSIS ====================

def calculate_cause_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze root causes and their impact."""
    df = df.dropna(subset=['CAUSE'])
    
    if len(df) == 0:
        return pd.DataFrame()
    
    cause_analysis = df.groupby('CAUSE').agg(
        Total_Tickets=('INC', 'count'),
        Avg_Duration=('DURATION', 'mean'),
        Median_Duration=('DURATION', 'median'),
        Total_Duration=('DURATION', 'sum'),
        Min_Duration=('DURATION', 'min'),
        Max_Duration=('DURATION', 'max')
    ).reset_index()
    
    # Rename for consistency
    cause_analysis = cause_analysis.rename(columns={'Avg_Duration': 'Avg_MTTR_Hours'})
    
    total_incidents = cause_analysis['Total_Tickets'].sum()
    cause_analysis['Frequency_Percentage'] = (cause_analysis['Total_Tickets'] / total_incidents * 100)
    cause_analysis['Percentage'] = cause_analysis['Frequency_Percentage']  # Alias
    cause_analysis['Time_Impact_Percentage'] = (cause_analysis['Total_Duration'] / cause_analysis['Total_Duration'].sum() * 100)
    cause_analysis['Priority_Score'] = (cause_analysis['Frequency_Percentage'] * cause_analysis['Avg_MTTR_Hours']) / 100
    
    # Calculate SLA if available
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['BREACHED_NUMERIC'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = df_temp.groupby('CAUSE').agg(
            Breached_Tickets=('BREACHED_NUMERIC', 'sum'),
            Ticket_Count=('INC', 'count')
        ).reset_index()
        sla_df['SLA_Compliance'] = ((sla_df['Ticket_Count'] - sla_df['Breached_Tickets']) / sla_df['Ticket_Count'] * 100)
        cause_analysis = cause_analysis.merge(sla_df[['CAUSE', 'SLA_Compliance', 'Breached_Tickets']], on='CAUSE', how='left')
    else:
        cause_analysis['SLA_Compliance'] = 100.0
        cause_analysis['Breached_Tickets'] = 0
    
    cause_analysis = cause_analysis.sort_values('Total_Tickets', ascending=False).reset_index(drop=True)
    
    return cause_analysis


def calculate_challenge_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze challenges and their impact."""
    df = df.dropna(subset=['CHALLENGE'])
    
    if len(df) == 0:
        return pd.DataFrame()
    
    challenge_analysis = df.groupby('CHALLENGE').agg(
        Total_Tickets=('INC', 'count'),
        Avg_Duration=('DURATION', 'mean'),
        Median_Duration=('DURATION', 'median'),
        Total_Duration=('DURATION', 'sum')
    ).reset_index()
    
    # Rename for consistency
    challenge_analysis = challenge_analysis.rename(columns={'Avg_Duration': 'Avg_MTTR_Hours'})
    
    total_incidents = challenge_analysis['Total_Tickets'].sum()
    challenge_analysis['Frequency_Percentage'] = (challenge_analysis['Total_Tickets'] / total_incidents * 100)
    challenge_analysis['Percentage'] = challenge_analysis['Frequency_Percentage']  # Alias
    challenge_analysis['Impact_Score'] = (challenge_analysis['Frequency_Percentage'] + 
                                          (challenge_analysis['Total_Duration'] / challenge_analysis['Total_Duration'].sum() * 100)) / 2
    
    # Calculate SLA if available
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['BREACHED_NUMERIC'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = df_temp.groupby('CHALLENGE').agg(
            Breached_Tickets=('BREACHED_NUMERIC', 'sum'),
            Ticket_Count=('INC', 'count')
        ).reset_index()
        sla_df['SLA_Compliance'] = ((sla_df['Ticket_Count'] - sla_df['Breached_Tickets']) / sla_df['Ticket_Count'] * 100)
        challenge_analysis = challenge_analysis.merge(sla_df[['CHALLENGE', 'SLA_Compliance', 'Breached_Tickets']], on='CHALLENGE', how='left')
    else:
        challenge_analysis['SLA_Compliance'] = 100.0
        challenge_analysis['Breached_Tickets'] = 0
    
    challenge_analysis = challenge_analysis.sort_values('Total_Tickets', ascending=False).reset_index(drop=True)
    
    return challenge_analysis


# ==================== DISPATCHER ANALYSIS ====================

def calculate_dispatcher_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate dispatcher performance metrics."""
    df = df.dropna(subset=['DISPATCHER'])
    df = df[df['DISPATCHER'].str.strip().str.upper() != 'NONE']
    
    if len(df) == 0:
        return pd.DataFrame()
    
    dispatcher_perf = df.groupby('DISPATCHER').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean'),
        Median_MTTR=('DURATION', 'median'),
        Total_Hours=('DURATION', 'sum')
    ).reset_index()
    
    # Calculate SLA if available
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['BREACHED_NUMERIC'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y']).astype(int)
        sla_df = df_temp.groupby('DISPATCHER').agg(
            Breached_Tickets=('BREACHED_NUMERIC', 'sum')
        ).reset_index()
        dispatcher_perf = dispatcher_perf.merge(sla_df, on='DISPATCHER', how='left')
        dispatcher_perf['SLA_Compliance'] = ((dispatcher_perf['Total_Tickets'] - dispatcher_perf['Breached_Tickets']) / dispatcher_perf['Total_Tickets'] * 100)
    else:
        dispatcher_perf['Breached_Tickets'] = 0
        dispatcher_perf['SLA_Compliance'] = 100.0
    
    dispatcher_perf['Throughput'] = dispatcher_perf['Total_Tickets'] / (dispatcher_perf['Avg_MTTR_Hours'] + 1)
    dispatcher_perf = dispatcher_perf.sort_values('Total_Tickets', ascending=False).reset_index(drop=True)
    
    return dispatcher_perf


# ==================== RECURRING ISSUES ====================

def analyze_recurring_issues(df: pd.DataFrame, min_occurrences: int = 2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify recurring issues based on SUMMARY and LINK_DESCRIPTION patterns.
    Returns two dataframes: one for SUMMARY analysis, one for LINK_DESCRIPTION analysis.
    """
    df = filter_non_alarm_data(df)
    
    # Check which columns are available
    has_summary = 'SUMMARY' in df.columns
    has_link_desc = 'LINK_DESCRIPTION' in df.columns
    
    summary_recurring = pd.DataFrame()
    link_recurring = pd.DataFrame()
    
    # Column 1: Analyze SUMMARY
    if has_summary:
        df_clean = df.copy()
        df_clean['SUMMARY'] = df_clean['SUMMARY'].astype(str).str.strip()
        
        agg_dict = {
            'INC': 'count',
            'DURATION': ['mean', 'sum', 'min', 'max']
        }
        
        if 'ESCALATED_TIME' in df_clean.columns:
            agg_dict['ESCALATED_TIME'] = ['min', 'max']
        
        grouped = df_clean.groupby('SUMMARY').agg(agg_dict)
        grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
        grouped = grouped.reset_index()
        
        # Rename columns to expected format
        grouped = grouped.rename(columns={
            'INC_count': 'Occurrences',
            'DURATION_mean': 'Avg_MTTR_Hours',
            'DURATION_sum': 'Total_MTTR_Hours',
            'DURATION_min': 'Min_MTTR_Hours',
            'DURATION_max': 'Max_MTTR_Hours',
            'ESCALATED_TIME_min': 'First_Occurrence',
            'ESCALATED_TIME_max': 'Last_Occurrence'
        })
        
        # Add cluster info if available
        if 'CLUSTER' in df_clean.columns:
            cluster_info = df_clean.groupby('SUMMARY')['CLUSTER'].first().reset_index()
            grouped = grouped.merge(cluster_info, on='SUMMARY', how='left')
        
        summary_recurring = grouped[grouped['Occurrences'] >= min_occurrences].copy()
        summary_recurring = summary_recurring.sort_values('Occurrences', ascending=False).reset_index(drop=True)
    
    # Column 2: Analyze LINK_DESCRIPTION
    if has_link_desc:
        df_clean = df.copy()
        df_clean['LINK_DESCRIPTION'] = df_clean['LINK_DESCRIPTION'].astype(str).str.strip()
        df_clean = df_clean[df_clean['LINK_DESCRIPTION'] != 'nan']
        df_clean = df_clean[df_clean['LINK_DESCRIPTION'] != '']
        
        if len(df_clean) > 0:
            agg_dict = {
                'INC': 'count',
                'DURATION': ['mean', 'sum', 'min', 'max']
            }
            
            if 'ESCALATED_TIME' in df_clean.columns:
                agg_dict['ESCALATED_TIME'] = ['min', 'max']
            
            grouped = df_clean.groupby('LINK_DESCRIPTION').agg(agg_dict)
            grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
            grouped = grouped.reset_index()
            
            # Rename columns to expected format
            grouped = grouped.rename(columns={
                'INC_count': 'Occurrences',
                'DURATION_mean': 'Avg_MTTR_Hours',
                'DURATION_sum': 'Total_MTTR_Hours',
                'DURATION_min': 'Min_MTTR_Hours',
                'DURATION_max': 'Max_MTTR_Hours',
                'ESCALATED_TIME_min': 'First_Occurrence',
                'ESCALATED_TIME_max': 'Last_Occurrence'
            })
            
            # Add cluster info if available
            if 'CLUSTER' in df_clean.columns:
                cluster_info = df_clean.groupby('LINK_DESCRIPTION')['CLUSTER'].first().reset_index()
                grouped = grouped.merge(cluster_info, on='LINK_DESCRIPTION', how='left')
            
            link_recurring = grouped[grouped['Occurrences'] >= min_occurrences].copy()
            link_recurring = link_recurring.sort_values('Occurrences', ascending=False).reset_index(drop=True)
    
    return summary_recurring, link_recurring


# ==================== TEMPORAL ANALYSIS ====================

def get_hourly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get ticket distribution by hour."""
    if 'HOUR' not in df.columns:
        return pd.DataFrame()
    
    hourly = df.groupby('HOUR').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean')
    ).reset_index()
    
    return hourly


def get_daily_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get ticket distribution by day of week."""
    if 'DAY_OF_WEEK' not in df.columns:
        return pd.DataFrame()
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    daily = df.groupby('DAY_OF_WEEK').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean')
    ).reset_index()
    
    daily['DAY_OF_WEEK'] = pd.Categorical(daily['DAY_OF_WEEK'], categories=day_order, ordered=True)
    daily = daily.sort_values('DAY_OF_WEEK')
    
    return daily


def get_weekly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Get weekly ticket trend."""
    if 'ESCALATED_TIME' not in df.columns:
        return pd.DataFrame()
    
    df = df.copy()
    df['WEEK_START'] = df['ESCALATED_TIME'].dt.to_period('W').apply(lambda p: p.start_time)
    
    weekly = df.groupby('WEEK_START').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean')
    ).reset_index()
    
    return weekly.sort_values('WEEK_START')


def get_daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Get daily ticket trend."""
    if 'DATE' not in df.columns:
        return pd.DataFrame()
    
    daily = df.groupby('DATE').agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean')
    ).reset_index()
    
    return daily.sort_values('DATE')


def get_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Get monthly ticket trend."""
    if 'MONTH_NAME' not in df.columns or 'YEAR_MONTH' not in df.columns:
        return pd.DataFrame()
    
    monthly = df.groupby(['YEAR_MONTH', 'MONTH_NAME']).agg(
        Total_Tickets=('INC', 'count'),
        Avg_MTTR_Hours=('DURATION', 'mean'),
        Total_Downtime=('DURATION', 'sum')
    ).reset_index()
    
    return monthly.sort_values('YEAR_MONTH')


# ==================== GRADE/COLOR HELPERS ====================

def get_sla_grade(sla_compliance: float) -> str:
    """Get SLA grade based on compliance percentage."""
    if sla_compliance >= 99.5:
        return "A+"
    elif sla_compliance >= 98:
        return "A"
    elif sla_compliance >= 95:
        return "B"
    elif sla_compliance >= 90:
        return "C"
    elif sla_compliance >= 85:
        return "D"
    else:
        return "F"


def get_performance_grade(avg_duration: float) -> str:
    """Get performance grade based on average duration (MTTR)."""
    for grade, threshold in PERFORMANCE_GRADES.items():
        if avg_duration <= threshold:
            return grade
    return "F"


def get_grade_color(grade: str) -> str:
    """Get color for grade display."""
    colors = {
        'A+': '#10b981',  # Green
        'A': '#22c55e',   # Light green
        'B': '#f59e0b',   # Yellow/amber
        'C': '#f97316',   # Orange
        'D': '#ef4444',   # Red
        'F': '#dc2626'    # Dark red
    }
    return colors.get(grade, '#6b7280')


def get_sla_color(sla_compliance: float) -> str:
    """Get color based on SLA compliance."""
    if sla_compliance >= 98:
        return '#10b981'  # Green
    elif sla_compliance >= 95:
        return '#3b82f6'  # Blue
    elif sla_compliance >= 90:
        return '#f59e0b'  # Yellow
    else:
        return '#ef4444'  # Red


def get_trend_icon(direction: str) -> str:
    """Get icon for trend direction."""
    icons = {
        'INCREASING': '^',
        'DECREASING': 'v',
        'STABLE': '-'
    }
    return icons.get(direction, '-')


# ==================== FORMATTING HELPERS ====================

def format_duration(hours: float) -> str:
    """Format duration in hours to HH:MM:SS format."""
    if pd.isna(hours) or hours is None:
        return "00:00:00"
    
    total_seconds = int(hours * 3600)
    hours_part = total_seconds // 3600
    minutes_part = (total_seconds % 3600) // 60
    seconds_part = total_seconds % 60
    
    return f"{hours_part:02d}:{minutes_part:02d}:{seconds_part:02d}"


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with thousand separators."""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage value."""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"
