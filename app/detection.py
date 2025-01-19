import cv2
import torch

# Load YOLOv8 model (from Ultralytics)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def analyze_frame(frame, confidence_threshold=0.75):
    # Run YOLOv8 detection
    results = model(frame)

    # Parse results
    detected_objects = []
    human_detected = False
    save_frame = False
    for obj in results.xyxy[0]:  # Bounding boxes
        x1, y1, x2, y2, confidence, cls = obj.tolist()
        label = model.names[int(cls)]  # Class name
        detected_objects.append({"label": label, "confidence": confidence})
        
        if label == "person" and confidence >= confidence_threshold:
            human_detected = True
            save_frame = True

    return {
        "human_detected": human_detected,
        "detected_objects": detected_objects,
        "save_frame": save_frame
    }
