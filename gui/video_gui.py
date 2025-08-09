import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import tempfile
import os

class VideoCaptureApp:
    def __init__(self, window, window_title, fps=20.0):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0
        self.width = 960  
        self.height = 720  
        self.vid = cv2.VideoCapture(self.video_source)
        self.fps = fps
        self.recording = False
        self.frames = []
        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()
        self.btn_record = tk.Button(window, text="Start Recording", width=20, command=self.toggle_recording)
        self.btn_record.pack(anchor=tk.CENTER, expand=True)
        self.btn_quit = tk.Button(window, text="Quit", width=10, command=self.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)
        self.label = tk.Label(window, text="Adjust your orientation, then click 'Start Recording'.")
        self.label.pack(anchor=tk.CENTER, expand=True)
        self.delay = 15
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.video_bytes = None

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.frames = []
            self.btn_record.config(text="Stop Recording")
            self.label.config(text="Recording... Click 'Stop Recording' to finish.")
        else:
            self.recording = False
            self.btn_record.config(text="Start Recording")
            self.label.config(text="Adjust your orientation, then click 'Start Recording'.")
            self.save_video()

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))  # Resize to match window
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.imgtk = imgtk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            if self.recording:
                self.frames.append(frame)
        self.window.after(self.delay, self.update)

    def save_video(self):
        if not self.frames:
            messagebox.showinfo("Video", "No frames recorded.")
            return
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_path = temp_file.name
        height, width, _ = self.frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, self.fps, (width, height))
        for frame in self.frames:
            out.write(frame)
        out.release()
        with open(temp_path, "rb") as f:
            self.video_bytes = f.read()
        os.remove(temp_path)
        messagebox.showinfo("Video", "Video captured! Close window to finish.")

    def quit(self):
        self.vid.release()
        self.window.destroy()

def record_video_gui():
    root = tk.Tk()
    app = VideoCaptureApp(root, "Video Capture")
    root.mainloop()
    return app.video_bytes

if __name__ == "__main__":
    video_bytes = record_video_gui()
    if video_bytes:
        with open("captured_video.mp4", "wb") as f:
            f.write(video_bytes)
        print("Video saved as captured_video.mp4")
    else:
        print("No video captured.")