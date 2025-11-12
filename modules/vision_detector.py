"""
Visual Highlight Detection Module
Uses CLIP to analyze video frames and detect visually exciting moments
"""

import torch
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict

try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False


class VisionDetector:
    """Detects visually exciting moments using CLIP"""
    
    def __init__(self):
        """Initialize the vision detector"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.preprocess = None
    
    def load_model(self):
        """Load CLIP model"""
        if self.model is None:
            print("Loading CLIP model...")
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            self.model.eval()
    
    def detect_highlights(self, video_path: str, sample_interval: int = 2) -> List[Dict]:
        """
        Analyze video frames to find exciting moments
        
        Args:
            video_path: Path to video file
            sample_interval: Sample every N seconds
            
        Returns:
            List of potential highlight moments with timestamps and scores
        """
        if not CLIP_AVAILABLE:
            print("CLIP not available - visual detection skipped. Install CLIP for visual analysis.")
            return []
        
        self.load_model()
        
        # NBA action keywords for CLIP
        exciting_texts = [
            "spectacular dunk", "amazing block", "clutch shot", "incredible pass",
            "game-winning play", "fast break", "alley-oop", "deep three pointer",
            "steal and score", "poster dunk", "game-tying shot", "behind the back pass"
        ]
        
        try:
            # Prepare text encodings
            text_tokens = clip.tokenize(exciting_texts).to(self.device)
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            highlights = []
            frame_num = 0
            
            print(f"Analyzing video: {duration:.1f}s, sampling every {sample_interval}s")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_num / fps
                
                # Sample at intervals
                if frame_num % int(fps * sample_interval) == 0:
                    # Convert frame to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    
                    # Preprocess and encode
                    image_input = self.preprocess(frame_pil).unsqueeze(0).to(self.device)
                    
                    with torch.no_grad():
                        image_features = self.model.encode_image(image_input)
                        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                        
                        # Compute similarity scores
                        similarities = (image_features @ text_features.T).squeeze().cpu().numpy()
                        max_score = float(np.max(similarities))
                    
                    # Store if above threshold
                    if max_score > 0.25:  # Threshold for exciting moments
                        highlights.append({
                            "timestamp": current_time,
                            "score": max_score,
                            "description": exciting_texts[np.argmax(similarities)]
                        })
                
                frame_num += 1
            
            cap.release()
            
            # Sort by score and return top highlights
            highlights.sort(key=lambda x: x["score"], reverse=True)
            return highlights[:10]  # Return top 10 visual highlights
            
        except Exception as e:
            print(f"Vision detection error: {e}")
            return []

