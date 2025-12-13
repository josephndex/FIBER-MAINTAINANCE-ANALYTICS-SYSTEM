# Fiber Maintenance Analytics System

A comprehensive analytics platform for fiber network maintenance operations with desktop and mobile applications.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Server (FastAPI)                      ││
│  │  - REST API for data access                                 ││
│  │  - JWT Authentication                                       ││
│  │  - Database connections                                     ││
│  │  - Running at: http://100.83.80.26:8000                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MySQL Database                            ││
│  │  - engineered_tickets                                       ││
│  │  - app_users                                                ││
│  │  - activity_logs                                            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                               │
                    REST API (HTTPS)
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  Desktop App  │      │  Mobile App   │      │  Web Browser  │
│  (Electron)   │      │  (React Native)│     │  (Streamlit)  │
│  Win/Mac/Linux│      │  Android/iOS  │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
```

## 📁 Project Structure

```
FIBER-MAINTAINANCE-ANALYTICS-SYSTEM/
│
├── server/                     # Backend API Server
│   ├── api_server.py           # FastAPI REST API
│   ├── .env                    # Database configuration
│   ├── requirements.txt        # Python dependencies
│   └── start.sh / start.bat    # Startup scripts
│
├── desktop_app/                # Desktop Application
│   └── electron/               # Electron app with Streamlit
│       ├── electron_main.js    # Main process
│       ├── package.json        # Build configuration
│       ├── streamlit_app/      # Bundled Streamlit app
│       └── dist/               # Built executables
│
└── mobile_app/                 # Mobile Application
    └── (React Native project)
```

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd server
pip install -r requirements.txt
python api_server.py
```

Server runs at: http://100.83.80.26:8000

### 2. Run Desktop App (Development)

```bash
cd desktop_app/electron
npm install
npm start
```

### 3. Build Desktop App (Distribution)

```bash
cd desktop_app/electron
npm run build:win    # Windows EXE
npm run build:linux  # Linux AppImage
npm run build:mac    # macOS DMG
```

## 📊 Features

### Dashboard Pages (17+)
- **Home** - Executive overview with key metrics
- **KPI Dashboard** - Performance indicators with gauges
- **CEO Dashboard** - High-level summary for executives
- **Engineer Performance** - Individual engineer metrics
- **Dispatcher Performance** - Dispatch efficiency analysis
- **Regional Analysis** - Geographic performance breakdown
- **Service Analysis** - Service type analytics
- **Trends** - Temporal pattern analysis
- **SLA Analysis** - Service level compliance
- **Challenges** - Root cause analysis
- **Recurring Issues** - Pattern detection
- **Predictions** - ML-based forecasting
- **Ticket Search** - Advanced search functionality
- **Reports** - PDF/Excel export
- **Comparison** - Period-over-period analysis

### Technical Features
- 🔐 JWT Authentication
- 📊 Interactive Plotly Charts
- 🔄 Auto-Updates (Desktop)
- 🌙 Dark Theme
- 📱 Responsive Design
- 📥 Data Export (PDF, Excel, CSV)

## 🔄 Auto-Updates

The desktop app automatically checks for updates from GitHub Releases.

### Publishing Updates

1. Update version in `package.json`
2. Build and publish:
   ```bash
   export GH_TOKEN=your_github_token
   npm run publish:win
   ```
3. Users receive update notification automatically

See `desktop_app/README.md` for detailed instructions.

## 📱 Mobile App

Coming soon! React Native app for Android/iOS.

```bash
cd mobile_app
npm install
npm run android  # For Android
npm run ios      # For iOS
```

## 🔧 Configuration

### Server URL
Default: `http://100.83.80.26:8000`

Configure in:
- Desktop: `desktop_app/electron/electron_main.js`
- Mobile: `mobile_app/src/config.js`

### Database
Configure in `server/.env`:
```env
DB_HOST=100.83.80.26
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=fiber_maintainance_department
```

## 📄 License

MIT License - Fireside Communications Kenya Ltd

## 👨‍💻 Author

**Joseph Nderitu**
- Email: josephnderito16@gmail.com
- GitHub: [@josephndex](https://github.com/josephndex)

# force trigger
