import cv2
import torch

# Load YOLOv8 model (from Ultralytics)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def analyze_frame(frame):
    # Run YOLOv8 detection
    results = model(frame)

    # Parse results
    detected_objects = []
    for obj in results.xyxy[0]:  # Bounding boxes
        x1, y1, x2, y2, confidence, cls = obj.tolist()
        label = model.names[int(cls)]  # Class name
        detected_objects.append({"label": label, "confidence": confidence})

    # Check for specific objects
    motion_detected = len(detected_objects) > 0
    human_detected = any(obj["label"] == "person" for obj in detected_objects)
    cat_detected = any(obj["label"] == "cat" for obj in detected_objects)
    bag_detected = any(obj["label"] == "backpack" or obj["label"] == "handbag" for obj in detected_objects)

    return {
        "motion_detected": motion_detected,
        "human_detected": human_detected,
        "cat_detected": cat_detected,
        "bag_detected": bag_detected,
        "detected_objects": detected_objects,
    }
