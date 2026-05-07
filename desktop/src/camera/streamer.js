const WebSocket = require('ws');
const wrtc = require('wrtc');
const { getStore } = require('../store');

let pc = null;
let ws = null;
let videoSource = null;

/**
 * Connect to the signaling server and wait for a viewer to request a stream.
 * Frames are pushed from monitor.js via the onFrame callback.
 */
async function connectSignaling() {
  const store = getStore();
  const apiUrl = store.get('apiUrl').replace(/^http/, 'ws');
  const deviceId = store.get('deviceId');
  const token = store.get('accessToken');

  ws = new WebSocket(`${apiUrl}/ws/signal/${deviceId}?token=${token}`);

  ws.on('message', async (raw) => {
    const msg = JSON.parse(raw);

    if (msg.type === 'request-offer') {
      await createOffer();
    } else if (msg.type === 'answer') {
      await pc.setRemoteDescription(new wrtc.RTCSessionDescription(msg));
    } else if (msg.type === 'ice-candidate') {
      await pc.addIceCandidate(new wrtc.RTCIceCandidate(msg.candidate));
    }
  });

  ws.on('close', () => setTimeout(connectSignaling, 5000)); // auto-reconnect
}

async function createOffer() {
  const store = getStore();
  pc = new wrtc.RTCPeerConnection({
    iceServers: [
      { urls: 'stun:stun.cloudflare.com:3478' },
      { urls: 'stun:stun.l.google.com:19302' },
    ],
  });

  // Create a video track from our frame source
  videoSource = new wrtc.nonstandard.RTCVideoSource();
  const track = videoSource.createTrack();
  pc.addTrack(track);

  pc.onicecandidate = ({ candidate }) => {
    if (candidate && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ice-candidate', candidate }));
    }
  };

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  ws.send(JSON.stringify({ type: 'offer', sdp: offer.sdp }));
}

/**
 * Called by monitor.js with each JPEG frame buffer.
 * Decodes to raw I420 and pushes to WebRTC video source.
 */
function pushFrame(jpegBuf) {
  if (!videoSource) return;
  // wrtc expects I420 frames; use sharp or jimp for conversion in production
  // For MVP we push raw data — replace with proper yuv conversion
  try {
    const { createCanvas, loadImage } = require('canvas');
    loadImage(jpegBuf).then(img => {
      const canvas = createCanvas(img.width, img.height);
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const { data, width, height } = ctx.getImageData(0, 0, img.width, img.height);
      videoSource.onFrame({ width, height, data: new Uint8ClampedArray(data) });
    }).catch(() => {});
  } catch (_) {}
}

function disconnect() {
  if (pc) { pc.close(); pc = null; }
  if (ws) { ws.close(); ws = null; }
  videoSource = null;
}

module.exports = { connectSignaling, pushFrame, disconnect };
