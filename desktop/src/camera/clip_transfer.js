/**
 * Direct P2P clip transfer over WebRTC data channel.
 * No bytes touch our backend. Phone gets clips straight from the laptop.
 *
 * Flow:
 *   1. Phone subscribes to WS signaling room (already done for live view)
 *   2. Laptop opens a WebRTC data channel
 *   3. When a clip is recorded, laptop sends:
 *        { type: 'clip-meta', filename, size, mime, eventType, ts }
 *        then chunks of base64-encoded mp4 (16 KB at a time)
 *   4. Phone reassembles + saves to its CameraRoll / Photos / Files app
 *
 * Encryption: WebRTC data channels are DTLS-encrypted by default.
 * Even if our signaling server is compromised, clips can't be intercepted.
 */
const fs = require('fs');
const path = require('path');

const CHUNK = 16 * 1024;

class ClipTransfer {
  constructor(getDataChannel) {
    this.getDC = getDataChannel; // function that returns the open RTCDataChannel
  }

  async sendClip(filePath, eventType = 'person') {
    const dc = this.getDC();
    if (!dc || dc.readyState !== 'open') {
      console.log('[clip-transfer] no peer connected — clip kept on disk:', filePath);
      return false;
    }

    const stat = fs.statSync(filePath);
    const filename = path.basename(filePath);

    // Send metadata
    dc.send(JSON.stringify({
      type: 'clip-meta',
      filename,
      size: stat.size,
      mime: 'video/mp4',
      eventType,
      ts: Date.now(),
    }));

    // Stream chunks
    return new Promise((resolve, reject) => {
      const stream = fs.createReadStream(filePath, { highWaterMark: CHUNK });
      let sent = 0;
      stream.on('data', (chunk) => {
        // Backpressure
        if (dc.bufferedAmount > 16 * 1024 * 1024) {
          stream.pause();
          dc.onbufferedamountlow = () => stream.resume();
          dc.bufferedAmountLowThreshold = 4 * 1024 * 1024;
        }
        dc.send(chunk);
        sent += chunk.length;
      });
      stream.on('end', () => {
        dc.send(JSON.stringify({ type: 'clip-end', filename, sent }));
        console.log('[clip-transfer] delivered', filename, '→ phone');
        resolve(true);
      });
      stream.on('error', reject);
    });
  }
}

module.exports = { ClipTransfer };
