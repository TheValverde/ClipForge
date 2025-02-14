import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import vlc
import yt_dlp

# ----------------- Video Preview Class -----------------

class VideoPreview:
    def __init__(self, parent):
        self.parent = parent
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.preview_start_ms = 0
        self.preview_end_ms = 0
        self.slider_dragging = False

        # Frame for video preview and controls.
        self.frame = tk.Frame(parent)
        self.frame.pack(fill="x", padx=10, pady=5)
        self.canvas = tk.Canvas(self.frame, width=400, height=300, bg="black")
        self.canvas.pack()

        self.controls_frame = tk.Frame(self.frame)
        self.controls_frame.pack(fill="x", pady=5)

        self.btn_play_pause = tk.Button(self.controls_frame, text="Play", command=self.toggle_play)
        self.btn_play_pause.pack(side="left", padx=5)
        self.btn_mute = tk.Button(self.controls_frame, text="Mute", command=self.toggle_mute)
        self.btn_mute.pack(side="left", padx=5)

        self.slider = tk.Scale(self.controls_frame, from_=0, to=100, orient="horizontal",
                               command=self.on_slider_move, length=200)
        self.slider.pack(side="left", fill="x", expand=True, padx=5)
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.update_slider()

    def load_video(self, video_file):
        self.media = self.instance.media_new(video_file)
        self.player.set_media(self.media)
        # Embed video in canvas
        if os.name == "nt":
            self.player.set_hwnd(self.canvas.winfo_id())
        else:
            self.player.set_xwindow(self.canvas.winfo_id())

    def set_range(self, start_time_str, end_time_str):
        self.preview_start_ms = self.time_str_to_ms(start_time_str)
        self.preview_end_ms = self.time_str_to_ms(end_time_str)
        if self.preview_end_ms > self.preview_start_ms:
            self.slider.config(from_=0, to=self.preview_end_ms - self.preview_start_ms)
        else:
            self.slider.config(from_=0, to=0)
        self.player.set_time(self.preview_start_ms)

    def time_str_to_ms(self, time_str):
        parts = time_str.split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            seconds = parts[0] * 60 + parts[1]
        else:
            seconds = parts[0]
        return seconds * 1000

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.btn_play_pause.config(text="Play")
        else:
            self.player.play()
            self.btn_play_pause.config(text="Pause")

    def toggle_mute(self):
        muted = self.player.audio_get_mute()
        self.player.audio_set_mute(not muted)
        self.btn_mute.config(text="Unmute" if not muted else "Mute")

    def on_slider_move(self, value):
        if self.slider_dragging:
            new_time = self.preview_start_ms + int(value)
            self.player.set_time(new_time)

    def on_slider_press(self, event):
        self.slider_dragging = True

    def on_slider_release(self, event):
        self.slider_dragging = False

    def update_slider(self):
        if self.player.is_playing() and not self.slider_dragging:
            current_time = self.player.get_time()
            if current_time < self.preview_start_ms:
                current_time = self.preview_start_ms
            if current_time > self.preview_end_ms:
                self.player.set_time(self.preview_start_ms)
                current_time = self.preview_start_ms
            slider_value = current_time - self.preview_start_ms
            self.slider.set(slider_value)
        self.parent.after(200, self.update_slider)


# ----------------- YouTube Downloader Tab -----------------

class DownloaderFrame(tk.Frame):
    def __init__(self, parent, auto_load_callback):
        super().__init__(parent)
        self.auto_load_callback = auto_load_callback
        self.create_widgets()

    def create_widgets(self):
        # URL input
        lbl_url = tk.Label(self, text="YouTube URL:")
        lbl_url.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_url = tk.Entry(self, width=50)
        self.entry_url.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Resolution selection
        lbl_res = tk.Label(self, text="Resolution:")
        lbl_res.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.res_options = ["1080p", "720p", "480p", "360p", "best"]
        self.res_var = tk.StringVar(value=self.res_options[0])
        self.dropdown_res = ttk.Combobox(self, textvariable=self.res_var, values=self.res_options, state="readonly")
        self.dropdown_res.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Auto-load toggle
        self.auto_load_var = tk.BooleanVar(value=True)
        chk_auto = tk.Checkbutton(self, text="Auto-load into Trimmer", variable=self.auto_load_var)
        chk_auto.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Download button
        self.btn_download = tk.Button(self, text="Download", command=self.start_download)
        self.btn_download.grid(row=3, column=1, padx=5, pady=10, sticky="w")

        # Log output
        self.text_log = tk.Text(self, height=8)
        self.text_log.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Configure grid weights
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def log(self, message):
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)

    def start_download(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
            return

        # Disable button to prevent duplicate downloads.
        self.btn_download.config(state="disabled")
        self.log("Starting download...")

        # Run download in a separate thread.
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        # Build format string based on resolution selection.
        res = self.res_var.get()
        if res == "best":
            fmt = "best"
        else:
            try:
                # Strip the 'p' and convert to int.
                height = int(res[:-1])
            except ValueError:
                height = 720
            fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        # Set output template to include video id if possible.
        outtmpl = os.path.join(os.getcwd(), "downloaded_video.%(ext)s")
        ydl_opts = {
            "format": fmt,
            "outtmpl": outtmpl,
            # "verbose": True,  # Uncomment for more logs.
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.log("Download complete.")
                # Determine the output filename.
                filename = ydl.prepare_filename(info)
                self.log(f"Saved as: {filename}")
                # If auto-load is enabled, call the callback.
                if self.auto_load_var.get():
                    self.auto_load_callback(filename)
        except Exception as e:
            self.log(f"Download failed: {e}")
        finally:
            self.btn_download.config(state="normal")


# ----------------- Video Trimmer Tab -----------------

class TrimmerFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tasks = []  # Each task: {"video": path, "start": start, "end": end}
        self.current_video_file = None
        self.create_widgets()

    def create_widgets(self):
        # Task creation frame
        frame_task_create = tk.Frame(self)
        frame_task_create.pack(padx=10, pady=10, fill="x")
        btn_select_video = tk.Button(frame_task_create, text="Select Video for Task", command=self.select_video)
        btn_select_video.grid(row=0, column=0, padx=5, pady=5)
        self.lbl_current_video = tk.Label(frame_task_create, text="No video selected", width=40, anchor="w")
        self.lbl_current_video.grid(row=0, column=1, padx=5, pady=5)

        # Start Time spinboxes
        tk.Label(frame_task_create, text="Start Time:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        frame_start = tk.Frame(frame_task_create)
        frame_start.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.spin_start_hour = tk.Spinbox(frame_start, from_=0, to=23, width=3, format="%02.0f")
        self.spin_start_hour.pack(side="left")
        tk.Label(frame_start, text=":").pack(side="left")
        self.spin_start_minute = tk.Spinbox(frame_start, from_=0, to=59, width=3, format="%02.0f")
        self.spin_start_minute.pack(side="left")
        tk.Label(frame_start, text=":").pack(side="left")
        self.spin_start_second = tk.Spinbox(frame_start, from_=0, to=59, width=3, format="%02.0f")
        self.spin_start_second.pack(side="left")

        # End Time spinboxes
        tk.Label(frame_task_create, text="End Time:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        frame_end = tk.Frame(frame_task_create)
        frame_end.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.spin_end_hour = tk.Spinbox(frame_end, from_=0, to=23, width=3, format="%02.0f")
        self.spin_end_hour.pack(side="left")
        tk.Label(frame_end, text=":").pack(side="left")
        self.spin_end_minute = tk.Spinbox(frame_end, from_=0, to=59, width=3, format="%02.0f")
        self.spin_end_minute.pack(side="left")
        tk.Label(frame_end, text=":").pack(side="left")
        self.spin_end_second = tk.Spinbox(frame_end, from_=0, to=59, width=3, format="%02.0f")
        self.spin_end_second.pack(side="left")

        btn_add_task = tk.Button(frame_task_create, text="Add Trim Task", command=self.add_task)
        btn_add_task.grid(row=3, column=0, columnspan=2, pady=5)

        btn_preview = tk.Button(frame_task_create, text="Preview Range", command=self.preview_range)
        btn_preview.grid(row=4, column=0, columnspan=2, pady=5)

        # Preview Frame
        frame_preview = tk.Frame(self)
        frame_preview.pack(padx=10, pady=10, fill="x")
        tk.Label(frame_preview, text="Video Preview:").pack(anchor="w")
        self.video_preview = VideoPreview(frame_preview)

        # Queue Frame for tasks
        frame_queue = tk.Frame(self)
        frame_queue.pack(padx=10, pady=5, fill="both", expand=True)
        self.listbox_tasks = tk.Listbox(frame_queue)
        self.listbox_tasks.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame_queue, command=self.listbox_tasks.yview)
        scrollbar.pack(side="left", fill="y")
        self.listbox_tasks.config(yscrollcommand=scrollbar.set)

        frame_queue_buttons = tk.Frame(frame_queue)
        frame_queue_buttons.pack(side="left", padx=5)
        btn_remove = tk.Button(frame_queue_buttons, text="Remove", command=self.remove_task)
        btn_remove.pack(fill="x", pady=2)
        btn_up = tk.Button(frame_queue_buttons, text="Move Up", command=self.move_task_up)
        btn_up.pack(fill="x", pady=2)
        btn_down = tk.Button(frame_queue_buttons, text="Move Down", command=self.move_task_down)
        btn_down.pack(fill="x", pady=2)

        btn_start_queue = tk.Button(self, text="Start Queue", command=self.start_queue)
        btn_start_queue.pack(pady=10)

        # Log area
        self.text_log = tk.Text(self, height=8)
        self.text_log.pack(padx=10, pady=5, fill="both", expand=True)

    def log(self, message):
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)

    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4;*.mov;*.mkv;*.avi;*.webm"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_video_file = file_path
            self.lbl_current_video.config(text=os.path.basename(file_path))

    def load_video_for_trimming(self, video_file):
        """Called by the downloader when auto-load is enabled."""
        self.current_video_file = video_file
        self.lbl_current_video.config(text=os.path.basename(video_file))
        # Automatically load the video into the preview.
        self.video_preview.load_video(video_file)

    def preview_range(self):
        if not self.current_video_file:
            messagebox.showwarning("No Video Selected", "Please select a video file for preview.")
            return
        start = f"{int(self.spin_start_hour.get()):02}:{int(self.spin_start_minute.get()):02}:{int(self.spin_start_second.get()):02}"
        end = f"{int(self.spin_end_hour.get()):02}:{int(self.spin_end_minute.get()):02}:{int(self.spin_end_second.get()):02}"
        self.video_preview.load_video(self.current_video_file)
        self.video_preview.set_range(start, end)
        self.video_preview.player.play()
        self.video_preview.btn_play_pause.config(text="Pause")

    def add_task(self):
        if not self.current_video_file:
            messagebox.showwarning("No Video Selected", "Please select a video file for this task.")
            return
        start = f"{int(self.spin_start_hour.get()):02}:{int(self.spin_start_minute.get()):02}:{int(self.spin_start_second.get()):02}"
        end = f"{int(self.spin_end_hour.get()):02}:{int(self.spin_end_minute.get()):02}:{int(self.spin_end_second.get()):02}"
        task = {"video": self.current_video_file, "start": start, "end": end}
        self.tasks.append(task)
        self.update_task_listbox()
        self.current_video_file = None
        self.lbl_current_video.config(text="No video selected")
        self.reset_spinboxes()

    def reset_spinboxes(self):
        for spin in [self.spin_start_hour, self.spin_start_minute, self.spin_start_second,
                     self.spin_end_hour, self.spin_end_minute, self.spin_end_second]:
            spin.delete(0, tk.END)
            spin.insert(0, "00")

    def update_task_listbox(self):
        self.listbox_tasks.delete(0, tk.END)
        for idx, task in enumerate(self.tasks):
            video_name = os.path.basename(task["video"])
            self.listbox_tasks.insert(tk.END, f"{idx+1}: {video_name} | {task['start']} - {task['end']}")

    def remove_task(self):
        selection = self.listbox_tasks.curselection()
        if not selection:
            return
        index = selection[0]
        del self.tasks[index]
        self.update_task_listbox()

    def move_task_up(self):
        selection = self.listbox_tasks.curselection()
        if not selection:
            return
        index = selection[0]
        if index == 0:
            return
        self.tasks[index-1], self.tasks[index] = self.tasks[index], self.tasks[index-1]
        self.update_task_listbox()
        self.listbox_tasks.selection_set(index-1)

    def move_task_down(self):
        selection = self.listbox_tasks.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(self.tasks) - 1:
            return
        self.tasks[index], self.tasks[index+1] = self.tasks[index+1], self.tasks[index]
        self.update_task_listbox()
        self.listbox_tasks.selection_set(index+1)

    @staticmethod
    def time_to_seconds(t_str):
        parts = t_str.split(":")
        try:
            parts = [int(p) for p in parts]
        except ValueError:
            return None
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            return parts[0]*60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
        return None

    def start_queue(self):
        if not self.tasks:
            messagebox.showwarning("No Tasks", "No trim tasks in the queue.")
            return
        threading.Thread(target=self.process_queue, daemon=True).start()

    def process_queue(self):
        for idx, task in enumerate(self.tasks):
            video_file = task["video"]
            start = task["start"]
            end = task["end"]

            start_sec = self.time_to_seconds(start)
            end_sec = self.time_to_seconds(end)
            if start_sec is None or end_sec is None or end_sec <= start_sec:
                self.log(f"Task {idx+1}: Invalid time range (start: {start}, end: {end}). Skipping.")
                continue

            duration = end_sec - start_sec
            base, ext = os.path.splitext(video_file)
            output_file = f"{base}_trim_{idx+1}{ext}"

            cmd = [
                "ffmpeg", "-y",
                "-ss", start,
                "-i", video_file,
                "-t", str(duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                output_file
            ]
            self.log(f"Processing task {idx+1}: {os.path.basename(video_file)} {start} to {end} -> {os.path.basename(output_file)}")
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.log(f"Saved: {output_file}")
            except subprocess.CalledProcessError as e:
                self.log(f"Error processing task {idx+1}: {e}")
        self.log("Queue processing complete.")


# ----------------- Main Application -----------------

class ComprehensiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clip Farming Tool")
        self.create_widgets()

    def create_widgets(self):
        # Create Notebook (Tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Downloader tab
        self.downloader_frame = DownloaderFrame(self.notebook, self.auto_load_video)
        self.notebook.add(self.downloader_frame, text="YouTube Downloader")

        # Trimmer tab
        self.trimmer_frame = TrimmerFrame(self.notebook)
        self.notebook.add(self.trimmer_frame, text="Video Trimmer")

    def auto_load_video(self, video_file):
        # Switch to Trimmer tab and load the video.
        self.notebook.select(self.trimmer_frame)
        self.trimmer_frame.load_video_for_trimming(video_file)


def main():
    root = tk.Tk()
    app = ComprehensiveApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
