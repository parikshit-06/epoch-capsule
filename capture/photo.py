# capture/photo.py
import cv2
import tempfile
import os

def capture_photo(retake_allowed=True, resolution=(640, 480)):
    """
    Captures a photo from webcam and returns it as JPEG bytes.
    """
    final_photo_bytes = None

    while True:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera.")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise RuntimeError("Failed to capture image.")

        frame = cv2.resize(frame, resolution)
        cv2.imshow("Preview - Press 's' to save, 'r' to retake", frame)
        
        key = cv2.waitKey(0) & 0xFF
        if key == ord('s'):
            # Save to temp and read bytes
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_path = temp_file.name
            cv2.imwrite(temp_path, frame)

            with open(temp_path, "rb") as f:
                final_photo_bytes = f.read()

            os.remove(temp_path)
            cv2.destroyAllWindows()
            break
        elif key == ord('r') and retake_allowed:
            cv2.destroyAllWindows()
            continue
        else:
            cv2.destroyAllWindows()
            break

    return final_photo_bytes