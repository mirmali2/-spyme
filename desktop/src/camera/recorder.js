const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

const CLIP_DIR = path.join(os.homedir(), '.spyme', 'clips');
fs.mkdirSync(CLIP_DIR, { recursive: true });

/**
 * Ring buffer of pre-event frames (5s at 10fps = 50 frames).
 * When triggered, flush pre-buffer + continue recording for POST_SECONDS.
 */
class Recorder {
  constructor({ fps = 10, preSeconds = 5, postSeconds = 10 } = {}) {
    this.fps = fps;
    this.preFrames = fps * preSeconds;
    this.postSeconds = postSeconds;
    this.ring = [];
    this.recording = false;
    this.ffmpeg = null;
    this.currentFile = null;
    this.postTimer = null;
    this.onClipReady = null;  // callback(filePath)
  }

  pushFrame(frameJpeg) {
    // maintain pre-buffer ring
    this.ring.push(frameJpeg);
    if (this.ring.length > this.preFrames) this.ring.shift();

    if (this.recording && this.ffmpeg) {
      this.ffmpeg.stdin.write(frameJpeg);
    }
  }

  trigger() {
    if (this.recording) {
      // extend post-buffer timer
      clearTimeout(this.postTimer);
      this._scheduleStop();
      return;
    }

    const filename = `clip_${Date.now()}.mp4`;
    this.currentFile = path.join(CLIP_DIR, filename);
    this.recording = true;

    this.ffmpeg = spawn('ffmpeg', [
      '-f', 'image2pipe',
      '-framerate', String(this.fps),
      '-i', 'pipe:0',
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-pix_fmt', 'yuv420p',
      '-movflags', '+faststart',
      this.currentFile,
    ], { stdio: ['pipe', 'ignore', 'ignore'] });

    // flush pre-buffer
    for (const f of this.ring) this.ffmpeg.stdin.write(f);
    this.ring = [];

    this._scheduleStop();
  }

  _scheduleStop() {
    this.postTimer = setTimeout(() => this.stop(), this.postSeconds * 1000);
  }

  stop() {
    if (!this.recording) return;
    this.recording = false;
    clearTimeout(this.postTimer);
    if (this.ffmpeg) {
      this.ffmpeg.stdin.end();
      this.ffmpeg.on('close', () => {
        if (this.onClipReady && this.currentFile) {
          this.onClipReady(this.currentFile);
        }
      });
      this.ffmpeg = null;
    }
  }
}

module.exports = { Recorder };
