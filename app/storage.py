from pymongo import MongoClient
from datetime import datetime
import os
import cv2

# MongoDB connection
client = MongoClient("mongodb+srv://badawyam:AGuIvjt3zioH8Xhw@ecommerce-platform.grje3.mongodb.net/")
db = client["security_analysis"]
collection = db["detections"]
FRAME_STORAGE_DIR = "frames"

# Ensure the directory exists
os.makedirs(FRAME_STORAGE_DIR, exist_ok=True)

def save_frame_to_disk(frame):
    """
    Save the frame to disk and return the file path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frame_path = os.path.join(FRAME_STORAGE_DIR, f"frame_{timestamp}.jpg")
    cv2.imwrite(frame_path, frame)
    return frame_path

def store_analysis(results):
    # Prepare data to store
    data = {
        "timestamp": datetime.now().isoformat(),
        "human_detected": results["human_detected"],
        "detected_objects": results["detected_objects"],
    }
    collection.insert_one(data)
    print("Data stored in MongoDB:", data)
