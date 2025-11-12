# 🏀 NBA Shorts AI

**Automatically create short-form NBA highlights from any YouTube video using AI**

NBA Shorts AI is a complete Python + Streamlit application that analyzes YouTube videos using AI (text + vision) to automatically detect and create highlight clips ready for YouTube Shorts or TikTok.

## ✨ Features

- **Automatic Video Download**: Downloads NBA videos from YouTube using yt-dlp
- **AI Transcription**: Uses OpenAI Whisper for accurate audio transcription with timestamps
- **Smart Highlight Detection**: 
  - **Text Analysis**: DeepSeek AI analyzes transcripts to find exciting moments
  - **Visual Analysis**: CLIP vision model detects visually exciting plays
  - **Intelligent Fusion**: Combines both methods for optimal results
- **Video Clip Generation**: Extracts and processes 30-second highlight clips
- **Professional Overlays**: Adds titles, captions, and subtitles to clips
- **Beautiful UI**: Dark-themed Streamlit interface with NBA colors

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** - Web UI
- **yt-dlp** - YouTube video download
- **OpenAI Whisper** - Audio transcription
- **DeepSeek** (via OpenRouter) - Text analysis
- **CLIP** - Visual analysis
- **FFmpeg** - Video processing
- **MoviePy** - Video editing

## 📁 Project Structure

```
NBA tool/
├── main.py                  # Streamlit application
├── modules/
│   ├── __init__.py
│   ├── downloader.py       # YouTube download
│   ├── transcriber.py      # Whisper transcription
│   ├── highlight_finder.py # DeepSeek text analysis
│   ├── vision_detector.py  # CLIP visual analysis
│   ├── fusion.py           # Merge text + visual
│   ├── clipper.py          # FFmpeg clip extraction
│   └── overlay.py          # Captions & overlays
├── requirements.txt        # Python dependencies
├── env_example.txt        # Environment variables template
├── setup.py               # Setup verification script
├── README.md              # This file
├── QUICKSTART.md          # Quick start guide
├── PROJECT_SUMMARY.md     # Project summary
└── output/                # Generated clips and data
    └── clips/             # Final highlight clips
```

## 🚀 Installation

### Prerequisites

1. **Python 3.10+** installed
2. **FFmpeg** installed on your system
3. **OpenRouter API Key** (free tier available)

### FFmpeg Installation

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Setup Steps

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Verify installation (optional but recommended):**
```bash
python setup.py
```

3. **Set up environment variables:**
```bash
# Copy the example file
copy env_example.txt .env

# Edit .env and add your OpenRouter API key
# Get your API key from https://openrouter.ai/
```

4. **Create output directories:**
```bash
mkdir output
mkdir output\clips
```

Or run `python setup.py` to create them automatically.

## 🎮 Usage

### Running the Application

```bash
streamlit run main.py
```

The app will open in your default browser at `http://localhost:8501`

### How to Use

1. **Get OpenRouter API Key**
   - Sign up at https://openrouter.ai/
   - Get your API key from the dashboard
   - Add it to your `.env` file

2. **Find a YouTube Video**
   - Any NBA game highlights video
   - Example: "Lakers vs Warriors Game Highlights"

3. **Paste the URL**
   - Enter the YouTube link in the app

4. **Configure Settings** (Optional)
   - Select Whisper model size (larger = more accurate but slower)
   - Set number of highlights to generate
   - Choose clip duration
   - Enable/disable visual analysis, titles, subtitles

5. **Generate Highlights**
   - Click "🚀 Generate Highlights"
   - Wait 5-15 minutes (depending on video length)
   - First run will download AI models (~500MB)

6. **Download Your Clips**
   - Preview generated clips in the app
   - Download individual clips or all as ZIP
   - Upload to YouTube Shorts or TikTok!

## ⚙️ Configuration

### Whisper Models

- **tiny**: Fastest, least accurate (~40MB)
- **base**: Good balance (default, ~150MB)
- **small**: Better accuracy (~500MB)
- **medium**: High accuracy (~1.5GB)
- **large**: Best accuracy (~3GB)

### Clip Duration

Default is 30 seconds (ideal for Shorts/TikTok), adjustable from 15-60 seconds.

### Advanced Options

- **Vision Analysis**: Uses CLIP to detect visually exciting moments (slower but more comprehensive)
- **Add Titles**: Overlays clip title at the beginning
- **Add Subtitles**: Adds transcript-based subtitles to clips

## 📊 How It Works

1. **Download**: Uses yt-dlp to download video in best quality
2. **Transcribe**: Whisper converts audio to text with timestamps
3. **Text Analysis**: DeepSeek AI finds exciting moments in transcript
4. **Visual Analysis**: CLIP analyzes frames for exciting visuals (optional)
5. **Fusion**: Combines text + visual detections (within ±5s overlap)
6. **Extract**: FFmpeg cuts 30s clips from highlights
7. **Overlay**: MoviePy adds titles and subtitles
8. **Output**: Final clips ready for upload

## 🎯 Best Practices

- **Video Selection**: Choose videos with clear commentary/excitement
- **Video Length**: 15-30 minute highlight videos work best
- **First Run**: Expect longer processing time (model downloads)
- **GPU**: Faster processing if CUDA-compatible GPU available
- **Storage**: Ensure enough disk space for downloads and clips

## 🐛 Troubleshooting

**"No OPENROUTER_API_KEY found"**
- Create `.env` file with your API key
- Restart the app

**"FFmpeg not found"**
- Install FFmpeg system-wide
- Verify with: `ffmpeg -version`

**"Download failed"**
- Check internet connection
- Verify YouTube URL is valid
- YouTube may block downloads (rare)

**"Out of memory"**
- Use smaller Whisper model (tiny/base)
- Disable vision analysis
- Close other applications

**"CLIP model not found"**
- First run downloads models automatically
- Check internet connection
- Wait for download to complete

## 📝 Notes

- Processing time: ~5-15 minutes per video
- First run downloads AI models (~500MB)
- GPU recommended for faster processing
- Requires internet for API calls
- Output files stored in `output/` directory

## 🔧 Development

### Module Architecture

Each module is self-contained with a clean interface:

- `VideoDownloader`: Downloads YouTube videos
- `AudioTranscriber`: Whisper-based transcription
- `HighlightFinder`: DeepSeek API integration
- `VisionDetector`: CLIP visual analysis
- `HighlightFusion`: Combines detections
- `VideoClipper`: FFmpeg clip extraction
- `CaptionOverlay`: MoviePy overlays

### Adding New Features

1. Create new module in `modules/`
2. Import in `main.py`
3. Integrate into processing pipeline
4. Update UI if needed

## 📄 License

MIT License - feel free to modify and distribute

## 🙏 Credits

- **OpenAI** for Whisper and CLIP
- **DeepSeek** for AI analysis
- **OpenRouter** for API hosting
- **Streamlit** for the UI framework

## ⚠️ Disclaimer

This tool is for educational and personal use. Please respect YouTube's Terms of Service and copyright laws when using downloaded content.

## 🎉 Get Started!

1. Install dependencies
2. Add API key to `.env`
3. Run `streamlit run main.py`
4. Paste a YouTube URL
5. Generate your first AI highlight!

---

**Made with ❤️ for NBA fans**

