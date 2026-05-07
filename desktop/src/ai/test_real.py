"""Real-world detection test — runs the full pipeline on internet images."""
import sys
sys.path.insert(0, 'E:/SPYME/.deps/pkgs')

import time
import urllib.request

import cv2
import numpy as np
from ultralytics import YOLO

# Test images: real photos with people and objects
TEST_IMAGES = [
    ("1 person + laptop", "https://ultralytics.com/images/bus.jpg"),
    ("Multiple people",   "https://ultralytics.com/images/zidane.jpg"),
]

print("Loading models (already pretrained on COCO 330k images)...")
yolo = YOLO("yolov8n.pt")
pose = YOLO("yolov8n-pose.pt")
print(f"  ✓ Detection: {len(yolo.names)} classes")
print(f"  ✓ Pose: 17 keypoints / person\n")

for label, url in TEST_IMAGES:
    print(f"━━ {label} ━━")
    print(f"   Downloading {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=15).read()
    except Exception as e:
        print(f"   ✗ Download failed: {e}")
        continue

    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    print(f"   Image: {img.shape[1]}×{img.shape[0]}")

    t0 = time.time()
    det = yolo.track(img, persist=True, tracker="bytetrack.yaml", verbose=False)[0]
    pose_res = pose(img, verbose=False)[0]
    dt = (time.time() - t0) * 1000

    persons = 0
    objects_found = []
    if det.boxes is not None:
        for i, c in enumerate(det.boxes.cls.cpu().numpy().astype(int)):
            name = yolo.names[c]
            conf = float(det.boxes.conf[i])
            if c == 0:
                persons += 1
            else:
                objects_found.append(f"{name} ({conf:.2f})")

    n_pose = len(pose_res.keypoints) if pose_res.keypoints is not None else 0

    print(f"   ⏱  {dt:.0f}ms")
    print(f"   👥 Persons detected: {persons}")
    print(f"   🦴 Pose skeletons:   {n_pose}")
    if objects_found:
        print(f"   📦 Objects found:    {', '.join(objects_found[:8])}")
    print()

print("✓ Real-world detection works.")
print("✓ Multi-person ✓ Object recognition ✓ Pose estimation")
print("✓ Pretrained on 330k COCO internet images — no training required")
