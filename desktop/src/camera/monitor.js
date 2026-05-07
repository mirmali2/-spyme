const { FrameCapture } = require('./capture');
const { Recorder } = require('./recorder');
const { Detector } = require('../ai/detector');
const streamer = require('./streamer');
const { uploadClip, postEvent } = require('../utils/api');
const { getStore } = require('../store');

let capture = null;
let recorder = null;
let detector = null;

// debounce: don't spam identical events
const lastFiredAt = new Map(); // key -> timestamp ms
function shouldFire(key, cooldownMs = 8000) {
  const now = Date.now();
  if (now - (lastFiredAt.get(key) || 0) < cooldownMs) return false;
  lastFiredAt.set(key, now);
  return true;
}

async function start() {
  const store = getStore();
  capture = new FrameCapture({ fps: 8, width: 640, height: 480 });
  recorder = new Recorder({ fps: 8, preSeconds: 5, postSeconds: 12 });
  detector = new Detector();
  detector.start();

  recorder.onClipReady = async (filePath) => {
    try {
      const { clipId } = await uploadClip(filePath, store.get('deviceId'));
      console.log('[monitor] clip uploaded:', clipId);
    } catch (e) {
      console.error('[monitor] upload failed:', e.message);
    }
  };

  streamer.connectSignaling().catch(err => console.error('Signaling failed:', err));

  capture.onFrame(async (frameJpeg) => {
    recorder.pushFrame(frameJpeg);
    streamer.pushFrame(frameJpeg);

    const r = await detector.analyze(frameJpeg);
    const deviceId = store.get('deviceId');
    if (!deviceId) return;

    // 1. Multi-person detection
    if (r.people_count > 0 && shouldFire('person', 6000)) {
      const personSummary = r.persons.map(p => `#${p.id} ${p.action}`).join(', ');
      recorder.trigger();
      await postEvent({
        deviceId,
        type: 'person',
        confidence: Math.max(...r.persons.map(p => p.confidence)),
        metadata: {
          people_count: r.people_count,
          persons: r.persons.map(p => ({ id: p.id, pose: p.pose, action: p.action, conf: p.confidence })),
          summary: `${r.people_count} ${r.people_count === 1 ? 'person' : 'people'} — ${personSummary}`,
        },
      }).catch(() => {});
    }

    // 2. Multiple-people alert (specifically flag)
    if (r.people_count >= 2 && shouldFire('multi-person', 15000)) {
      await postEvent({
        deviceId,
        type: 'multi_person',
        confidence: 1.0,
        metadata: { people_count: r.people_count },
      }).catch(() => {});
    }

    // 3. Action: someone reaching (potential grab in progress)
    const reaching = r.persons.find(p => p.action === 'reaching');
    if (reaching && shouldFire(`reach-${reaching.id}`, 5000)) {
      await postEvent({
        deviceId,
        type: 'reaching',
        confidence: reaching.confidence,
        metadata: { person_id: reaching.id, pose: reaching.pose },
      }).catch(() => {});
    }

    // 4. GRAB EVENT — confirmed object disappeared while person was nearby
    for (const ev of (r.events || [])) {
      if (ev.type === 'grab' && shouldFire(`grab-${ev.object}`, 30000)) {
        recorder.trigger();
        await postEvent({
          deviceId,
          type: 'theft',
          confidence: 0.85,
          metadata: {
            object: ev.object,
            person_id: ev.person_id,
            summary: `Person #${ev.person_id} possibly took ${ev.object}`,
          },
        }).catch(() => {});
      }

      // 4b. 🔥 FIRE — top-priority emergency, fires every 30s while ongoing
      if (ev.type === 'fire' && shouldFire('fire-emergency', 30000)) {
        recorder.trigger();
        await postEvent({
          deviceId,
          type: 'fire',
          confidence: ev.confidence,
          metadata: {
            severity: 'critical',
            area_pct: ev.area_pct,
            summary: `🔥 FIRE DETECTED — ${(ev.area_pct * 100).toFixed(1)}% of frame on fire`,
          },
        }).catch(() => {});
      }

      // 4c. 💨 SMOKE — high priority but not critical
      if (ev.type === 'smoke' && shouldFire('smoke-warning', 60000)) {
        await postEvent({
          deviceId,
          type: 'smoke',
          confidence: ev.confidence,
          metadata: { summary: 'Smoke detected — possible fire developing' },
        }).catch(() => {});
      }
    }

    // 5. Plain motion (low priority — only if no person)
    if (r.motion && r.people_count === 0 && shouldFire('motion', 12000)) {
      await postEvent({ deviceId, type: 'motion' }).catch(() => {});
    }
  });

  capture.start();
  store.set('isArmed', true);
  console.log('[monitor] armed — watching for persons, actions, and theft');
}

function stop() {
  if (capture) { capture.stop(); capture = null; }
  if (recorder) { recorder.stop(); recorder = null; }
  if (detector) { detector.stop(); detector = null; }
  streamer.disconnect();
  getStore().set('isArmed', false);
}

module.exports = { start, stop };
