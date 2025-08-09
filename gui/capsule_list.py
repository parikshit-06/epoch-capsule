import tkinter as tk
from tkinter import ttk, messagebox
from core.storage import init_db, check_capsules, DB_PATH
import sqlite3
import os
from PIL import Image, ImageTk
import cv2

class CapsuleListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeCapsule - Capsule List")
        self.tree = ttk.Treeview(root, columns=("ID", "Title", "Unlock Time", "Type", "Status"), show="headings")
        for col in ("ID", "Title", "Unlock Time", "Type", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.preview_btn = tk.Button(root, text="Preview Capsule", command=self.preview_capsule)
        self.preview_btn.pack(pady=5)
        self.refresh_btn = tk.Button(root, text="Refresh", command=self.load_capsules)
        self.refresh_btn.pack(pady=5)
        self.load_capsules()

    def load_capsules(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, title, unlock_time, type, status, file_path FROM capsules")
        for row in cur.fetchall():
            self.tree.insert("", tk.END, values=row[:5], tags=(row[3], row[4], row[5]))
        conn.close()

    def preview_capsule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Preview", "Select a capsule to preview.")
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        capsule_id, title, unlock_time, ctype, status = values
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT file_path FROM capsules WHERE id=?", (capsule_id,))
        file_path = cur.fetchone()[0]
        conn.close()
        if not os.path.exists(file_path):
            messagebox.showerror("Preview", "Capsule file not found.")
            return
        if ctype == "photo":
            self.show_image(file_path, title)
        elif ctype == "video":
            self.play_video(file_path, title)
        else:
            with open(file_path, "rb") as f:
                data = f.read()
            self.show_text(data, title)

    def show_image(self, file_path, title):
        win = tk.Toplevel(self.root)
        win.title(f"Preview: {title}")
        img = Image.open(file_path)
        img.thumbnail((480, 360))
        imgtk = ImageTk.PhotoImage(img)
        label = tk.Label(win, image=imgtk)
        label.image = imgtk
        label.pack()

    def play_video(self, file_path, title):
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            messagebox.showerror("Preview", "Cannot open video.")
            return
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, 480, 360)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(title, frame)
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyWindow(title)

    def show_text(self, data, title):
        win = tk.Toplevel(self.root)
        win.title(f"Preview: {title}")
        txt = data.decode("utf-8", errors="replace")
        text_widget = tk.Text(win, wrap="word", width=60, height=20)
        text_widget.insert("1.0", txt)
        text_widget.config(state="disabled")
        text_widget.pack()

def run_capsule_list_gui():
    root = tk.Tk()
    app = CapsuleListApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_capsule_list_gui()