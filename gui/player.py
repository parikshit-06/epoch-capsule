# gui/player.py
import cv2
import time
import os
from utils.secure_temp import create_secure_temp_file, secure_delete
from datetime import datetime
from typing import Optional
from PIL import Image
import tempfile

def play_video_from_bytes(data: bytes, window_title: str = "TimeCapsule Video"):
    path = create_secure_temp_file(data, suffix=".mp4")
    try:
        while True:
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                cap.release()
                raise RuntimeError("Unable to open video with OpenCV. Your system may lack codec support.")
            cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_title, 960, 720)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow(window_title, frame)
                if cv2.waitKey(33) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyWindow(window_title)
            replay = input("Replay video? (y/n): ").strip().lower()
            if replay != "y":
                break
    finally:
        secure_delete(path)

def show_image_from_bytes(data: bytes, window_title: str = "TimeCapsule Photo"):
    """
    Display an image using OpenCV (via PIL for more formats).
    """
    path = create_secure_temp_file(data, suffix=".jpg")
    try:
        img = cv2.imread(path)
        if img is None:
            # fallback: use PIL to convert then read
            from PIL import Image
            tmp = Image.open(path)
            tmp_path = create_secure_temp_file(tmp.tobytes(), suffix=".bmp")
            img = cv2.imread(tmp_path)
            secure_delete(tmp_path)

        if img is None:
            raise RuntimeError("Cannot decode image for display.")
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_title, 960, 720)
        cv2.imshow(window_title, img)
        print("Press any key in the image window to continue...")
        cv2.waitKey(0)
        cv2.destroyWindow(window_title)
    finally:
        secure_delete(path)

def show_text_from_bytes(data: bytes, title: Optional[str] = None):
    """
    Print text in console and wait for user acknowledgement.
    """
    try:
        txt = data.decode("utf-8")
    except Exception:
        txt = data.decode("latin-1", errors="replace")
    if title:
        print(f"--- {title} ---")
    print(txt)
    input("\nPress Enter after you've read the message...")