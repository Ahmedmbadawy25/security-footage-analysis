import cv2
import time
import numpy as np
from ultralytics import YOLO
from config import CAMERA_STREAM
from supervision import ByteTrack
from supervision.detection.core import Detections
import supervision
from thread import VideoCaptureThread


video_info = supervision.VideoInfo.from_video_path('./movie.mov')
# video_thread = VideoCaptureThread(CAMERA_STREAM, cv2.CAP_FFMPEG)
video_thread = VideoCaptureThread('./movie.mov', None)

model = YOLO("yolov8n.pt")
tracker = ByteTrack(frame_rate=video_info.fps)

pre_obj = {}
down, up, total_counts = 0, 0, 0

START = (0, video_info.height // 2)
END = (video_info.width, video_info.height // 2)

skip_frames = 3
frame_count = 0

while True:
    img = video_thread.read()

    if img is None:
        break  # End of video

    frame_count += 1
    if frame_count % skip_frames != 0:
        continue  # Skip frames

    results = model(img, conf=0.4, verbose=False)[0]

    # if results.boxes.data.shape[0] == 0:
        # continue  # Skip frame if no detections

    detections = []
    for box in results.boxes:
        if int(box.cls) == 0:  # Only process people
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf.item()
            detections.append([x1, y1, x2, y2, confidence])

    if detections:
        detections = Detections(
            xyxy=np.array(detections, dtype=np.float32)[:, :4],
            confidence=np.array(detections, dtype=np.float32)[:, 4],
            class_id=np.zeros((len(detections),), dtype=int)
        )
        tracked_objects = tracker.update_with_detections(detections)
    else:
        tracked_objects = []
    
    for track in tracked_objects:
        x1, y1, x2, y2 = map(int, track[0])
        track_id = int(track[4])
        centroid_x = (x1 + x2) // 2
        centroid_y = (y1 + y2) // 2
        
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"ID:{track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.circle(img, (centroid_x, centroid_y), 5, (255, 0, 0), -1)
        
        if track_id not in pre_obj:
            pre_obj[track_id] = {"y": centroid_y, "counted": False, "direction": None}
        
        prev_y = pre_obj[track_id]["y"]
        pre_obj[track_id]["y"] = centroid_y

        if not pre_obj[track_id]["counted"]:
            if prev_y < (video_info.height // 2) <= centroid_y:
                up += 1
                total_counts += 1
                pre_obj[track_id]["counted"] = True
                pre_obj[track_id]["direction"] = "up"
                print(f"🔼 Person {track_id} entered")
            elif prev_y > (video_info.height // 2) >= centroid_y:
                down += 1
                total_counts -= 1
                pre_obj[track_id]["counted"] = True
                pre_obj[track_id]["direction"] = "down"
                print(f"🔽 Person {track_id} exited")
    
    cv2.putText(img, f"People Entered: {up}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(img, f"People Exited: {down}", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(img, f"Total Inside: {total_counts}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.line(img, START, END, (0, 255, 0), 2)
  
    cv2.imshow("Footfall Analysis", img)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

video_thread.release()
video_thread.stop()
cv2.destroyAllWindows()
