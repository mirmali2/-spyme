const { ipcMain, powerSaveBlocker } = require('electron');
const monitor = require('../camera/monitor');
const { getStore } = require('../store');
const fetch = (...args) => import('node-fetch').then(({ default: f }) => f(...args));

let blockerId = null;

ipcMain.handle('arm', async () => {
  await monitor.start();
  if (!blockerId) blockerId = powerSaveBlocker.start('prevent-display-sleep');
  return {
    armed: true,
    reminders: [
      'Leave the laptop LID OPEN — closing it disables the camera.',
      'Keep it plugged in for monitoring longer than 4 hours.',
      'SPYME does NOT replace a smoke detector. Test yours monthly.',
    ],
  };
});

ipcMain.handle('disarm', async () => {
  monitor.stop();
  if (blockerId !== null) { powerSaveBlocker.stop(blockerId); blockerId = null; }
  return { armed: false };
});

ipcMain.handle('get-store', (_, key) => getStore().get(key));
ipcMain.handle('set-store', (_, key, value) => { getStore().set(key, value); });

ipcMain.handle('login', async (_, { email, password, apiUrl }) => {
  const store = getStore();
  store.set('apiUrl', apiUrl);
  const res = await fetch(`${apiUrl}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  const { access_token, refresh_token } = await res.json();
  store.set('accessToken', access_token);
  store.set('refreshToken', refresh_token);
  return { ok: true };
});

ipcMain.handle('register-device', async (_, { name }) => {
  const store = getStore();
  const res = await fetch(`${store.get('apiUrl')}/api/v1/devices`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${store.get('accessToken')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, platform: process.platform }),
  });
  const device = await res.json();
  store.set('deviceId', device.id);
  store.set('deviceName', device.name);
  return device;
});
