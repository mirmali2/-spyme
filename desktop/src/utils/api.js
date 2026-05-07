const fs = require('fs');
const fetch = (...args) => import('node-fetch').then(({ default: f }) => f(...args));
const { getStore } = require('../store');

function baseUrl() {
  return getStore().get('apiUrl') || 'http://localhost:8000';
}

function headers() {
  const token = getStore().get('accessToken');
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

async function postEvent({ deviceId, type, confidence = null, clipId = null }) {
  const res = await fetch(`${baseUrl()}/api/v1/events`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ device_id: deviceId, type, confidence, clip_id: clipId }),
  });
  return res.json();
}

async function uploadClip(filePath, deviceId) {
  const filename = require('path').basename(filePath);
  const stat = fs.statSync(filePath);

  // get pre-signed URL
  const urlRes = await fetch(`${baseUrl()}/api/v1/clips/upload-url`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ device_id: deviceId, filename }),
  });
  const { upload_url, storage_key } = await urlRes.json();

  // upload directly to S3/R2
  await fetch(upload_url, {
    method: 'PUT',
    body: fs.createReadStream(filePath),
    headers: { 'Content-Length': stat.size },
  });

  // register clip in backend
  const clipRes = await fetch(`${baseUrl()}/api/v1/clips`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ device_id: deviceId, storage_key, size_bytes: stat.size }),
  });
  const clip = await clipRes.json();
  return { storageKey: storage_key, clipId: clip.id };
}

async function patchDevice(deviceId, patch) {
  const res = await fetch(`${baseUrl()}/api/v1/devices/${deviceId}`, {
    method: 'PATCH',
    headers: headers(),
    body: JSON.stringify(patch),
  });
  return res.json();
}

module.exports = { postEvent, uploadClip, patchDevice };
