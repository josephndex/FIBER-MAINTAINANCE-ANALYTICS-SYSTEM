/**
 * Preload script for Electron app
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App info
    getAppVersion: () => '2.0.0',
    getPlatform: () => process.platform,
    
    // Window controls
    minimize: () => ipcRenderer.send('window-minimize'),
    maximize: () => ipcRenderer.send('window-maximize'),
    close: () => ipcRenderer.send('window-close'),
    
    // Notifications
    showNotification: (title, body) => {
        new Notification(title, { body });
    }
});

// Add custom styling when the page loads
window.addEventListener('DOMContentLoaded', () => {
    // Add desktop-specific CSS
    const style = document.createElement('style');
    style.textContent = `
        /* Hide Streamlit's hamburger menu and footer in desktop mode */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden !important; }
        
        /* Improve scrollbar appearance */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e293b;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #f97316, #a855f7);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #fb923c, #c084fc);
        }
        
        /* Custom selection color */
        ::selection {
            background: rgba(249, 115, 22, 0.3);
        }
    `;
    document.head.appendChild(style);
    
    console.log('Fiber Maintenance Analytics - Desktop Mode Loaded');
});
