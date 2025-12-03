"""
Predictive Analytics - Fiber Maintenance Analytics System
Advanced ML-based predictions with multiple models and user options
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    calculate_comprehensive_kpis, filter_non_alarm_data,
    format_duration
)
from auth import require_page_access, get_current_user, log_page_visit

# Check page access
require_page_access("15_Predictions.py")
log_page_visit("Predictions")

# Try importing ML libraries
try:
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    .prediction-header {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
    }
    
    .prediction-header h1, .prediction-header p {
        color: white !important;
        text-align: center;
        margin: 0;
    }
    
    .prediction-header p {
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    .config-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    
    .metric-box {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        text-align: center;
    }
    
    .metric-box h3 {
        color: #667eea !important;
        font-size: 1.8rem;
        margin: 0;
    }
    
    .metric-box p {
        color: #94a3b8 !important;
        margin: 0.5rem 0 0 0;
    }
    
    .model-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .model-rf { background: #22c55e; color: white; }
    .model-gb { background: #3b82f6; color: white; }
    .model-ridge { background: #f59e0b; color: white; }
    .model-stat { background: #a855f7; color: white; }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)


def create_header():
    """Create page header"""
    st.markdown("""
    <div class='prediction-header'>
        <h1>Predictive Analytics</h1>
        <p>AI-powered forecasting for maintenance operations</p>
    </div>
    """, unsafe_allow_html=True)


def prepare_time_series_data(df, include_alarms=True):
    """Prepare data for time series prediction"""
    df = df.copy()
    
    # Filter alarms if requested - use the IS_ALARM column computed during data loading
    if not include_alarms:
        if 'IS_ALARM' in df.columns:
            df = df[~df['IS_ALARM']].copy()
        elif 'ALARM_CATEGORY' in df.columns:
            df = df[df['ALARM_CATEGORY'] != 'ALARM'].copy()
        else:
            # Fallback: check CAUSE column for alarm keyword
            if 'CAUSE' in df.columns:
                df = df[~df['CAUSE'].astype(str).str.upper().str.contains('ALARM', na=False)]
    
    if df.empty:
        return pd.DataFrame()
    
    if 'DATE' not in df.columns and 'ESCALATED_TIME' in df.columns:
        df['DATE'] = pd.to_datetime(df['ESCALATED_TIME']).dt.date
    
    # Daily aggregation
    daily = df.groupby('DATE').agg({
        'INC': 'count',
        'DURATION': 'mean'
    }).reset_index()
    daily.columns = ['Date', 'Tickets', 'Avg_MTTR']
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.sort_values('Date')
    
    # Add SLA breach rate
    if 'EXTERNAL_BREACHED' in df.columns:
        df_temp = df.copy()
        df_temp['DATE'] = pd.to_datetime(df_temp['ESCALATED_TIME']).dt.date
        df_temp['IS_BREACHED'] = df_temp['EXTERNAL_BREACHED'].astype(str).str.upper().isin(['YES', 'TRUE', '1', 'Y'])
        
        breach_daily = df_temp.groupby('DATE').agg({
            'IS_BREACHED': ['sum', 'count']
        }).reset_index()
        breach_daily.columns = ['Date', 'Breached', 'Total']
        breach_daily['Date'] = pd.to_datetime(breach_daily['Date'])
        breach_daily['Breach_Rate'] = (breach_daily['Breached'] / breach_daily['Total']) * 100
        
        daily = daily.merge(breach_daily[['Date', 'Breach_Rate', 'Breached']], on='Date', how='left')
    
    # Add time features
    daily['DayOfWeek'] = daily['Date'].dt.dayofweek
    daily['DayOfMonth'] = daily['Date'].dt.day
    daily['WeekOfYear'] = daily['Date'].dt.isocalendar().week.astype(int)
    daily['Month'] = daily['Date'].dt.month
    daily['IsWeekend'] = daily['DayOfWeek'].isin([5, 6]).astype(int)
    daily['Quarter'] = daily['Date'].dt.quarter
    
    # Rolling features
    daily['Tickets_MA3'] = daily['Tickets'].rolling(window=3, min_periods=1).mean()
    daily['Tickets_MA7'] = daily['Tickets'].rolling(window=7, min_periods=1).mean()
    daily['Tickets_MA14'] = daily['Tickets'].rolling(window=14, min_periods=1).mean()
    daily['Tickets_Std7'] = daily['Tickets'].rolling(window=7, min_periods=1).std().fillna(0)
    daily['MTTR_MA7'] = daily['Avg_MTTR'].rolling(window=7, min_periods=1).mean()
    
    # Lag features
    daily['Tickets_Lag1'] = daily['Tickets'].shift(1).fillna(daily['Tickets'].mean())
    daily['Tickets_Lag7'] = daily['Tickets'].shift(7).fillna(daily['Tickets'].mean())
    
    return daily


def prepare_cluster_data(df, include_alarms=True):
    """Prepare data for cluster-level predictions"""
    df = df.copy()
    
    # Filter alarms if requested - use the IS_ALARM column
    if not include_alarms:
        if 'IS_ALARM' in df.columns:
            df = df[~df['IS_ALARM']].copy()
        elif 'ALARM_CATEGORY' in df.columns:
            df = df[df['ALARM_CATEGORY'] != 'ALARM'].copy()
        elif 'CAUSE' in df.columns:
            df = df[~df['CAUSE'].astype(str).str.upper().str.contains('ALARM', na=False)]
    
    if 'CLUSTER' not in df.columns:
        return None
    
    df['DATE'] = pd.to_datetime(df['ESCALATED_TIME']).dt.date
    
    cluster_daily = df.groupby(['DATE', 'CLUSTER']).agg({
        'INC': 'count',
        'DURATION': 'mean'
    }).reset_index()
    cluster_daily.columns = ['Date', 'Cluster', 'Tickets', 'Avg_MTTR']
    
    return cluster_daily


def simple_forecast(daily_data, target_col, forecast_days=14):
    """Simple statistical forecast without ML libraries"""
    if daily_data.empty or target_col not in daily_data.columns:
        return None, {'model': 'Statistical', 'r2': None, 'mae': None}
    
    # Calculate trends
    recent_data = daily_data.tail(30)
    
    # Average by day of week
    dow_avg = daily_data.groupby('DayOfWeek')[target_col].mean().to_dict()
    
    # Recent trend
    if len(recent_data) > 7:
        recent_avg = recent_data[target_col].mean()
        older_avg = daily_data.tail(60).head(30)[target_col].mean() if len(daily_data) > 60 else recent_avg
        trend_factor = recent_avg / older_avg if older_avg > 0 else 1
    else:
        trend_factor = 1
        recent_avg = daily_data[target_col].mean()
    
    # Generate forecast
    last_date = daily_data['Date'].max()
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
    
    forecasts = []
    for date in forecast_dates:
        dow = date.weekday()
        base_prediction = dow_avg.get(dow, recent_avg)
        prediction = base_prediction * trend_factor
        
        # Add some variance based on historical std
        std = daily_data[target_col].std() * 0.3
        lower = max(0, prediction - std)
        upper = prediction + std
        
        forecasts.append({
            'Date': date,
            'Predicted': round(prediction, 2),
            'Lower_Bound': round(lower, 2),
            'Upper_Bound': round(upper, 2)
        })
    
    return pd.DataFrame(forecasts), {'model': 'Statistical', 'r2': None, 'mae': None}


def ml_forecast(daily_data, target_col, forecast_days=14, model_type='random_forest'):
    """ML-based forecast using scikit-learn"""
    if not SKLEARN_AVAILABLE:
        return simple_forecast(daily_data, target_col, forecast_days)
    
    # Prepare features
    features = ['DayOfWeek', 'DayOfMonth', 'WeekOfYear', 'Month', 'IsWeekend', 'Quarter',
                'Tickets_MA3', 'Tickets_MA7', 'Tickets_MA14', 'Tickets_Std7',
                'Tickets_Lag1', 'Tickets_Lag7']
    
    # Adjust features based on target
    if target_col == 'Tickets':
        pass  # Use all features
    elif target_col == 'Breach_Rate':
        features = ['DayOfWeek', 'DayOfMonth', 'Month', 'IsWeekend', 'Tickets_MA7']
    elif target_col == 'Avg_MTTR':
        features = ['DayOfWeek', 'DayOfMonth', 'Month', 'IsWeekend', 'Tickets_MA7']
    
    # Filter to available features
    available_features = [f for f in features if f in daily_data.columns]
    
    # Remove NaN rows
    train_data = daily_data.dropna(subset=available_features + [target_col])
    
    if len(train_data) < 14:
        return simple_forecast(daily_data, target_col, forecast_days)
    
    X = train_data[available_features].values
    y = train_data[target_col].values
    
    # Train model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Select model
    if model_type == 'random_forest':
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        model_name = 'Random Forest'
    elif model_type == 'gradient_boosting':
        model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        model_name = 'Gradient Boosting'
    elif model_type == 'ridge':
        model = Ridge(alpha=1.0)
        model_name = 'Ridge Regression'
    else:
        model = Ridge(alpha=1.0)
        model_name = 'Ridge Regression'
    
    # Train with cross-validation
    try:
        cv_folds = min(5, len(train_data)//3)
        if cv_folds >= 2:
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds, scoring='r2')
            cv_r2 = cv_scores.mean()
        else:
            cv_r2 = None
    except:
        cv_r2 = None
    
    model.fit(X_scaled, y)
    
    # Calculate training metrics
    y_pred = model.predict(X_scaled)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    
    # Generate future dates
    last_date = daily_data['Date'].max()
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
    
    # Prepare future features
    last_values = {f: daily_data[f].iloc[-1] if f in daily_data.columns else 0 for f in available_features}
    
    forecasts = []
    predictions_for_rolling = list(daily_data['Tickets'].tail(14))
    
    for i, date in enumerate(forecast_dates):
        # Build feature vector
        feature_values = []
        for f in available_features:
            if f == 'DayOfWeek':
                feature_values.append(date.weekday())
            elif f == 'DayOfMonth':
                feature_values.append(date.day)
            elif f == 'WeekOfYear':
                feature_values.append(date.isocalendar()[1])
            elif f == 'Month':
                feature_values.append(date.month)
            elif f == 'IsWeekend':
                feature_values.append(1 if date.weekday() in [5, 6] else 0)
            elif f == 'Quarter':
                feature_values.append((date.month - 1) // 3 + 1)
            elif f == 'Tickets_MA3':
                feature_values.append(np.mean(predictions_for_rolling[-3:]))
            elif f == 'Tickets_MA7':
                feature_values.append(np.mean(predictions_for_rolling[-7:]))
            elif f == 'Tickets_MA14':
                feature_values.append(np.mean(predictions_for_rolling[-14:]))
            elif f == 'Tickets_Std7':
                feature_values.append(np.std(predictions_for_rolling[-7:]))
            elif f == 'Tickets_Lag1':
                feature_values.append(predictions_for_rolling[-1])
            elif f == 'Tickets_Lag7':
                feature_values.append(predictions_for_rolling[-7] if len(predictions_for_rolling) >= 7 else predictions_for_rolling[0])
            else:
                feature_values.append(last_values.get(f, 0))
        
        X_future = np.array([feature_values])
        X_future_scaled = scaler.transform(X_future)
        
        prediction = model.predict(X_future_scaled)[0]
        prediction = max(0, prediction)
        
        # Confidence interval based on MAE
        lower = max(0, prediction - 1.96 * mae)
        upper = prediction + 1.96 * mae
        
        forecasts.append({
            'Date': date,
            'Predicted': round(prediction, 2),
            'Lower_Bound': round(lower, 2),
            'Upper_Bound': round(upper, 2)
        })
        
        # Update rolling predictions for next iteration
        if target_col == 'Tickets':
            predictions_for_rolling.append(prediction)
    
    metrics = {
        'model': model_name,
        'r2': r2,
        'cv_r2': cv_r2,
        'mae': mae,
        'rmse': rmse
    }
    
    return pd.DataFrame(forecasts), metrics


def create_forecast_chart(daily_data, forecast_data, target_col, title):
    """Create interactive forecast visualization"""
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data[target_col],
        mode='lines',
        name='Historical',
        line=dict(color='#667eea', width=2)
    ))
    
    # Moving average if exists
    ma_col = 'Tickets_MA7' if 'Tickets_MA7' in daily_data.columns else None
    if ma_col:
        fig.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data[ma_col],
            mode='lines',
            name='7-Day Moving Avg',
            line=dict(color='#a78bfa', width=1, dash='dash')
        ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_data['Date'],
        y=forecast_data['Predicted'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#10b981', width=2),
        marker=dict(size=8)
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_data['Date'], forecast_data['Date'][::-1]]),
        y=pd.concat([forecast_data['Upper_Bound'], forecast_data['Lower_Bound'][::-1]]),
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence',
        showlegend=True
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=target_col.replace('_', ' '),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    
    fig.update_xaxes(gridcolor='#334155', showgrid=True)
    fig.update_yaxes(gridcolor='#334155', showgrid=True)
    
    return fig


def predict_breach_risk(daily_data, df):
    """Predict SLA breach risk factors"""
    if 'Breach_Rate' not in daily_data.columns:
        return None, None
    
    # Analyze breach patterns
    breach_data = daily_data.dropna(subset=['Breach_Rate'])
    
    if len(breach_data) < 7:
        return None, None
    
    # Day of week analysis
    dow_breach = breach_data.groupby('DayOfWeek').agg({
        'Breach_Rate': 'mean',
        'Tickets': 'mean'
    }).reset_index()
    dow_breach['DayName'] = dow_breach['DayOfWeek'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 
        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })
    
    # High volume impact
    median_tickets = breach_data['Tickets'].median()
    high_volume = breach_data[breach_data['Tickets'] > median_tickets]
    low_volume = breach_data[breach_data['Tickets'] <= median_tickets]
    
    volume_impact = {
        'high_volume_breach_rate': high_volume['Breach_Rate'].mean() if len(high_volume) > 0 else 0,
        'low_volume_breach_rate': low_volume['Breach_Rate'].mean() if len(low_volume) > 0 else 0
    }
    
    # Identify risk factors
    risk_factors = []
    
    # Weekend risk
    weekend_breach = breach_data[breach_data['IsWeekend'] == 1]['Breach_Rate'].mean()
    weekday_breach = breach_data[breach_data['IsWeekend'] == 0]['Breach_Rate'].mean()
    if pd.notna(weekend_breach) and pd.notna(weekday_breach) and weekend_breach > weekday_breach * 1.2:
        risk_factors.append({
            'factor': 'Weekend Operations',
            'risk_level': 'High',
            'detail': f'Breach rate {weekend_breach:.1f}% on weekends vs {weekday_breach:.1f}% on weekdays',
            'recommendation': 'Consider additional weekend staffing'
        })
    
    # High volume risk
    if volume_impact['high_volume_breach_rate'] > volume_impact['low_volume_breach_rate'] * 1.3:
        risk_factors.append({
            'factor': 'Volume Overload',
            'risk_level': 'Medium',
            'detail': f"Breach rate increases to {volume_impact['high_volume_breach_rate']:.1f}% during high volume periods",
            'recommendation': 'Implement capacity scaling during peak periods'
        })
    
    # Trend risk
    recent_breach = breach_data.tail(7)['Breach_Rate'].mean()
    overall_breach = breach_data['Breach_Rate'].mean()
    if recent_breach > overall_breach * 1.2:
        risk_factors.append({
            'factor': 'Rising Trend',
            'risk_level': 'High',
            'detail': f'Recent breach rate {recent_breach:.1f}% vs average {overall_breach:.1f}%',
            'recommendation': 'Investigate recent operational changes'
        })
    
    return dow_breach, risk_factors


# ==================== MAIN PAGE ====================

create_header()

# Check for data
if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.warning("No data loaded. Please load data from the sidebar first.")
    st.stop()

df = st.session_state['df'].copy()

# Configuration Section
st.markdown("### Configuration")

col1, col2, col3, col4 = st.columns(4)

with col1:
    prediction_target = st.selectbox(
        "What to Predict",
        options=["Ticket Volume", "SLA Breach Rate", "MTTR (Resolution Time)", "Workload by Cluster"],
        help="Select what you want to predict"
    )

with col2:
    forecast_days = st.slider("Forecast Period (days)", 7, 30, 14)

with col3:
    include_alarms = st.selectbox(
        "Include Alarms",
        options=["Yes", "No"],
        index=0,
        help="Whether to include alarm tickets in predictions"
    )

with col4:
    if SKLEARN_AVAILABLE:
        model_type = st.selectbox(
            "Model Type",
            options=["Random Forest", "Gradient Boosting", "Ridge Regression", "Statistical"],
            help="Random Forest and Gradient Boosting are more accurate for complex patterns"
        )
    else:
        model_type = "Statistical"
        st.info("Install sklearn for ML models")

# Map UI selections to code
target_mapping = {
    "Ticket Volume": "Tickets",
    "SLA Breach Rate": "Breach_Rate",
    "MTTR (Resolution Time)": "Avg_MTTR",
    "Workload by Cluster": "Tickets"
}
model_mapping = {
    "Random Forest": "random_forest",
    "Gradient Boosting": "gradient_boosting",
    "Ridge Regression": "ridge",
    "Statistical": "statistical"
}

target_col = target_mapping[prediction_target]
model_code = model_mapping.get(model_type, "statistical")
include_alarms_bool = include_alarms == "Yes"

# Show alarm count info
if 'IS_ALARM' in df.columns:
    alarm_count = df['IS_ALARM'].sum()
    non_alarm_count = len(df) - alarm_count
    alarm_pct = (alarm_count / len(df) * 100) if len(df) > 0 else 0
    
    if not include_alarms_bool:
        st.info(f"Excluding {alarm_count:,} alarm tickets ({alarm_pct:.1f}%). Using {non_alarm_count:,} non-alarm tickets for predictions.")
    else:
        st.caption(f"Data includes {alarm_count:,} alarm tickets ({alarm_pct:.1f}%) and {non_alarm_count:,} non-alarm tickets.")
    if alarm_count > 0:
        st.info(f"Excluding approximately {alarm_count:,} alarm-related tickets from predictions")

st.markdown("---")

# Prepare data
with st.spinner("Preparing predictive models..."):
    daily_data = prepare_time_series_data(df, include_alarms_bool)

if daily_data.empty or len(daily_data) < 7:
    st.error("Insufficient data for predictions. Need at least 7 days of data.")
    st.stop()

# Check if target column exists
if target_col not in daily_data.columns:
    if target_col == "Breach_Rate":
        st.error("SLA breach data not available in the dataset.")
    elif target_col == "Avg_MTTR":
        st.error("Resolution time data not available in the dataset.")
    st.stop()

# Generate predictions
if prediction_target == "Workload by Cluster":
    # Special handling for cluster predictions
    st.markdown("### Workload Predictions by Cluster")
    
    cluster_data = prepare_cluster_data(df, include_alarms_bool)
    if cluster_data is None:
        st.error("Cluster data not available")
        st.stop()
    
    # Get top clusters
    top_clusters = cluster_data.groupby('Cluster')['Tickets'].sum().nlargest(10).index.tolist()
    
    selected_clusters = st.multiselect(
        "Select Clusters to Predict",
        options=top_clusters,
        default=top_clusters[:3] if len(top_clusters) >= 3 else top_clusters
    )
    
    if selected_clusters:
        # Create forecast for each cluster
        cluster_forecasts = {}
        
        for cluster in selected_clusters:
            cluster_df = cluster_data[cluster_data['Cluster'] == cluster].copy()
            cluster_df['Date'] = pd.to_datetime(cluster_df['Date'])
            cluster_df = cluster_df.sort_values('Date')
            
            # Add time features
            cluster_df['DayOfWeek'] = cluster_df['Date'].dt.dayofweek
            cluster_df['IsWeekend'] = cluster_df['DayOfWeek'].isin([5, 6]).astype(int)
            cluster_df['Tickets_MA7'] = cluster_df['Tickets'].rolling(window=7, min_periods=1).mean()
            
            if len(cluster_df) >= 7:
                # Calculate forecast
                last_avg = cluster_df.tail(7)['Tickets'].mean()
                trend = cluster_df.tail(14)['Tickets'].mean() - cluster_df.tail(28).head(14)['Tickets'].mean() if len(cluster_df) >= 28 else 0
                
                cluster_forecasts[cluster] = {
                    'daily_avg': last_avg,
                    'weekly_total': last_avg * 7,
                    'trend': trend,
                    'last_week': cluster_df.tail(7)['Tickets'].sum()
                }
        
        # Display cluster metrics
        cols = st.columns(min(len(selected_clusters), 4))
        
        for i, cluster in enumerate(selected_clusters):
            if cluster in cluster_forecasts:
                cf = cluster_forecasts[cluster]
                with cols[i % len(cols)]:
                    trend_icon = "+" if cf['trend'] > 0 else ""
                    trend_color = "#ef4444" if cf['trend'] > 2 else "#f59e0b" if cf['trend'] > 0 else "#22c55e"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
                                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                                border-left: 4px solid #667eea;'>
                        <h4 style='color: #a78bfa; margin: 0 0 1rem 0;'>{cluster}</h4>
                        <p style='color: #e2e8f0; margin: 0.5rem 0;'>
                            Daily Avg: <strong>{cf['daily_avg']:.0f}</strong> tickets
                        </p>
                        <p style='color: #e2e8f0; margin: 0.5rem 0;'>
                            Weekly Forecast: <strong>{cf['weekly_total']:.0f}</strong>
                        </p>
                        <p style='color: {trend_color}; margin: 0.5rem 0;'>
                            Trend: {trend_icon}{cf['trend']:.1f} tickets/day
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Cluster comparison chart
        if cluster_forecasts:
            st.markdown("### Cluster Comparison")
            
            comparison_data = pd.DataFrame([
                {'Cluster': k, 'Daily Average': v['daily_avg'], 'Weekly Forecast': v['weekly_total']}
                for k, v in cluster_forecasts.items()
            ])
            
            fig = px.bar(
                comparison_data,
                x='Cluster',
                y='Daily Average',
                title='Predicted Daily Average by Cluster',
                color='Daily Average',
                color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
            )
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    # Regular predictions
    if model_code == "statistical" or not SKLEARN_AVAILABLE:
        forecast_data, metrics = simple_forecast(daily_data, target_col, forecast_days)
    else:
        forecast_data, metrics = ml_forecast(daily_data, target_col, forecast_days, model_code)
    
    if forecast_data is None:
        st.error("Could not generate predictions. Check your data.")
        st.stop()
    
    # Display model info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        model_badge_class = {
            'Random Forest': 'model-rf',
            'Gradient Boosting': 'model-gb',
            'Ridge Regression': 'model-ridge',
            'Statistical': 'model-stat'
        }.get(metrics['model'], 'model-stat')
        st.markdown(f"<span class='model-badge {model_badge_class}'>{metrics['model']}</span>", unsafe_allow_html=True)
    
    with col2:
        if metrics.get('r2') is not None:
            r2_color = "#22c55e" if metrics['r2'] > 0.7 else "#f59e0b" if metrics['r2'] > 0.4 else "#ef4444"
            st.markdown(f"<span style='color: {r2_color};'>R Score: {metrics['r2']:.3f}</span>", unsafe_allow_html=True)
    
    with col3:
        if metrics.get('mae') is not None:
            st.markdown(f"<span style='color: #94a3b8;'>MAE: {metrics['mae']:.2f}</span>", unsafe_allow_html=True)
    
    with col4:
        if metrics.get('cv_r2') is not None:
            st.markdown(f"<span style='color: #a78bfa;'>CV Score: {metrics['cv_r2']:.3f}</span>", unsafe_allow_html=True)
    
    # Forecast Chart
    st.markdown(f"### {prediction_target} Forecast")
    
    chart_title = f"{prediction_target} - {forecast_days} Day Forecast"
    if not include_alarms_bool:
        chart_title += " (Excluding Alarms)"
    
    fig = create_forecast_chart(daily_data, forecast_data, target_col, chart_title)
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast summary metrics
    st.markdown("### Forecast Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    unit = "" if prediction_target == "Ticket Volume" else ("%" if "Rate" in prediction_target else " min")
    
    with col1:
        next_week = forecast_data.head(7)['Predicted'].sum() if prediction_target == "Ticket Volume" else forecast_data.head(7)['Predicted'].mean()
        label = "Next 7 Days Total" if prediction_target == "Ticket Volume" else "Next 7 Days Avg"
        st.markdown(f"""
        <div class='metric-box'>
            <h3>{next_week:,.0f}{unit}</h3>
            <p>{label}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_forecast = forecast_data['Predicted'].mean()
        st.markdown(f"""
        <div class='metric-box'>
            <h3>{avg_forecast:.1f}{unit}</h3>
            <p>Average Forecast</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        peak_row = forecast_data.loc[forecast_data['Predicted'].idxmax()]
        st.markdown(f"""
        <div class='metric-box'>
            <h3>{peak_row['Predicted']:.0f}{unit}</h3>
            <p>Peak: {peak_row['Date'].strftime('%b %d')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Compare to historical
        hist_avg = daily_data[target_col].mean()
        change = ((avg_forecast - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
        trend = "+" if change > 0 else ""
        trend_color = "#ef4444" if change > 10 else "#f59e0b" if change > 0 else "#22c55e"
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='color: {trend_color} !important;'>{trend}{change:.1f}%</h3>
            <p>vs Historical Avg</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed forecast table
    with st.expander("Detailed Forecast Table"):
        display_forecast = forecast_data.copy()
        display_forecast['Date'] = display_forecast['Date'].dt.strftime('%Y-%m-%d (%a)')
        display_forecast.columns = ['Date', 'Predicted', 'Lower Bound', 'Upper Bound']
        st.dataframe(display_forecast, use_container_width=True, hide_index=True)
        
        # Download button
        csv = display_forecast.to_csv(index=False)
        st.download_button(
            "Download Forecast CSV",
            csv,
            f"forecast_{prediction_target.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

# SLA Breach Risk Analysis (always show if data available)
if 'Breach_Rate' in daily_data.columns:
    st.markdown("---")
    st.markdown("### SLA Breach Risk Analysis")
    
    dow_breach, risk_factors = predict_breach_risk(daily_data, df)
    
    if dow_breach is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                dow_breach,
                x='DayName',
                y='Breach_Rate',
                title='Breach Rate by Day of Week',
                color='Breach_Rate',
                color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
            )
            fig.update_layout(
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title='',
                yaxis_title='Breach Rate (%)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Risk Factors:**")
            if risk_factors:
                for rf in risk_factors:
                    color = '#ef4444' if rf['risk_level'] == 'High' else '#f59e0b'
                    st.markdown(f"""
                    <div style='background: rgba(239,68,68,0.1); border-left: 4px solid {color};
                                padding: 0.75rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0;'>
                        <strong style='color: {color};'>{rf['risk_level']}: {rf['factor']}</strong>
                        <p style='color: #94a3b8; margin: 0.25rem 0; font-size: 0.85rem;'>{rf['detail']}</p>
                        <p style='color: #22c55e; margin: 0; font-size: 0.8rem;'>{rf['recommendation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No significant risk factors identified")

# Model Information
st.markdown("---")
with st.expander("About the Prediction Models"):
    st.markdown("""
    **Available Models:**
    
    | Model | Best For | Accuracy | Speed |
    |-------|----------|----------|-------|
    | **Random Forest** | Complex patterns, high accuracy | High | Medium |
    | **Gradient Boosting** | Non-linear relationships | Very High | Slow |
    | **Ridge Regression** | Linear trends, fast predictions | Medium | Fast |
    | **Statistical** | Simple patterns, no ML required | Basic | Very Fast |
    
    **Tips for Better Predictions:**
    - Use at least 30 days of historical data
    - Random Forest works best with seasonal patterns
    - Exclude alarms for operational predictions
    - Gradient Boosting gives best accuracy but takes longer
    
    **Understanding Metrics:**
    - **R Score**: How well the model fits (closer to 1 is better)
    - **MAE**: Average prediction error (lower is better)
    - **CV Score**: Cross-validation score (more reliable than R)
    
    **Alarm Filtering:**
    - Set "Include Alarms" to "No" to exclude alarm-related tickets
    - This gives more accurate predictions for manual work
    """)

if not SKLEARN_AVAILABLE:
    st.warning("Install scikit-learn for advanced ML models: `pip install scikit-learn`")

# Footer
st.markdown(f"""
<div style='text-align: center; padding: 2rem; color: #6b7280; border-top: 2px solid #8b5cf6; margin-top: 3rem;'>
    <p>Predictive Analytics | AI-Powered Forecasting</p>
</div>
""", unsafe_allow_html=True)
