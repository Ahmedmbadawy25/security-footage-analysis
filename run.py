from app.camera import capture_frames
from app.detection import analyze_frame
from app.storage import store_analysis, save_frame_to_disk
from app.alert import send_alert

def main():
    print("Starting security footage analysis...")
    try:
        for frame in capture_frames():
            # Analyze the frame
            results = analyze_frame(frame)

            if results['save_frame']:
                frame_path = save_frame_to_disk(frame)
                print(f"Frame saved: {frame_path}")
                send_alert(recipient="badawy.am@gmail.com", subject="Human detected",message="A human was detected: \n", attachment_path=frame_path)

                # Store the results
                store_analysis(results)

    except KeyboardInterrupt:
        print("Stopping analysis...")
    finally:
        print("System shut down.")

if __name__ == "__main__":
    main()
