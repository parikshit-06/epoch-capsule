import cv2
import tempfile
import os

def capture_photo(retake_allowed=True, resolution=(640, 480)):
    """
    Captures a photo from webcam and returns it as JPEG bytes.
    Press 's' to save, 'r' to retake, 'q' to quit/cancel.
    """
    final_photo_bytes = None

    while True:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera.")

        print("[INFO] Press 's' to save, 'r' to retake, 'q' to cancel.")
        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise RuntimeError("Failed to capture image.")

        frame = cv2.resize(frame, resolution)
        cv2.imshow("Preview - Press 's' to save, 'r' to retake, 'q' to stop", frame)

        key = cv2.waitKey(0) & 0xFF
        cap.release()
        cv2.destroyAllWindows()

        if key == ord('s'):
            # Save to temp and read bytes
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_path = temp_file.name
            temp_file.close()  # <-- Ensure file is closed before writing
            cv2.imwrite(temp_path, frame)

            with open(temp_path, "rb") as f:
                final_photo_bytes = f.read()

            os.remove(temp_path)
            break
        elif key == ord('r') and retake_allowed:
            continue
        elif key == ord('q'):
            print("Photo capture cancelled.")
            break

    return final_photo_bytes