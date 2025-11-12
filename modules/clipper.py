"""
Video Clip Extraction Module
Uses FFmpeg to cut clips from the original video and format for YouTube Shorts
"""

from pathlib import Path
import subprocess
from typing import Dict, List
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import numpy as np
import cv2

try:
    from modules.ball_tracker import PlayerTracker
    TRACKING_AVAILABLE = True
except ImportError:
    TRACKING_AVAILABLE = False
    PlayerTracker = None


class VideoClipper:
    """Handles cutting video clips using FFmpeg and formatting for YouTube Shorts"""
    
    def __init__(self, output_dir: str = "output/clips", enable_ball_tracking: bool = True):
        """
        Initialize the clipper
        
        Args:
            output_dir: Directory to save clips
            enable_ball_tracking: Whether to track ball and center crop on it
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.clip_duration = 30  # 30 seconds for shorts
        self.shorts_width = 1080
        self.shorts_height = 1920  # 9:16 aspect ratio for YouTube Shorts
        self.enable_ball_tracking = enable_ball_tracking and TRACKING_AVAILABLE
        
        if self.enable_ball_tracking:
            self.tracker = PlayerTracker()
        else:
            self.tracker = None
    
    def create_clip(self, video_path: str, timestamp: float, clip_id: int, 
                    duration: float = None) -> str:
        """
        Create a video clip from the original video
        
        Args:
            video_path: Path to source video
            timestamp: Start time in seconds
            clip_id: Unique identifier for the clip
            duration: Clip duration (default: 30s)
            
        Returns:
            Path to created clip, or empty string if failed
        """
        if duration is None:
            duration = self.clip_duration
        
        output_path = self.output_dir / f"clip_{clip_id}.mp4"
        
        try:
            # Use FFmpeg to cut the clip
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(timestamp),
                "-t", str(duration),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-avoid_negative_ts", "make_zero",
                "-y",  # Overwrite output file
                str(output_path)
            ]
            
            # Run FFmpeg with suppressed output
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            
            if output_path.exists():
                # Format clip for YouTube Shorts (vertical 9:16) with ball tracking
                formatted_path = self.format_for_shorts(str(output_path), clip_id)
                return formatted_path if formatted_path else str(output_path)
            else:
                return ""
                
        except subprocess.CalledProcessError as e:
            print(f"Clip creation error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error creating clip: {e}")
            return ""
    
    def format_for_shorts(self, video_path: str, clip_id: int) -> str:
        """
        Format video clip for YouTube Shorts (9:16 vertical format, 1080x1920)
        With optional ball tracking to center crop on the ball
        
        Args:
            video_path: Path to input video clip
            clip_id: Clip identifier
            
        Returns:
            Path to formatted video, or empty string if failed
        """
        output_path = self.output_dir / f"clip_{clip_id}_shorts.mp4"
        
        try:
            if self.enable_ball_tracking and self.tracker:
                # Use MoviePy for dynamic ball-tracking-based cropping
                return self._format_with_ball_tracking(video_path, output_path, clip_id)
            else:
                # Use FFmpeg for simple center crop
                return self._format_simple_center_crop(video_path, output_path)
                
        except Exception as e:
            print(f"Error formatting for shorts: {e}")
            # Fallback to simple center crop
            return self._format_simple_center_crop(video_path, output_path)
    
    def _format_simple_center_crop(self, video_path: str, output_path: Path) -> str:
        """Simple center crop without tracking"""
        try:
            filter_complex = (
                f"scale=-1:{self.shorts_height},"
                f"crop={self.shorts_width}:{self.shorts_height}:"
                f"(iw-{self.shorts_width})/2:(ih-{self.shorts_height})/2,"
                f"scale={self.shorts_width}:{self.shorts_height},"
                f"setsar=1"
            )
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", filter_complex,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-profile:v", "high",
                "-level", "4.0",
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar", "44100",
                "-movflags", "+faststart",
                "-y",
                str(output_path)
            ]
            
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            
            if output_path.exists():
                try:
                    os.remove(video_path)
                except:
                    pass
                return str(output_path)
            return ""
        except Exception as e:
            print(f"Simple crop error: {e}")
            return ""
    
    def _format_with_ball_tracking(self, video_path: str, output_path: Path, clip_id: int) -> str:
        """Format with player tracking - dynamic crop that follows the player with the ball"""
        try:
            print(f"Tracking player with ball in clip {clip_id}...")
            
            # Track player positions
            player_positions = self.tracker.track_player_with_ball(video_path, start_time=0, 
                                                                   duration=self.clip_duration)
            
            if not player_positions:
                print("No player detected, using center crop")
                return self._format_simple_center_crop(video_path, output_path)
            
            # Load video with MoviePy
            clip = VideoFileClip(video_path)
            original_width, original_height = clip.size
            fps = clip.fps
            
            # Scale factor to fit height
            scale_factor = self.shorts_height / original_height
            scaled_width = int(original_width * scale_factor)
            
            # Frame counter for tracking
            frame_counter = [0]
            
            # Function to crop frame based on ball position
            def make_frame(frame):
                # Calculate current time from frame number
                current_time = frame_counter[0] / fps
                frame_counter[0] += 1
                
                # Find closest player position for this time
                if player_positions:
                    closest_pos = min(player_positions, key=lambda x: abs(x[0] - current_time))
                    _, player_x, player_y = closest_pos
                else:
                    # Fallback to center
                    player_x, player_y = original_width // 2, original_height // 2
                
                # Scale frame
                frame_scaled = cv2.resize(frame, (scaled_width, self.shorts_height))
                
                # Calculate crop region centered on player (offset slightly upward)
                player_x_scaled = int(player_x * scale_factor)
                player_y_scaled = int(player_y * scale_factor)
                offset_y = int(self.shorts_height * 0.1)  # Shift up 10% for better player framing
                
                crop_x = max(0, min(player_x_scaled - self.shorts_width // 2, 
                                   scaled_width - self.shorts_width))
                crop_y = max(0, min(player_y_scaled - self.shorts_height // 2 - offset_y, 
                                   self.shorts_height - self.shorts_height))
                
                # Crop
                frame_cropped = frame_scaled[crop_y:crop_y+self.shorts_height, 
                                            crop_x:crop_x+self.shorts_width]
                
                # If crop is smaller than target, pad it
                if frame_cropped.shape[0] < self.shorts_height or \
                   frame_cropped.shape[1] < self.shorts_width:
                    padded = np.zeros((self.shorts_height, self.shorts_width, 3), 
                                    dtype=np.uint8)
                    h, w = frame_cropped.shape[:2]
                    y_offset = (self.shorts_height - h) // 2
                    x_offset = (self.shorts_width - w) // 2
                    padded[y_offset:y_offset+h, x_offset:x_offset+w] = frame_cropped
                    frame_cropped = padded
                
                return frame_cropped
            
            # Create new clip with tracked cropping using fl_image
            tracked_clip = clip.fl_image(make_frame)
            
            # Write output
            tracked_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                bitrate='8000k',
                preset='medium',
                audio_bitrate='128k',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            clip.close()
            tracked_clip.close()
            
            if output_path.exists():
                try:
                    os.remove(video_path)
                except:
                    pass
                return str(output_path)
            return ""
            
        except Exception as e:
            print(f"Player tracking error: {e}, falling back to center crop")
            if 'clip' in locals():
                clip.close()
            return self._format_simple_center_crop(video_path, output_path)
    
    def create_all_clips(self, video_path: str, highlights: List[Dict]) -> List[Dict]:
        """
        Create clips for all highlights
        
        Args:
            video_path: Path to source video
            highlights: List of highlight dictionaries
            
        Returns:
            List of clips with metadata
        """
        clips = []
        
        for idx, highlight in enumerate(highlights):
            timestamp = highlight.get("timestamp", 0)
            
            # Create clip
            clip_path = self.create_clip(video_path, timestamp, idx)
            
            if clip_path:
                clips.append({
                    "id": idx,
                    "path": clip_path,
                    "timestamp": timestamp,
                    "description": highlight.get("description", ""),
                    "score": highlight.get("score", 0)
                })
        
        return clips

