const { app, BrowserWindow, ipcMain, Tray, Menu, nativeImage, screen } = require('electron');
const path = require('path');

let mainWindow = null;
let coverWindow = null;
let tray = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 380,
    height: 640,
    frame: false,
    resizable: false,
    backgroundColor: '#0a0a0a',
    webPreferences: {
      preload: path.join(__dirname, 'ui/preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'ui/index.html'));
  mainWindow.on('close', (e) => {
    e.preventDefault();
    mainWindow.hide();
  });
}

function createTray() {
  // Use 16x16 transparent fallback if icon missing
  let icon;
  try {
    icon = nativeImage.createFromPath(path.join(__dirname, '../assets/tray.png'));
    if (icon.isEmpty()) icon = nativeImage.createEmpty();
  } catch { icon = nativeImage.createEmpty(); }

  tray = new Tray(icon);
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Open SPYME', click: () => mainWindow.show() },
    { label: 'Exit Cover Mode', click: () => closeCover() },
    { type: 'separator' },
    { label: 'Quit', click: () => { app.exit(0); } },
  ]));
  tray.setToolTip('SPYME');
  tray.on('double-click', () => mainWindow.show());
}

function openCover() {
  if (coverWindow) return;
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  coverWindow = new BrowserWindow({
    width, height,
    fullscreen: true,
    frame: false,
    skipTaskbar: false,
    webPreferences: {
      preload: path.join(__dirname, 'ui/preload.js'),
      contextIsolation: true,
    },
  });
  coverWindow.loadFile(path.join(__dirname, 'cover/cover.html'));
  coverWindow.on('closed', () => { coverWindow = null; });
  if (mainWindow) mainWindow.hide();
}

function closeCover() {
  if (coverWindow) { coverWindow.close(); coverWindow = null; }
}

ipcMain.handle('toggle-cover', () => {
  coverWindow ? closeCover() : openCover();
});
ipcMain.handle('exit-cover', () => closeCover());

app.whenReady().then(() => {
  createWindow();
  createTray();
  require('./ipc/handlers');
  require('./utils/heartbeat').start();
});

app.on('window-all-closed', (e) => { e.preventDefault(); });

module.exports = { getMainWindow: () => mainWindow };
