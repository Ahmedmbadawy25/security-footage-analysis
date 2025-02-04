import cv2
import time
import math
import numpy as np
import torch
from ultralytics import YOLO
from config import CAMERA_STREAM
# from bytetrack.byte_tracker import BYTETracker  # Import ByteTrack
from supervision import ByteTrack
from supervision.detection.core import Detections

FRAME_DELAY = 1 / 7  # 10 FPS
last_frame_time = time.time()

# Load Video
# video = cv2.VideoCapture(CAMERA_STREAM, cv2.CAP_FFMPEG)
# video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduce resolution for faster processing
# video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video = cv2.VideoCapture('./movie.mov')
if not video.isOpened():
    print("ERROR: Could not open camera stream. Check the RTSP URL or camera connection.")
    exit(1)


model = YOLO("yolov8n.pt")

# Initialize ByteTrack
# tracker = BYTETracker()
tracker = ByteTrack(frame_rate=10)

# Tracking variables
pre_obj = {}
down = 0  # Count people exiting
up = 0  # Count people entering
total_counts = 0
init_time = time.time()

# Processing Loop
while True:
    retry_count = 0
    while retry_count < 3:
        ret, img = video.read()
        if ret:
            break
        retry_count += 1
        print(f"WARNING: Retrying frame read ({retry_count}/3)...")

    # DELETE 
    if img is None:
        print("Done")
        break
    
    if time.time() - last_frame_time >= FRAME_DELAY:
        last_frame_time = time.time()  # Only update when actually processing a frame
    else:
        continue  # Skip frame if it's too soon
    # while time.time() - last_frame_time < FRAME_DELAY:
    #     pass  # Simple wait loop
    # last_frame_time = time.time()

    # Run YOLOv8 model for detection
    results = model(img, conf=0.4, verbose=False)[0]  # Get detection results

    # if results.boxes.data.shape[0] == 0:
        # continue  # Skip frame if no detections


    detections = []
    for box in results.boxes:
        if int(box.cls) == 0:  # Only process people
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Correctly extract (x1, y1, x2, y2)
            confidence = box.conf.item()
            detections.append([x1, y1, x2, y2, confidence])  # Store correct format


    # Run ByteTrack on detected people
    if len(detections) > 0:
        detections = Detections(
            xyxy=np.array(detections, dtype=np.float32)[:, :4],
            confidence=np.array(detections, dtype=np.float32)[:, 4],
            class_id=np.zeros((len(detections),), dtype=int)
        )
        tracked_objects = tracker.update_with_detections(detections)
    else:
        tracked_objects = []


    # Define the counting zone
    line_start = (500, 500)  # Top-left corner
    line_end = (2850, 1300)    # Bottom-right corner
    cv2.line(img, line_start, line_end, (0, 255, 0), 2)

    def is_point_below_line(x, y, line_start, line_end):
        x1, y1 = line_start
        x2, y2 = line_end
        return (y2 - y1) * x - (x2 - x1) * y + (x2 * y1 - x1 * y2) > 0

    # Process tracked people
    for track in tracked_objects:
        x1, y1, x2, y2 = map(int, track[0])
        bbox, _, confidence, _, track_id, _ = track
        track_id = int(track_id)

        # Compute width and height from (x1, y1, x2, y2)
        centroid_x = (x1 + x2) // 2
        centroid_y = (y1 + y2) // 2
        

        # Draw bounding boxes & track ID & centroid
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"ID:{track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.circle(img, (x1 + (x2 - x1) // 2, centroid_y), 5, (255, 0, 0), -1)

        if str(track_id) not in pre_obj:
            pre_obj[str(track_id)] = {"y": centroid_y, "counted": False, "last_direction": None}
        
        HYSTERESIS = 10

        # Check if person crosses the counting zone
        if abs(pre_obj[str(track_id)]["y"] - centroid_y) > HYSTERESIS:
            if is_point_below_line(centroid_x, centroid_y, line_start, line_end):
                    if str(track_id) not in pre_obj:
                        pre_obj[str(track_id)] = {"y": centroid_y, "counted": False, "last_direction": None}

                    if not pre_obj[str(track_id)]["counted"]:
                        prev_y = pre_obj[str(track_id)]["y"]

                        if prev_y < centroid_y - HYSTERESIS and pre_obj[str(track_id)]["last_direction"] != "down":
                            print(f"🔽 Person {track_id} exited")
                            down += 1
                            total_counts -= 1
                            pre_obj[str(track_id)]["counted"] = True
                            pre_obj[str(track_id)]["last_direction"] = "down"

                        elif prev_y > centroid_y + HYSTERESIS and pre_obj[str(track_id)]["last_direction"] != "up":
                            print(f"🔼 Person {track_id} entered")
                            up += 1
                            total_counts += 1
                            pre_obj[str(track_id)]["counted"] = True
                            pre_obj[str(track_id)]["last_direction"] = "up"


    # Display information on screen
    cv2.putText(img, f"People Entered: {up}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(img, f"People Exited: {down}", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(img, f"Total Inside: {total_counts}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Show and save output
    cv2.imshow("Video", img)

    # Press 'q' to exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Cleanup
video.release()
cv2.destroyAllWindows()
