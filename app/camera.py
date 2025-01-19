import cv2

from config import CAMERA_STREAM


def capture_frames():
    cap = cv2.VideoCapture(CAMERA_STREAM, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise Exception("Failed to connect to the camera stream.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        print("frame read successfully")
        print(ret)
        yield frame

    cap.release()

capture_frames()