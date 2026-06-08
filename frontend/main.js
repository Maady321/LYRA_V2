const { app, BrowserWindow, Menu, ipcMain, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

const globalLogPath = 'c:\\sabari\\Lyra\\lyra_global.log';
function logGlobal(msg) {
  try {
    fs.appendFileSync(globalLogPath, `[${new Date().toISOString()}] ${msg}\n`);
  } catch (e) {}
}

logGlobal('Main script loaded at top-level.');

process.on('uncaughtException', (err) => {
  logGlobal(`UNCAUGHT EXCEPTION: ${err.message}\n${err.stack}`);
});

process.on('unhandledRejection', (reason, promise) => {
  logGlobal(`UNHANDLED REJECTION: ${reason}`);
});

let mainWindow;
let backendProcess;
let tray;

// --- Automated Backend Process Lifecycle ---
function startBackend() {
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  
  // Resolve backend directory path
  const backendPath = isDev 
    ? path.join(__dirname, '..', 'backend') 
    : path.join(process.resourcesPath, 'backend');
    
  // Resolve python executable path
  const pythonExe = process.platform === 'win32'
    ? path.join(backendPath, 'venv', 'Scripts', 'python.exe')
    : path.join(backendPath, 'venv', 'bin', 'python');

  const debugLogPath = 'c:\\sabari\\Lyra\\lyra_debug.log';
  
  function writeDebug(msg) {
    try {
      fs.appendFileSync(debugLogPath, `[${new Date().toISOString()}] ${msg}\n`);
    } catch (e) {}
  }

  writeDebug(`Wake System Launcher: Starting backend.`);
  writeDebug(`isDev: ${isDev}`);
  writeDebug(`process.resourcesPath: ${process.resourcesPath}`);
  writeDebug(`backendPath: ${backendPath}`);
  writeDebug(`pythonExe: ${pythonExe}`);
  writeDebug(`pythonExe exists: ${fs.existsSync(pythonExe)}`);
  writeDebug(`backendPath exists: ${fs.existsSync(backendPath)}`);

  try {
    const logPath = path.join(backendPath, 'backend_spawn.log');
    writeDebug(`Creating stream to logPath: ${logPath}`);
    const logStream = fs.createWriteStream(logPath, { flags: 'w' });
    
    writeDebug(`Spawning backendProcess...`);
    backendProcess = spawn(pythonExe, ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
      cwd: backendPath,
      shell: false
    });
    
    writeDebug(`backendProcess PID: ${backendProcess ? backendProcess.pid : 'undefined'}`);
    
    if (backendProcess) {
      backendProcess.on('error', (err) => {
        writeDebug(`Process ERROR event: ${err.message}\n${err.stack}`);
        try {
          fs.writeFileSync('c:\\sabari\\Lyra\\lyra_spawn_error.log', `Spawn Error: ${err.message}\nStack: ${err.stack}\npythonExe: ${pythonExe}\nbackendPath: ${backendPath}`);
        } catch (e) {}
      });
      
      backendProcess.stdout.pipe(logStream);
      backendProcess.stderr.pipe(logStream);
      
      backendProcess.stdout.on('data', (data) => {
        writeDebug(`stdout: ${data.toString().trim()}`);
      });
      
      backendProcess.stderr.on('data', (data) => {
        writeDebug(`stderr: ${data.toString().trim()}`);
      });
      
      backendProcess.on('close', (code) => {
        writeDebug(`Process CLOSE event: exited with code ${code}`);
      });
      
      backendProcess.on('exit', (code, signal) => {
        writeDebug(`Process EXIT event: exited with code ${code}, signal ${signal}`);
      });
    }
  } catch (err) {
    writeDebug(`CATCH block error: ${err.message}\n${err.stack}`);
  }
}

// --- IPC App Wake Listeners ---
ipcMain.on('wake-app', () => {
  console.log("Wake System: Received 'wake-app' IPC event in main process.");
  if (mainWindow) {
    if (mainWindow.isMinimized()) {
      console.log("Wake System: Restoring minimized window.");
      mainWindow.restore();
    }
    
    console.log("Wake System: Showing and focusing main window.");
    mainWindow.show();
    mainWindow.focus();
    
    // Bypass Windows background focus restrictions
    mainWindow.setAlwaysOnTop(true);
    mainWindow.setAlwaysOnTop(false);
  } else {
    console.error("Wake System: Main process error - mainWindow is undefined.");
  }
});

// --- Native Windows System Tray (App Tray) Setup ---
function createTray() {
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  
  // Resolve icon path dynamically for Dev and Production bundles
  const iconPath = isDev
    ? path.join(__dirname, 'public', 'favicon.png')
    : path.join(__dirname, 'dist', 'favicon.png');
    
  let icon;
  
  try {
    if (fs.existsSync(iconPath)) {
      icon = nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 });
      console.log(`Wake System Tray: Loaded active app tray logo from: ${iconPath}`);
    } else {
      console.warn(`Wake System Tray: Icon not found at: ${iconPath}. Using fallback.`);
      icon = nativeImage.createEmpty();
    }
  } catch (e) {
    icon = nativeImage.createEmpty();
  }

  tray = new Tray(icon);
  
  const contextMenu = Menu.buildFromTemplate([
    { 
      label: 'Restore Assistant', 
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
          mainWindow.setAlwaysOnTop(true);
          mainWindow.setAlwaysOnTop(false);
        }
      } 
    },
    { 
      label: 'Minimize to Tray', 
      click: () => {
        if (mainWindow) mainWindow.hide();
      } 
    },
    { type: 'separator' },
    { 
      label: 'Quit Lyra', 
      click: () => {
        app.isQuitting = true;
        app.quit();
      } 
    }
  ]);
  
  tray.setToolTip('Lyra AI OS Platform');
  tray.setContextMenu(contextMenu);
  
  // Toggle visibility on left click
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible() && !mainWindow.isMinimized()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
        mainWindow.setAlwaysOnTop(true);
        mainWindow.setAlwaysOnTop(false);
      }
    }
  });
}

// --- Create UI Window ---
function createWindow() {
  const shouldHide = process.argv.includes('--hidden');
  logGlobal(`createWindow: shouldHide=${shouldHide}`);

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 700,
    title: "Lyra AI OS Platform",
    frame: true, 
    backgroundColor: "#060A13", 
    show: !shouldHide,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, 
    },
  });

  // Hide the default standard menu bar for a clean dashboard look
  Menu.setApplicationMenu(null);

  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
  }

  // Inject a reliable, transpilation-safe global wake helper once loaded
  mainWindow.webContents.on('did-finish-load', () => {
    console.log("Wake System: Page load complete. Injecting wakeElectronApp on window context.");
    mainWindow.webContents.executeJavaScript(`
      window.wakeElectronApp = () => {
        try {
          const { ipcRenderer } = require('electron');
          ipcRenderer.send('wake-app');
          console.log("Wake System: wake-app IPC triggered successfully from window.");
        } catch (e) {
          console.error("Wake System: Failed inside injected wakeElectronApp:", e);
        }
      };
      void 0;
    `).catch(err => {
      console.error("Wake System: Failed to inject wake helper:", err);
    });
  });

  // Intercept Close Button to hide window to tray instead of quitting
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      console.log("Wake System: Main window minimized to System Tray. Background wake features remain active.");
    }
    return false;
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// --- App Startup Lifecycle Hooks ---
app.whenReady().then(() => {
  logGlobal('app.whenReady() fired.');

  // Set login items auto-start settings dynamically on boot
  try {
    app.setLoginItemSettings({
      openAtLogin: true,
      path: process.execPath,
      args: ['--hidden']
    });
    logGlobal('Successfully registered Lyra AI auto-boot login settings.');
  } catch (err) {
    logGlobal(`Failed to set login item settings: ${err.message}`);
  }

  startBackend();
  logGlobal('startBackend() finished.');
  createWindow();
  logGlobal('createWindow() finished.');
  createTray();
  logGlobal('createTray() finished.');

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('will-quit', () => {
  if (backendProcess) {
    console.log("Wake System Launcher: Terminating background FastAPI backend process.");
    try {
      backendProcess.kill();
    } catch (e) {}
  }
});

app.on('window-all-closed', () => {
  // Keep app alive in tray even if all windows are closed on Windows OS
  if (process.platform !== 'darwin' && app.isQuitting) {
    app.quit();
  }
});
