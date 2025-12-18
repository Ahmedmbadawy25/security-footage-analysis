# People Counter In Real-Time
People Counter in real-time connects to a live video stream/IP camera using RTSP and uses OpenCV and supervision for tracking and counting people.

<div align="center">
<img width=550 src="https://user-images.githubusercontent.com/79955754/145162429-ecadab6f-9314-410f-9fb7-aabac23405d5.png">
</div>

- The primary aim is to use the project to suppoer businesses, ready to scale.
- Use case: counting the number of people in the stores/buildings/shopping malls etc., in real-time.
- Writing visit details to a database to be coupled with an analysis dashboard to provide insights into user visitation details
- Automating features and optimising the real-time stream for better performance (with threading).
- Acts as a measure towards footfall analysis


## Running Inference

### Install the dependencies

First up, install all the required Python dependencies by running: ```
pip install -r requirements.txt ```

> NOTE: Supported Python version is 3.8.9 (there can always be version conflicts between the dependencies, OS, hardware etc.).

### Test video file

To run inference on a test video file, head into the root directory and run the command:

```sh
python footfall.py
```

### IP camera

To run on an IP camera, setup your camera url in ```config.py```, e.g., ```"CAMERA_STREAM": 'http://191.138.0.100:8040/video'```.

Then locate the ```footfall.py``` file and uncomment the following lines of code and comment out the lines that run the test video. Your code should look like so:
```sh
video_info = supervision.VideoInfo.from_video_path(CAMERA_STREAM)
video_thread = VideoCaptureThread(CAMERA_STREAM, cv2.CAP_FFMPEG)

# video_info = supervision.VideoInfo.from_video_path('./people-walking.mp4')
# video_thread = VideoCaptureThread('./people-walking.mp4', None)
```
