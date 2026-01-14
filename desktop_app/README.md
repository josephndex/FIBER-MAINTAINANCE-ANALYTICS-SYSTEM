# Fiber Maintenance Analytics - Desktop Application

A modern Electron-based desktop application for fiber network maintenance analytics with **auto-update** capability.

## 📁 Project Structure

```
FIBER-MAINTAINANCE-ANALYTICS-SYSTEM/
├── desktop_app/                    # Desktop application (Electron)
│   └── electron/
│       ├── electron_main.js        # Main Electron process
│       ├── preload.js              # Preload script
│       ├── updater.js              # Auto-update module
│       ├── package.json            # Electron config & build settings
│       ├── build-linux.sh          # Linux build script (automated)
│       ├── python/                 # Bundled Python (created during build)
│       ├── streamlit_app/          # Bundled Streamlit application
│       │   ├── main.py             # Main Streamlit app
│       │   ├── pages/              # All dashboard pages
│       │   ├── components/         # UI components
│       │   └── .env                # Database config (copy from server/)
│       └── assets/                 # App icons
│
├── server/                         # API Server (FastAPI)
│   ├── api_server.py               # REST API backend
│   ├── .env                        # Database configuration
│   └── requirements.txt            # Python dependencies
│
└── mobile_app/                     # Mobile application (React Native)
```

---

## 🚀 Quick Start (Development)

### Prerequisites

- **Node.js 18+**: https://nodejs.org/
- **Python 3.11+**: https://python.org/

### Run in Development Mode

```bash
cd desktop_app/electron
npm install
npm start
```

---

## 🔨 Building for Distribution

### 🐧 Build for Linux (Recommended: Use build script)

```bash
cd desktop_app/electron

# Make script executable and run
chmod +x build-linux.sh
./build-linux.sh
```

This script automatically:
1. Creates a portable Python environment with all dependencies
2. Installs Node.js packages
3. Copies your `.env` configuration
4. Builds AppImage and DEB packages

**Output:**
- `dist/Fiber Maintenance Analytics-2.0.0-linux-x64.AppImage`
- `dist/Fiber Maintenance Analytics-2.0.0-linux-amd64.deb`

**To run:**
```bash
chmod +x dist/*.AppImage
./dist/Fiber\ Maintenance\ Analytics-2.0.0-linux-x64.AppImage
```

**To install DEB:**
```bash
sudo dpkg -i dist/*.deb
```

---

### 🪟 Build for Windows

**Option 1: Manual build (on Windows)**

```bash
cd desktop_app/electron

# 1. Create embedded Python in a short path (avoids path length issues)
cd C:\temp
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip" -OutFile python.zip
Expand-Archive python.zip -DestinationPath python -Force
Remove-Item python.zip

# 2. Enable pip in embedded Python
# Edit python/python311._pth - uncomment "import site" and add "Lib\site-packages"

# 3. Install pip and packages
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile get-pip.py
.\python\python.exe get-pip.py
.\python\python.exe -m pip install streamlit plotly pandas numpy mysql-connector-python python-dotenv bcrypt sqlalchemy requests tqdm openpyxl scipy

# 4. Copy Python to project
Copy-Item -Path "C:\temp\python" -Destination "desktop_app\electron\python" -Recurse -Force

# 5. Build
cd desktop_app\electron
npm install
npm run build:win
```

**Output:** `dist/Fiber Maintenance Analytics-2.0.0-win-x64.exe`

---

### 🍎 Build for macOS

```bash
cd desktop_app/electron

# Create Python environment
python3 -m venv python
source python/bin/activate
pip install streamlit plotly pandas numpy mysql-connector-python python-dotenv bcrypt sqlalchemy requests tqdm openpyxl scipy
deactivate

# Build
npm install
npm run build:mac
```

**Output:** `dist/Fiber Maintenance Analytics-2.0.0-mac-x64.dmg`

---

## ⚙️ Configuration

After building, copy your `.env` file to the app:

```bash
# For unpacked testing
cp server/.env desktop_app/electron/dist/linux-unpacked/resources/streamlit_app/.env

# For Windows
copy server\.env desktop_app\electron\dist\win-unpacked\resources\streamlit_app\.env
```

The `.env` file should contain:
```env
DB_NAME_1=fiber_maintainance_department
DB_HOST_1=your_database_host
DB_USER_1=your_username
DB_PASSWORD_1=your_password
```

---

## 🔄 Auto-Update System

The app includes automatic updates from GitHub Releases.

### How Auto-Update Works

1. When the app starts, it checks GitHub Releases for new versions
2. If an update is available, a dialog prompts the user to download
3. Updates download in the background with a progress bar
4. Once downloaded, the app prompts to restart and install

### Setting Up Auto-Updates

1. **Configure GitHub Repository** in `package.json`:
   ```json
   "publish": {
     "provider": "github",
     "owner": "josephndex",
     "repo": "FIBER-MAINTAINANCE-ANALYTICS-SYSTEM"
   }
   ```

2. **Create a GitHub Personal Access Token**:
   - Go to GitHub → Settings → Developer Settings → Personal Access Tokens
   - Create a token with `repo` scope
   - Set as environment variable: `GH_TOKEN=your_token`

3. **Publish a Release**:
   ```bash
   # Set your GitHub token
   export GH_TOKEN=your_github_token
   
   # Build and publish
   npm run publish:win    # For Windows
   npm run publish:linux  # For Linux
   npm run publish:mac    # For macOS
   npm run publish:all    # For all platforms
   ```

---

## 📦 Releasing Updates

### Step-by-Step Release Process

1. **Update Version Number** in `package.json`:
   ```json
   "version": "2.1.0"
   ```

2. **Commit and Tag**:
   ```bash
   git add .
   git commit -m "Release v2.1.0"
   git tag v2.1.0
   git push origin main --tags
   ```

3. **Build and Publish**:
   ```bash
   export GH_TOKEN=your_github_token
   npm run publish:win
   ```

4. **Verify on GitHub**:
   - Go to your repository's Releases page
   - You should see a new release with the installer files
   - Users with the app installed will automatically receive the update

### Version Numbering (Semantic Versioning)

- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, minor improvements

Example:
- `2.0.0` → `2.0.1` (bug fix)
- `2.0.1` → `2.1.0` (new feature)
- `2.1.0` → `3.0.0` (major redesign)

---

## 🖼️ Custom Icons

Replace the placeholder icons in `assets/`:

| File | Format | Size | Platform |
|------|--------|------|----------|
| `icon.png` | PNG | 512x512 | Linux |
| `icon.ico` | ICO | Multi-size | Windows |
| `icon.icns` | ICNS | Multi-size | macOS |

### Creating Icons

Use an online tool like https://www.icoconvert.com/ or https://iconverticons.com/ to convert your PNG to ICO and ICNS formats.

---

## ⚙️ Configuration

### Server URL

Edit `electron_main.js` to change the API server URL:

```javascript
const CONFIG = {
    serverUrl: 'http://100.83.80.26:8000',
    // ...
};
```

### Window Size

```javascript
const CONFIG = {
    windowWidth: 1400,
    windowHeight: 900,
    minWidth: 1200,
    minHeight: 700,
    // ...
};
```

---

## 🔧 Bundling Python (Advanced)

For fully self-contained distribution without requiring Python installation:

### Option 1: Embed Python

1. Download Python embeddable package from https://python.org/downloads/
2. Extract to `desktop_app/electron/python/`
3. Install dependencies:
   ```bash
   cd python
   ./python.exe -m pip install streamlit plotly pandas numpy requests
   ```
4. The app will automatically detect and use the bundled Python

### Option 2: Use PyInstaller

Bundle the Streamlit app separately and launch it from Electron.

---

## 🐛 Troubleshooting

### "Python not found"

Ensure Python is installed and in your PATH:
```bash
python --version  # Should show Python 3.8+
```

### "Streamlit not found"

Install Streamlit:
```bash
pip install streamlit
```

### "Cannot connect to API server"

1. Ensure the server is running: `cd server && python api_server.py`
2. Check the server URL in `electron_main.js`
3. Verify network connectivity to `100.83.80.26:8000`

### Build fails on Windows

Install Windows Build Tools:
```bash
npm install --global windows-build-tools
```

### Build fails on Linux

Install required libraries:
```bash
sudo apt-get install build-essential libgtk-3-dev libnotify-dev libnss3 libxss1
```

---

## 📄 License

MIT License - Fireside Communications Kenya Ltd

---

## 👨‍💻 Author

**Joseph Nderitu**
- Email: josephnderito16@gmail.com
- GitHub: [@josephndex](https://github.com/josephndex)
