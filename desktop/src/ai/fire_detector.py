"""
Fire & smoke detection — HSV color analysis + temporal flicker.

Why no ML training: fire has a unique signature — high red/orange in HSV,
high luminance, and characteristic flicker (rapid pixel intensity change).
Combined with motion gating this is very accurate and runs in <5ms.

Returns per-frame dict: { fire: bool, smoke: bool, confidence: float, area_pct: float }
"""
from collections import deque

import cv2
import numpy as np

# Fire HSV ranges (two — red wraps around 180)
FIRE_HSV_1 = (np.array([0, 120, 200]),    np.array([20, 255, 255]))   # orange-red
FIRE_HSV_2 = (np.array([160, 120, 200]),  np.array([180, 255, 255]))  # deep red wrap

# Smoke: desaturated grays with motion
SMOKE_HSV  = (np.array([0, 0, 100]),      np.array([180, 50, 220]))

# Tunables
MIN_FIRE_AREA_PX     = 800        # ~ 0.25% of 640x480 = obvious fire
MIN_FIRE_AREA_PCT    = 0.005      # 0.5% of frame
FLICKER_WINDOW       = 8          # frames to track flicker
MIN_FLICKER_VARIANCE = 200        # required intensity variance for confirmed fire
SMOKE_MIN_AREA_PCT   = 0.04
SMOKE_MIN_MOTION_PX  = 1500


class FireDetector:
    def __init__(self):
        self.intensity_history = deque(maxlen=FLICKER_WINDOW)
        self.fire_area_history = deque(maxlen=FLICKER_WINDOW)
        self.consecutive_fire_frames = 0

    def analyze(self, frame_bgr: np.ndarray, motion_mask: np.ndarray | None = None) -> dict:
        h, w = frame_bgr.shape[:2]
        total_px = h * w
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # ----- Fire color mask -----
        m1 = cv2.inRange(hsv, *FIRE_HSV_1)
        m2 = cv2.inRange(hsv, *FIRE_HSV_2)
        fire_mask = cv2.bitwise_or(m1, m2)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        fire_mask = cv2.dilate(fire_mask, np.ones((5, 5), np.uint8), iterations=1)
        fire_area_px = int(np.count_nonzero(fire_mask))
        fire_area_pct = fire_area_px / total_px

        # ----- Track flicker (intensity variance over time) -----
        # Compute mean intensity inside the fire-color mask only
        if fire_area_px > 0:
            mean_intensity = float(cv2.mean(hsv[:, :, 2], mask=fire_mask)[0])
        else:
            mean_intensity = 0.0
        self.intensity_history.append(mean_intensity)
        self.fire_area_history.append(fire_area_pct)

        flicker_var = float(np.var(self.intensity_history)) if len(self.intensity_history) >= 4 else 0.0
        sustained = (sum(1 for a in self.fire_area_history if a >= MIN_FIRE_AREA_PCT)
                     >= max(3, FLICKER_WINDOW // 2))

        # ----- Fire decision -----
        fire = (
            fire_area_px >= MIN_FIRE_AREA_PX
            and fire_area_pct >= MIN_FIRE_AREA_PCT
            and flicker_var >= MIN_FLICKER_VARIANCE
            and sustained
        )

        # Confidence — combination of size + flicker
        if fire_area_pct == 0:
            confidence = 0.0
        else:
            size_score = min(fire_area_pct / 0.05, 1.0)             # 5% area = 1.0
            flicker_score = min(flicker_var / 1500.0, 1.0)
            sustain_score = 1.0 if sustained else 0.3
            confidence = round(0.5 * size_score + 0.3 * flicker_score + 0.2 * sustain_score, 3)

        if fire:
            self.consecutive_fire_frames += 1
        else:
            self.consecutive_fire_frames = max(0, self.consecutive_fire_frames - 1)

        # ----- Smoke detection (only if motion mask provided) -----
        smoke = False
        smoke_area_pct = 0.0
        if motion_mask is not None:
            smoke_mask = cv2.inRange(hsv, *SMOKE_HSV)
            # smoke must overlap with motion (smoke moves)
            smoke_motion = cv2.bitwise_and(smoke_mask, motion_mask)
            smoke_area_pct = float(np.count_nonzero(smoke_motion)) / total_px
            smoke = (
                smoke_area_pct >= SMOKE_MIN_AREA_PCT
                and np.count_nonzero(motion_mask) >= SMOKE_MIN_MOTION_PX
            )

        return {
            "fire": fire,
            "smoke": smoke,
            "confidence": confidence,
            "area_pct": round(fire_area_pct, 4),
            "smoke_area_pct": round(smoke_area_pct, 4),
            "consecutive_frames": self.consecutive_fire_frames,
            "flicker": round(flicker_var, 1),
        }
