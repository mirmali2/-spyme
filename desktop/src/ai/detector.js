const { spawn } = require('child_process');
const path = require('path');

/**
 * Wraps the Python detection worker.
 * Worker emits per-frame JSON: { motion, persons[], people_count, objects[], events[] }
 *
 * events[] entries can include:
 *   { type: 'grab', object: 'laptop', person_id: 3, ... }
 */
class Detector {
  constructor() {
    this.proc = null;
    this.pending = null;
    this.ready = false;
    this.lastResult = null;
  }

  start() {
    this.proc = spawn('python', [path.join(__dirname, 'detector_worker.py')], {
      stdio: ['pipe', 'pipe', 'inherit'],
    });

    let buf = '';
    this.proc.stdout.on('data', (data) => {
      buf += data.toString();
      let nl;
      while ((nl = buf.indexOf('\n')) !== -1) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;
        try {
          const result = JSON.parse(line);
          if (result.status === 'ready') {
            this.ready = true;
            console.log('[detector] ready —', result.models?.join(', '));
            continue;
          }
          this.lastResult = result;
          if (this.pending) {
            this.pending(result);
            this.pending = null;
          }
        } catch (_) { /* ignore parse errs */ }
      }
    });

    this.proc.on('exit', (code) => {
      console.error('[detector] worker exited with code', code);
      this.ready = false;
    });
  }

  async analyze(frameJpeg) {
    if (!this.proc || !this.ready) {
      return { motion: false, persons: [], people_count: 0, objects: [], events: [] };
    }

    const b64 = frameJpeg.toString('base64');
    this.proc.stdin.write(b64 + '\n');

    return new Promise((resolve) => {
      this.pending = resolve;
      setTimeout(() => {
        if (this.pending) {
          this.pending = null;
          resolve(this.lastResult || { motion: false, persons: [], people_count: 0, objects: [], events: [] });
        }
      }, 800);
    });
  }

  stop() {
    if (this.proc) {
      try { this.proc.stdin.end(); } catch (_) {}
      this.proc.kill();
      this.proc = null;
      this.ready = false;
    }
  }
}

module.exports = { Detector };
