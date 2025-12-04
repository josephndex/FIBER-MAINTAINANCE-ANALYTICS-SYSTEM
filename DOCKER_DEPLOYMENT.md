# Docker Deployment Guide - Fiber Maintenance Analytics System

## Overview

This guide will help you deploy the Fiber Maintenance Analytics System using Docker on your Windows PC. The app will run in a Docker container while connecting to your MySQL database running on the Windows host.

---

## Prerequisites

### On Your Windows PC:
1. **Docker Desktop** installed and running
2. **MySQL Server** running with your database (`fiber_maintainance_department`)
3. **Git** (optional, for cloning the project)

### MySQL Configuration (IMPORTANT!)

Your MySQL must accept connections from Docker containers. Run these commands in MySQL:

```sql
-- Allow connections from Docker containers
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'Fireside.Africa1or!';
GRANT ALL PRIVILEGES ON fiber_maintainance_department.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

Also ensure MySQL is configured to listen on all interfaces:
- Edit `my.ini` (usually in `C:\ProgramData\MySQL\MySQL Server 8.0\`)
- Change: `bind-address = 0.0.0.0`
- Restart MySQL service

---

## Deployment Steps

### Step 1: Transfer Project to Windows PC

Copy the entire project folder to your Windows PC. You can:
- Use USB drive
- Use cloud storage (Google Drive, OneDrive)
- Use `scp` or `rsync` if you have SSH access
- Use Git (push to GitHub from Linux, pull on Windows)

### Step 2: Open Command Prompt/PowerShell

Navigate to the project folder:

```powershell
cd C:\path\to\FIBER-MAINTAINANCE-ANALYTICS-SYSTEM
```

### Step 3: Build the Docker Image

```powershell
docker-compose build
```

This will take a few minutes the first time as it downloads Python and installs dependencies.

### Step 4: Start the Application

```powershell
docker-compose up -d
```

The `-d` flag runs it in the background (detached mode).

### Step 5: Access the Application

Open your browser and go to:
```
http://localhost:8501
```

The app should be running!

---

## Making it Accessible to Everyone on the Network

### Option 1: Local Network Access (Same WiFi/LAN)

1. **Find your Windows PC's IP address:**
   ```powershell
   ipconfig
   ```
   Look for `IPv4 Address` (e.g., `192.168.1.100`)

2. **Open Windows Firewall for port 8501:**
   ```powershell
   netsh advfirewall firewall add rule name="Fiber Analytics" dir=in action=allow protocol=tcp localport=8501
   ```

3. **Users on the same network can access:**
   ```
   http://192.168.1.100:8501
   ```

### Option 2: Internet Access (Outside Network)

To make the app accessible from the internet:

1. **Port Forwarding on Router:**
   - Login to your router (usually `192.168.1.1`)
   - Add port forwarding rule: External port `8501` → Internal IP:port `192.168.1.100:8501`

2. **Or use a tunneling service like ngrok:**
   ```powershell
   # Install ngrok, then run:
   ngrok http 8501
   ```
   This gives you a public URL like `https://abc123.ngrok.io`

---

## Useful Docker Commands

### Check if container is running:
```powershell
docker ps
```

### View logs:
```powershell
docker-compose logs -f
```

### Stop the application:
```powershell
docker-compose down
```

### Restart the application:
```powershell
docker-compose restart
```

### Rebuild after code changes:
```powershell
docker-compose build --no-cache
docker-compose up -d
```

### View container resource usage:
```powershell
docker stats fiber-maintenance-analytics
```

---

## Troubleshooting

### Issue: "Cannot connect to database"

1. **Check MySQL is running:**
   - Open Services (`services.msc`) and ensure MySQL is running

2. **Check MySQL allows remote connections:**
   ```sql
   SELECT user, host FROM mysql.user WHERE user='root';
   -- Should show 'root'@'%' or 'root'@'localhost'
   ```

3. **Test connection from Docker:**
   ```powershell
   docker run --rm -it mysql:8 mysql -h host.docker.internal -u root -p
   ```

### Issue: "Port 8501 already in use"

1. **Find what's using the port:**
   ```powershell
   netstat -ano | findstr :8501
   ```

2. **Kill the process or change port in docker-compose.yml:**
   ```yaml
   ports:
     - "8502:8501"  # Use port 8502 instead
   ```

### Issue: "Docker build fails"

1. **Ensure Docker Desktop is running**
2. **Check internet connection**
3. **Try building with no cache:**
   ```powershell
   docker-compose build --no-cache
   ```

---

## Environment Variables

The `docker-compose.yml` includes all database credentials. To change them:

1. Edit `docker-compose.yml`
2. Update the `environment` section
3. Rebuild: `docker-compose up -d --build`

---

## Updating the Application

When you make code changes:

1. **Copy updated files to Windows PC**
2. **Rebuild and restart:**
   ```powershell
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

---

## Security Notes

1. **Never commit `.env` with real passwords to Git**
2. **Use strong database passwords**
3. **Consider using HTTPS (SSL) for production**
4. **Regularly update Docker images for security patches**

---

## Quick Start Summary

```powershell
# 1. Navigate to project
cd C:\path\to\FIBER-MAINTAINANCE-ANALYTICS-SYSTEM

# 2. Build image
docker-compose build

# 3. Start container
docker-compose up -d

# 4. Access app
# Open browser: http://localhost:8501

# 5. Check logs if issues
docker-compose logs -f
```

---

## Contact

For issues or questions, contact: **Joseph Nderitu** (josephnderito16@gmail.com)
