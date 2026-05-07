const si = require('systeminformation');
const { patchDevice } = require('./api');
const { getStore } = require('../store');

let interval = null;

async function sendHeartbeat() {
  try {
    const deviceId = getStore().get('deviceId');
    if (!deviceId) return;

    const [battery, fs] = await Promise.all([si.battery(), si.fsSize()]);
    const freeMb = Math.round(
      fs.reduce((sum, d) => sum + (d.available || 0), 0) / (1024 * 1024)
    );

    await patchDevice(deviceId, {
      battery_pct: battery.hasBattery ? battery.percent : null,
      storage_free_mb: freeMb,
      last_seen: new Date().toISOString(),
    });
  } catch (e) { /* offline — sync later */ }
}

function start() {
  if (interval) return;
  sendHeartbeat();
  interval = setInterval(sendHeartbeat, 30_000);
}

function stop() {
  if (interval) { clearInterval(interval); interval = null; }
}

module.exports = { start, stop };
