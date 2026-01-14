# Copilot Instructions - Fiber Maintenance Analytics System

## Architecture Overview

This is a **multi-platform analytics system** for fiber network maintenance with three client applications sharing a central API server:

```
server/api_server.py (FastAPI) ← MySQL Database
     ↓ REST API + JWT Auth
┌────┴────┬────────────────┐
Desktop   Mobile           Web
(Electron (React Native/   (Streamlit
+Streamlit) Expo)          Cloud)
```

- **Server**: FastAPI at `http://100.83.80.26:8000` with MySQL backend, JWT authentication
- **Desktop**: Electron wrapper running bundled Streamlit app (Python) with auto-update via GitHub Releases
- **Mobile**: React Native + Expo with EAS Build for Android/iOS
- **Data**: Main table is `engineered_tickets` with `app_users` for auth and `activity_logs` for auditing

## Key Conventions

### Database Credentials Pattern
All apps use numbered environment variables (`DB_NAME_1`, `DB_HOST_1`, etc.) supporting multiple database configs:
```python
# config.py / data_loader.py pattern
db_name = os.environ.get(f'DB_NAME_{db_config}')
```
Priority: Environment Variables → Streamlit Secrets → `.env` file

### Authentication Flow
- Server: JWT tokens via `/auth/login`, `/auth/verify` endpoints
- Desktop (Streamlit): Session-based auth via `auth.py` with position-based access control
- Mobile: Secure token storage via `expo-secure-store`
- Positions: `MANAGEMENT`, `ENGINEER`, `NOC` with page-level access defined in `auth.py:POSITIONS`

### Streamlit Page Structure
Pages live in `desktop_app/electron/streamlit_app/pages/` with numbered prefixes for ordering:
```
0_Login.py → 1_Home.py → 2_KPI_Dashboard.py → ... → 21_Suggestions.py
```
Each page must start with:
```python
from auth import require_authentication, require_page_access, log_page_visit
require_authentication()
require_page_access("1_Home.py")  # Use exact filename
log_page_visit("1_Home.py")
```

### Theme & Styling
Use the consistent dark theme from `config.py:THEME_COLORS`:
- Primary: `#f97316` (orange), Secondary: `#a855f7` (purple), Accent: `#667eea` (blue)
- All Plotly charts should use `paper_bgcolor='rgba(0,0,0,0)'` and `plot_bgcolor='rgba(0,0,0,0)'`

## Developer Workflows

### Running Locally
```bash
# API Server (required first)
cd server && python api_server.py  # Runs on :8000

# Desktop App (dev mode)
cd desktop_app/electron && npm start  # Spawns Streamlit on :8501

# Mobile App
cd mobile_app && npm start  # Expo dev server
```

### Building Desktop Distributables
```bash
cd desktop_app/electron
npm run build:win    # → dist/*.exe (NSIS installer)
npm run build:linux  # → dist/*.AppImage, *.deb
npm run publish:win  # Builds + uploads to GitHub Releases (triggers auto-update)
```

### Mobile Builds
```bash
cd mobile_app
npm run build:apk    # EAS cloud build for Android
npx eas-cli build --platform ios  # iOS build
```

## Project-Specific Patterns

### Data Loading (Desktop/Streamlit)
Always use cached functions from `data_loader.py`:
```python
from utils import load_data_from_db, prepare_dataframe
df = load_data_from_db(start_date, end_date, db_config=1)
df = prepare_dataframe(df)  # Adds computed columns, cleans data
```
Use `@st.cache_resource` for database engines, `@st.cache_data` for query results.

### Excluded Engineers
Filter out non-field personnel defined in `config.py:EXCLUDED_ENGINEERS` before analysis.

### SLA Calculations
- 24-hour resolution target (`config.py:SLA_TARGET_HOURS`)
- Grades: A+ (≥98%), A (≥95%), B (≥90%), C (≥85%), F (<85%)

### Metric Cards (Streamlit)
Use the `render_metric_card()` pattern with inline HTML/CSS, not Streamlit's `st.metric`:
```python
render_metric_card("Total Tickets", "1,234", subtitle="This Period", color="primary")
```

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Database connectivity check |
| `/auth/login` | POST | Returns JWT token |
| `/auth/verify` | GET | Token validation |
| `/data/tickets` | POST | Main data query (requires date range) |
| `/data/summary` | GET | Aggregate statistics |

## Important Files

- [server/api_server.py](server/api_server.py) - All API endpoints and database logic
- [desktop_app/electron/streamlit_app/config.py](desktop_app/electron/streamlit_app/config.py) - Constants, thresholds, excluded engineers
- [desktop_app/electron/streamlit_app/auth.py](desktop_app/electron/streamlit_app/auth.py) - Position definitions, page access control
- [desktop_app/electron/electron_main.js](desktop_app/electron/electron_main.js) - Desktop app lifecycle, Streamlit process management
- [mobile_app/src/config.js](mobile_app/src/config.js) - Mobile API URL and theme colors

## Notes

- Desktop app bundles Python environment for distribution (see `package.json:extraResources`)
- Auto-updates published to GitHub repo `josephndex/FIBER-MAINTAINANCE-ANALYTICS-SYSTEM`
- Server hardcoded to `100.83.80.26:8000` (Tailscale network IP)
