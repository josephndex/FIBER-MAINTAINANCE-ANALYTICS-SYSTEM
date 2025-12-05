# Fiber Maintenance Analytics System - Docker Image
# OPTIMIZED FOR 16GB MACHINE WITH 5-10 CONCURRENT USERS
# Based on Python 3.11 slim for smaller image size

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ============ OPTIMIZED ENVIRONMENT VARIABLES ============
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION=true \
    STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200 \
    STREAMLIT_CLIENT_TOOLBAR_MODE=minimal

# Install system dependencies required for MySQL connector and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir mysql-connector-python && \
    python -m compileall -q /usr/local/lib/python3.11/

# Copy application code
COPY . .

# Pre-compile Python files for faster startup
RUN python -m compileall -q .

# Create data directory
RUN mkdir -p /app/data

# Expose the Streamlit port
EXPOSE 8501

# Health check to ensure the container is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit with OPTIMIZED settings for multi-user on 16GB machine
CMD ["streamlit", "run", "main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--server.enableWebsocketCompression=true", \
     "--server.maxMessageSize=200", \
     "--browser.gatherUsageStats=false", \
     "--client.toolbarMode=minimal"]
