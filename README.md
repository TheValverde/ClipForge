# ClipForge

ClipForge is a powerful, modular clip farming tool that streamlines the process of extracting high-quality clips from YouTube videos and local video files. Built with Python, ClipForge integrates a YouTube downloader (powered by yt-dlp) with a robust video trimmer and previewer (leveraging VLC and Tkinter) in a user-friendly, tabbed interface.

## Features

- **Integrated YouTube Downloader:**  
  Download videos from YouTube at your desired resolution with an option to automatically load the downloaded video into the trimmer.

- **Advanced Video Trimmer:**  
  Trim videos with precision using an intuitive GUI. Set start and end times with easy-to-use spinboxes, preview the clip in real-time with a VLC-based video player, and manage a queue of multiple clip tasks.

- **Modular and Extensible:**  
  Designed with a modular architecture so that each component (downloader, trimmer, previewer) can be maintained and extended independently. Perfect for scaling up as new features are added.

- **Clip Farming Workflow:**  
  Perfect for content creators and internal teams who need to extract clips quickly and efficiently, streamlining the process from download to final trim.

## Installation

### Prerequisites

- **Python 3.x**  
- **ffmpeg:** Make sure [ffmpeg](https://ffmpeg.org/) is installed and available in your system's PATH.
- **yt-dlp:**  
  Install using pip:  
  ```bash
  pip install yt-dlp
  ```
- **python-vlc:**  
  Install using pip:  
  ```bash
  pip install python-vlc
  ```
- **Tkinter:**  
  Typically included with Python installations. If not, install it according to your OS instructions.

### Clone the Repository

```bash
git clone https://github.com/yourusername/ClipForge.git
cd ClipForge
```

### Install Additional Dependencies

If you are using a virtual environment, activate it and run:

```bash
pip install -r requirements.txt
```

*(If a `requirements.txt` is not present, ensure that you have installed `yt-dlp` and `python-vlc` as shown above.)*

## Usage

To start ClipForge, simply run:

```bash
python main_app.py
```

### Workflow

1. **YouTube Downloader Tab:**  
   - Paste a YouTube URL.
   - Select the desired resolution from the dropdown.
   - Optionally enable "Auto-load into Trimmer" to automatically send the downloaded video to the trimmer.
   - Click **Download** and monitor progress in the log area.

2. **Video Trimmer Tab:**  
   - Load a local video (or use the auto-loaded video from the downloader).
   - Set the clip’s start and end times using the spinboxes.
   - Click **Preview Range** to verify the clip; the preview player will start playback from the specified start time.
   - Add the clip task to the queue and manage multiple tasks as needed.
   - Click **Start Queue** to process all tasks using ffmpeg.

## File Structure

ClipForge is organized into modular components:

- `video_preview.py` – Contains the `VideoPreview` class for handling video preview and playback.
- `downloader.py` – Encapsulates the YouTube downloader UI and logic.
- `trimmer.py` – Implements the video trimmer UI, task queue, and ffmpeg processing.
- `main_app.py` – Integrates all components into a tabbed interface and launches the application.

*Note: The repository is structured for easy expansion and maintenance. Feel free to refactor or add new modules as needed.*

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your improvements or bug fixes. For major changes, open an issue first to discuss what you would like to change.

## License

ClipForge is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the video downloading capabilities.
- [python-vlc](https://pypi.org/project/python-vlc/) for the video playback integration.
- All contributors and the open-source community for supporting tools that made this project possible.

---

Feel free to reach out via [GitHub Issues](https://github.com/yourusername/ClipForge/issues) for any questions, feedback, or support requests.

Happy clip farming with ClipForge!