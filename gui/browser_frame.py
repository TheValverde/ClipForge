import tkinter as tk
import webview
import threading
from tkinter import ttk, messagebox

class BrowserFrame(tk.Frame):
    """
    A Tkinter Frame that controls a PyWebView YouTube browser.
    The browser opens inside a floating Toplevel window that resizes with the Downloader tab.
    """
    def __init__(self, parent, on_video_selected):
        """
        :param parent: Tkinter parent widget
        :param on_video_selected: Callback function to receive the selected video URL
        """
        super().__init__(parent)
        self.parent = parent
        self.on_video_selected = on_video_selected
        self.browser_window = None  # Holds the Toplevel window
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates the Tkinter UI elements inside the Downloader frame.
        """
        lbl_instructions = ttk.Label(self, text="Browse YouTube below. Click 'Select Video' to choose a video.")
        lbl_instructions.pack(pady=5, anchor="w")

        self.btn_select_video = ttk.Button(self, text="Select Video", command=self._select_video)
        self.btn_select_video.pack(pady=5, anchor="w")

        self.btn_open_browser = ttk.Button(self, text="Open Browser", command=self._open_browser)
        self.btn_open_browser.pack(pady=5, anchor="w")

    def _open_browser(self):
        """
        Creates a floating browser window inside a `Toplevel` that follows this frame.
        """
        if self.browser_window:
            self.browser_window.deiconify()  # Show window if already created
            return
        
        # Create a new floating Toplevel window
        self.browser_window = tk.Toplevel(self)
        self.browser_window.title("YouTube Browser")
        self.browser_window.geometry("800x600")  # Set an initial size
        self.browser_window.protocol("WM_DELETE_WINDOW", self._hide_browser)  # Hide instead of closing

        # Ensure window follows the parent layout
        self.browser_window.transient(self.parent)

        # Run the browser in a new thread
        threading.Thread(target=self._start_webview, daemon=True).start()

    def _hide_browser(self):
        """Hides the browser window instead of closing it."""
        if self.browser_window:
            self.browser_window.withdraw()  # Hide instead of destroying

    def _start_webview(self):
        """
        Starts the PyWebView browser in a separate thread.
        """
        webview.create_window(
            "YouTube Browser",
            url="https://www.youtube.com",
            frameless=False,
            easy_drag=True
        )
        webview.start(gui="tk", debug=False)

    def _select_video(self):
        """
        Gets the current URL from PyWebView and sends it to the parent frame.
        """
        if not webview.windows:
            messagebox.showwarning("Browser Not Ready", "The browser is still loading. Try again in a few seconds.")
            return
        
        current_url = webview.windows[0].get_current_url()  # Ensure the browser is loaded
        if "youtube.com/watch" in current_url:
            self.on_video_selected(current_url)
        else:
            messagebox.showwarning("Not a Video Page", "Please navigate to a valid YouTube video URL.")
