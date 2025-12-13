/**
 * Auto-Updater Module for Fiber Maintenance Analytics
 * 
 * Handles automatic updates from GitHub Releases.
 * Updates are downloaded in the background and installed on restart.
 */

const { autoUpdater } = require('electron-updater');
const { dialog, BrowserWindow } = require('electron');
const log = require('electron-log');

// Configure logging
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';

// Disable auto-download - we'll prompt the user first
autoUpdater.autoDownload = false;
autoUpdater.autoInstallOnAppQuit = true;

class AppUpdater {
    constructor(mainWindow) {
        this.mainWindow = mainWindow;
        this.updateAvailable = false;
        this.updateDownloaded = false;
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Checking for updates
        autoUpdater.on('checking-for-update', () => {
            log.info('Checking for updates...');
            this.sendStatusToWindow('Checking for updates...');
        });
        
        // Update available
        autoUpdater.on('update-available', (info) => {
            log.info('Update available:', info.version);
            this.updateAvailable = true;
            
            dialog.showMessageBox(this.mainWindow, {
                type: 'info',
                title: 'Update Available',
                message: `A new version (${info.version}) is available!`,
                detail: `Current version: ${require('./package.json').version}\n\nWould you like to download it now?`,
                buttons: ['Download', 'Later'],
                defaultId: 0,
                cancelId: 1
            }).then((result) => {
                if (result.response === 0) {
                    autoUpdater.downloadUpdate();
                    this.sendStatusToWindow('Downloading update...');
                }
            });
        });
        
        // No update available
        autoUpdater.on('update-not-available', (info) => {
            log.info('No update available');
            this.sendStatusToWindow('App is up to date');
        });
        
        // Download progress
        autoUpdater.on('download-progress', (progressObj) => {
            const percent = Math.round(progressObj.percent);
            log.info(`Download progress: ${percent}%`);
            this.sendStatusToWindow(`Downloading: ${percent}%`);
            
            // Update window progress bar
            if (this.mainWindow) {
                this.mainWindow.setProgressBar(progressObj.percent / 100);
            }
        });
        
        // Update downloaded
        autoUpdater.on('update-downloaded', (info) => {
            log.info('Update downloaded:', info.version);
            this.updateDownloaded = true;
            
            if (this.mainWindow) {
                this.mainWindow.setProgressBar(-1); // Remove progress bar
            }
            
            dialog.showMessageBox(this.mainWindow, {
                type: 'info',
                title: 'Update Ready',
                message: 'Update downloaded successfully!',
                detail: `Version ${info.version} has been downloaded.\n\nThe app will restart to install the update.`,
                buttons: ['Restart Now', 'Later'],
                defaultId: 0,
                cancelId: 1
            }).then((result) => {
                if (result.response === 0) {
                    autoUpdater.quitAndInstall();
                }
            });
        });
        
        // Error handling
        autoUpdater.on('error', (err) => {
            log.error('Update error:', err);
            this.sendStatusToWindow(`Update error: ${err.message}`);
            
            if (this.mainWindow) {
                this.mainWindow.setProgressBar(-1);
            }
        });
    }
    
    // Check for updates
    checkForUpdates() {
        log.info('Manually checking for updates...');
        autoUpdater.checkForUpdates();
    }
    
    // Check silently (no dialogs if no update)
    checkForUpdatesSilent() {
        log.info('Silent update check...');
        autoUpdater.checkForUpdates().catch((err) => {
            log.error('Silent update check failed:', err);
        });
    }
    
    // Send status to renderer window
    sendStatusToWindow(text) {
        if (this.mainWindow && this.mainWindow.webContents) {
            this.mainWindow.webContents.send('update-status', text);
        }
    }
    
    // Get update feed URL (for debugging)
    getFeedURL() {
        return autoUpdater.getFeedURL();
    }
}

module.exports = { AppUpdater, autoUpdater };
