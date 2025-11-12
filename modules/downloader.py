"""
YouTube Video Downloader Module
Downloads videos from YouTube using yt-dlp
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class VideoDownloader:
    """Handles downloading YouTube videos using yt-dlp"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the downloader
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def download(self, url: str, video_id: Optional[str] = None) -> Optional[str]:
        """
        Download a video from YouTube
        
        Args:
            url: YouTube video URL
            video_id: Optional video ID for naming the file
            
        Returns:
            Path to the downloaded video file, or None if download failed
        """
        try:
            # Generate output filename
            if video_id:
                filename = f"{video_id}.mp4"
            else:
                filename = "video.mp4"
            
            output_path = self.output_dir / filename
            
            # Download using yt-dlp
            cmd = [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "-o", str(output_path),
                "--no-playlist",
                url
            ]
            
            # Run download with suppressed output
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if output_path.exists():
                return str(output_path)
            else:
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Download error: {e.stderr}")
            return None
        except Exception as e:
            print(f"Unexpected error during download: {e}")
            return None
    
    def get_video_info(self, url: str) -> dict:
        """
        Get video metadata without downloading
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video info (title, duration, etc.)
        """
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                url
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            import json
            return json.loads(process.stdout)
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}

