import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import tempfile
import os

class PhotoCaptureApp:
    def __init__(self, window, window_title, countdown=3):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0
        self.width = 960  
        self.height = 720  
        self.vid = cv2.VideoCapture(self.video_source)
        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()
        self.btn_prepare = tk.Button(window, text="Prepare Photo", width=20, command=self.start_countdown)
        self.btn_prepare.pack(anchor=tk.CENTER, expand=True)
        self.btn_capture = tk.Button(window, text="Capture Photo", width=20, command=self.capture_photo, state=tk.DISABLED)
        self.btn_capture.pack(anchor=tk.CENTER, expand=True)
        self.btn_quit = tk.Button(window, text="Quit", width=10, command=self.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)
        self.label = tk.Label(window, text="Adjust your orientation, then click 'Prepare Photo'.")
        self.label.pack(anchor=tk.CENTER, expand=True)
        self.delay = 15
        self.photo_bytes = None
        self.captured = False
        self.countdown = countdown
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.quit)

    def start_countdown(self):
        self.btn_prepare.config(state=tk.DISABLED)
        self.label.config(text=f"Get ready! Capturing in {self.countdown} seconds...")
        self._countdown(self.countdown)

    def _countdown(self, remaining):
        if remaining > 0:
            self.label.config(text=f"Get ready! Capturing in {remaining} seconds...")
            self.window.after(1000, self._countdown, remaining - 1)
        else:
            self.label.config(text="Press 'Capture Photo' to take the picture.")
            self.btn_capture.config(state=tk.NORMAL)

    def capture_photo(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))  # Resize to match window
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_path = temp_file.name
            cv2.imwrite(temp_path, frame)
            with open(temp_path, "rb") as f:
                self.photo_bytes = f.read()
            os.remove(temp_path)
            messagebox.showinfo("Photo", "Photo captured! Close window to finish.")
            self.captured = True
            self.btn_capture.config(state=tk.DISABLED)
            self.label.config(text="Photo captured. You may close the window.")

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))  
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.imgtk = imgtk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        if not self.captured:
            self.window.after(self.delay, self.update)

    def quit(self):
        self.vid.release()
        self.window.destroy()

def capture_photo_gui():
    root = tk.Tk()
    app = PhotoCaptureApp(root, "Photo Capture")
    root.mainloop()
    return app.photo_bytes

if __name__ == "__main__":
    photo_bytes = capture_photo_gui()
    if photo_bytes:
        with open("captured_photo.jpg", "wb") as f:
            f.write(photo_bytes)
        print("Photo saved as captured_photo.jpg")
    else:
        print("No photo captured.")