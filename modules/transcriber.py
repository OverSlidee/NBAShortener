"""
Audio Transcription Module
Uses OpenAI Whisper to transcribe video audio with timestamps
"""

import json
import whisper
from pathlib import Path
from typing import Dict, List, Optional


class AudioTranscriber:
    """Handles audio transcription using OpenAI Whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the transcriber
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
    
    def load_model(self):
        """Load the Whisper model"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
    
    def transcribe(self, video_path: str) -> Dict:
        """
        Transcribe audio from video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with transcription and segments
        """
        self.load_model()
        
        try:
            # Transcribe with timestamps
            result = self.model.transcribe(
                video_path,
                task="transcribe",
                verbose=False,
                word_timestamps=False
            )
            
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result["language"]
            }
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return {
                "text": "",
                "segments": [],
                "language": "unknown"
            }
    
    def save_transcript(self, transcript: Dict, output_path: str):
        """
        Save transcript to JSON file
        
        Args:
            transcript: Transcript dictionary
            output_path: Path to save the transcript
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
    
    def load_transcript(self, transcript_path: str) -> Dict:
        """
        Load transcript from JSON file
        
        Args:
            transcript_path: Path to transcript file
            
        Returns:
            Transcript dictionary
        """
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return json.load(f)

