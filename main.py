"""
NBA Shorts AI - Main Streamlit Application
Automatically creates short-form NBA highlights from YouTube videos using AI
"""

import streamlit as st
import os
from pathlib import Path
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from modules.downloader import VideoDownloader
from modules.transcriber import AudioTranscriber
from modules.highlight_finder import HighlightFinder
from modules.vision_detector import VisionDetector
from modules.fusion import HighlightFusion
from modules.clipper import VideoClipper
from modules.overlay import CaptionOverlay

# Page configuration
st.set_page_config(
    page_title="NBA Shorts AI",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for NBA theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .stButton>button {
        background: linear-gradient(90deg, #c8102e 0%, #1d428a 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #a50d25 0%, #15306b 100%);
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #c8102e 0%, #1d428a 100%);
    }
    .highlight-box {
        background: rgba(29, 66, 138, 0.2);
        border-left: 4px solid #c8102e;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Header
    st.markdown("""
    # 🏀 NBA Shorts AI
    ### Create AI-powered NBA highlights from any YouTube video
    """)
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None
    if 'highlights' not in st.session_state:
        st.session_state.highlights = None
    if 'clips' not in st.session_state:
        st.session_state.clips = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key check
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            st.error("⚠️ Please set OPENROUTER_API_KEY in .env file")
        else:
            st.success("✅ API key configured")
        
        # Model selection
        st.subheader("Model Options")
        whisper_model = st.selectbox(
            "Whisper Model",
            ["tiny", "base", "small", "medium", "large"],
            index=1,
            help="Larger models are more accurate but slower"
        )
        
        num_highlights = st.slider(
            "Number of Highlights",
            min_value=1,
            max_value=10,
            value=5,
            help="How many highlight clips to generate"
        )
        
        clip_duration = st.slider(
            "Clip Duration (seconds)",
            min_value=15,
            max_value=60,
            value=30,
            help="Duration of each highlight clip"
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            enable_vision = st.checkbox("Enable Vision Analysis", value=True)
            add_titles = st.checkbox("Add Titles to Clips", value=True)
            add_subtitles = st.checkbox("Add Subtitles to Clips", value=True)
    
    # Main content
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        youtube_url = st.text_input(
            "Paste YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            disabled=st.session_state.processing
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        process_button = st.button(
            "🚀 Generate Highlights",
            disabled=st.session_state.processing or not youtube_url,
            use_container_width=True
        )
    
    if process_button and youtube_url:
        process_video(youtube_url, whisper_model, num_highlights, clip_duration, 
                     enable_vision, add_titles, add_subtitles)
    
    # Display results
    if st.session_state.clips:
        display_results()
    
    # Instructions
    with st.expander("📖 How to use"):
        st.markdown("""
        1. **Install Dependencies**: Run `pip install -r requirements.txt`
        2. **Set API Key**: Create a `.env` file with your OpenRouter API key
        3. **Install FFmpeg**: Make sure FFmpeg is installed on your system
        4. **Paste URL**: Enter any NBA YouTube video URL
        5. **Configure**: Adjust settings in the sidebar (optional)
        6. **Generate**: Click "Generate Highlights" and wait
        7. **Download**: Preview and download your AI-generated clips!
        
        **Note**: First run will download AI models (~500MB). Processing may take 5-15 minutes depending on video length.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using OpenAI Whisper, DeepSeek, CLIP, and Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


def process_video(url, whisper_model, num_highlights, clip_duration, 
                  enable_vision, add_titles, add_subtitles):
    """Process a YouTube video and generate highlights"""
    
    st.session_state.processing = True
    video_id = str(uuid.uuid4())[:8]
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Download video
        status_text.info("📥 Downloading video from YouTube...")
        downloader = VideoDownloader()
        video_path = downloader.download(url, video_id)
        progress_bar.progress(10)
        
        if not video_path or not Path(video_path).exists():
            st.error("❌ Failed to download video. Please check the URL.")
            st.session_state.processing = False
            return
        
        # Get video info
        video_info = downloader.get_video_info(url)
        st.session_state.video_info = video_info
        st.success(f"✅ Downloaded: {video_info.get('title', 'Unknown')}")
        
        # Step 2: Transcribe audio
        status_text.info("🎤 Transcribing audio with Whisper...")
        transcriber = AudioTranscriber(model_size=whisper_model)
        transcript = transcriber.transcribe(video_path)
        st.session_state.transcript = transcript
        progress_bar.progress(30)
        
        if not transcript.get("segments"):
            st.error("❌ Transcription failed.")
            st.session_state.processing = False
            return
        
        # Save transcript
        transcript_path = Path("output") / f"{video_id}_transcript.json"
        transcriber.save_transcript(transcript, str(transcript_path))
        
        # Display transcript preview
        with st.expander("📝 View Transcript"):
            st.json(transcript)
        
        st.success(f"✅ Transcribed {len(transcript['segments'])} segments")
        
        # Step 3: Find text highlights
        status_text.info("🤖 Analyzing transcript with AI...")
        finder = HighlightFinder()
        text_highlights = finder.find_highlights(transcript, top_k=num_highlights)
        progress_bar.progress(50)
        
        if not text_highlights:
            st.warning("⚠️ No text highlights found. Trying visual analysis...")
            text_highlights = []
        
        # Step 4: Visual detection (optional)
        visual_highlights = []
        if enable_vision:
            status_text.info("👁️ Analyzing video frames with CLIP...")
            detector = VisionDetector()
            visual_highlights = detector.detect_highlights(video_path)
            progress_bar.progress(65)
        
        # Step 5: Fuse highlights
        if text_highlights or visual_highlights:
            status_text.info("🔗 Combining text and visual highlights...")
            fusion = HighlightFusion()
            highlights = fusion.fuse(text_highlights, visual_highlights)
            st.session_state.highlights = highlights
            progress_bar.progress(70)
            
            # Display highlights
            st.subheader("🎯 Detected Highlights")
            for i, hl in enumerate(highlights, 1):
                st.markdown(f"""
                <div class="highlight-box">
                    <b>Highlight {i}</b> - {hl.get('timestamp', 0):.1f}s<br>
                    {hl.get('description', 'N/A')} | Score: {hl.get('score', 0):.2f}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ No highlights detected. Try adjusting settings or a different video.")
            st.session_state.processing = False
            return
        
        # Step 6: Create clips
        status_text.info("✂️ Creating video clips...")
        clipper = VideoClipper()
        clipper.clip_duration = clip_duration
        clips = clipper.create_all_clips(video_path, highlights)
        progress_bar.progress(85)
        
        # Step 7: Add overlays
        if clips and (add_titles or add_subtitles):
            status_text.info("🎨 Adding titles and subtitles...")
            overlay_tool = CaptionOverlay()
            
            processed_clips = []
            for clip_data in clips:
                processed_path = overlay_tool.process_clip(
                    clip_data['path'],
                    clip_data,
                    transcript['segments'],
                    add_title=add_titles,
                    add_subtitles=add_subtitles
                )
                clip_data['processed_path'] = processed_path
                processed_clips.append(clip_data)
            
            clips = processed_clips
            progress_bar.progress(95)
        
        st.session_state.clips = clips
        progress_bar.progress(100)
        
        status_text.success("✅ All highlights generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error processing video: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    finally:
        st.session_state.processing = False


def display_results():
    """Display generated clips with download options"""
    
    st.markdown("---")
    st.header("🎬 Generated Highlights")
    
    clips = st.session_state.clips
    if not clips:
        st.warning("No clips available")
        return
    
    # Display clips in columns
    num_cols = 2
    cols = st.columns(num_cols)
    
    for idx, clip_data in enumerate(clips):
        with cols[idx % num_cols]:
            st.markdown(f"""
            <div class="highlight-box">
                <h4>Highlight {idx + 1}</h4>
                <p>{clip_data.get('description', 'NBA Highlight')}</p>
                <p><small>Score: {clip_data.get('score', 0):.2f} | Time: {clip_data.get('timestamp', 0):.1f}s</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Video player
            final_path = clip_data.get('processed_path', clip_data.get('path'))
            if Path(final_path).exists():
                with open(final_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                    
                    # Download button
                    st.download_button(
                        label=f"⬇️ Download Clip {idx + 1}",
                        data=video_bytes,
                        file_name=f"nba_highlight_{idx + 1}.mp4",
                        mime="video/mp4",
                        key=f"download_{idx}"
                    )
            else:
                st.error(f"Clip file not found: {final_path}")
    
    # Download all button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⬇️ Download All Clips", use_container_width=True):
            # Create zip file
            import zipfile
            import shutil
            
            zip_path = Path("output/all_clips.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for idx, clip_data in enumerate(clips):
                    final_path = clip_data.get('processed_path', clip_data.get('path'))
                    if Path(final_path).exists():
                        zipf.write(final_path, f"highlight_{idx + 1}.mp4")
            
            if zip_path.exists():
                with open(zip_path, "rb") as zip_file:
                    st.download_button(
                        label="Download ZIP",
                        data=zip_file.read(),
                        file_name="nba_highlights.zip",
                        mime="application/zip"
                    )


if __name__ == "__main__":
    main()

