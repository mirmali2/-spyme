"""Smoke test — verifies the full detection pipeline works."""
import sys
sys.path.insert(0, 'E:/SPYME/.deps/pkgs')

import time
import cv2
import numpy as np
from ultralytics import YOLO

print("Loading models...")
yolo = YOLO("yolov8n.pt")           # 80-class detection
pose_model = YOLO("yolov8n-pose.pt") # multi-person pose (17 keypoints each)

print(f"  • Detection: {len(yolo.names)} COCO classes (person + 79 objects)")
print(f"  • Pose: 17 keypoints per person, multi-person built-in")

print("\nRunning 5-frame benchmark...")
total = 0
for i in range(5):
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cv2.rectangle(img, (200 + i*15, 150), (350 + i*15, 380), (50, 100, 200), -1)

    t0 = time.time()
    det = yolo.track(img, persist=True, tracker="bytetrack.yaml", verbose=False)[0]
    pose = pose_model(img, verbose=False)[0]
    dt = (time.time() - t0) * 1000
    total += dt
    n_det = len(det.boxes) if det.boxes is not None else 0
    n_pose = len(pose.keypoints) if pose.keypoints is not None else 0
    print(f"  Frame {i}: {dt:6.1f}ms  ({n_det} det, {n_pose} pose)")

avg = total / 5
print(f"\nAvg: {avg:.1f}ms/frame → {1000/avg:.1f} FPS")
print("✓ Pipeline operational")
