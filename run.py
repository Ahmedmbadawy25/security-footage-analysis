from app.camera import capture_frames
from app.detection import analyze_frame
from app.storage import store_analysis

def main():
    print("Starting security footage analysis...")
    try:
        for frame in capture_frames():
            # Analyze the frame
            results = analyze_frame(frame)

            # Store the results
            store_analysis(results)
    except KeyboardInterrupt:
        print("Stopping analysis...")
    finally:
        print("System shut down.")

if __name__ == "__main__":
    main()
