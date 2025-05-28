# 🎵 Easy YT Saver

<div align="center">

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-required-red.svg?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge)
![License](https://img.shields.io/badge/License-Open_Source-green.svg?style=for-the-badge)

<br>
<a href="https://github.com/emdes515/easy-yt-saver/releases">
  <img src="https://img.shields.io/badge/Download-Latest_Release-2ea44f?style=for-the-badge&logo=github" alt="Download Latest Release">
</a>

</div>

A modern, user-friendly GUI application for downloading YouTube videos as MP3 audio or MP4 video
files.

## ✨ Features

- 🎵 Download YouTube videos as MP3 audio files
- 📹 Download YouTube videos as MP4 video files
- 🔍 Select quality options for both audio and video formats
- 🖼️ Preview video thumbnail and title before downloading
- 📊 Show download progress with percentage and speed
- 📝 Log window to display application messages
- 💾 Saves last used download directory
- 🎨 Clean and modern user interface

## 📋 Requirements

- Python 3.6 or higher
- FFmpeg (REQUIRED for MP3 conversion and video processing)
- Required Python packages:
  - yt-dlp
  - pillow

## 🔧 Installation

### 1. Clone or download this repository

```bash
git clone https://github.com/mateuszjankowski/youtube-downloader.git
cd youtube-downloader
```

### 2. Install the required Python packages

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (Required)

FFmpeg is essential for audio extraction and video processing. Here are detailed installation
instructions:

#### Windows Installation Options

##### Option 1: Using Scoop (Recommended)

1. **Install Scoop** (if not already installed):

   Open PowerShell and run:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   irm get.scoop.sh | iex
   ```

2. **Install FFmpeg** using Scoop:

   ```powershell
   scoop install ffmpeg
   ```

##### Option 2: Manual Installation

1. Download the FFmpeg build from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the zip file to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH:
   - Right-click on 'This PC' or 'My Computer' and select 'Properties'
   - Click on 'Advanced system settings'
   - Click on 'Environment Variables'
   - Under 'System variables', find and select 'Path', then click 'Edit'
   - Click 'New' and add the path to the `bin` folder (e.g., `C:\ffmpeg\bin`)
   - Click 'OK' on all dialogs to save the changes

#### macOS

Using Homebrew:

```bash
brew install ffmpeg
```

#### Linux

```bash
sudo apt install ffmpeg  # For Debian/Ubuntu
# or
sudo dnf install ffmpeg  # For Fedora
```

## 🚀 Usage

Run the application:

```bash
python youtube_downloader.py
```

1. Enter a YouTube URL in the URL field and click "Fetch" to load video details
2. Select your desired output format (MP3 or MP4) and quality
3. Choose a download directory (defaults to your Downloads folder)
4. Click "Download" to start the download process
5. Monitor progress in the progress bar and log window

## ❓ Troubleshooting

If you see an error message like "You have requested merging of multiple formats but ffmpeg is not
installed", you need to install FFmpeg as described in the Installation section.

After installing FFmpeg, you may need to restart your computer for the changes to take effect.

To verify FFmpeg is properly installed, open a command prompt or terminal and type:

```bash
ffmpeg -version
```

## 👨‍💻 Author

**Mateusz Jankowski**

- GitHub: [mateuszjankowski](https://github.com/mateuszjankowski)

## 📄 License

This project is open source and available for personal and educational use.

---

<div align="center">
<p>⭐ If you find this tool useful, please consider giving it a star! ⭐</p>
</div>
