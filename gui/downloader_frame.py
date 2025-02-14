# downloader_frame.py (Reverted to Original Version)

import tkinter as tk
from tkinter import ttk, messagebox

from core.event_bus import event_bus
from core.downloader import download_video

class DownloaderFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        event_bus.subscribe("download_complete", self.on_download_complete)
        event_bus.subscribe("download_failed", self.on_download_failed)
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates the original Downloader layout (no embedded browser).
        """
        lbl_url = tk.Label(self, text="YouTube URL:")
        lbl_url.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.entry_url = tk.Entry(self, width=50)
        self.entry_url.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        lbl_res = tk.Label(self, text="Resolution:")
        lbl_res.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.res_options = ["1080p", "720p", "480p", "360p", "best"]
        self.res_var = tk.StringVar(value=self.res_options[0])
        self.dropdown_res = ttk.Combobox(
            self,
            textvariable=self.res_var,
            values=self.res_options,
            state="readonly"
        )
        self.dropdown_res.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.auto_load_var = tk.BooleanVar(value=True)
        chk_auto = tk.Checkbutton(self, text="Auto-load into Trimmer", variable=self.auto_load_var)
        chk_auto.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.btn_download = tk.Button(self, text="Download", command=self.start_download)
        self.btn_download.grid(row=3, column=1, padx=5, pady=10, sticky="w")

        self.text_log = tk.Text(self, height=5)
        self.text_log.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def log(self, message):
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)

    def start_download(self):
        """
        Called when the user clicks the 'Download' button.
        """
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
            return
        self.btn_download.config(state="disabled")
        self.log("Starting download...")
        download_video(url, self.res_var.get(), self.auto_load_var.get())

    def on_download_complete(self, filename):
        self.log("Download complete.")
        self.log(f"Saved as: {filename}")
        self.btn_download.config(state="normal")
        if self.auto_load_var.get():
            event_bus.publish("auto_load_video", filename)

    def on_download_failed(self, error_message):
        self.log(f"Download failed: {error_message}")
        self.btn_download.config(state="normal")
