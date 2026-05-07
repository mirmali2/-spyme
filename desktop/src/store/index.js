let _store = null;

function getStore() {
  if (!_store) {
    const Store = require('electron-store');
    _store = new Store({
      schema: {
        apiUrl: { type: 'string', default: 'http://localhost:8000' },
        accessToken: { type: 'string', default: '' },
        refreshToken: { type: 'string', default: '' },
        deviceId: { type: 'string', default: '' },
        deviceName: { type: 'string', default: '' },
        isArmed: { type: 'boolean', default: false },
      },
    });
  }
  return _store;
}

module.exports = { getStore };
