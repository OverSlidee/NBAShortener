# 🚀 NBA Shorts AI - Quick Start Guide

## 3-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Verify FFmpeg is installed
ffmpeg -version
```

**If FFmpeg is not installed:**

- **Windows**: `choco install ffmpeg` or download from https://ffmpeg.org/download.html
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Step 2: Get API Key (1 minute)

1. Go to https://openrouter.ai/
2. Sign up (free tier available)
3. Copy your API key from dashboard
4. Create `.env` file in project root:

```bash
OPENROUTER_API_KEY=your_actual_api_key_here
DEEPSEEK_MODEL=deepseek/deepseek-chat
```

### Step 3: Run the App

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

## First Use

1. **Paste a YouTube URL** of any NBA highlights video
2. **Click "Generate Highlights"**
3. **Wait 5-15 minutes** (first run downloads AI models)
4. **Download your clips!**

## Example URLs to Try

- `https://www.youtube.com/watch?v=example` (any NBA highlights)
- Game highlights work best
- Look for videos with commentary

## Troubleshooting

**"API key not found"**
- Make sure `.env` file exists in project root
- Check API key is correct
- Restart the app

**"FFmpeg not found"**
- Install FFmpeg system-wide
- Restart terminal/IDE

**"Slow processing"**
- Use "tiny" or "base" Whisper model
- Disable Vision Analysis
- Use smaller videos

## Tips

✅ **Best Results:**
- 15-30 minute highlight videos
- Videos with clear commentary
- Recent games with good quality

❌ **Avoid:**
- Very old/low-quality videos
- Videos without commentary
- Extremely long videos (>60 min)

---

**Ready to create highlights? Run `streamlit run main.py` now!**

