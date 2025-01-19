from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb+srv://badawyam:AGuIvjt3zioH8Xhw@ecommerce-platform.grje3.mongodb.net/")
db = client["security_analysis"]
collection = db["detections"]

def store_analysis(results):
    # Prepare data to store
    data = {
        "timestamp": datetime.now().isoformat(),
        "motion_detected": results["motion_detected"],
        "human_detected": results["human_detected"],
        "cat_detected": results["cat_detected"],
        "bag_detected": results["bag_detected"],
        "detected_objects": results["detected_objects"],
    }
    collection.insert_one(data)
    print("Data stored in MongoDB:", data)
