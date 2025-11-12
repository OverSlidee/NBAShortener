"""
Caption and Overlay Module
Adds subtitles and title overlays to clips using MoviePy
"""

from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.credits import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from typing import Dict, List, Optional
import os


class CaptionOverlay:
    """Adds captions and overlays to video clips"""
    
    def __init__(self, font_size: int = 40, font_color: str = "white"):
        """
        Initialize the overlay tool
        
        Args:
            font_size: Size of caption text
            font_color: Color of caption text
        """
        self.font_size = font_size
        self.font_color = font_color
    
    def add_title(self, video_path: str, title: str, output_path: str, 
                  duration: float = 3.0) -> str:
        """
        Add a title overlay to the beginning of a video
        
        Args:
            video_path: Path to input video
            title: Title text
            duration: How long to show title (seconds)
            
        Returns:
            Path to output video with title
        """
        try:
            video = VideoFileClip(video_path)
            
            # Create title text clip
            txt_clip = TextClip(
                title,
                fontsize=self.font_size,
                color=self.font_color,
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            ).set_duration(duration).set_position('center')
            
            # Composite with video
            final = CompositeVideoClip([video, txt_clip.set_start(0)])
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            video.close()
            final.close()
            
            return output_path
            
        except Exception as e:
            print(f"Title overlay error: {e}")
            return video_path  # Return original if failed
    
    def add_subtitles(self, video_path: str, transcript_segments: List[Dict], 
                      output_path: str) -> str:
        """
        Add subtitles to video from transcript segments
        
        Args:
            video_path: Path to input video
            transcript_segments: List of transcript segments with timestamps
            output_path: Path to save output video
            
        Returns:
            Path to output video with subtitles
        """
        try:
            video = VideoFileClip(video_path)
            
            # Find relevant segments for this clip
            clip_duration = video.duration
            relevant_segments = [
                seg for seg in transcript_segments
                if 0 <= seg.get("start", 0) < clip_duration
            ]
            
            # Create text clips for each segment
            text_clips = []
            for seg in relevant_segments:
                start = seg.get("start", 0)
                end = seg.get("end", clip_duration)
                text = seg.get("text", "").strip()
                
                if text and 0 <= start < clip_duration:
                    txt_clip = TextClip(
                        text,
                        fontsize=self.font_size,
                        color=self.font_color,
                        font='Arial',
                        stroke_color='black',
                        stroke_width=2,
                        bg_color='black',
                        size=(video.w, None),
                        method='caption'
                    ).set_duration(end - start).set_position(('center', 'bottom')).set_start(start)
                    
                    text_clips.append(txt_clip)
            
            # Composite video with subtitles
            if text_clips:
                final = CompositeVideoClip([video] + text_clips)
            else:
                final = video
            
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            video.close()
            final.close()
            for clip in text_clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"Subtitle overlay error: {e}")
            return video_path  # Return original if failed
    
    def process_clip(self, clip_path: str, clip_metadata: Dict, 
                     transcript_segments: List[Dict], add_title: bool = True,
                     add_subtitles: bool = True) -> str:
        """
        Process a clip with title and subtitles
        
        Args:
            clip_path: Path to input clip
            clip_metadata: Metadata about the clip
            transcript_segments: Transcript segments
            add_title: Whether to add title
            add_subtitles: Whether to add subtitles
            
        Returns:
            Path to processed clip
        """
        output_path = clip_path.replace(".mp4", "_final.mp4")
        current_path = clip_path
        
        # Add title first
        if add_title:
            title = clip_metadata.get("description", "NBA Highlight")
            current_path = self.add_title(current_path, title, output_path, duration=3)
        
        # Add subtitles
        if add_subtitles:
            final_output = current_path.replace("_final.mp4", "_with_subs.mp4")
            current_path = self.add_subtitles(current_path, transcript_segments, final_output)
        
        return current_path if current_path != clip_path else clip_path

