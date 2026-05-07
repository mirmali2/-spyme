const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

// Cross-platform webcam frame capture using ffmpeg
// Returns a stream of JPEG frames at target FPS
class FrameCapture {
  constructor({ fps = 10, width = 640, height = 480 } = {}) {
    this.fps = fps;
    this.width = width;
    this.height = height;
    this.proc = null;
    this.listeners = [];
  }

  start() {
    const input = os.platform() === 'win32'
      ? ['-f', 'dshow', '-i', 'video=default']
      : ['-f', 'avfoundation', '-i', '0'];

    this.proc = spawn('ffmpeg', [
      ...input,
      '-vf', `scale=${this.width}:${this.height},fps=${this.fps}`,
      '-f', 'image2pipe',
      '-vcodec', 'mjpeg',
      '-q:v', '5',
      'pipe:1',
    ], { stdio: ['ignore', 'pipe', 'ignore'] });

    let buf = Buffer.alloc(0);
    const SOI = Buffer.from([0xff, 0xd8]);
    const EOI = Buffer.from([0xff, 0xd9]);

    this.proc.stdout.on('data', (chunk) => {
      buf = Buffer.concat([buf, chunk]);
      let start = buf.indexOf(SOI);
      let end = buf.indexOf(EOI, start + 2);

      while (start !== -1 && end !== -1) {
        const frame = buf.slice(start, end + 2);
        this.listeners.forEach(fn => fn(frame));
        buf = buf.slice(end + 2);
        start = buf.indexOf(SOI);
        end = buf.indexOf(EOI, start + 2);
      }
    });
  }

  onFrame(fn) {
    this.listeners.push(fn);
    return () => { this.listeners = this.listeners.filter(l => l !== fn); };
  }

  stop() {
    this.listeners = [];
    if (this.proc) {
      this.proc.kill('SIGKILL');
      this.proc = null;
    }
  }
}

module.exports = { FrameCapture };
