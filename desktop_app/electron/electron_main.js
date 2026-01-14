/**
 * Fiber Maintenance Analytics - Electron Desktop Application
 * Version 2.0.0
 * 
 * This creates a native desktop window that runs the Streamlit app
 * with full JavaScript support via Chromium.
 * 
 * Features:
 * - Bundled Python environment (portable)
 * - Auto-updates from GitHub Releases
 * - System tray support
 * - Native menus and shortcuts
 */

const { app, BrowserWindow, Menu, shell, dialog, ipcMain, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const http = require('http');
const fs = require('fs');

// Auto-updater (only in production)
let AppUpdater = null;
let appUpdater = null;
if (app.isPackaged) {
    try {
        const { AppUpdater: Updater } = require('./updater');
        AppUpdater = Updater;
    } catch (e) {
        console.log('Auto-updater not available:', e.message);
    }
}

// Configuration
const CONFIG = {
    streamlitPort: 8501,
    streamlitHost: 'localhost',
    serverUrl: 'http://100.83.80.26:8000',
    windowWidth: 1400,
    windowHeight: 900,
    minWidth: 1200,
    minHeight: 700,
    appName: 'Fiber Maintenance Analytics'
};

let mainWindow = null;
let splashWindow = null;
let streamlitProcess = null;
let tray = null;

// Get the base path for resources
function getResourcePath() {
    if (app.isPackaged) {
        return process.resourcesPath;
    }
    return __dirname;
}

// Get the Streamlit app path
function getStreamlitAppPath() {
    const resourcePath = getResourcePath();
    
    // Check bundled streamlit_app folder first
    const bundledPath = path.join(resourcePath, 'streamlit_app');
    if (fs.existsSync(path.join(bundledPath, 'main.py'))) {
        return bundledPath;
    }
    
    // Development: look in the streamlit_app folder
    const devPath = path.join(__dirname, 'streamlit_app');
    if (fs.existsSync(path.join(devPath, 'main.py'))) {
        return devPath;
    }
    
    // Fallback to parent directories
    const parentPath = path.join(__dirname, '..', '..');
    if (fs.existsSync(path.join(parentPath, 'main.py'))) {
        return parentPath;
    }
    
    return null;
}

// Get the bundled Python path or system Python
function getPythonPath() {
    const resourcePath = getResourcePath();
    
    // Check for bundled Python (Windows)
    const bundledPythonWin = path.join(resourcePath, 'python', 'python.exe');
    if (fs.existsSync(bundledPythonWin)) {
        return bundledPythonWin;
    }
    
    // Check for bundled Python (Linux/Mac)
    const bundledPythonUnix = path.join(resourcePath, 'python', 'bin', 'python3');
    if (fs.existsSync(bundledPythonUnix)) {
        return bundledPythonUnix;
    }
    
    // Fall back to system Python
    return findSystemPython();
}

// Find system Python
function findSystemPython() {
    const commands = process.platform === 'win32' 
        ? ['python', 'python3', 'py']
        : ['python3', 'python'];
    
    for (const cmd of commands) {
        try {
            const result = spawnSync(cmd, ['--version'], { encoding: 'utf8' });
            if (result.status === 0) {
                console.log(`Found system Python: ${cmd} (${result.stdout.trim()})`);
                return cmd;
            }
        } catch (e) {
            continue;
        }
    }
    
    return 'python';
}

// Check if port is available
function isPortAvailable(port) {
    return new Promise((resolve) => {
        const server = require('net').createServer();
        server.once('error', () => resolve(false));
        server.once('listening', () => {
            server.close();
            resolve(true);
        });
        server.listen(port, 'localhost');
    });
}

// Find available port
async function findAvailablePort(startPort) {
    let port = startPort;
    while (port < startPort + 100) {
        if (await isPortAvailable(port)) {
            return port;
        }
        port++;
    }
    return startPort;
}

// Check if Streamlit is ready
function checkStreamlitReady(port, callback, retries = 60, delay = 500) {
    const checkHealth = () => {
        const req = http.get(`http://${CONFIG.streamlitHost}:${port}/_stcore/health`, (res) => {
            if (res.statusCode === 200) {
                callback(true);
            } else if (retries > 0) {
                retries--;
                setTimeout(checkHealth, delay);
            } else {
                callback(false);
            }
        });
        
        req.on('error', () => {
            if (retries > 0) {
                retries--;
                setTimeout(checkHealth, delay);
            } else {
                callback(false);
            }
        });
        
        req.end();
    };
    
    checkHealth();
}

// Start Streamlit process
async function startStreamlit() {
    const appDir = getStreamlitAppPath();
    if (!appDir) {
        throw new Error('Streamlit app not found! Please ensure main.py is in the streamlit_app folder.');
    }

    // Try to find bundled binary first
    let binaryName = 'fiber_maintenance_analytics';
    if (process.platform === 'win32') binaryName += '.exe';
    const bundledBinary = path.join(appDir, binaryName);
    const useBundled = fs.existsSync(bundledBinary);

    // Find available port
    let port = CONFIG.streamlitPort;
    if (!(await isPortAvailable(port))) {
        port = await findAvailablePort(port);
        console.log(`Port ${CONFIG.streamlitPort} in use, using ${port}`);
    }
    CONFIG.streamlitPort = port;

    return new Promise((resolve, reject) => {
        // Prepare environment
        const env = {
            ...process.env,
            STREAMLIT_SERVER_PORT: port.toString(),
            STREAMLIT_BROWSER_GATHER_USAGE_STATS: 'false',
            STREAMLIT_THEME_BASE: 'dark',
            API_SERVER_URL: CONFIG.serverUrl,
            PYTHONUNBUFFERED: '1'
        };

        let child, args;
        if (useBundled) {
            // Run the bundled binary directly
            console.log(`Launching bundled binary: ${bundledBinary}`);
            args = ['--server.port', port.toString(), '--server.address', CONFIG.streamlitHost, '--server.headless', 'true'];
            child = spawn(bundledBinary, args, {
                cwd: appDir,
                env: env,
                stdio: ['ignore', 'pipe', 'pipe']
            });
        } else {
            // Fallback to old method (system Python)
            const pythonPath = getPythonPath();
            const mainPyPath = path.join(appDir, 'main.py');
            console.log(`Python: ${pythonPath}`);
            console.log(`App directory: ${appDir}`);
            console.log(`Main script: ${mainPyPath}`);
            args = [
                '-m', 'streamlit', 'run',
                mainPyPath,
                '--server.port', port.toString(),
                '--server.address', CONFIG.streamlitHost,
                '--server.headless', 'true',
                '--browser.gatherUsageStats', 'false',
                '--theme.base', 'dark'
            ];
            child = spawn(pythonPath, args, {
                cwd: appDir,
                env: env,
                stdio: ['ignore', 'pipe', 'pipe']
            });
        }

        streamlitProcess = child;
        streamlitProcess.stdout.on('data', (data) => {
            console.log(`[Streamlit] ${data.toString().trim()}`);
        });
        streamlitProcess.stderr.on('data', (data) => {
            console.log(`[Streamlit] ${data.toString().trim()}`);
        });
        streamlitProcess.on('error', (err) => {
            console.error('Failed to start Streamlit:', err);
            reject(err);
        });
        streamlitProcess.on('close', (code) => {
            console.log(`Streamlit process exited with code ${code}`);
            streamlitProcess = null;
        });

        // Wait for Streamlit to be ready
        checkStreamlitReady(port, (ready) => {
            if (ready) {
                console.log('Streamlit is ready!');
                resolve(port);
            } else {
                reject(new Error('Streamlit failed to start within timeout'));
            }
        });
    });
}

// Stop Streamlit process
function stopStreamlit() {
    if (streamlitProcess) {
        console.log('Stopping Streamlit...');
        
        if (process.platform === 'win32') {
            spawn('taskkill', ['/pid', streamlitProcess.pid, '/f', '/t']);
        } else {
            streamlitProcess.kill('SIGTERM');
        }
        
        streamlitProcess = null;
    }
}

// Create splash/loading window
function createSplashWindow() {
    splashWindow = new BrowserWindow({
        width: 500,
        height: 350,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        resizable: false,
        skipTaskbar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });
    
    const splashHTML = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: white;
                border-radius: 20px;
                overflow: hidden;
                -webkit-app-region: drag;
            }
            .container { text-align: center; padding: 40px; }
            .logo { font-size: 48px; margin-bottom: 20px; }
            h1 {
                font-size: 22px;
                background: linear-gradient(135deg, #f97316, #a855f7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            h2 { font-size: 12px; color: #94a3b8; font-weight: normal; margin-bottom: 35px; }
            .loader {
                width: 200px;
                height: 4px;
                background: rgba(255,255,255,0.1);
                border-radius: 2px;
                overflow: hidden;
                margin: 0 auto;
            }
            .loader-bar {
                width: 30%;
                height: 100%;
                background: linear-gradient(90deg, #f97316, #a855f7);
                border-radius: 2px;
                animation: loading 1.5s infinite;
            }
            @keyframes loading {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(400%); }
            }
            .status { margin-top: 20px; font-size: 11px; color: #64748b; }
            .version { margin-top: 30px; font-size: 10px; color: #475569; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🔧</div>
            <h1>${CONFIG.appName}</h1>
            <h2>Desktop Application</h2>
            <div class="loader"><div class="loader-bar"></div></div>
            <div class="status" id="status">Starting application...</div>
            <div class="version">v${require('./package.json').version}</div>
        </div>
        <script>
            const { ipcRenderer } = require('electron');
            ipcRenderer.on('splash-status', (event, text) => {
                document.getElementById('status').textContent = text;
            });
        </script>
    </body>
    </html>
    `;
    
    splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`);
}

// Update splash status
function updateSplashStatus(text) {
    if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.webContents.send('splash-status', text);
    }
}

// Create the main application window
function createMainWindow(port) {
    mainWindow = new BrowserWindow({
        width: CONFIG.windowWidth,
        height: CONFIG.windowHeight,
        minWidth: CONFIG.minWidth,
        minHeight: CONFIG.minHeight,
        show: false,
        title: CONFIG.appName,
        icon: path.join(__dirname, 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        backgroundColor: '#0f172a'
    });
    
    // Create application menu
    createAppMenu(port);
    
    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
    
    // When ready to show
    mainWindow.once('ready-to-show', () => {
        if (splashWindow && !splashWindow.isDestroyed()) {
            splashWindow.close();
            splashWindow = null;
        }
        mainWindow.show();
        mainWindow.focus();
        
        // Check for updates after window is shown (in production)
        if (AppUpdater && app.isPackaged) {
            setTimeout(() => {
                appUpdater = new AppUpdater(mainWindow);
                appUpdater.checkForUpdatesSilent();
            }, 5000);
        }
    });
    
    // Handle window close
    mainWindow.on('close', (event) => {
        if (tray) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
    
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
    
    // Load the Streamlit app
    mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}`);
}

// Create application menu
function createAppMenu(port) {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Refresh',
                    accelerator: 'CmdOrCtrl+R',
                    click: () => mainWindow.reload()
                },
                { type: 'separator' },
                {
                    label: 'Check for Updates',
                    click: () => {
                        if (appUpdater) {
                            appUpdater.checkForUpdates();
                        } else {
                            dialog.showMessageBox(mainWindow, {
                                type: 'info',
                                title: 'Updates',
                                message: 'Auto-updates are only available in the installed version.'
                            });
                        }
                    }
                },
                { type: 'separator' },
                {
                    label: 'Exit',
                    accelerator: 'CmdOrCtrl+Q',
                    click: () => {
                        tray = null;
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'View',
            submenu: [
                {
                    label: 'Toggle Fullscreen',
                    accelerator: 'F11',
                    click: () => mainWindow.setFullScreen(!mainWindow.isFullScreen())
                },
                { type: 'separator' },
                {
                    label: 'Zoom In',
                    accelerator: 'CmdOrCtrl+Plus',
                    click: () => {
                        const zoom = mainWindow.webContents.getZoomFactor();
                        mainWindow.webContents.setZoomFactor(Math.min(zoom + 0.1, 3));
                    }
                },
                {
                    label: 'Zoom Out',
                    accelerator: 'CmdOrCtrl+-',
                    click: () => {
                        const zoom = mainWindow.webContents.getZoomFactor();
                        mainWindow.webContents.setZoomFactor(Math.max(zoom - 0.1, 0.5));
                    }
                },
                {
                    label: 'Reset Zoom',
                    accelerator: 'CmdOrCtrl+0',
                    click: () => mainWindow.webContents.setZoomFactor(1)
                },
                { type: 'separator' },
                {
                    label: 'Developer Tools',
                    accelerator: 'F12',
                    click: () => mainWindow.webContents.toggleDevTools()
                }
            ]
        },
        {
            label: 'Navigate',
            submenu: [
                { label: 'Home', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/Home`) },
                { label: 'KPI Dashboard', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/KPI_Dashboard`) },
                { label: 'CEO Dashboard', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/CEO_Dashboard`) },
                { type: 'separator' },
                { label: 'Engineer Performance', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/Engineer_Performance`) },
                { label: 'Regional Analysis', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/Regional_Analysis`) },
                { label: 'Trends', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/Trends`) }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'About',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'About',
                            message: CONFIG.appName,
                            detail: `Version: ${require('./package.json').version}\n\nDeveloped by Joseph Nderitu\njosephnderito16@gmail.com\n\n© 2024 Fireside Communications Kenya Ltd`
                        });
                    }
                },
                { label: 'Help', click: () => mainWindow.loadURL(`http://${CONFIG.streamlitHost}:${port}/Help`) },
                { type: 'separator' },
                {
                    label: 'Report Issue',
                    click: () => shell.openExternal('mailto:josephnderito16@gmail.com?subject=Fiber%20Analytics%20Issue')
                },
                {
                    label: 'GitHub Repository',
                    click: () => shell.openExternal('https://github.com/josephndex/FIBER-MAINTAINANCE-ANALYTICS-SYSTEM')
                }
            ]
        }
    ];
    
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Create system tray
function createTray(port) {
    const iconPath = path.join(__dirname, 'assets', 'icon.png');
    let icon;
    
    if (fs.existsSync(iconPath)) {
        icon = nativeImage.createFromPath(iconPath);
    } else {
        // Create a simple colored icon
        icon = nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKPSURBVFiF7ZdNaBNBFMd/s5tNmjQftWJrrWAPihU/QFFQwYsHRcSDInjwIngQPHjQi+jFi3jQi6AHD4IIXgQPggiCIIgiIogiKH5RrYq2JjVpsiY7HjZJE9tstzWxoH8YZnbem/ntzL6ZXfjPPwLB31j0H8DyBFXUqUMg3YlN7BKQjzL6t9UaDVuRGLqCzxMo+SJ2lQy3oFoQRYogjqaoV4FKhAdRQnNJzY2GRgkY0gm5YFejYGVdE6I2u0BVEQ+hdHqRLxZxhzU0KmELnCQd7D+wLYDSTZhUQaII2xKoQGWCClfhBxGpAkxdK0FFBfSSV0DnchQSKEq0JFBC7CKOEjTHNQpVQNdJE5qEYJVJJb2kkslEz3wB/C7e0P1OBK8CVCaWKFRJGKx0aJqCYIVJJ1qGLJy0Kpu3OYiQoghSCRJ5o1zGMNmHNmUDBVQ0SQK2EFEnDSMJGALlSQPeQAHVICYxDQWXI5CdWMoQZCdJwDZIYJoGvdMk4G1p5Q4EHCbITuKmDfBJQrfhvw0h4QRyBVRJmEDQBliBbIQkELSBXAErIKchJEPIJmiDTCqojCBNkJR+H4lqoDKBJEE2IaGCLFRJqMagkYT5BGrWO5DGJC5hJgE3wCKEHAK2Qc4K5CeQ/g8k7BpkH0J5AiM0ZC8xSUJdQJVKJIiESTsxqSZNQFFCQNRGYoIipCWgIoECSAoqJVAMVAogWVAlNBMQJWC0hk0IKhUo+pYJkAoUJyC5/WYy8oSkBJUJqHN0k0A1BtS5xSkNpQmq9p0EPL7hQMKCSNIL+ARCNoH5pIFcAgYRqhNQLnBqGrJbwEoNwwGBnITZBJJamqLlCWUCMhMwHIgnoMf6FchIoJiA2QTmCxT/ItL/AX4CR7L0AeNVA9MAAAAASUVORK5CYII=');
    }
    
    tray = new Tray(icon.resize({ width: 16, height: 16 }));
    tray.setToolTip(CONFIG.appName);
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show App',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Check for Updates',
            click: () => {
                if (appUpdater) {
                    appUpdater.checkForUpdates();
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Exit',
            click: () => {
                tray = null;
                app.quit();
            }
        }
    ]);
    
    tray.setContextMenu(contextMenu);
    
    tray.on('double-click', () => {
        if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
        }
    });
}

// App lifecycle events
app.whenReady().then(async () => {
    // Create splash screen
    createSplashWindow();
    
    try {
        updateSplashStatus('Loading Python environment...');
        
        // Start Streamlit
        updateSplashStatus('Starting Streamlit application...');
        const port = await startStreamlit();
        
        updateSplashStatus('Creating application window...');
        
        // Create main window and tray
        createMainWindow(port);
        createTray(port);
        
    } catch (error) {
        console.error('Failed to start application:', error);
        
        if (splashWindow && !splashWindow.isDestroyed()) {
            splashWindow.close();
        }
        
        dialog.showErrorBox(
            'Startup Error',
            `Failed to start the application.\n\nError: ${error.message}\n\nPlease ensure:\n1. Python 3.8+ is installed\n2. Streamlit is installed (pip install streamlit)\n3. The API server is running`
        );
        
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        // Re-create window if needed
    } else {
        mainWindow.show();
    }
});

app.on('before-quit', () => {
    stopStreamlit();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        stopStreamlit();
        app.quit();
    }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    dialog.showErrorBox('Error', `An unexpected error occurred: ${error.message}`);
});
