import os
import threading
import yt_dlp
import re
from core.event_bus import event_bus

def sanitize_filename(title):
    """Removes invalid characters from a filename."""
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()

def get_video_title(url):
    """Fetches the YouTube video title using yt-dlp."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'force_generic_extractor': False,
        'extract_flat': True,  # Only extract metadata
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return sanitize_filename(info.get("title", "unknown_video"))
    except Exception as e:
        print(f"Error fetching title: {e}")
        return "unknown_video"

def download_video(url, resolution, auto_load):
    # Fetch the video title before downloading
    video_title = get_video_title(url)
    output_path = os.path.join(os.getcwd(), "videos/downloads/",f"{video_title}.%(ext)s")

    # Build format string based on resolution selection.
    if resolution == "best":
        fmt = "bestvideo+bestaudio/best"
    else:
        try:
            height = int(resolution[:-1])
        except ValueError:
            height = 720
        fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

    ydl_opts = {
        "format": fmt,
        "outtmpl": output_path,
    }

    def _download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                event_bus.publish("download_complete", filename)
        except Exception as e:
            event_bus.publish("download_failed", str(e))

    threading.Thread(target=_download, daemon=True).start()
