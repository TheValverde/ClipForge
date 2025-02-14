# comprehensive_app.py

import tkinter as tk
from tkinter import ttk
from .downloader_frame import DownloaderFrame
from .trimmer_frame import TrimmerFrame

class ComprehensiveApp:
    """Holds the main Notebook and adds the frames as tabs."""
    def __init__(self, root):
        self.root = root
        self.root.title("Clip Farming Tool")
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.downloader_frame = DownloaderFrame(self.notebook)
        self.notebook.add(self.downloader_frame, text="YouTube Downloader")

        self.trimmer_frame = TrimmerFrame(self.notebook)
        self.notebook.add(self.trimmer_frame, text="Video Trimmer")
