# Fiber Maintenance Analytics - Deployment Checklist

## Pre-Deployment Checklist

### Files to Upload to GitHub
- [x] main.py - Application entry point
- [x] auth.py - Authentication system
- [x] config.py - Configuration settings
- [x] data_loader.py - Database connectivity
- [x] utils.py - Utility functions
- [x] requirements.txt - Python dependencies
- [x] runtime.txt - Python version specification
- [x] packages.txt - System dependencies
- [x] README.md - Documentation
- [x] CONTRIBUTING.md - Contributor guidelines
- [x] .gitignore - Git ignore rules
- [x] .env.example - Environment template
- [x] .streamlit/config.toml - Streamlit configuration
- [x] .streamlit/secrets.toml.example - Secrets template
- [x] pages/ - All 12 dashboard pages
- [x] data/.gitkeep - Data folder placeholder

### Files NOT to Upload (in .gitignore)
- [ ] .env - Local credentials (NEVER upload)
- [ ] .streamlit/secrets.toml - Local secrets (NEVER upload)
- [ ] __pycache__/ - Python cache
- [ ] data/*.csv, *.xlsx, *.json - Data files
- [ ] *.log - Log files
- [ ] venv/ - Virtual environment

## Streamlit Cloud Deployment Steps

### Step 1: Push to GitHub
```bash
cd fiber_app
git init
git add .
git commit -m "Initial commit - Fiber Analytics Dashboard v1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fiber-analytics.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub account if not connected
4. Select repository: fiber-analytics
5. Branch: main
6. Main file path: main.py
7. Click "Deploy"

### Step 3: Configure Secrets (CRITICAL)
1. In Streamlit Cloud, click your app's menu (...)
2. Select "Settings" > "Secrets"
3. Paste your database credentials:

```toml
[database_1]
DB_NAME = "fiber_maintainance_department"
DB_HOST = "YOUR_DATABASE_HOST_IP"
DB_USER = "YOUR_USERNAME"
DB_PASSWORD = "YOUR_PASSWORD"

[database_2]
DB_NAME = "fiber_maintainance_department"
DB_HOST = "BACKUP_HOST_IP"
DB_USER = "YOUR_USERNAME"
DB_PASSWORD = "YOUR_PASSWORD"
```

4. Click "Save"
5. Reboot the app

### Step 4: Database Configuration
Ensure your MySQL server allows connections from Streamlit Cloud:
- Whitelist Streamlit Cloud IP ranges
- Or allow connections from any IP (less secure)
- Enable SSL for database connections (recommended)

## Post-Deployment Verification

1. [ ] App loads without errors
2. [ ] Login page displays correctly
3. [ ] Can register new user
4. [ ] Can login with credentials
5. [ ] Data loads from database
6. [ ] All 11 dashboard pages work
7. [ ] Charts render correctly
8. [ ] Admin panel accessible to admins

## Troubleshooting

### Database Connection Issues
- Check secrets are configured correctly
- Verify database host allows external connections
- Test credentials locally first

### App Crashes
- Check Streamlit Cloud logs
- Verify all dependencies in requirements.txt
- Check for Python version compatibility

### Slow Performance
- Optimize database queries
- Add date range filters
- Consider caching with @st.cache_data

## Security Reminders

- NEVER commit .env or secrets.toml to GitHub
- Use strong passwords
- Regularly rotate database credentials
- Monitor activity logs
- Keep dependencies updated

---
Developed by Joseph Nderitu
josephnderito16@gmail.com
