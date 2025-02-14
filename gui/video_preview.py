# video_preview.py

import os
import tkinter as tk
import vlc

class VideoPreview:
    def __init__(self, parent):
        self.parent = parent
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.preview_start_ms = 0
        self.preview_end_ms = 0
        self.slider_dragging = False

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

        self.slider = tk.Scale(
            self.controls_frame,
            from_=0,
            to=100,
            orient="horizontal",
            command=self.on_slider_move,
            length=200
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=5)
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.update_slider()

    def load_video(self, video_file):
        self.media = self.instance.media_new(video_file)
        self.player.set_media(self.media)
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
            seconds = parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            seconds = parts[0]*60 + parts[1]
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
