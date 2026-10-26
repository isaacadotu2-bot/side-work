import ctypes
import platform
import random
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def set_wallpaper(path: str):
    system = platform.system()
    if system == "Windows":
        # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE = 3
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
    elif system == "Darwin":
        script = f'tell application "System Events" to set picture of every desktop to POSIX file "{path}"'
        subprocess.run(["osascript", "-e", script], check=True)
    else:  # Linux, GNOME-family desktops
        uri = Path(path).resolve().as_uri()
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri], check=False)


class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Changer")
        self.images = []
        self.timer_id = None

        top = tk.Frame(root)
        top.pack(fill="x", padx=10, pady=10)
        tk.Button(top, text="Choose folder", command=self.choose_folder).pack(side="left")
        self.folder_label = tk.Label(top, text="No folder selected", anchor="w")
        self.folder_label.pack(side="left", padx=10)

        self.listbox = tk.Listbox(root, width=60, height=15)
        self.listbox.pack(padx=10, fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.apply_selected())

        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=10, pady=10)
        tk.Button(bottom, text="Set selected", command=self.apply_selected).pack(side="left")
        tk.Button(bottom, text="Random", command=self.apply_random).pack(side="left", padx=5)
        tk.Label(bottom, text="Rotate every (min):").pack(side="left", padx=(20, 5))
        self.interval = tk.Spinbox(bottom, from_=1, to=1440, width=5)
        self.interval.delete(0, "end")
        self.interval.insert(0, "30")
        self.interval.pack(side="left")
        self.rotate_btn = tk.Button(bottom, text="Start rotation", command=self.toggle_rotation)
        self.rotate_btn.pack(side="left", padx=5)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.images = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in IMAGE_EXTS)
        self.listbox.delete(0, "end")
        for img in self.images:
            self.listbox.insert("end", img.name)
        self.folder_label.config(text=folder)

    def apply_selected(self):
        sel = self.listbox.curselection()
        if sel:
            self.apply(self.images[sel[0]])

    def apply_random(self):
        if self.images:
            self.apply(random.choice(self.images))

    def apply(self, path: Path):
        try:
            set_wallpaper(str(path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not set wallpaper:\n{e}")

    def toggle_rotation(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            self.rotate_btn.config(text="Start rotation")
        else:
            self.rotate_btn.config(text="Stop rotation")
            self.tick()

    def tick(self):
        self.apply_random()
        minutes = max(1, int(self.interval.get()))
        self.timer_id = self.root.after(minutes * 60 * 1000, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    WallpaperApp(root)
    root.mainloop()