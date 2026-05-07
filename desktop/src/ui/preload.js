const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('spyme', {
  login: (args) => ipcRenderer.invoke('login', args),
  registerDevice: (args) => ipcRenderer.invoke('register-device', args),
  arm: () => ipcRenderer.invoke('arm'),
  disarm: () => ipcRenderer.invoke('disarm'),
  getStore: (key) => ipcRenderer.invoke('get-store', key),
  setStore: (key, value) => ipcRenderer.invoke('set-store', key, value),
  toggleCover: () => ipcRenderer.invoke('toggle-cover'),
});
