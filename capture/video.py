import cv2
import tempfile
import os

def record_video(retake_allowed=True, fps=20.0, resolution=(640, 480), max_duration=None):
    """
    Records a video from the default camera.
    Returns video bytes (MP4 format) without saving permanently.
    Press 'q' to stop recording.
    """
    final_video_bytes = None

    while True:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera.")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_path = temp_file.name
        out = cv2.VideoWriter(temp_path, fourcc, fps, resolution)

        print("[INFO] Recording started. Press 'q' to stop recording.")
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, resolution)
            out.write(frame)
            cv2.imshow("Recording - Press 'q' to stop", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if max_duration and frame_count >= (max_duration * fps):
                break
            frame_count += 1

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Read into memory
        with open(temp_path, "rb") as f:
            final_video_bytes = f.read()

        os.remove(temp_path)  # Remove temp file from disk

        if retake_allowed:
            choice = input("Retake video? (y/n): ").strip().lower()
            if choice == 'y':
                continue
        break

    return final_video_bytes