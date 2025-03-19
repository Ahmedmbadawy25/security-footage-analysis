import cv2
from bson import ObjectId
from datetime import datetime
import pytz
import numpy as np
from ultralytics import YOLO
from config import CAMERA_STREAM, collection, STORE_ID
from supervision import ByteTrack
from supervision.detection.core import Detections
import supervision
from thread import VideoCaptureThread
from db_writer_thread import log_event
import logging

# ------------------------ Configuration & Setup ------------------------

# Configure logging for better monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Edge mode flag: set True when deploying on resource-constrained devices (e.g., Raspberry Pi)
EDGE_MODE = False
# When EDGE_MODE is True, we downscale input frames to reduce inference cost.
INFERENCE_SCALE = 0.5 if EDGE_MODE else 1.0

SKIP_FRAMES = 3               # Process every third frame to reduce load
SMOOTHING_FACTOR = 0.5        # For exponential smoothing of the centroid position

# Timezone for timestamping
egypt_tz = pytz.timezone("Africa/Cairo")


# ------------------------ Video Capture & Model Initialization ------------------------

# video_info = supervision.VideoInfo.from_video_path(CAMERA_STREAM)
# video_thread = VideoCaptureThread(CAMERA_STREAM, cv2.CAP_FFMPEG)

video_info = supervision.VideoInfo.from_video_path('./people-walking.mp4')
video_thread = VideoCaptureThread('./people-walking.mp4', None)

# Attempt to use GPU acceleration if available
try:
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
except ImportError:
    device = 'cpu'
logging.info(f"Using device: {device}")

# Load YOLO model and set device
model = YOLO("yolov8n.pt")
model.to(device)

# Initialize the tracker (ByteTrack) with the video's FPS
tracker = ByteTrack(frame_rate=video_info.fps)


# ------------------------ State Variables & Helper Functions ------------------------

pre_obj = {}
down, up, total_counts = 0, 0, 0

START = (0, video_info.height // 2)
END = (video_info.width, video_info.height // 2)

frame_count = 0
# Define track expiry: if a track is not updated for this many frames, remove it (here, 2 seconds worth)
TRACK_EXPIRY_FRAMES = int(video_info.fps * 2)

def cleanup_tracks(current_frame):
    """Remove tracks from pre_obj that haven't been updated within a given threshold."""
    keys_to_delete = []
    for track_id, data in pre_obj.items():
        if current_frame - data.get("last_frame", current_frame) > TRACK_EXPIRY_FRAMES:
            keys_to_delete.append(track_id)
    for key in keys_to_delete:
        del pre_obj[key]

# ------------------------ Main Processing Loop ------------------------


while True:
    try:
        img = video_thread.read()
        if img is None:
            logging.info("End of video or stream.")
            break
    except Exception as e:
        logging.error(f"Video capture error: {e}")
        break

    frame_count += 1
    if frame_count % SKIP_FRAMES != 0:
        continue  # Skip frames

    # Work on a copy of the original image for display purposes
    original_img = img.copy()

    # If in edge mode, downscale image for inference and then rescale results later
    if INFERENCE_SCALE != 1.0:
        img = cv2.resize(img, (0, 0), fx=INFERENCE_SCALE, fy=INFERENCE_SCALE)

    try:
        # Run model inference (the confidence threshold is still static; consider adapting it further if needed)
        results = model(img, conf=0.4, verbose=False)[0]
    except Exception as e:
        logging.error(f"Model inference error: {e}")
        continue

    # if results.boxes.data.shape[0] == 0:
        # cleanup_tracks(frame_count)
        # continue  # Skip frame if no detections

    detections = []
    for box in results.boxes:
        if int(box.cls) == 0:  # Only process people
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # If the frame was downscaled, convert coordinates back to original scale
            if INFERENCE_SCALE != 1.0:
                x1 = int(x1 / INFERENCE_SCALE)
                y1 = int(y1 / INFERENCE_SCALE)
                x2 = int(x2 / INFERENCE_SCALE)
                y2 = int(y2 / INFERENCE_SCALE)
            # Filter out detections that are too small (may be false positives)
            width = x2 - x1
            height = y2 - y1
            if width < 20 or height < 20:
                continue
            confidence = box.conf.item()
            detections.append([x1, y1, x2, y2, confidence])

    # Update tracker with valid detections
    if detections:
        detections = Detections(
            xyxy=np.array(detections, dtype=np.float32)[:, :4],
            confidence=np.array(detections, dtype=np.float32)[:, 4],
            class_id=np.zeros((len(detections),), dtype=int)
        )
        tracked_objects = tracker.update_with_detections(detections)
    else:
        tracked_objects = []
        cleanup_tracks(frame_count)
        continue

    # Process each tracked object
    for track in tracked_objects:
        x1, y1, x2, y2 = map(int, track[0])
        track_id = int(track[4])
        centroid_x = (x1 + x2) // 2
        centroid_y = (y1 + y2) // 2
        
        # Draw the bounding box, track ID, and centroid on the original image
        cv2.rectangle(original_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(original_img, f"ID:{track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.circle(original_img, (centroid_x, centroid_y), 5, (255, 0, 0), -1)
        
        # Apply exponential smoothing to the y-coordinate of the centroid
        if track_id in pre_obj:
            prev_centroid = pre_obj[track_id]["y"]
            smoothed_centroid = int(SMOOTHING_FACTOR * centroid_y + (1 - SMOOTHING_FACTOR) * prev_centroid)
        else:
            smoothed_centroid = centroid_y

        # Update the track info with the current frame number for expiry management
        pre_obj.setdefault(track_id, {})
        pre_obj[track_id]["last_frame"] = frame_count

        # Initialize the previous y-coordinate if not present
        if "y" not in pre_obj[track_id]:
            pre_obj[track_id]["y"] = smoothed_centroid

        prev_y = pre_obj[track_id]["y"]
        pre_obj[track_id]["y"] = smoothed_centroid

        # Count logic: check if the smoothed centroid has crossed the mid-line
        if not pre_obj[track_id].get("counted", False):
            event = None
            # Person moving upward (entering)
            if prev_y < (video_info.height // 2) <= smoothed_centroid:
                up += 1
                total_counts += 1
                pre_obj[track_id]["counted"] = True
                pre_obj[track_id]["direction"] = "up"
                event = 'entry'
                logging.info(f"🔼 Person {track_id} entered")
            # Person moving downward (exiting)
            elif prev_y > (video_info.height // 2) >= smoothed_centroid:
                down += 1
                total_counts = max(0, total_counts - 1)
                pre_obj[track_id]["counted"] = True
                pre_obj[track_id]["direction"] = "down"
                event = 'exit'
                logging.info(f"🔽 Person {track_id} exited")

            if event == 'entry':
                egypt_time = datetime.now(egypt_tz)
                event_data = {
                    "store_id": ObjectId(STORE_ID),
                    "timestamp": egypt_time,
                    "event_type": event,
                    "hour": egypt_time.hour,
                    "day": egypt_time.strftime("%A"),
                    "day_of_month": egypt_time.day,
                    "week": egypt_time.isocalendar()[1],
                    "month": egypt_time.month,
                    "year": egypt_time.year,
                }
                log_event(event_data)
    
    # Draw UI elements (counts, mid-line) on the display image
    cv2.putText(original_img, f"People Entered: {up}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(original_img, f"People Exited: {down}", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(original_img, f"Total Inside: {total_counts}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.line(original_img, START, END, (0, 255, 0), 2)
  
    cv2.imshow("Footfall Analysis", original_img)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    # Periodically clean up expired tracks
    cleanup_tracks(frame_count)

# ------------------------ Cleanup & Shutdown ------------------------

video_thread.release()
video_thread.stop()
cv2.destroyAllWindows()
log_event(None)

