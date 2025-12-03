# Fiber Maintenance Analytics System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange)
![License](https://img.shields.io/badge/License-Proprietary-green)

A comprehensive, production-ready analytics dashboard for fiber network maintenance operations. This system provides real-time performance insights, KPI tracking, SLA monitoring, and detailed analytics to help operations teams optimize their maintenance workflows.

**Developed by:** Joseph Nderitu  
**Contact:** josephnderito16@gmail.com

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Dashboard Pages](#dashboard-pages)
8. [Authentication System](#authentication-system)
9. [Database Schema](#database-schema)
10. [Project Structure](#project-structure)
11. [Troubleshooting](#troubleshooting)
12. [Maintenance](#maintenance)
13. [Security Considerations](#security-considerations)

---

## Overview

The Fiber Maintenance Analytics System is designed to transform raw maintenance ticket data into actionable insights. It enables operations managers and field supervisors to:

- Monitor real-time SLA compliance
- Track engineer performance metrics
- Identify recurring issues and patterns
- Analyze regional and cluster performance
- Make data-driven decisions for resource allocation

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Real-time Analytics** | Live data updates from MySQL database |
| **Multi-dimensional Analysis** | Analyze data by region, cluster, engineer, service, and time |
| **SLA Monitoring** | Track 24-hour SLA compliance with breach alerts |
| **Performance Grading** | Automatic A+ to F grading based on MTTR |
| **User Authentication** | Secure login with role-based access control |
| **Activity Logging** | Complete audit trail of user actions |
| **Interactive Visualizations** | Charts, heatmaps, and trend graphs using Plotly |
| **Export Capabilities** | Download reports and filtered data |

### Dashboard Modules

1. **Home Dashboard** - Executive overview with key metrics
2. **KPI Dashboard** - Comprehensive KPI breakdown
3. **Cluster Analysis** - Cluster performance rankings
4. **Engineer Performance** - Individual engineer metrics
5. **Regional Analysis** - Geographic performance distribution
6. **Service Analysis** - Service-level metrics
7. **Trends and Patterns** - Daily/weekly/monthly trends
8. **SLA Analysis** - Detailed breach analysis
9. **Challenges and Causes** - Root cause analysis
10. **Recurring Issues** - Pattern detection and frequency analysis
11. **Admin Panel** - User management and system administration

---

## System Requirements

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM       | 4 GB    | 8 GB        |
| Storage   | 1 GB    | 5 GB        |
| CPU       | 2 cores | 4 cores     |

### Software Requirements

- **Operating System:** Windows 10/11, Linux (Ubuntu 20.04+), macOS 12+
- **Python:** Version 3.9 or higher
- **MySQL:** Version 8.0 or higher
- **Browser:** Chrome, Firefox, Edge, or Safari (latest versions)

---

## Installation

### Step 1: Clone or Download the Project

```bash
cd /path/to/your/projects
# If using git:
git clone <repository-url>
cd fiber_app
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your database credentials (see Configuration section).

### Step 5: Run the Application

```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Database Configuration 1 (Primary)
DB_NAME_1=your_database_name
DB_HOST_1=your_host_address
DB_USER_1=your_username
DB_PASSWORD_1=your_password

# Database Configuration 2 (Secondary/Local)
DB_NAME_2=your_database_name
DB_HOST_2=localhost
DB_USER_2=root
DB_PASSWORD_2=your_password

# Additional database configurations (optional)
DB_NAME_3=...
DB_HOST_3=...
DB_USER_3=...
DB_PASSWORD_3=...
```

### Database Configurations

The application supports multiple database configurations:

| Config ID | Description | Use Case |
|-----------|-------------|----------|
| 1         | Primary Production | Main data source |
| 2         | Secondary/Local | Backup or development |
| 3-6       | Additional Sources | CRQ, OSP, and other databases |

### Application Settings

Settings can be modified in `config.py`:

```python
# SLA Configuration
SLA_TARGET_HOURS = 24  # 24-hour SLA target

# Performance Thresholds
SLA_THRESHOLDS = {
    'excellent': 98,
    'good': 95,
    'warning': 90,
    'danger': 85
}

# MTTR-based Performance Grades
PERFORMANCE_GRADES = {
    'A+': 2,   # Under 2 hours
    'A': 4,    # 2-4 hours
    'B': 6,    # 4-6 hours
    'C': 8,    # 6-8 hours
    'D': 10,   # 8-10 hours
    'F': inf   # Over 10 hours
}
```

---

## Usage

### First-Time Setup

1. Launch the application with `streamlit run main.py`
2. Register a new user account on the login page
3. The first registered user (username: "NDERITU") becomes the super admin
4. Load data by selecting a database configuration from the sidebar
5. Use date filters to analyze specific time periods

### Navigation

- Use the sidebar menu to navigate between dashboard pages
- Click on charts and tables for interactive filtering
- Use the date range picker to filter data by time period
- Export data using download buttons where available

### Loading Data

1. Select a database configuration from the dropdown
2. Click the "Load Data" button
3. Wait for data to load (progress bar will show status)
4. Apply date filters as needed

---

## Dashboard Pages

### 1. Home Dashboard
Executive overview displaying:
- Total tickets and SLA compliance rate
- Average resolution time (MTTR)
- Performance grade distribution
- Daily trend charts
- Top causes of SLA breaches

### 2. KPI Dashboard
Comprehensive metrics including:
- Volume metrics (tickets, regions, clusters)
- Time metrics (MTTR, response times)
- SLA metrics (compliance, breaches)
- Resource metrics (engineers, workload)

### 3. Cluster Analysis
Cluster performance insights:
- Performance scoring (ticket volume + MTTR)
- Ranking tables with grades
- Comparison charts and heatmaps
- Scatter plot analysis

### 4. Engineer Performance
Individual engineer analytics:
- Ticket counts and SLA compliance
- Efficiency scores and rankings
- Top and bottom performers
- Workload distribution

### 5. Regional Analysis
Geographic performance metrics:
- Regional comparisons
- Radar charts for multi-dimensional analysis
- Regional heatmaps
- Trend analysis by region

### 6. Service Analysis
Service-level insights:
- Service breakdown by metrics
- Deep dive into specific services
- Cause and challenge analysis per service
- Service trend analysis

### 7. Trends and Patterns
Time-based analysis:
- Daily, weekly, and monthly trends
- Hourly distribution patterns
- Moving averages
- Day-of-week performance

### 8. SLA Analysis
SLA compliance details:
- Breach analysis by dimension
- SLA trends over time
- Breach patterns by hour and day
- Top breach contributors

### 9. Challenges and Causes
Root cause analysis:
- Challenge frequency and impact
- Cause-challenge relationships
- Sankey diagrams showing flow
- Sunburst charts for hierarchy

### 10. Recurring Issues
Pattern detection:
- Repeat issue identification
- Frequency analysis
- Priority scoring algorithm
- Impact assessment

### 11. Admin Panel
System administration:
- User management
- Activity log viewing
- System statistics
- User role management

---

## Authentication System

### User Roles

| Role | Capabilities |
|------|--------------|
| **User**  | View dashboards, load data, export reports |
| **Admin** | User role + manage users, view activity logs |
| **Super Admin** | Admin role + promote/demote admins, deactivate users |

### Super Admin

The first user with username "NDERITU" automatically becomes the super admin with full system privileges.

### Security Features

- **bcrypt password hashing** (with SHA-256 fallback for backwards compatibility)
- **UUID-based session management** for multi-user support
- **Session timeout** (configurable, default 30 minutes)
- **Activity logging** for audit trails
- **Role-based access control**
- **Login attempt rate limiting** (configurable)

### Multi-User Support

The system is designed to support multiple concurrent users:
- Each user gets a unique session ID on login
- Session data is isolated per user
- Data loading and filtering is user-specific
- Users can work on the same deployment simultaneously

---

## Database Schema

### Required Tables

The application expects the following data structure:

#### Main Data Table (Ticket Data)

| Column | Type | Description |
|--------|------|-------------|
| CREATED_DATE | DATETIME | Ticket creation timestamp |
| CLOSED_DATE | DATETIME | Ticket resolution timestamp |
| EXTERNAL_BREACHED | VARCHAR | SLA breach indicator (Yes/No) |
| EXTERNAL_BREACHED_HOURS | DECIMAL | Hours over SLA if breached |
| CLUSTER | VARCHAR | Service cluster name |
| REGION | VARCHAR | Geographic region |
| SERVICE | VARCHAR | Service type |
| CAUSE | VARCHAR | Root cause category |
| CHALLENGE | VARCHAR | Challenge faced |
| ASSIGNED_ENGINEER | VARCHAR | Engineer assigned |
| SUMMARY | VARCHAR | Ticket summary |
| LINK_DESCRIPTION | VARCHAR | Link description |

### Authentication Tables (Auto-Created)

The system automatically creates:
- `app_users` - User credentials and profiles
- `activity_logs` - User activity audit trail

---

## Project Structure

```
fiber_app/
├── main.py                      # Application entry point
├── config.py                    # Configuration settings
├── auth.py                      # Authentication module
├── utils.py                     # Utility functions
├── data_loader.py               # Database connection
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Environment template
├── data/                        # Data storage folder
├── data_exploration.ipynb       # Data exploration notebook
├── __pycache__/                 # Python cache (auto-generated)
└── pages/                       # Dashboard pages
    ├── 0_Login.py               # Login and registration
    ├── 1_Home.py                # Home dashboard
    ├── 2_KPI_Dashboard.py       # KPI metrics
    ├── 3_Cluster_Analysis.py    # Cluster analysis
    ├── 4_Engineer_Performance.py # Engineer metrics
    ├── 5_Regional_Analysis.py   # Regional analysis
    ├── 6_Service_Analysis.py    # Service analysis
    ├── 7_Trends.py              # Trend analysis
    ├── 8_SLA_Analysis.py        # SLA analysis
    ├── 9_Challenges.py          # Challenge analysis
    ├── 10_Recurring_Issues.py   # Recurring issues
    └── 11_Admin.py              # Admin panel
```

---

## Troubleshooting

### Common Issues

#### Database Connection Failed
```
Error: Could not connect to database
```
**Solution:**
1. Verify database credentials in `.env` file
2. Check network connectivity to database server
3. Ensure MySQL service is running
4. Verify firewall settings allow database port

#### Module Not Found Error
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:**
1. Activate virtual environment
2. Run `pip install -r requirements.txt`
3. Verify Python version is 3.9+

#### Page Not Loading
```
Error: Unable to display page
```
**Solution:**
1. Clear browser cache
2. Restart the Streamlit server
3. Check for syntax errors in page files

#### SLA Calculations Incorrect
**Solution:**
1. Verify CREATED_DATE and CLOSED_DATE formats
2. Check EXTERNAL_BREACHED column values (Yes/No)
3. Review SLA_TARGET_HOURS in config.py

### Performance Optimization

For large datasets:
1. Use date filters to limit data range
2. Consider adding database indexes
3. Increase server RAM if needed
4. Use pagination for large tables

---

## Maintenance

### Regular Tasks

| Task | Frequency | Description |
|------|-----------|-------------|
| Log Cleanup | Monthly | Archive old activity logs |
| Data Backup | Daily | Backup database |
| Dependency Update | Quarterly | Update Python packages |
| Security Audit | Annually | Review access controls |

### Updating the Application

```bash
# Pull latest changes (if using git)
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the application
streamlit run main.py
```

---

## Streamlit Cloud Deployment

### Quick Deploy Guide

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/fiber-analytics.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `main.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard, click your app's menu (⋮)
   - Select "Settings" → "Secrets"
   - Add your database credentials (copy from `.streamlit/secrets.toml.example`):
   
   ```toml
   [database_1]
   DB_NAME = "your_database_name"
   DB_HOST = "your_host_ip"
   DB_USER = "your_username"
   DB_PASSWORD = "your_password"
   
   [database_2]
   DB_NAME = "your_database_name"
   DB_HOST = "your_host_ip"
   DB_USER = "your_username"
   DB_PASSWORD = "your_password"
   
   # App Settings
   [app]
   session_timeout_minutes = 30
   enable_demo_mode = false
   
   # Security Settings
   [security]
   max_login_attempts = 5
   lockout_duration_minutes = 15
   ```

4. **Reboot the app** to apply secrets

### Important Notes for Cloud Deployment

- **Database Access:** Ensure your MySQL server allows connections from Streamlit Cloud IPs
- **Firewall:** You may need to whitelist Streamlit Cloud's IP ranges
- **SSL:** Consider using SSL for database connections in production
- **Memory:** Streamlit Cloud has resource limits; optimize data queries if needed

---

## Security Considerations

### Production Deployment

1. **Environment Variables:** Never commit `.env` or `secrets.toml` to version control
2. **HTTPS:** Streamlit Cloud provides HTTPS automatically
3. **Authentication:** Enable strong password policies
4. **Database:** Use read-only database users where possible
5. **Access Control:** Regularly audit user access and activity logs
6. **Updates:** Keep all dependencies updated

### Network Security

- Ensure database allows connections from Streamlit Cloud
- Use firewall rules to limit access to known IPs
- Consider VPN for sensitive data
- Implement rate limiting

---

## License

This software is proprietary and developed for internal company use. Unauthorized distribution, modification, or use without permission is prohibited.

---

## Support

For technical support or feature requests, contact:

- **Developer:** Joseph Nderitu
- **Email:** josephnderito16@gmail.com

---

## Changelog

### Version 2.0.0 (Current)

**New Features:**
- Multi-user concurrent session support
- bcrypt password hashing for enhanced security
- Session timeout with configurable duration
- Help & Documentation page
- Data refresh button in sidebar
- Introduction page for new users
- CEO Dashboard with executive view
- Coming Soon page for restricted features
- Comprehensive audit trail system

**Improvements:**
- Stunning dark theme with animations
- Improved sidebar navigation styling
- Better error handling
- Position-based access control (MANAGEMENT, ENGINEER, NOC)
- Email validation for staff accounts

### Version 1.0.0

- Initial production release
- 11 dashboard pages
- User authentication system
- Activity logging
- Multiple database support
- Streamlit Cloud deployment ready

---

**Last Updated:** January 2025

