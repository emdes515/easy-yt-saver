import os
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, StringVar, BooleanVar
import logging
import json
import yt_dlp
from PIL import Image, ImageTk
import urllib.request
import urllib.parse
import io
import subprocess


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        self.root.configure(padx=10, pady=10)

        # Set application icon
        try:
            if os.path.exists("youtube_icon.ico"):
                self.root.iconbitmap("youtube_icon.ico")
        except Exception:
            # Icon not found or not supported, continue without icon
            pass

        # Variables
        self.url_var = StringVar()
        self.download_path_var = StringVar()
        self.format_var = StringVar(value="mp3")
        self.progress_var = StringVar(value="0%")
        self.progress_value = tk.DoubleVar(value=0.0)
        self.download_thread = None
        self.is_downloading = BooleanVar(value=False)
        self.current_task = None
        self.video_title = StringVar()
        self.quality_var = StringVar()

        # Load saved settings
        self.settings_file = "settings.json"

        # Configure logging
        self.setup_logging()

        # Now load settings after logging is set up
        self.load_settings()

        # Create UI
        self.create_widgets()

        # Quality options for MP3 and MP4
        self.mp3_qualities = ["128kbps", "192kbps", "256kbps", "320kbps"]
        self.mp4_qualities = ["360p", "480p", "720p", "1080p", "Best"]
        self.update_quality_options()

        # Check for FFmpeg
        self.root.after(1000, self.check_ffmpeg)

    def setup_logging(self):
        self.log_handler = None
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger("YouTubeDownloader")

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL section
        url_frame = ttk.LabelFrame(main_frame, text="YouTube URL")
        url_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(url_frame, text="URL:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        ttk.Entry(url_frame, textvariable=self.url_var, width=50).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E
        )
        ttk.Button(url_frame, text="Fetch", command=self.fetch_video_info).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Video title display
        ttk.Label(url_frame, text="Title:").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        ttk.Label(url_frame, textvariable=self.video_title, wraplength=400).grid(
            row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W
        )

        # Thumbnail frame (will be populated when URL is fetched)
        self.thumbnail_frame = ttk.LabelFrame(main_frame, text="Thumbnail")
        self.thumbnail_frame.pack(fill=tk.X, padx=5, pady=5)
        self.thumbnail_label = ttk.Label(self.thumbnail_frame)
        self.thumbnail_label.pack(padx=5, pady=5)

        # Download location section
        path_frame = ttk.LabelFrame(main_frame, text="Download Location")
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(path_frame, text="Save to:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        ttk.Entry(path_frame, textvariable=self.download_path_var, width=50).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E
        )
        ttk.Button(path_frame, text="Browse", command=self.browse_directory).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Format section
        format_frame = ttk.LabelFrame(main_frame, text="Format Options")
        format_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Radiobutton(
            format_frame,
            text="Audio (MP3)",
            variable=self.format_var,
            value="mp3",
            command=self.update_quality_options,
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(
            format_frame,
            text="Video (MP4)",
            variable=self.format_var,
            value="mp4",
            command=self.update_quality_options,
        ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(format_frame, text="Quality:").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.quality_combobox = ttk.Combobox(
            format_frame, textvariable=self.quality_var, state="readonly", width=10
        )
        self.quality_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Download Progress")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_value, length=100, mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(padx=5, pady=2)

        # Action buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        self.download_button = ttk.Button(
            buttons_frame, text="Download", command=self.start_download
        )
        self.download_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.cancel_download,
            state=tk.DISABLED,
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            log_frame, wrap=tk.WORD, height=10, yscrollcommand=scrollbar.set
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.log_text.yview)

        # Configure log handler
        self.log_handler = logging.StreamHandler(io.StringIO())
        self.log_handler.setLevel(logging.INFO)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(self.log_handler)

        # Start log update timer
        self.root.after(100, self.update_log)

    def update_quality_options(self):
        if self.format_var.get() == "mp3":
            self.quality_combobox["values"] = self.mp3_qualities
            self.quality_var.set(self.mp3_qualities[-1])  # Default to highest quality
        else:
            self.quality_combobox["values"] = self.mp4_qualities
            self.quality_var.set(self.mp4_qualities[-1])  # Default to highest quality

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path_var.set(directory)
            self.save_settings()

    def fetch_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            self.logger.error("Please enter a YouTube URL")
            return

        if not self.is_valid_youtube_url(url):
            self.logger.error("Invalid YouTube URL")
            return

        self.logger.info(f"Fetching video information for: {url}")

        def fetch_thread():
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", "Unknown Title")

                    # Update UI elements in the main thread
                    self.root.after(0, lambda: self.video_title.set(title))
                    self.root.after(
                        0, lambda: self.logger.info(f"Video title: {title}")
                    )

                    # Fetch thumbnail
                    thumbnail_url = info.get("thumbnail")
                    if thumbnail_url:
                        try:
                            response = urllib.request.urlopen(thumbnail_url)
                            data = response.read()
                            image = Image.open(io.BytesIO(data))

                            # Resize thumbnail to fit in the UI
                            image = image.resize((200, 120), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(image)

                            # Update thumbnail in the main thread
                            self.root.after(0, lambda: self.update_thumbnail(photo))
                        except Exception as e:
                            self.root.after(
                                0,
                                lambda: self.logger.error(
                                    f"Error loading thumbnail: {str(e)}"
                                ),
                            )
            except Exception as e:
                self.root.after(
                    0, lambda: self.logger.error(f"Error fetching video info: {str(e)}")
                )

        threading.Thread(target=fetch_thread, daemon=True).start()

    def update_thumbnail(self, photo):
        self.thumbnail_photo = photo  # Keep a reference to prevent garbage collection
        self.thumbnail_label.config(image=photo)

    def is_valid_youtube_url(self, url):
        youtube_regex = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
        return bool(re.match(youtube_regex, url))

    def sanitize_filename(self, filename):
        # Remove invalid characters for filenames
        invalid_chars = r'[\\/*?:"<>|]'
        return re.sub(invalid_chars, "_", filename)

    def start_download(self):
        url = self.url_var.get().strip()
        download_path = self.download_path_var.get()

        if not url:
            self.logger.error("Please enter a YouTube URL")
            return

        if not download_path:
            self.logger.error("Please select a download location")
            return

        if not os.path.exists(download_path):
            self.logger.error(f"Download path does not exist: {download_path}")
            return

        if not self.is_valid_youtube_url(url):
            self.logger.error("Invalid YouTube URL")
            return

        # Update UI for download state
        self.is_downloading.set(True)
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_value.set(0)
        self.progress_var.set("0%")

        # Save settings
        self.save_settings()

        # Start download in a separate thread
        self.download_thread = threading.Thread(target=self.download_video, daemon=True)
        self.download_thread.start()

    def download_video(self):
        url = self.url_var.get().strip()
        download_path = self.download_path_var.get()
        file_format = self.format_var.get()
        quality = self.quality_var.get()

        self.logger.info(f"Starting download: {url}")
        self.logger.info(f"Format: {file_format.upper()}, Quality: {quality}")

        try:
            output_template = os.path.join(download_path, "%(title)s.%(ext)s")

            ydl_opts = {
                "outtmpl": output_template,
                "progress_hooks": [self.progress_hook],
                "quiet": True,
                "no_warnings": True,
            }

            if file_format == "mp3":
                # Audio download options
                bitrate = quality.replace("kbps", "")
                ydl_opts.update(
                    {
                        "format": "bestaudio/best",
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": bitrate,
                            }
                        ],
                    }
                )
            else:
                # Video download options
                if quality == "Best":
                    format_code = (
                        "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                    )
                else:
                    height = quality.replace("p", "")
                    format_code = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best"

                ydl_opts.update(
                    {
                        "format": format_code,
                        "merge_output_format": "mp4",
                    }
                )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.current_task = ydl
                ydl.download([url])

            self.root.after(
                0, lambda: self.logger.info("Download completed successfully")
            )
        except Exception as e:
            error_message = str(e)
            self.root.after(
                0,
                lambda error=error_message: self.logger.error(
                    f"Download error: {error}"
                ),
            )
        finally:
            self.current_task = None
            self.root.after(0, self.reset_download_state)

    def progress_hook(self, d):
        if d["status"] == "downloading":
            # Calculate progress
            if "total_bytes" in d and d["total_bytes"] > 0:
                percentage = (d["downloaded_bytes"] / d["total_bytes"]) * 100
            elif "total_bytes_estimate" in d and d["total_bytes_estimate"] > 0:
                percentage = (d["downloaded_bytes"] / d["total_bytes_estimate"]) * 100
            else:
                # Can't calculate percentage, show indeterminate progress
                percentage = -1

            # Format download speed
            if "speed" in d and d["speed"] is not None:
                speed = d["speed"] / 1024 / 1024  # Convert to MB/s
                speed_str = f"{speed:.2f} MB/s"
            else:
                speed_str = "N/A"

            # Update UI in main thread
            if percentage >= 0:
                self.root.after(0, lambda: self.progress_value.set(percentage))
                self.root.after(
                    0, lambda: self.progress_var.set(f"{percentage:.1f}% ({speed_str})")
                )
            else:
                self.root.after(
                    0, lambda: self.progress_var.set(f"Downloading... ({speed_str})")
                )

            # Log progress occasionally (every 10%)
            if "downloaded_bytes" in d and "total_bytes" in d:
                if (
                    int(percentage) % 10 == 0
                    and hasattr(self, "last_logged_percent")
                    and self.last_logged_percent != int(percentage)
                ):
                    self.last_logged_percent = int(percentage)
                    mb_down = d["downloaded_bytes"] / 1024 / 1024
                    mb_total = d["total_bytes"] / 1024 / 1024
                    self.root.after(
                        0,
                        lambda: self.logger.info(
                            f"Downloaded {mb_down:.1f}MB of {mb_total:.1f}MB ({percentage:.1f}%)"
                        ),
                    )

            if not hasattr(self, "last_logged_percent"):
                self.last_logged_percent = 0

        elif d["status"] == "finished":
            self.root.after(
                0, lambda: self.logger.info("Download finished, now processing...")
            )
            self.root.after(0, lambda: self.progress_var.set("Processing..."))

    def cancel_download(self):
        if self.current_task:
            self.logger.info("Cancelling download...")
            # yt-dlp doesn't support direct cancellation, but we can reset the UI state
            self.reset_download_state()

    def reset_download_state(self):
        self.is_downloading.set(False)
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.current_task = None

    def update_log(self):
        # Get log content from handler
        if self.log_handler and hasattr(self.log_handler, "stream"):
            log_stream = self.log_handler.stream
            log_content = log_stream.getvalue()
            if log_content:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_content)
                self.log_text.config(state=tk.DISABLED)
                self.log_text.see(tk.END)
                # Clear the stream
                log_stream.truncate(0)
                log_stream.seek(0)

        # Schedule next update
        self.root.after(100, self.update_log)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                    download_path = settings.get("download_path", "")
                    if download_path and os.path.exists(download_path):
                        self.download_path_var.set(download_path)
                    self.logger.info(f"Loaded settings from {self.settings_file}")
            else:
                # Set default download path to user's Downloads folder
                default_download_path = os.path.join(
                    os.path.expanduser("~"), "Downloads"
                )
                self.download_path_var.set(default_download_path)
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            # Set default download path to user's Downloads folder as fallback
            default_download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            self.download_path_var.set(default_download_path)

    def save_settings(self):
        try:
            settings = {"download_path": self.download_path_var.get()}
            with open(self.settings_file, "w") as f:
                json.dump(settings, f)
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")

    def check_ffmpeg(self):
        """Check if FFmpeg is installed and available in PATH"""
        try:
            with open(os.devnull, "w") as devnull:
                subprocess_result = subprocess.call(
                    ["ffmpeg", "-version"], stdout=devnull, stderr=devnull
                )
                if subprocess_result != 0:
                    self.logger.warning(
                        "FFmpeg not found! MP3 conversion and some video formats will not work."
                    )
                    self.logger.warning(
                        "Please install FFmpeg: https://ffmpeg.org/download.html"
                    )
                else:
                    self.logger.info("FFmpeg detected. Full functionality available.")
        except Exception:
            self.logger.warning(
                "FFmpeg not found! MP3 conversion and some video formats will not work."
            )
            self.logger.warning(
                "Please install FFmpeg: https://ffmpeg.org/download.html"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
