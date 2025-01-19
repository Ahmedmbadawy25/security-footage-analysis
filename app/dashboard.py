from flask import Flask, render_template
from pymongo import MongoClient
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '../templates'))

# MongoDB connection
client = MongoClient("mongodb+srv://badawyam:AGuIvjt3zioH8Xhw@ecommerce-platform.grje3.mongodb.net/")
db = client["security_analysis"]
collection = db["detections"]

@app.route("/")
def index():
    # Fetch the latest 10 results from MongoDB
    data = list(collection.find().sort("timestamp", -1).limit(10))
    return render_template("dashboard.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
