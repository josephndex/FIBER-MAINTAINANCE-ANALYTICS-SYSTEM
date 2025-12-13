# Fiber Maintenance Analytics - API Server

This folder is **self-contained** and contains everything needed to run the API server.
Deploy this entire folder to your server to serve data to desktop clients.

## 📁 Files Included

| File | Description |
|------|-------------|
| `api_server.py` | Main API server application |
| `requirements.txt` | Python dependencies |
| `.env` | Database credentials (configure this!) |
| `.env.example` | Template for environment variables |
| `start.sh` | Linux/Mac startup script |
| `start.bat` | Windows startup script |
| `README.md` | This documentation |

## 🚀 Quick Start

### Option 1: Using Startup Script (Recommended)

**On Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**On Windows:**
```batch
start.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env file (edit with your credentials)
cp .env.example .env
nano .env

# 4. Start the server
python api_server.py
```

## ⚙️ Configuration

Edit the `.env` file with your database credentials:

```env
# Primary Database (default)
DB_NAME_1=fiber_maintainance_department
DB_HOST_1=your_database_host
DB_USER_1=your_database_user
DB_PASSWORD_1=your_database_password

# Secondary Database (optional)
DB_NAME_2=fiber_maintainance_department
DB_HOST_2=localhost
DB_USER_2=root
DB_PASSWORD_2=your_password
```

The server will start on `http://0.0.0.0:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI:** http://your-server:8000/docs
- **ReDoc:** http://your-server:8000/redoc

## 🔧 API Endpoints

### Health Check
```
GET /health
```

### Authentication
```
POST /auth/login
POST /auth/register
POST /auth/logout
GET /auth/verify?token=xxx
```

### Data
```
POST /data/tickets
GET /data/summary
GET /data/columns
```

### Admin
```
GET /admin/users
GET /admin/activity-logs
```

## 🔐 Security Notes

- Uses token-based authentication (24-hour expiry)
- Passwords hashed with bcrypt
- Use HTTPS in production (configure nginx/apache as reverse proxy)
- Restrict firewall to only allow port 8000 from trusted IPs

## 🐳 Docker Deployment (Optional)

```bash
docker build -t fiber-api-server .
docker run -p 8000:8000 -v $(pwd)/.env:/app/.env fiber-api-server
```
- Connection recycling every 30 minutes
- 60-second timeout for slow queries

## 🛠️ Configuration Options

Environment variables:
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `DB_NAME_1`: Database name for config 1
- `DB_HOST_1`: Database host for config 1
- `DB_USER_1`: Database user for config 1
- `DB_PASSWORD_1`: Database password for config 1
