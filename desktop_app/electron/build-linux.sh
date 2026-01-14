#!/bin/bash
# =============================================================
# Fiber Maintenance Analytics - Linux Build Script
# =============================================================
# This script bundles Python with all dependencies and builds
# the Electron app for Linux (AppImage + DEB)
# =============================================================

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "  Fiber Maintenance Analytics - Linux Build"
echo "=================================================="

# Step 1: Check prerequisites
echo ""
echo "[1/6] Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Install it from https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    exit 1
fi

echo "✓ Node.js: $(node --version)"
echo "✓ npm: $(npm --version)"
echo "✓ Python: $(python3 --version)"

# Step 2: Create portable Python environment
echo ""
echo "[2/6] Creating portable Python environment..."

# Remove old python folder if exists
rm -rf python

# Create virtual environment
python3 -m venv python

# Activate and install packages
source python/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip
pip install streamlit plotly pandas numpy mysql-connector-python \
    python-dotenv bcrypt sqlalchemy requests tqdm openpyxl scipy

deactivate

echo "✓ Python environment created with all dependencies"

# Step 3: Install Node dependencies
echo ""
echo "[3/6] Installing Node.js dependencies..."
npm install

echo "✓ Node dependencies installed"

# Step 4: Copy .env file if exists in server folder
echo ""
echo "[4/6] Setting up configuration..."

if [ -f "../../../server/.env" ]; then
    cp "../../../server/.env" "streamlit_app/.env"
    echo "✓ Copied .env from server folder"
else
    echo "⚠ No .env file found in server folder"
    echo "  Create streamlit_app/.env with your database credentials"
fi

# Step 5: Build the app
echo ""
echo "[5/6] Building Linux packages..."
npm run build:linux

echo "✓ Build complete!"

# Step 6: Copy .env to built app
echo ""
echo "[6/6] Finalizing..."

if [ -f "streamlit_app/.env" ]; then
    cp "streamlit_app/.env" "dist/linux-unpacked/resources/streamlit_app/.env" 2>/dev/null || true
    echo "✓ Configuration copied to build"
fi

echo ""
echo "=================================================="
echo "  BUILD SUCCESSFUL!"
echo "=================================================="
echo ""
echo "Output files in dist/:"
ls -lh dist/*.AppImage dist/*.deb 2>/dev/null || echo "  (check dist/ folder)"
echo ""
echo "To run the AppImage:"
echo "  chmod +x dist/*.AppImage"
echo "  ./dist/Fiber*.AppImage"
echo ""
echo "To install the DEB package:"
echo "  sudo dpkg -i dist/*.deb"
echo ""
