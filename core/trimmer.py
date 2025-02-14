import os
import subprocess
import threading
from pathlib import Path
from core.event_bus import event_bus

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

def process_trim_tasks(tasks):
    def _process():
        root_dir = Path().resolve()  # Get the root directory of the project
        output_dir = root_dir / "videos" / "trimmed"
        output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists

        for idx, task in enumerate(tasks):
            video_file = task["video"]
            start = task["start"]
            end = task["end"]

            start_sec = time_to_seconds(start)
            end_sec = time_to_seconds(end)
            if start_sec is None or end_sec is None or end_sec <= start_sec:
                event_bus.publish("trim_task_failed", f"Task {idx+1}: Invalid time range (start: {start}, end: {end}). Skipping.")
                continue

            duration = end_sec - start_sec
            base, ext = os.path.splitext(os.path.basename(video_file))
            output_file = output_dir / f"{base}_trim_{idx+1}{ext}"

            cmd = [
                "ffmpeg", "-y",
                "-ss", start,
                "-i", video_file,
                "-t", str(duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                str(output_file)
            ]
            event_bus.publish("trim_task_started", f"Processing task {idx+1}: {os.path.basename(video_file)} {start} to {end} -> {output_file}")
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                event_bus.publish("trim_task_complete", f"Saved: {output_file}")
            except subprocess.CalledProcessError as e:
                event_bus.publish("trim_task_failed", f"Error processing task {idx+1}: {e}")
        event_bus.publish("trim_queue_complete", None)
        
    threading.Thread(target=_process, daemon=True).start()
