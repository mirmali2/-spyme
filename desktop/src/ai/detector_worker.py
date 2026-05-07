"""
SPYME advanced detection worker — pretrained on COCO (330k internet images).

Models (no training needed — both pretrained):
  • YOLOv8n          — 80-class object detection (person + 79 objects) + ByteTrack multi-object tracking
  • YOLOv8n-pose     — 17-keypoint pose per person (multi-person)

Per-frame pipeline:
  1. Cheap motion check (frame diff)        — gates expensive ML
  2. YOLO detect + ByteTrack                — multi-person + object tracking with persistent IDs
  3. YOLO pose                              — skeleton per person
  4. Action classifier (skeleton heuristics)— standing/sitting/walking/reaching/holding
  5. Object-state monitor                   — detects "grab" events (object disappears while
                                              person was nearby and reaching)

Reads base64 JPEG frames from stdin, writes JSON detections to stdout.
"""
import base64
import json
import math
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

import cv2
import numpy as np
from ultralytics import YOLO

from fire_detector import FireDetector

# ---------------------------------------------------------------------------
# Models — pretrained on COCO (downloaded automatically on first run)
# ---------------------------------------------------------------------------
yolo_det = YOLO("yolov8n.pt")
yolo_pose = YOLO("yolov8n-pose.pt")
fire_engine = FireDetector()

PERSON = 0
GRABBABLE_OBJECTS = {
    24: "backpack", 26: "handbag", 28: "suitcase",
    39: "bottle", 41: "cup", 43: "knife",
    63: "laptop", 64: "mouse", 65: "remote",
    66: "keyboard", 67: "cell phone", 73: "book",
    74: "clock", 76: "scissors",
}

# COCO 17-keypoint indices (yolov8-pose)
KP = {
    "nose": 0, "l_eye": 1, "r_eye": 2, "l_ear": 3, "r_ear": 4,
    "l_shoulder": 5, "r_shoulder": 6, "l_elbow": 7, "r_elbow": 8,
    "l_wrist": 9, "r_wrist": 10, "l_hip": 11, "r_hip": 12,
    "l_knee": 13, "r_knee": 14, "l_ankle": 15, "r_ankle": 16,
}

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------
PERSON_CONF = 0.40
OBJECT_CONF = 0.35
MOTION_THRESHOLD = 22
MOTION_MIN_AREA = 600
OBJECT_MISSING_FRAMES = 8
NEAR_DIST_PX = 200

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
@dataclass
class TrackedObject:
    cls_name: str
    last_seen: int
    last_box: tuple
    nearby_person_id: int | None = None
    confirmed_baseline: bool = False
    seen_count: int = 0


prev_gray: np.ndarray | None = None
frame_idx = 0
tracked_objects: dict[int, TrackedObject] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def detect_motion(gray: np.ndarray) -> bool:
    global prev_gray
    if prev_gray is None:
        prev_gray = gray
        return False
    diff = cv2.absdiff(prev_gray, gray)
    prev_gray = gray
    _, thresh = cv2.threshold(diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return any(cv2.contourArea(c) >= MOTION_MIN_AREA for c in contours)


def box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def classify_pose_action(keypoints_xy: np.ndarray, kp_conf: np.ndarray) -> tuple[str, str]:
    """
    Heuristic action classifier from 17 COCO keypoints.
    Returns (pose, action).
    """
    def vis(i):
        return kp_conf[i] > 0.3

    # Need shoulders + hips at minimum
    if not (vis(KP["l_shoulder"]) and vis(KP["r_shoulder"]) and
            vis(KP["l_hip"]) and vis(KP["r_hip"])):
        return ("unknown", "idle")

    sho_y = (keypoints_xy[KP["l_shoulder"]][1] + keypoints_xy[KP["r_shoulder"]][1]) / 2
    hip_y = (keypoints_xy[KP["l_hip"]][1] + keypoints_xy[KP["r_hip"]][1]) / 2

    # Pose: standing vs sitting vs crouching
    if vis(KP["l_knee"]) and vis(KP["l_ankle"]):
        knee_y = keypoints_xy[KP["l_knee"]][1]
        ankle_y = keypoints_xy[KP["l_ankle"]][1]
        torso = abs(hip_y - sho_y)
        legs = abs(ankle_y - hip_y)
        if legs < torso * 0.5:
            pose = "sitting"
        elif knee_y > hip_y and abs(knee_y - ankle_y) < torso * 0.4:
            pose = "crouching"
        else:
            pose = "standing"
    else:
        pose = "standing"

    # Action: wrist position relative to shoulders
    action = "idle"
    if vis(KP["l_wrist"]) or vis(KP["r_wrist"]):
        wrists_y = []
        wrists_x = []
        if vis(KP["l_wrist"]):
            wrists_y.append(keypoints_xy[KP["l_wrist"]][1])
            wrists_x.append(keypoints_xy[KP["l_wrist"]][0])
        if vis(KP["r_wrist"]):
            wrists_y.append(keypoints_xy[KP["r_wrist"]][1])
            wrists_x.append(keypoints_xy[KP["r_wrist"]][0])
        wrist_y = min(wrists_y)
        sho_height = abs(hip_y - sho_y)

        if wrist_y < sho_y - sho_height * 0.3:
            action = "reaching"   # arms raised — possible grab
        elif wrist_y < sho_y + sho_height * 0.2:
            action = "holding"    # hands at chest level
        elif pose == "sitting":
            action = "sitting"
        else:
            action = "walking" if pose == "standing" else "idle"
    elif pose == "sitting":
        action = "sitting"
    else:
        action = "walking"

    return (pose, action)


def get_wrist_positions(keypoints_xy, kp_conf, person_box):
    """Return list of (x, y) wrist positions visible in frame coords."""
    x1, y1, _, _ = person_box
    wrists = []
    for side in ("l_wrist", "r_wrist"):
        i = KP[side]
        if kp_conf[i] > 0.3:
            wrists.append((keypoints_xy[i][0], keypoints_xy[i][1]))
    return wrists


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
print(json.dumps({"status": "ready", "models": ["yolov8n", "yolov8n-pose", "bytetrack", "fire-hsv"]}), flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        frame_idx += 1
        img_bytes = base64.b64decode(line)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        motion = detect_motion(gray)

        # ALWAYS run fire detection — fire can appear without "motion" mask trigger
        # (compute motion mask from gray frame difference for smoke check)
        if prev_gray is not None:
            motion_mask = cv2.absdiff(prev_gray, gray)
            _, motion_mask = cv2.threshold(motion_mask, 18, 255, cv2.THRESH_BINARY)
        else:
            motion_mask = None
        fire_result = fire_engine.analyze(frame, motion_mask)

        result = {
            "frame": frame_idx, "ts": time.time(), "motion": motion,
            "persons": [], "people_count": 0, "objects": [], "events": [],
            "fire": fire_result,
        }

        # Fire is a critical event — fire it immediately without dedup gate
        if fire_result["fire"] or fire_result["smoke"]:
            result["events"].append({
                "type": "fire" if fire_result["fire"] else "smoke",
                "confidence": fire_result["confidence"],
                "area_pct": fire_result["area_pct"],
                "ts": time.time(),
            })

        if not motion and not fire_result["fire"] and not fire_result["smoke"]:
            print(json.dumps(result), flush=True)
            continue

        # 1. Object detection + tracking
        det = yolo_det.track(frame, persist=True, tracker="bytetrack.yaml",
                             verbose=False, conf=OBJECT_CONF)[0]

        # 2. Pose estimation (separate model — runs on full frame, multi-person)
        pose_res = yolo_pose(frame, verbose=False, conf=PERSON_CONF)[0]

        persons = []
        seen_obj_ids: set[int] = set()

        # Process detected persons + their pose
        if det.boxes is not None and det.boxes.id is not None:
            cls_ids = det.boxes.cls.cpu().numpy().astype(int)
            track_ids = det.boxes.id.cpu().numpy().astype(int)
            confs = det.boxes.conf.cpu().numpy()
            boxes_xyxy = det.boxes.xyxy.cpu().numpy()

            # Build mapping: person box -> closest pose keypoints
            pose_kp_xy = []
            pose_kp_conf = []
            if pose_res.keypoints is not None and len(pose_res.keypoints):
                pose_kp_xy = pose_res.keypoints.xy.cpu().numpy()      # (N, 17, 2)
                pose_kp_conf = pose_res.keypoints.conf.cpu().numpy()  # (N, 17)

            for i, cls_id in enumerate(cls_ids):
                if cls_id == PERSON and confs[i] >= PERSON_CONF:
                    pid = int(track_ids[i])
                    box = tuple(boxes_xyxy[i].astype(float))

                    # Match this detection box to closest pose
                    pose_label, action = "unknown", "idle"
                    if len(pose_kp_xy):
                        det_center = box_center(box)
                        best_idx, best_d = -1, 1e9
                        for j, kps in enumerate(pose_kp_xy):
                            # use mid-shoulder as person center
                            sx = (kps[KP["l_shoulder"]][0] + kps[KP["r_shoulder"]][0]) / 2
                            sy = (kps[KP["l_shoulder"]][1] + kps[KP["r_shoulder"]][1]) / 2
                            d = euclid((sx, sy), det_center)
                            if d < best_d:
                                best_d, best_idx = d, j
                        if best_idx >= 0:
                            pose_label, action = classify_pose_action(
                                pose_kp_xy[best_idx], pose_kp_conf[best_idx]
                            )
                            wrists = get_wrist_positions(
                                pose_kp_xy[best_idx], pose_kp_conf[best_idx], box
                            )
                        else:
                            wrists = []
                    else:
                        wrists = []

                    persons.append({
                        "id": pid,
                        "box": list(box),
                        "confidence": float(confs[i]),
                        "pose": pose_label,
                        "action": action,
                        "wrists": wrists,
                    })

                elif cls_id in GRABBABLE_OBJECTS:
                    tid = int(track_ids[i])
                    seen_obj_ids.add(tid)
                    box = tuple(boxes_xyxy[i].astype(float))
                    name = GRABBABLE_OBJECTS[cls_id]

                    if tid in tracked_objects:
                        obj = tracked_objects[tid]
                        obj.last_seen = frame_idx
                        obj.last_box = box
                        obj.seen_count += 1
                        if obj.seen_count > 30:
                            obj.confirmed_baseline = True
                    else:
                        tracked_objects[tid] = TrackedObject(
                            cls_name=name, last_seen=frame_idx,
                            last_box=box, seen_count=1,
                        )

                    # Track who is nearest
                    center = box_center(box)
                    nearest, nd = None, 1e9
                    for p in persons:
                        d = euclid(center, box_center(p["box"]))
                        if d < nd:
                            nd, nearest = d, p["id"]
                    if nd <= NEAR_DIST_PX:
                        tracked_objects[tid].nearby_person_id = nearest

                    result["objects"].append({"name": name, "box": list(box), "track_id": tid})

        # 3. Detect grab events: confirmed objects that vanished while a person was near
        grab_events = []
        for tid, obj in list(tracked_objects.items()):
            if tid in seen_obj_ids:
                continue
            missing = frame_idx - obj.last_seen
            if missing == OBJECT_MISSING_FRAMES and obj.confirmed_baseline and obj.nearby_person_id is not None:
                grab_events.append({
                    "type": "grab",
                    "object": obj.cls_name,
                    "person_id": obj.nearby_person_id,
                    "last_box": list(obj.last_box),
                    "ts": time.time(),
                })
            if missing > 90:
                tracked_objects.pop(tid, None)

        result["persons"] = persons
        result["people_count"] = len(persons)
        result["events"] = grab_events

        print(json.dumps(result), flush=True)

    except Exception as e:
        print(json.dumps({"error": str(e), "frame": frame_idx}), flush=True)
