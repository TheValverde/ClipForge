# trimmer_frame.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from core.event_bus import event_bus
from core.trimmer import process_trim_tasks
from .video_preview import VideoPreview

class TrimmerFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tasks = []
        self.current_video_file = None
        self.create_widgets()
        event_bus.subscribe("auto_load_video", self.load_video_for_trimming)
        event_bus.subscribe("trim_task_started", self.on_trim_task_started)
        event_bus.subscribe("trim_task_complete", self.on_trim_task_complete)
        event_bus.subscribe("trim_task_failed", self.on_trim_task_failed)
        event_bus.subscribe("trim_queue_complete", self.on_trim_queue_complete)

    def create_widgets(self):
        frame_task_create = tk.Frame(self)
        frame_task_create.pack(padx=10, pady=10, fill="x")
        btn_select_video = tk.Button(frame_task_create, text="Select Video for Task", command=self.select_video)
        btn_select_video.grid(row=0, column=0, padx=5, pady=5)
        self.lbl_current_video = tk.Label(frame_task_create, text="No video selected", width=40, anchor="w")
        self.lbl_current_video.grid(row=0, column=1, padx=5, pady=5)

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

        frame_preview = tk.Frame(self)
        frame_preview.pack(padx=10, pady=10, fill="x")
        tk.Label(frame_preview, text="Video Preview:").pack(anchor="w")
        self.video_preview = VideoPreview(frame_preview)

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

        self.btn_start_queue = tk.Button(self, text="Start Queue", command=self.start_queue)
        self.btn_start_queue.pack(pady=10)

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
        self.current_video_file = video_file
        self.lbl_current_video.config(text=os.path.basename(video_file))
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
        for spin in [
            self.spin_start_hour,
            self.spin_start_minute,
            self.spin_start_second,
            self.spin_end_hour,
            self.spin_end_minute,
            self.spin_end_second
        ]:
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

    def start_queue(self):
        if not self.tasks:
            messagebox.showwarning("No Tasks", "No trim tasks in the queue.")
            return
        self.btn_start_queue.config(state="disabled")
        process_trim_tasks(self.tasks)

    def on_trim_task_started(self, message):
        self.log(message)

    def on_trim_task_complete(self, message):
        self.log(message)

    def on_trim_task_failed(self, message):
        self.log(message)

    def on_trim_queue_complete(self, _):
        self.log("Queue processing complete.")
        self.btn_start_queue.config(state="normal")
