import cv2, threading, queue

class VideoCaptureThread:
    def __init__(self, video_source, extras):
        self.cap = cv2.VideoCapture(video_source, extras)
        self.q = queue.Queue()  # Set max queue size
        self.stopped = False
        self.t = threading.Thread(target=self._reader, daemon=True)
        self.t.start()

    def _reader(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not self.cap.isOpened():
              print("ERROR: Could not open camera stream. Check the RTSP URL or camera connection.")
              exit(1)
            if not ret:
                self.stopped= True
                self.q.put(None)
                print("Video ended or failed to read frame.")
                break
            self.q.put(frame, block=True)  # Add frame to queue if there's space

    def read(self):
        return self.q.get()  # Fetch frames from queue

    def release(self):
        self.cap.release()

    def stop(self):
        self.stopped = True
        self.t.join()
        self.cap.release()